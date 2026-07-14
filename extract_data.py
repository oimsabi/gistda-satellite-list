# -*- coding: utf-8 -*-
"""GISTDA satellite price list -> JSON / CSV / web data.js

Source of truth: records transcribed from the official GISTDA Price List PDF
(usd@gistda.or.th, 0 2141 4564-66,69). All prices exclude 7% VAT.
Re-run this script after editing RECORDS to regenerate every output:

    .venv\\Scripts\\python.exe extract_data.py
"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
CSV_DIR = DATA_DIR / "csv"
WEB_DIR = ROOT / "web"

CATEGORIES = [
    {
        "id": "vhr",
        "name_th": "ดาวเทียมรายละเอียดสูงมาก (30 – 50 ซม.)",
        "name_en": "Very High Resolution Optical (30–50 cm)",
        "price_columns": {"archive": {"th": "ข้อมูลในคลัง", "en": "Standard Archive"},
                          "tasking": {"th": "ข้อมูลชนิดสั่งถ่าย", "en": "Standard Tasking"}},
        "notes_th": ["ข้อมูลในคลัง: พื้นที่การสั่งขั้นต่ำ 25 ตร.กม. ราคาสำหรับ level Primary (PAN, MS, Pansharpened)",
                     "ข้อมูลชนิดสั่งถ่าย: พื้นที่การสั่งขั้นต่ำ 100 ตร.กม."],
        "notes_en": ["Archive: minimum order 25 km², price for Primary level (PAN, MS, Pansharpened)",
                     "Tasking: minimum order 100 km²"],
    },
    {
        "id": "hr",
        "name_th": "ดาวเทียมรายละเอียดสูง (60 ซม. – 2 ม.)",
        "name_en": "High Resolution Optical (60 cm – 2 m)",
        "price_columns": {"archive": {"th": "ข้อมูลในคลัง", "en": "Standard Archive"},
                          "tasking": {"th": "ข้อมูลชนิดสั่งถ่าย", "en": "Standard Tasking"}},
        "notes_th": ["ราคาต่อหน่วยแตกต่างกันตามดาวเทียม — ดูป้ายหน่วยในแต่ละแถว"],
        "notes_en": ["Price units vary by satellite — see the unit badge on each row"],
    },
    {
        "id": "medium",
        "name_th": "ดาวเทียมรายละเอียดปานกลาง (มากกว่า 2 เมตร)",
        "name_en": "Medium Resolution (> 2 m)",
        "price_columns": {"archive": {"th": "ข้อมูลในคลัง", "en": "Standard Archive"},
                          "tasking": {"th": "ข้อมูลชนิดสั่งถ่าย / การติดตาม", "en": "Standard Tasking / Monitoring"}},
        "notes_th": ["LANDSAT: คิดเฉพาะค่าดำเนินการผลิตข้อมูลจากคลังข้อมูล (Level 1T)"],
        "notes_en": ["LANDSAT: processing fee only, produced from archive (Level 1T)"],
    },
    {
        "id": "radar",
        "name_th": "ดาวเทียมระบบเรดาร์",
        "name_en": "Radar (SAR)",
        "price_columns": {"archive": {"th": "ข้อมูลในคลัง / SLC", "en": "Standard Archive / SLC"},
                          "tasking": {"th": "ข้อมูลชนิดสั่งถ่าย / Path Image", "en": "Standard Tasking / Path Image"}},
        "notes_th": ["RADARSAT-2: ราคา Single Look Complex / Path Image",
                     "COSMO-SkyMed: ราคาสั่งถ่ายใหม่ (New Acquisition) เท่านั้น"],
        "notes_en": ["RADARSAT-2: prices are Single Look Complex / Path Image",
                     "COSMO-SkyMed: New Acquisition price only"],
    },
]

# Per-satellite overrides for what the two price columns mean (radar)
PRICE_LABELS = {
    "RADARSAT-2": {"archive": "Single Look Complex", "tasking": "Path Image"},
    "COSMO-SkyMed": {"archive": "—", "tasking": "New Acquisition"},
}

U_KM2 = "บาท/ตร.กม. (THB/km²)"
U_SCENE = "บาท/ภาพ (THB/scene)"
U_VIDEO = "บาท/30 วินาที (THB/30 sec)"
U_KM2_YR = "บาท/ตร.กม./ปี (THB/km²/yr)"


def r(category, satellite, resolution_label, resolution_m, archive, tasking, unit,
      mode=None, band=None, polarization=None, min_order_th=None, min_order_en=None,
      notes_th=None, notes_en=None):
    return {
        "category": category,
        "satellite": satellite,
        "mode": mode,
        "resolution_label": resolution_label,
        "resolution_m": resolution_m,
        "band": band,
        "polarization": polarization,
        "price_archive": archive,
        "price_tasking": tasking,
        "price_unit": unit,
        "min_order_th": min_order_th,
        "min_order_en": min_order_en,
        "notes_th": notes_th,
        "notes_en": notes_en,
    }


MIN_25_100_TH = "คลัง 25 ตร.กม. / สั่งถ่าย 100 ตร.กม."
MIN_25_100_EN = "Archive 25 km² / Tasking 100 km²"

RECORDS = [
    # ---------- 1) Very high resolution optical (30-50 cm), THB/km2 ----------
    r("vhr", "Pléiades NEO", "30 cm", 0.30, 880, 1270, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "WorldView-4", "30 cm", 0.30, 920, 1560, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "SuperView-2", "42 cm", 0.42, 700, 1100, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "WorldView-1", "50 cm", 0.50, 700, 1100, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "WorldView-2", "50 cm", 0.50, 700, 1100, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "WorldView-3", "50 cm", 0.50, 700, 1100, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "GeoEye-1", "50 cm", 0.50, 700, 1100, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "Pléiades", "50 cm", 0.50, 490, 830, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "EarthScanner", "50 cm", 0.50, 400, 800, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "SuperView-1", "50 cm", 0.50, 500, 900, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "KOMPSAT-3", "50 cm", 0.50, 400, 700, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("vhr", "SKYSAT", "50 cm", 0.50, 300, 560, U_KM2,
      min_order_th="คลัง 1,250 ตร.กม.", min_order_en="Archive 1,250 km²",
      notes_th="ข้อมูลในคลังเข้าดูผ่าน API/Explorer • ข้อมูลสั่งถ่ายโปรดติดต่อเจ้าหน้าที่",
      notes_en="Archive accessed via API/Explorer • For tasking please contact staff"),

    # ---------- 2) High resolution optical (60 cm - 2 m) ----------
    r("hr", "QuickBird", "60 cm", 0.60, 700, None, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "GaoFen-7", "65 cm", 0.65, 400, 700, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "Jilin", "75 cm", 0.75, 300, 600, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "DailyVision", "75 cm", 0.75, 300, 600, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "GaoFen-2", "80 cm", 0.80, 300, 400, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "IKONOS", "1 m", 1.0, 400, None, U_KM2, min_order_th=MIN_25_100_TH, min_order_en=MIN_25_100_EN),
    r("hr", "Video Constellation", "1 m", 1.0, 142500, 285000, U_VIDEO,
      notes_th="ถ่ายภาพเคลื่อนไหว (วิดีโอ) และภาพกลางคืน • วิดีโอแต่ละช่วงจำกัดความยาว 30 วินาที",
      notes_en="Captures video and night imagery • Each video clip limited to 30 seconds"),
    r("hr", "Night Imaging", "1 m", 1.0, 800, 1400, U_KM2,
      min_order_th="100 ตร.กม. (ทั้งคลังและสั่งถ่าย)", min_order_en="100 km² (archive and tasking)",
      notes_th="ถ่ายวิดีโอและภาพกลางคืน • ความกว้างแนวถ่ายภาพอย่างน้อย 5 กม.",
      notes_en="Video and night imaging capable • Swath width at least 5 km"),
    r("hr", "SPOT-6", "1.5 m", 1.5, 190, 230, U_KM2,
      min_order_th="คลัง 100 ตร.กม. / สั่งถ่าย 500 ตร.กม.", min_order_en="Archive 100 km² / Tasking 500 km²"),
    r("hr", "SPOT-7", "1.5 m", 1.5, 190, 230, U_KM2,
      min_order_th="คลัง 100 ตร.กม. / สั่งถ่าย 500 ตร.กม.", min_order_en="Archive 100 km² / Tasking 500 km²"),
    r("hr", "ไทยโชต (Thaichote)", "2 m", 2.0, 700, 6500, U_SCENE,
      notes_th="ราคาที่ปรับ Orthorectification แล้ว 910 บาท/ภาพ",
      notes_en="Orthorectified product: 910 THB/scene"),

    # ---------- 3) Medium resolution (> 2 m) ----------
    r("medium", "LANDSAT-5", "30 m", 30.0, 150, None, U_SCENE, band="7 bands",
      notes_th="Level 1T • คิดเฉพาะค่าดำเนินการผลิตข้อมูลจากคลังข้อมูล",
      notes_en="Level 1T • Processing fee only, produced from archive"),
    r("medium", "LANDSAT-7", "30 m", 30.0, 150, None, U_SCENE, band="8 bands",
      notes_th="Level 1T • คิดเฉพาะค่าดำเนินการผลิตข้อมูลจากคลังข้อมูล",
      notes_en="Level 1T • Processing fee only, produced from archive"),
    r("medium", "LANDSAT-8", "30 m", 30.0, 150, None, U_SCENE, band="11 bands",
      notes_th="Level 1T • หากให้ สทอภ. ดาวน์โหลด คิดค่าดำเนินการ 150 บาท/ภาพ",
      notes_en="Level 1T • Download service by GISTDA: 150 THB/scene"),
    r("medium", "LANDSAT-9", "30 m", 30.0, 150, None, U_SCENE, band="11 bands",
      notes_th="Level 1T • หากให้ สทอภ. ดาวน์โหลด คิดค่าดำเนินการ 150 บาท/ภาพ",
      notes_en="Level 1T • Download service by GISTDA: 150 THB/scene"),
    r("medium", "PLANETSCOPE", "3 m", 3.0, 180, 240, U_KM2_YR, mode="Access+Download",
      min_order_th="100 ตร.กม.", min_order_en="100 km²",
      notes_th="ราคา = คลัง 180 / การติดตาม (Monitoring) 240 • ระยะเวลาสัญญา 1 ปี • เข้าดูและดาวน์โหลดผ่าน Planet Explorer, Planet API, Desktop GIS",
      notes_en="Prices = Archive 180 / Monitoring 240 • 1-year contract • Access via Planet Explorer, Planet API, Desktop GIS"),

    # ---------- 4) Radar (SAR), THB/scene ----------
    # RADARSAT-2 (C band): archive = Single Look Complex, tasking = Path Image
    r("radar", "RADARSAT-2", "25 m", 25.0, 57600, 57600, U_SCENE, mode="Standard", band="C"),
    r("radar", "RADARSAT-2", "1 m", 1.0, 134400, 134400, U_SCENE, mode="Spotlight A", band="C"),
    r("radar", "RADARSAT-2", "3 m", 3.0, 86400, 86400, U_SCENE, mode="Ultra-Fine", band="C"),
    r("radar", "RADARSAT-2", "3 m", 3.0, 124800, 124800, U_SCENE, mode="Wide Ultra-Fine", band="C"),
    r("radar", "RADARSAT-2", "8 m", 8.0, 67200, 67200, U_SCENE, mode="Multi-Look Fine", band="C"),
    r("radar", "RADARSAT-2", "8 m", 8.0, 120000, 120000, U_SCENE, mode="Wide Multi-Look Fine", band="C"),
    r("radar", "RADARSAT-2", "8 m", 8.0, 57600, 57600, U_SCENE, mode="Fine", band="C"),
    r("radar", "RADARSAT-2", "30 m", 30.0, 57600, 57600, U_SCENE, mode="Wide", band="C"),
    r("radar", "RADARSAT-2", "50 m", 50.0, None, 57600, U_SCENE, mode="ScanSAR Narrow", band="C"),
    r("radar", "RADARSAT-2", "100 m", 100.0, None, 57600, U_SCENE, mode="ScanSAR Wide", band="C"),
    r("radar", "RADARSAT-2", "25 m", 25.0, 57600, 57600, U_SCENE, mode="Extended High, Low", band="C"),
    r("radar", "RADARSAT-2", "8 m", 8.0, 86400, None, U_SCENE, mode="Fine Quad-Pol", band="C"),
    r("radar", "RADARSAT-2", "8 m", 8.0, 124800, None, U_SCENE, mode="Wide Fine Quad-Pol", band="C"),
    # TerraSAR-X (X band): archive / tasking
    r("radar", "TerraSAR-X", "0.25 m", 0.25, 162630, 325260, U_SCENE, mode="Staring Spotlight (ST)", band="X"),
    r("radar", "TerraSAR-X", "1 m", 1.0, 139230, 278460, U_SCENE, mode="High Res Spotlight (HS)", band="X"),
    r("radar", "TerraSAR-X", "2 m", 2.0, 99450, 198900, U_SCENE, mode="Spotlight", band="X"),
    r("radar", "TerraSAR-X", "3 m", 3.0, 69030, 138060, U_SCENE, mode="StripMap", band="X"),
    r("radar", "TerraSAR-X", "18.5 m", 18.5, 40950, 81900, U_SCENE, mode="ScanSAR", band="X"),
    r("radar", "TerraSAR-X", "40 m", 40.0, 40950, 81900, U_SCENE, mode="Wide ScanSAR", band="X"),
    # COSMO-SkyMed (X band): New Acquisition only -> tasking column
    r("radar", "COSMO-SkyMed", "1×1 m", 1.0, None, 180000, U_SCENE, mode="Spotlight-2", band="X",
      polarization="HH, VV"),
    r("radar", "COSMO-SkyMed", "3×3 – 5×5 m", 3.0, None, 93000, U_SCENE, mode="StripMap Himage", band="X",
      polarization="HH, HV, VH, VV"),
    r("radar", "COSMO-SkyMed", "10×12 – 20×20 m", 10.0, None, 68000, U_SCENE, mode="StripMap PingPong", band="X",
      polarization="2-ch polarimetric: HH,VV / HH,HV / VV,VH"),
    r("radar", "COSMO-SkyMed", "14×22 – 30×30 m", 14.0, None, 78000, U_SCENE, mode="ScanSAR Wide", band="X",
      polarization="HH, HV, VH, VV"),
    r("radar", "COSMO-SkyMed", "14×38 – 100×100 m", 14.0, None, 78000, U_SCENE, mode="ScanSAR Huge", band="X",
      polarization="HH, HV, VH, VV"),
    # GaoFen-3 (C band): archive / tasking
    r("radar", "GaoFen-3", "1 m", 1.0, 116400, 180500, U_SCENE, mode="Spotlight (SL)", band="C",
      polarization="HH, VV"),
    r("radar", "GaoFen-3", "3 m", 3.0, 68900, 118800, U_SCENE, mode="Ultra-fine Stripmap (UFS)", band="C",
      polarization="HH, VV"),
    r("radar", "GaoFen-3", "5 m", 5.0, 64200, 95000, U_SCENE, mode="Fine Stripmap (FSI)", band="C",
      polarization="HH, VV"),
    r("radar", "GaoFen-3", "10 m", 10.0, 64200, 90300, U_SCENE, mode="Wide Fine Stripmap (FSII)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "25 m", 25.0, 54700, 85500, U_SCENE, mode="Standard Stripmap (SS)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "50 m", 50.0, 32100, 42800, U_SCENE, mode="Narrow ScanSAR (NSC)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "100 m", 100.0, 32100, 45800, U_SCENE, mode="Wide ScanSAR (WSC)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "8 m", 8.0, 71300, 137800, U_SCENE, mode="Quad-pol Stripmap (QPSI)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "25 m", 25.0, 71300, 137800, U_SCENE, mode="Wide Quad-pol Stripmap (QPSII)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "10 m", 10.0, 10700, 14300, U_SCENE, mode="Wave (WAV)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "500 m", 500.0, 10700, 14300, U_SCENE, mode="Global Observation (GLO)", band="C",
      polarization="HH, HV / VV, VH"),
    r("radar", "GaoFen-3", "25 m", 25.0, 42800, 57000, U_SCENE, mode="Extended Incidence Angle (EXT)", band="C",
      polarization="HH, HV / VV, VH"),
]

META = {
    "source": "GISTDA Price List (Business Development and Services Department)",
    "contact": {
        "email": "usd@gistda.or.th",
        "phone": "0 2141 4564-66,69",
        "fax": "0 2143 9593",
        "address_th": "สำนักงานพัฒนาเทคโนโลยีอวกาศและภูมิสารสนเทศ (องค์การมหาชน) ศูนย์ราชการเฉลิมพระเกียรติ อาคาร B ชั้น 6 ถนนแจ้งวัฒนะ แขวงทุ่งสองห้อง เขตหลักสี่ กรุงเทพฯ 10210",
    },
    "vat_note_th": "ราคาดังกล่าวยังไม่รวมภาษีมูลค่าเพิ่ม",
    "vat_note_en": "Prices exclude VAT (7%)",
    "currency": "THB",
    "price_labels": PRICE_LABELS,
}


def main():
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(RECORDS)

    dataset = {
        "meta": META,
        "categories": CATEGORIES,
        "records": RECORDS,
    }

    json_path = DATA_DIR / "gistda_price_list.json"
    json_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2), encoding="utf-8")

    # CSVs: utf-8-sig so Thai text opens correctly in Excel
    df.to_csv(CSV_DIR / "all.csv", index=False, encoding="utf-8-sig")
    for cat in CATEGORIES:
        sub = df[df["category"] == cat["id"]]
        sub.to_csv(CSV_DIR / f"{cat['id']}.csv", index=False, encoding="utf-8-sig")

    # Embedded data for the static web app (file:// friendly, no fetch/CORS)
    data_js = "// Generated by extract_data.py - do not edit by hand\nconst PRICE_DATA = " \
              + json.dumps(dataset, ensure_ascii=False, indent=2) + ";\n"
    (WEB_DIR / "data.js").write_text(data_js, encoding="utf-8")

    counts = df.groupby("category").size().to_dict()
    print(f"OK: {len(df)} records -> {json_path}")
    print(f"    per category: {counts}")
    print(f"    CSVs in {CSV_DIR} ({len(CATEGORIES) + 1} files), web/data.js written")


if __name__ == "__main__":
    main()
