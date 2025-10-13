#!/usr/bin/env python3
import os
import subprocess
import pandas as pd

# === Paths ===
project_root = "/nfs/research/rdf/kam/projects/EVADES_final-2025-10-09"
query_dir = os.path.join(project_root, "analyses/alphafold3_models/final_models")

# Reference Foldseek database (already built)
ref_db = "/hps/nobackup/rdf/metagenomics/service-team/ref-dbs/foldseek/structures_eukaryotic_viruses/structure_foldseek_database_2023-11-27/db"

# Output directories
out_dir = os.path.join(project_root, "analyses/hom_eukaryotic_viral_db")
os.makedirs(out_dir, exist_ok=True)

# Output files
query_db = os.path.join(out_dir, "EVADES_AF3_queries")
result_db = os.path.join(out_dir, "EVADES_vs_eukvirus_results")
results_tsv = os.path.join(out_dir, "foldseek_raw.tsv")

# === Step 1: Create query Foldseek database ===
print("📦 Creating FoldSeek query database...")
subprocess.run(["foldseek", "createdb", query_dir, query_db], check=True)

# === Step 2: Run FoldSeek search ===
print("🔍 Running FoldSeek search vs. eukaryotic virus structure DB...")
subprocess.run([
    "foldseek", "search",
    query_db,
    ref_db,
    result_db,
    out_dir,
    "--threads", "8",
    "-e", "0.00001"  # Filter on E-value directly
], check=True)

# === Step 3: Convert alignments to tabular format ===
print("🧩 Converting binary results to tabular format...")
subprocess.run([
    "foldseek", "convertalis",
    query_db,
    ref_db,
    result_db,
    results_tsv
], check=True)



