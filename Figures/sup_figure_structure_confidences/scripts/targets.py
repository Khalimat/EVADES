"""The 8 AF3 models shown in the figure, in panel order (paths relative to this folder)."""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AF = os.path.join(ROOT, "af3_results", "folds_2026_09_15_18_26")
NT = os.path.join(ROOT, "af3_results", "ntase_utp_utp_mg")
RENDERS = os.path.join(ROOT, "output", "panels")


def _af3(job, model=0, folder=AF):
    d = os.path.join(folder, job)
    return {
        "cif": os.path.join(d, f"fold_{job}_model_{model}.cif"),
        "full_data": os.path.join(d, f"fold_{job}_full_data_{model}.json"),
        "summary": os.path.join(d, f"fold_{job}_summary_confidences_{model}.json"),
    }


TARGETS = [
    {"name": "AcrIC5", "label": "AcrIC5-PaCas8c", **_af3("acric5_reseed_for_pae_seed1")},
    {"name": "AcrIC3", "label": "AcrIC3-PaCas3", **_af3("acric3_reseed_for_pae_seed1")},
    {"name": "AcrIB4", "label": "AcrIB4-LsCas8b1", **_af3("acrib4_reseed_for_pae_seed1")},
    {"name": "AcrIIA26", "label": "AcrIIA26-SpyCas9", **_af3("acriia26_reseed_for_pae_seed1")},
    # NTase models: a top-ranking_score model across 5 seeds x 5 samples (ties; see select_ntase_models.py)
    {"name": "NTase_bacteriophage", "label": "NTase Bcp1 (bacteriophage, YP_009031408)-UTP-UTP-Mg",
     **_af3("ntase_yp_009031408_utp_utp_mg3_seed4", model=0, folder=NT)},
    {"name": "NTase_eukaryotic_virus", "label": "NTase Erinnyis ello granulovirus (YP_009091875)-UTP-UTP-Mg",
     **_af3("ntase_yp_009091875_utp_utp_mg3_seed2", model=1, folder=NT)},
    {"name": "DISARM_Ocr_complex", "label": "Ocr-DISARM_DrmMII", **_af3("disarm_ocr_complex_reseed_for_pae_seed1")},
    {"name": "Panchino_Ocr_complex", "label": "Ocr-Panchino_gp28", **_af3("panchino_ocr_complex_reseed_for_pae_seed1")},
]

if __name__ == "__main__":
    for t in TARGETS:
        for k in ("cif", "full_data", "summary"):
            assert os.path.exists(t[k]), f"MISSING: {t['name']} {k} -> {t[k]}"
    print("all files present")
