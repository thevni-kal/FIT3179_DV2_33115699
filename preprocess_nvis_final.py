import csv
import json
import re
from pathlib import Path

# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

DESKTOP = Path("/Users/thevnikalansuriya/Desktop")
PROJECT = Path("/Users/thevnikalansuriya/Documents/GitHub/FIT3179_DV2_33115699")
DATA = PROJECT / "data"

PRE_GEOJSON = DESKTOP / "nvis_pre1750_fixed.geojson"
EXT_GEOJSON = DESKTOP / "nvis_extant_fixed.geojson"

PRE_RAT = DESKTOP / "pre_rat_full.txt"
EXT_RAT = DESKTOP / "ext_rat_full.txt"

OUT_PRE = DATA / "nvis_pre1750_mvg.geojson"
OUT_EXT = DATA / "nvis_extant_mvg.geojson"
OUT_CSV = DATA / "nvis_mvg_change.csv"

DATA.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------
# READ GDAL RASTER ATTRIBUTE TABLE
# ---------------------------------------------------------

def read_rat(path):
    text = path.read_text(encoding="utf-8")

    rows = re.findall(
        r'<Row index="\d+">(.*?)</Row>',
        text,
        flags=re.DOTALL
    )

    result = {}

    for row in rows:
        values = re.findall(r"<F>(.*?)</F>", row, flags=re.DOTALL)

        # Expected:
        # Value, Count, MVG_NAME, MVG_COMMON_DESC, SORT_ORDER
        if len(values) < 5:
            continue

        try:
            code = int(float(values[0]))
            count = int(round(float(values[1])))
        except ValueError:
            continue

        result[code] = {
            "mvg": code,
            "count": count,
            "mvg_name": values[2].strip(),
            "description": values[3].strip(),
            "sort_order": int(float(values[4]))
        }

    return result


pre = read_rat(PRE_RAT)
ext = read_rat(EXT_RAT)

print(f"Read {len(pre)} PRE classes")
print(f"Read {len(ext)} EXT classes")

# ---------------------------------------------------------
# MASTER MVG METADATA
# Prefer EXT metadata, then PRE metadata.
# ---------------------------------------------------------

metadata = {}

for code in sorted(set(pre) | set(ext)):
    source = ext.get(code) or pre.get(code)

    metadata[code] = {
        "mvg": code,
        "mvg_name": source["mvg_name"],
        "description": source["description"],
        "sort_order": source["sort_order"]
    }

# ---------------------------------------------------------
# BROADER FAMILIES FOR VEGA-LITE MAPS
# ---------------------------------------------------------

def family_for(code):
    if code == 1:
        return "Rainforest"

    if code in {2, 3, 4, 5, 11, 12}:
        return "Eucalypt forest & woodland"

    if code in {6, 13}:
        return "Acacia"

    if code in {7, 8, 9, 10, 23, 31}:
        return "Other forest & woodland"

    if code in {14, 15, 16, 17, 18, 22, 32}:
        return "Shrubland"

    if code in {19, 20, 21}:
        return "Grassland"

    if code in {24, 26, 27}:
        return "Other native vegetation"

    if code in {25, 29}:
        return "Modified / non-native"

    return "Other native vegetation"

# ---------------------------------------------------------
# ENRICH GEOJSON
# ---------------------------------------------------------

def enrich_geojson(source_path, output_path):
    with source_path.open("r", encoding="utf-8") as f:
        geo = json.load(f)

    output_features = []

    for feature in geo.get("features", []):
        props = feature.get("properties", {})

        raw_code = props.get("mvg")

        try:
            code = int(raw_code)
        except (TypeError, ValueError):
            continue

        # Exclude sea/estuaries and unknown/no-data.
        if code in {28, 99}:
            continue

        info = metadata.get(code)

        if not info:
            print(f"WARNING: no metadata for MVG {code}")
            continue

        feature["properties"] = {
            "mvg": code,
            "mvg_name": info["mvg_name"],
            "description": info["description"],
            "family": family_for(code)
        }

        output_features.append(feature)

    geo["features"] = output_features

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            geo,
            f,
            ensure_ascii=False,
            separators=(",", ":")
        )

    print(
        f"Wrote {output_path.name}: "
        f"{len(output_features)} features, "
        f"{output_path.stat().st_size / 1024 / 1024:.2f} MB"
    )

# ---------------------------------------------------------
# EXACT AREA/CHANGE TABLE
#
# Original raster resolution = 100 m x 100 m.
# Therefore:
# 1 pixel = 10,000 m² = 1 hectare.
#
# These counts come from the ORIGINAL 100 m raster attribute
# tables, NOT from the simplified 5 km display maps.
# ---------------------------------------------------------

csv_rows = []

for code in sorted(metadata):
    if code in {28, 99}:
        continue

    info = metadata[code]

    pre_ha = pre.get(code, {}).get("count", 0)
    ext_ha = ext.get(code, {}).get("count", 0)

    pre_mha = pre_ha / 1_000_000
    ext_mha = ext_ha / 1_000_000
    change_mha = ext_mha - pre_mha

    if pre_ha > 0:
        retention_pct = (ext_ha / pre_ha) * 100
        change_pct = ((ext_ha - pre_ha) / pre_ha) * 100
    else:
        retention_pct = None
        change_pct = None

    csv_rows.append({
        "mvg": code,
        "mvg_name": info["mvg_name"],
        "family": family_for(code),
        "pre1750_ha": pre_ha,
        "extant_ha": ext_ha,
        "pre1750_mha": round(pre_mha, 6),
        "extant_mha": round(ext_mha, 6),
        "change_mha": round(change_mha, 6),
        "retention_pct": (
            round(retention_pct, 2)
            if retention_pct is not None else ""
        ),
        "change_pct": (
            round(change_pct, 2)
            if change_pct is not None else ""
        )
    })

# ---------------------------------------------------------
# WRITE FILES
# ---------------------------------------------------------

enrich_geojson(PRE_GEOJSON, OUT_PRE)
enrich_geojson(EXT_GEOJSON, OUT_EXT)

fields = [
    "mvg",
    "mvg_name",
    "family",
    "pre1750_ha",
    "extant_ha",
    "pre1750_mha",
    "extant_mha",
    "change_mha",
    "retention_pct",
    "change_pct"
]

with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(csv_rows)

print(f"Wrote {OUT_CSV.name}: {len(csv_rows)} rows")

print("\nFinished.")
print(f"PRE map: {OUT_PRE}")
print(f"EXT map: {OUT_EXT}")
print(f"Change:  {OUT_CSV}")
