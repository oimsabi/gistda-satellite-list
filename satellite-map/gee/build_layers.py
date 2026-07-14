# -*- coding: utf-8 -*-
"""Generate the analytical raster layers for the Thailand satellite viewer and
inject them into ../index.html (Google Earth Engine).

Layers: True Color, NDVI, NDWI (water), NDMI (moisture) from Sentinel-2;
MOD16 ET, MOD17 GPP, PML ET, WUE from MODIS/PML. FAO65 / ET:SEBAL / VPM ship as
disabled "coming soon" stubs (not turnkey EE datasets).

Design note — performance vs precision:
  * Sentinel-2 uses a trailing 90-day window, cloud-masked, newest-valid-pixel mosaic.
  * MODIS/PML take the 3 most recent images mosaicked (fills gaps, stays light).
  * Band scale factors are always applied so pixel values are physically correct.
  * The viewer renders only ONE layer's tiles at a time (see index.html).

Earth Engine tile URLs expire in ~4 days — re-run this script to refresh them all:
    python satellite-map/gee/build_layers.py
"""
import datetime as dt
import json
import re
from pathlib import Path

import ee
import geopandas as gpd

PROJECT = "gee-geoai-gistda"
BUFFER_M = 15000  # extend imagery this far beyond the border line

BASE = Path(__file__).resolve().parents[1]          # satellite-map/
BOUNDARY_FILE = BASE / "boundary" / "Thailand.geojson"
HTML_FILE = BASE / "index.html"

ee.Initialize(project=PROJECT)

# ---- region (coarsely simplified — only used to filter/clip imagery) ----
gdf = gpd.read_file(BOUNDARY_FILE)
geom = gdf.geometry.union_all().simplify(0.01)
region = ee.Geometry(
    json.loads(gpd.GeoSeries([geom]).to_json())["features"][0]["geometry"]
).buffer(BUFFER_M)

TODAY = dt.date.today()
S2_START = str(TODAY - dt.timedelta(days=90))
S2_END = str(TODAY)


def latest_date(collection):
    """EE date string of the most recent image (resolved later, inside the guard)."""
    img = collection.sort("system:time_start", False).first()
    return ee.Date(img.get("system:time_start")).format("YYYY-MM-dd")


# ---- Sentinel-2 composite (built once, all four S2 layers derive from it) ----
def s2_mask_clouds(img):
    scl = img.select("SCL")
    bad = scl.eq(3).Or(scl.eq(8)).Or(scl.eq(9)).Or(scl.eq(10))  # shadow, cloud, cirrus
    return img.updateMask(bad.Not())


s2_coll = (
    ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
    .filterBounds(region)
    .filterDate(S2_START, S2_END)
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
    .map(s2_mask_clouds)
)
# newest valid pixel wins: sort ascending so the most recent image mosaics on top
s2 = s2_coll.sort("system:time_start", True).mosaic().clip(region)
S2_DATE = f"{S2_START} to {S2_END} (latest-pixel mosaic)"
S2_ATTR = "Sentinel-2 SR Harmonized · GEE · modified Copernicus data"


def latest_mosaic(dataset, n=3):
    """3 most recent images, newest mosaicked on top (fills gaps)."""
    col = ee.ImageCollection(dataset).filterBounds(region)
    recent = col.limit(n, "system:time_start", False)  # n newest, desc
    return recent.sort("system:time_start", True).mosaic().clip(region), latest_date(col)


# ---- palettes (CVD-safe scientific ramps) ----
P_NDVI = ["#9e6b3f", "#e0cda0", "#d9e6b0", "#a4d17a", "#4faf4f", "#1f7a33"]
P_WATER = ["#8c6d2f", "#d8c79a", "#f5f5f5", "#9ecae1", "#4292c6", "#08519c"]
P_MOIST = ["#a6611a", "#dfc27d", "#f5f5f5", "#80cdc1", "#018571"]
P_VIRIDIS = ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151", "#fde725"]
P_GPP = ["#ffffe5", "#d9f0a3", "#78c679", "#238443", "#004529"]


