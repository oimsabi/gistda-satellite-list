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
