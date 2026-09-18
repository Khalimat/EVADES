#!/usr/bin/env python3
"""Annotate protein sequences with Pfam domains using HMMER's hmmsearch.

WHAT IT DOES
    Runs `hmmsearch --cut_ga` of a Pfam HMM library against a protein FASTA. `--cut_ga`
    applies each family's curated gathering threshold, so only hits Pfam itself considers
    significant are reported. Results are written as a per-domain table (--domtblout).

INPUT   <hmm_file>    Pfam-A HMM library (e.g. Pfam-A.hmm, pressed or not)
        <fasta_file>  protein sequences to annotate
OUTPUT  <output_file> HMMER domain table (one line per domain hit)

USAGE
    python3 run_Pfam_annotation.py Pfam-A.hmm proteins.faa pfam_domains.domtblout
Requires HMMER (`hmmsearch`) on the PATH.
"""
import subprocess
import sys
import os

def main():
    """Validate the command-line inputs, run hmmsearch, and report success or failure."""
    if len(sys.argv) != 4:
        print("Usage: python run_Pfam_annotation.py <hmm_file> <fasta_file> <output_file>")
        sys.exit(1)

    hmm_file = sys.argv[1]
    fasta_file = sys.argv[2]
    output_file = sys.argv[3]

    # Check if input files exist
    if not os.path.isfile(hmm_file):
        print(f"Error: HMM file '{hmm_file}' not found.")
        sys.exit(1)
    if not os.path.isfile(fasta_file):
        print(f"Error: FASTA file '{fasta_file}' not found.")
        sys.exit(1)

    # Construct the hmmsearch command
    cmd = [
        "hmmsearch",
        "--cut_ga",
        "--domtblout", output_file,
        hmm_file,
        fasta_file
    ]

    print(f"Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print(f"\n✅ Domain table saved to '{output_file}'")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ hmmsearch failed with exit code {e.returncode}")
        sys.exit(e.returncode)
    except FileNotFoundError:
        print("\n❌ hmmsearch not found. Make sure HMMER is installed and in your PATH.")
        sys.exit(1)

if __name__ == "__main__":
    main()
