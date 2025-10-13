#!/usr/bin/env python3
import os
import subprocess

# === Paths ===
project_root = ".." # I removed the path, as it is specific to my setup
all_models_dir = os.path.join(project_root, "analyses/alphafold3_models/final_models")

# List of models to re-run
significant_models = [
    "acria1_model.cif", "acrva5bsp_model.cif", "acrvia2_model.cif", "apyc1_model.cif",
    "bgt_model.cif", "dam_model.cif", "darb_model.cif", "dcmp_hm_model.cif",
    "dnmp_model.cif", "fole_model.cif", "gad2_model.cif", "hia5_model.cif",
    "hin1523_model.cif", "jss1_004_model.cif", "nma1821_model.cif", "nmnat_model.cif",
    "ntase_model.cif", "orf55_model.cif", "orf83_model.cif", "pnk_model.cif",
    "quec_model.cif", "riia_model.cif", "rna_ligase_model.cif", "t7_pk_model.cif",
    "u56_model.cif", "vcrx089_model.cif", "vcrx093_model.cif"
]

# Prebuilt eukaryotic viral structure DB
ref_db = ".." # I removed the path, as it is specific to my setup

# Output directories
out_root = os.path.join(project_root, "analyses/hom_eukaryotic_viral_db/significant_matches")
os.makedirs(out_root, exist_ok=True)

# === Loop over each significant model ===
for model in significant_models:
    model_path = os.path.join(all_models_dir, model)
    if not os.path.exists(model_path):
        print(f"⚠️  Skipping missing file: {model}")
        continue

    # Define base names and output paths
    model_name = os.path.splitext(model)[0]
    tmp_dir = os.path.join(out_root, f"{model_name}_tmp")
    os.makedirs(tmp_dir, exist_ok=True)

    query_db = os.path.join(tmp_dir, f"{model_name}_query")
    result_db = os.path.join(tmp_dir, f"{model_name}_results")
    html_out = os.path.join(out_root, f"{model_name}.html")

    print(f"\n🔍 Running FoldSeek search for: {model_name}")

    # Step 1: Create a FoldSeek DB for the single model
    subprocess.run(["foldseek", "createdb", model_path, query_db], check=True)

    # Step 2: Run search with strict e-value cutoff
    subprocess.run([
        "foldseek", "search",
        query_db,
        ref_db,
        result_db,
        tmp_dir,
        "--threads", "4",
        "-e", "0.00001",
        "-a"
    ], check=True)

    # Step 3: Export as interactive HTML (format-mode 3)
    subprocess.run([
        "foldseek", "convertalis",
        query_db,
        ref_db,
        result_db,
        html_out,
        "--format-mode", "3"
    ], check=True)

    print(f"✅ HTML report saved: {html_out}")

print("\n🎉 All searches completed successfully!")

