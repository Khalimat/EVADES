#!/usr/bin/env python3
"""Attach amino-acid sequences to a table of BLAST hits.

WHAT IT DOES
    Reads a TSV that has a column `sseqid` (subject/hit ID, as in BLAST outfmt 6) and a
    FASTA file whose record IDs match those values, and adds a `sequence` column with the
    matching sequence (empty if the ID is not in the FASTA).

INPUT   <input.tsv> with an `sseqid` column; <input.fasta> holding the hit sequences.
OUTPUT  <input>_with_sequences.tsv next to the input file.

USAGE
    python3 add_sequences.py <input.tsv> <input.fasta>
"""
import sys
import pandas as pd
from Bio import SeqIO
from pathlib import Path

def add_sequences_to_tsv(tsv_file, fasta_file):
    """Add a `sequence` column to `tsv_file` from `fasta_file` (matched on `sseqid`) and save it as a new TSV."""
    # Read input files
    df = pd.read_csv(tsv_file, sep="\t")
    fasta_records = SeqIO.to_dict(SeqIO.parse(fasta_file, "fasta"))

    # Check if 'sseqid' column exists
    if "sseqid" not in df.columns:
        sys.exit("Error: The TSV file must contain a column named 'sseqid'.")

    # Map sequences from FASTA to the 'sseqid'
    sequences = []
    for sseqid in df["sseqid"]:
        seq_record = fasta_records.get(sseqid)
        if seq_record:
            sequences.append(str(seq_record.seq))
        else:
            sequences.append(None)  # Leave empty if not found

    df["sequence"] = sequences

    # Save output file
    output_path = Path(tsv_file)
    output_file = output_path.with_name(f"{output_path.stem}_with_sequences{output_path.suffix}")
    df.to_csv(output_file, sep="\t", index=False)

    print(f"✅ Saved file with sequences to: {output_file}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python add_sequences.py <input.tsv> <input.fasta>")
        sys.exit(1)

    tsv_file = sys.argv[1]
    fasta_file = sys.argv[2]
    add_sequences_to_tsv(tsv_file, fasta_file)

