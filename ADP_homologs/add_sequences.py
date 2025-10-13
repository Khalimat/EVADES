#!/usr/bin/env python3
import sys
import pandas as pd
from Bio import SeqIO
from pathlib import Path

def add_sequences_to_tsv(tsv_file, fasta_file):
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
        print("Usage: python add_sequences_to_tsv.py <input.tsv> <input.fasta>")
        sys.exit(1)

    tsv_file = sys.argv[1]
    fasta_file = sys.argv[2]
    add_sequences_to_tsv(tsv_file, fasta_file)

