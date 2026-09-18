#!/usr/bin/env python3
"""Search all EVADES AlphaFold 3 models against a database of eukaryotic-virus structures with Foldseek.

WHAT IT DOES
    1. Builds a Foldseek query database from every model in `query_dir`.
    2. Searches it against the reference eukaryotic-virus structure database
       (`foldseek search`, E-value <= 1e-5).
    3. Converts the binary alignments to a tab-separated table.

INPUT   folder of EVADES AF3 models (analyses/alphafold3_models/final_models);
        a prebuilt Foldseek database of eukaryotic-virus structures (`ref_db`)
OUTPUT  analyses/hom_eukaryotic_viral_db/foldseek_raw.tsv (+ Foldseek databases in the same folder)

NEXT    Models with significant hits are re-run with HTML output by
        make_html_files_for_significant_matches.py.
USAGE   Set project_root and ref_db below, then: python3 run_foldseek_EVADES_vs_euk_virusDB.py
"""
import os
import subprocess

# === Paths ===
project_root = ".."   # placeholder: set to your project root (site-specific path removed)
query_dir = os.path.join(project_root, "analyses/alphafold3_models/final_models")

# Reference Foldseek database (already built)
ref_db = ".."   # placeholder: prefix of the eukaryotic-virus Foldseek database (site-specific path removed)

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



