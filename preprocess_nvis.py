#!/usr/bin/env python3
"""
Creates the three small web files required by charts 6–8 from the user's
official NVIS Version 7 MVG rasters.

Before running, export the PRE and EXT MVG rasters from QGIS as GeoTIFF in
an Australian equal-area projected CRS. Name them:
  data/raw/nvis_pre1750_mvg.tif
  data/raw/nvis_extant_mvg.tif

Install:
  python -m pip install rasterio geopandas shapely pandas numpy pyproj

Run:
  python preprocess_nvis.py
"""
from pathlib import Path
import numpy as np
import pandas as pd
import rasterio
from rasterio.features import shapes
from rasterio.enums import Resampling
import geopandas as gpd
from shapely.geometry import shape

PRE = Path("data/raw/nvis_pre1750_mvg.tif")
EXT = Path("data/raw/nvis_extant_mvg.tif")
LOOKUP = Path("data/mvg_lookup.csv")
OUT = Path("data")
DOWNSAMPLE = 8

FAMILY = {
  1:"Rainforest & vine thickets",
  2:"Eucalypt forests",3:"Eucalypt forests",4:"Eucalypt forests",
  5:"Eucalypt woodlands",11:"Eucalypt woodlands",12:"Eucalypt woodlands",31:"Eucalypt woodlands",
  6:"Acacia",13:"Acacia",
  7:"Other forests & woodlands",8:"Other forests & woodlands",9:"Other forests & woodlands",
  10:"Other forests & woodlands",23:"Other forests & woodlands",30:"Other forests & woodlands",
  14:"Mallee & shrublands",15:"Mallee & shrublands",16:"Mallee & shrublands",
  17:"Mallee & shrublands",18:"Mallee & shrublands",22:"Mallee & shrublands",32:"Mallee & shrublands",
  19:"Grasslands & herblands",20:"Grasslands & herblands",21:"Grasslands & herblands"
}

names_df = pd.read_csv(LOOKUP)
NAMES = dict(zip(names_df.mvg.astype(int), names_df.mvg_name))

def stats(path):
    with rasterio.open(path) as src:
        if src.crs is None or src.crs.is_geographic:
            raise ValueError(f"{path} must be exported to a projected equal-area CRS first.")
        a = src.read(1)
        valid = np.isfinite(a)
        if src.nodata is not None:
            valid &= a != src.nodata
        vals, counts = np.unique(a[valid].astype(int), return_counts=True)
        pixel_ha = abs(src.transform.a * src.transform.e) / 10000
        return pd.DataFrame({"mvg":vals, "area_ha":counts * pixel_ha})

def make_geojson(path, outfile):
    with rasterio.open(path) as src:
        h = max(1, src.height // DOWNSAMPLE)
        w = max(1, src.width // DOWNSAMPLE)
        a = src.read(1, out_shape=(h,w), resampling=Resampling.nearest)
        transform = src.transform * src.transform.scale(src.width/w, src.height/h)
        valid = np.isfinite(a)
        if src.nodata is not None:
            valid &= a != src.nodata

        rows = []
        for geom, value in shapes(a.astype("int32"), mask=valid, transform=transform):
            code = int(value)
            if code not in NAMES or code in (28, 99):
                continue
            rows.append({
              "mvg":code,
              "mvg_name":NAMES[code],
              "family":FAMILY.get(code,"Other / modified"),
              "geometry":shape(geom)
            })

        g = gpd.GeoDataFrame(rows, crs=src.crs)
        g = g.dissolve(by=["mvg","mvg_name","family"], as_index=False)
        g["geometry"] = g.geometry.simplify(max(abs(transform.a),abs(transform.e))*0.6, preserve_topology=True)
        g.to_crs("EPSG:4326").to_file(outfile, driver="GeoJSON")

OUT.mkdir(exist_ok=True)
pre = stats(PRE).rename(columns={"area_ha":"pre1750_ha"})
ext = stats(EXT).rename(columns={"area_ha":"extant_ha"})
c = pre.merge(ext, on="mvg", how="outer").fillna(0)
c["mvg_name"] = c.mvg.map(NAMES)
c["pre1750_mha"] = c.pre1750_ha / 1_000_000
c["extant_mha"] = c.extant_ha / 1_000_000
c["change_mha"] = c.pre1750_mha - c.extant_mha
c["remaining_pct"] = np.where(c.pre1750_ha > 0, c.extant_ha/c.pre1750_ha*100, np.nan)
c.to_csv(OUT/"nvis_mvg_change.csv", index=False)

make_geojson(PRE, OUT/"nvis_pre1750_mvg.geojson")
make_geojson(EXT, OUT/"nvis_extant_mvg.geojson")

print("Created NVIS files for visualisations 6–8.")
