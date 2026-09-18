#!/usr/bin/env python3
"""Find structural similarities between EVADES AlphaFold 3 models and a set of trigger structures (Foldseek).

WHAT IT DOES
    1. Builds Foldseek databases for the query structures (trigger proteins) and for the
       reference set (final EVADES AF3 models).
    2. Searches queries against references (`foldseek search`, E-value <= 0.01).
    3. Converts the alignments to a TSV (`foldseek convertalis`).

INPUT   query_dir  folder of trigger structures        (data/triggers/Nagy)
        ref_dir    folder of EVADES AF3 models         (analyses/alphafold3_models/final_models)
OUTPUT  analyses/triggers/foldseek_EVADES_Nagy_filtered.tsv (+ Foldseek scratch in foldseek_tmp/)

USAGE   Set project_root below, then: python3 compare_structures.py   (needs `foldseek` on the PATH)
        Sequence-level counterpart: compare_sequences.py.
"""
import os
import subprocess
import pandas as pd

# === Paths ===
project_root = ".."   # placeholder: set to your project root (site-specific path removed)
ref_dir = os.path.join(project_root, "analyses/alphafold3_models/final_models")
query_dir = os.path.join(project_root, "data/triggers/Nagy")
tmp_dir = os.path.join(project_root, "analyses/triggers/foldseek_tmp")
result_db = os.path.join(tmp_dir, "results")
results_tsv = os.path.join(project_root, "analyses/triggers/foldseek_EVADES_Nagy_filtered.tsv")

# === Setup ===
os.makedirs(tmp_dir, exist_ok=True)

# === Create FoldSeek databases ===
print("📦 Creating FoldSeek databases...")
subprocess.run(["foldseek", "createdb", query_dir, os.path.join(tmp_dir, "queries")], check=True)
subprocess.run(["foldseek", "createdb", ref_dir, os.path.join(tmp_dir, "refs")], check=True)

# === Run FoldSeek search ===
print("🔍 Running FoldSeek search (this may take a while)...")
subprocess.run([
    "foldseek", "search",
    os.path.join(tmp_dir, "queries"),
    os.path.join(tmp_dir, "refs"),
    result_db,
    tmp_dir,
    "--threads", "8",
    "-e", "0.01"  # directly filter by E-value threshold
], check=True)

# === Convert results to text (TSV) ===
subprocess.run([
    "foldseek", "convertalis",
    os.path.join(tmp_dir, "queries"),
    os.path.join(tmp_dir, "refs"),
    result_db,
    results_tsv
], check=True)

# (The E-value filter is already applied by `foldseek search -e`, so no extra filtering is needed.)
print(f"✅ Done! Filtered results saved to:\n{results_tsv}")

