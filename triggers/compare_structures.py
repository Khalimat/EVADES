# Distributed under terms of the MIT license.
#!/usr/bin/env python3
import os
import subprocess
import pandas as pd

# === Paths ===
project_root = ".."
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

# === Filter (redundant safety step) ===

print(f"✅ Done! Filtered results saved to:\n{results_tsv}")

