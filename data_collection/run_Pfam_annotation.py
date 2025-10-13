#!/usr/bin/env python3
import subprocess
import sys
import os

def main():
    if len(sys.argv) != 4:
        print("Usage: python run_hmmsearch.py <hmm_file> <fasta_file> <output_file>")
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
