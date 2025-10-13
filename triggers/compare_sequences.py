#!/usr/bin/env python3
import subprocess
import pandas as pd
import argparse
import os


def run_blastp(query_fasta, subject_fasta, out_tsv, evalue_cutoff=0.001):
    # Make BLAST database for subject file
    subprocess.run(["makeblastdb", "-in", subject_fasta, "-dbtype", "prot"], check=True)

    # Run BLASTP
    subprocess.run([
        "blastp",
        "-query", query_fasta,
        "-db", subject_fasta,
        "-outfmt", "6 qseqid sseqid pident length evalue bitscore",
        "-evalue", str(evalue_cutoff),
        "-out", out_tsv
    ], check=True)

    # Load and filter results
    if os.path.getsize(out_tsv) > 0:
        df = pd.read_csv(out_tsv, sep="\t",
                         names=["qseqid", "sseqid", "pident", "length", "evalue", "bitscore"])
        df = df[df["evalue"] <= evalue_cutoff]
        filtered_tsv = out_tsv.replace(".tsv", "_filtered.tsv")
        df.to_csv(filtered_tsv, sep="\t", index=False)
        print(f"Filtered results written to: {filtered_tsv}")
    else:
        print("No matches found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run BLASTP and filter matches by e-value ≤ 0.001")
    parser.add_argument("query", help="Path to query FASTA file")
    parser.add_argument("subject", help="Path to subject FASTA file")
    parser.add_argument("-o", "--out", default="blastp_results.tsv",
                        help="Output filename (default: blastp_results.tsv)")
    parser.add_argument("-e", "--evalue", type=float, default=0.001, help="E-value cutoff (default: 0.001)")

    args = parser.parse_args()

    run_blastp(args.query, args.subject, args.out, args.evalue)