def build():
    layers = []

    # ---------- Sentinel-2 group ----------
    layers.append(dict(
        key="truecolor", label="True Color", group="Sentinel-2",
        sub="Natural colour (B4/B3/B2)",
        description="What the eye would see from orbit — the base optical view.",
        image=s2, vis={"bands": ["B4", "B3", "B2"], "min": 0, "max": 3000, "gamma": 1.1},
        legend=None, dataset="COPERNICUS/S2_SR_HARMONIZED", resolution="10 m",
        date=S2_DATE, attribution=S2_ATTR, source="Contains modified Copernicus data",
    ))
    ndvi = s2.normalizedDifference(["B8", "B4"]).rename("NDVI")
    layers.append(dict(
        key="ndvi", label="NDVI", group="Sentinel-2",
        sub="Vegetation vigour",
        description="Greenness / photosynthetic activity. High = dense healthy vegetation.",
        formula="(B8 − B4) / (B8 + B4)",
        image=ndvi, vis={"min": -0.2, "max": 0.9, "palette": P_NDVI},
        legend={"palette": P_NDVI, "min": -0.2, "max": 0.9, "unit": "NDVI (unitless)"},
        dataset="COPERNICUS/S2_SR_HARMONIZED", resolution="10 m", date=S2_DATE,
        attribution=S2_ATTR,
    ))
    ndwi = s2.normalizedDifference(["B3", "B8"]).rename("NDWI")
    layers.append(dict(
        key="ndwi", label="NDWI (water)", group="Sentinel-2",
        sub="Open water (McFeeters)",
        description="Highlights open water bodies. High (blue) = water.",
        formula="(B3 − B8) / (B3 + B8)",
        image=ndwi, vis={"min": -0.5, "max": 0.7, "palette": P_WATER},
        legend={"palette": P_WATER, "min": -0.5, "max": 0.7, "unit": "NDWI (unitless)"},
        dataset="COPERNICUS/S2_SR_HARMONIZED", resolution="10 m", date=S2_DATE,
        attribution=S2_ATTR,
    ))
    ndmi = s2.normalizedDifference(["B8", "B11"]).rename("NDMI")
    layers.append(dict(
        key="ndmi", label="NDMI (moisture)", group="Sentinel-2",
        sub="Vegetation / soil moisture (Gao)",
        description="Canopy & soil water content. High (teal) = moist.",
        formula="(B8 − B11) / (B8 + B11)",
        image=ndmi, vis={"min": -0.5, "max": 0.6, "palette": P_MOIST},
        legend={"palette": P_MOIST, "min": -0.5, "max": 0.6, "unit": "NDMI (unitless)"},
        dataset="COPERNICUS/S2_SR_HARMONIZED", resolution="20 m", date=S2_DATE,
        attribution=S2_ATTR,
    ))

    # ---------- MODIS / PML group ----------
    m16_raw, m16_date = latest_mosaic("MODIS/061/MOD16A2GF")
    et = m16_raw.select("ET")
    et = et.updateMask(et.lt(3000)).multiply(0.1).rename("ET")  # scale 0.1 -> mm/8-day
    layers.append(dict(
        key="mod16", label="MOD16 ET", group="Evapotranspiration / productivity",
        sub="Terra evapotranspiration",
        description="Actual evapotranspiration — water leaving the surface as vapour.",
        image=et, vis={"min": 0, "max": 60, "palette": P_VIRIDIS},
        legend={"palette": P_VIRIDIS, "min": 0, "max": 60, "unit": "mm / 8-day"},
        dataset="MODIS/061/MOD16A2GF (band ET ×0.1)", resolution="500 m",
        date=m16_date, attribution="NASA LP DAAC · MOD16A2GF",
    ))
    m17_raw, m17_date = latest_mosaic("MODIS/061/MOD17A2HGF")
    gpp = m17_raw.select("Gpp")
    gpp = gpp.updateMask(gpp.lt(3000)).multiply(0.1).rename("GPP")  # 0.0001 kgC -> 0.1 gC
    layers.append(dict(
        key="mod17", label="MOD17 GPP", group="Evapotranspiration / productivity",
        sub="Terra gross primary productivity",
        description="Carbon fixed by photosynthesis — ecosystem productivity.",
        image=gpp, vis={"min": 0, "max": 80, "palette": P_GPP},
        legend={"palette": P_GPP, "min": 0, "max": 80, "unit": "gC m⁻² / 8-day"},
        dataset="MODIS/061/MOD17A2HGF (band Gpp ×0.1)", resolution="500 m",
        date=m17_date, attribution="NASA LP DAAC · MOD17A2HGF",
    ))
    pml_raw, pml_date = latest_mosaic("projects/pml_evapotranspiration/PML/OUTPUT/PML_V22a")
    pml_et = pml_raw.select("Ec").add(pml_raw.select("Es")).add(pml_raw.select("Ei")).rename("ET")
    layers.append(dict(
        key="pml", label="PML ET", group="Evapotranspiration / productivity",
        sub="Penman-Monteith-Leuning ET",
        description="Total ET = transpiration + soil evaporation + intercepted rain.",
        formula="Ec + Es + Ei",
        image=pml_et, vis={"min": 0, "max": 6, "palette": P_VIRIDIS},
        legend={"palette": P_VIRIDIS, "min": 0, "max": 6, "unit": "mm / day"},
        dataset="PML_V22a (pml_evapotranspiration)", resolution="500 m", date=pml_date,
        attribution="PML_V2 · Zhang et al.",
    ))
    wue = gpp.divide(et).rename("WUE").updateMask(et.gt(0))
    layers.append(dict(
        key="wue", label="WUE", group="Evapotranspiration / productivity",
        sub="Water use efficiency (MOD17 ÷ MOD16)",
        description="Carbon gained per unit water lost — productivity vs water cost.",
        formula="GPP (MOD17) ÷ ET (MOD16)",
        image=wue, vis={"min": 0, "max": 6, "palette": P_VIRIDIS},
        legend={"palette": P_VIRIDIS, "min": 0, "max": 6, "unit": "gC / kg H₂O"},
        dataset="MOD17A2HGF ÷ MOD16A2GF", resolution="500 m",
        date=m17_date, attribution="Derived · NASA LP DAAC",
    ))

    return layers


