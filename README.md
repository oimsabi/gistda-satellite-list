# GISTDA Python environment

A self-contained Python 3.11 virtual environment for GISTDA-style geospatial + data
science work (GIS / remote sensing analysis).

## Activate

**PowerShell:**
```powershell
C:\Users\trainingpc01\gistda-env\.venv\Scripts\Activate.ps1
```
If activation is blocked by execution policy, run once:
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

**Or skip activation** and call the interpreter directly:
```powershell
& C:\Users\trainingpc01\gistda-env\.venv\Scripts\python.exe your_script.py
```

## Installed stack
- **Geospatial:** geopandas, rasterio, shapely, fiona, pyproj, rioxarray, xarray, contextily, folium
- **Data science:** numpy, pandas, matplotlib, seaborn, scikit-learn, jupyterlab

Reinstall / update from the pinned list:
```powershell
& C:\Users\trainingpc01\gistda-env\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Jupyter
Launch JupyterLab:
```powershell
& C:\Users\trainingpc01\gistda-env\.venv\Scripts\python.exe -m jupyterlab
```
Register as a named kernel (optional):
```powershell
& C:\Users\trainingpc01\gistda-env\.venv\Scripts\python.exe -m ipykernel install --user --name gistda-env
```

## Projects

The repo holds two independent projects:

```
satellite-map/     Interactive Thailand remote-sensing viewer (Leaflet + Google + Earth Engine)
  index.html         open in a browser (file:// works — data is inlined)
  boundary/          Thailand.geojson/.shp/.shx (country outline)
  gee/build_layers.py  regenerates the Earth Engine index layers
price-list/        GISTDA satellite price-list web app
  web/               open web/index.html in a browser
  data/              generated JSON + CSV
  extract_data.py    regenerates data/ and web/data.js from the RECORDS table
```

### satellite-map

A tabbed viewer over Google basemaps. Tabs: **True Color, NDVI, NDWI (water),
NDMI (moisture)** from Sentinel-2; **MOD16 ET, MOD17 GPP, PML ET, WUE** from
MODIS/PML. Each tab shows a legend + info panel and an opacity slider; only one
raster is rendered at a time (performance). FAO65 / ET:SEBAL / VPM appear as
disabled "coming soon" tabs.

Earth Engine tile URLs **expire in ~4 days** — refresh all layers with:
```powershell
& C:\Users\trainingpc01\gistda-env\.venv\Scripts\python.exe satellite-map\gee\build_layers.py
```
Requires a one-time `earthengine authenticate` (project `gee-geoai-gistda`).
Tuning knobs (composite window, buffer, dataset ids, palettes) are at the top of
`build_layers.py`. `satellite-map-architecture.drawio` documents the data flow.
