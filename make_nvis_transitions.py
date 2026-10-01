import csv
import subprocess
from collections import defaultdict

RASTER = "/Users/thevnikalansuriya/Desktop/nvis_transition_codes.tif"
OUTPUT = "data/nvis_family_transitions.csv"

# ---------------------------------------------------------
# Author-derived display families used throughout the site.
# These group official NVIS Major Vegetation Groups (MVGs)
# into broader storytelling categories.
# ---------------------------------------------------------

FAMILY = {}

def add(codes, name):
    for code in codes:
        FAMILY[code] = name

add([1], "Rainforest")
add([2, 3, 4, 5, 11, 12], "Eucalypt forest & woodland")
add([6, 13, 16], "Acacia")
add([7, 8, 9, 10, 23, 31], "Other forest & woodland")
add([14, 15, 17, 18, 22, 32], "Shrubland")
add([19, 20, 21], "Grassland")
add([24, 26, 27], "Other native vegetation")
add([25, 29], "Modified / non-native")

# Sea / estuaries and unknown/no-data are intentionally excluded.
EXCLUDED = {0, 28, 99}

# Each original raster cell is 100 m x 100 m = 1 hectare.
# Therefore:
# 1 cell = 1 ha = 0.000001 million hectares.
MHA_PER_CELL = 0.000001

counts = defaultdict(int)

print("Reading transition raster in blocks...")
print("This may take a few minutes.")

# Get raster dimensions.
info = subprocess.check_output(
    ["gdalinfo", "-json", RASTER],
    text=True
)

import json
metadata = json.loads(info)

width = metadata["size"][0]
height = metadata["size"][1]

# Process strips rather than loading the entire ~1.5B-cell raster.
BLOCK_HEIGHT = 500

for y in range(0, height, BLOCK_HEIGHT):

    rows = min(BLOCK_HEIGHT, height - y)

    cmd = [
        "gdal_translate",
        "-q",
        "-srcwin",
        "0", str(y),
        str(width), str(rows),
        "-of", "XYZ",
        RASTER,
        "/vsistdout/"
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1024 * 1024
    )

    for line in process.stdout:
        parts = line.split()

        if len(parts) < 3:
            continue

        try:
            transition = int(float(parts[2]))
        except ValueError:
            continue

        if transition <= 0:
            continue

        pre_code = transition // 100
        ext_code = transition % 100

        if pre_code in EXCLUDED or ext_code in EXCLUDED:
            continue

        pre_family = FAMILY.get(pre_code)
        ext_family = FAMILY.get(ext_code)

        if pre_family is None or ext_family is None:
            continue

        counts[(pre_family, ext_family)] += 1

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(
            f"gdal_translate failed while processing rows {y}-{y+rows}"
        )

    percent = min(100, ((y + rows) / height) * 100)

    print(
        f"\rProcessed {percent:5.1f}% "
        f"({min(y + rows, height):,}/{height:,} rows)",
        end="",
        flush=True
    )

print("\n\nWriting CSV...")

rows_out = []

for (pre_family, ext_family), cell_count in counts.items():

    area_mha = cell_count * MHA_PER_CELL

    rows_out.append({
        "from_family": pre_family,
        "to_family": ext_family,
        "cell_count": cell_count,
        "area_mha": round(area_mha, 6)
    })

rows_out.sort(
    key=lambda x: (
        x["from_family"],
        -x["area_mha"],
        x["to_family"]
    )
)

with open(OUTPUT, "w", newline="", encoding="utf-8") as f:

    writer = csv.DictWriter(
        f,
        fieldnames=[
            "from_family",
            "to_family",
            "cell_count",
            "area_mha"
        ]
    )

    writer.writeheader()
    writer.writerows(rows_out)

print(f"\nCreated: {OUTPUT}")
print(f"Transition combinations: {len(rows_out)}")
print(
    "Total mapped transition area: "
    f"{sum(r['area_mha'] for r in rows_out):,.2f} Mha"
)

print("\nLargest transitions:")

for row in sorted(
    rows_out,
    key=lambda x: x["area_mha"],
    reverse=True
)[:15]:

    print(
        f"{row['from_family']:<30} -> "
        f"{row['to_family']:<30} "
        f"{row['area_mha']:>8.2f} Mha"
    )