STUBS = [
    dict(key="fao65", label="FAO65", group="Coming soon", enabled=False,
         description="FAO reference evapotranspiration (ET₀).",
         stubReason="source not yet confirmed (FAO-56 ET₀ via ERA5-Land / TerraClimate pet is the likely fit)"),
    dict(key="sebal", label="ET:SEBAL", group="Coming soon", enabled=False,
         description="Surface Energy Balance Algorithm for Land ET.",
         stubReason="SEBAL is an algorithm, not a hosted dataset — needs geeSEBAL computed per scene"),
    dict(key="vpm", label="VPM", group="Coming soon", enabled=False,
         description="Vegetation Photosynthesis Model GPP.",
         stubReason="the VPM product (2000–2016) is on figshare, not hosted on Earth Engine yet"),
]


def to_config(layers):
    """Resolve each EE image to a tile URL; drop EE handles from the JSON."""
    out = []
    for spec in layers:
        image, vis = spec.pop("image"), spec.pop("vis")
        try:
            url = image.getMapId(vis)["tile_fetcher"].url_format
            spec["url"] = url
            spec["enabled"] = True
            if hasattr(spec.get("date"), "getInfo"):  # resolve EE date strings
                spec["date"] = spec["date"].getInfo()
            print(f"  OK  {spec['key']:10s} {spec.get('date','')}")
        except Exception as exc:  # noqa: BLE001 — one bad layer must not kill the run
            spec["enabled"] = False
            spec["stubReason"] = f"generation failed: {exc}"
            print(f"  ERR {spec['key']:10s} {exc}")
        out.append(spec)
    return out


def main():
    print(f"Building layers (S2 window {S2_START}..{S2_END})")
    config = to_config(build()) + STUBS
    block = "const LAYERS = " + json.dumps(config, ensure_ascii=False, indent=2) + ";"

    html = HTML_FILE.read_text(encoding="utf-8")
    html = re.sub(
        r"(/\* LAYERS_START.*?\*/\n).*?(\n/\* LAYERS_END \*/)",
        lambda m: m.group(1) + block + m.group(2),
        html,
        flags=re.S,
    )
    HTML_FILE.write_text(html, encoding="utf-8")
    enabled = sum(1 for c in config if c.get("enabled"))
    print(f"Injected {enabled} enabled + {len(config) - enabled} stub layers into {HTML_FILE.name}")


if __name__ == "__main__":
    main()
