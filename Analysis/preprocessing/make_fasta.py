#!/usr/bin/env python3
"""Convert a table of proteins (CSV) into a FASTA file.

WHAT IT DOES
    Reads a CSV, takes the sequence ID from one column and the amino-acid sequence from
    another, and writes one FASTA record per row (ID only in the header, no description).

INPUT   CSV with an ID column (default `ID`) and a sequence column (default `Protein sequence`),
        e.g. the EVADES table.
OUTPUT  FASTA file (used for BLAST/Foldseek searches and to make AlphaFold 3 inputs with
        run_alphafold3/create_single_json.py).

USAGE
    python3 make_fasta.py EVADES.csv EVADES.faa [--id_col ID] [--seq_col "Protein sequence"]
"""
import argparse
import pandas as pd
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio import SeqIO

def main():
    """Parse arguments, read the CSV and write the FASTA."""
    parser = argparse.ArgumentParser(
        description="Convert a CSV file into a FASTA file using ID and Protein sequence columns."
    )
    parser.add_argument("input_csv", help="Path to input CSV file")
    parser.add_argument("output_fasta", help="Path to output FASTA file")
    parser.add_argument(
        "--id_col", default="ID", help="Column name for sequence IDs (default: 'ID')"
    )
    parser.add_argument(
        "--seq_col", default="Protein sequence", help="Column name for protein sequences (default: 'Protein sequence')"
    )
    args = parser.parse_args()

    # Read CSV
    df = pd.read_csv(args.input_csv)

    # Convert to FASTA
    records = []
    for _, row in df.iterrows():
        seq_id = str(row[args.id_col])
        seq_str = str(row[args.seq_col])
        records.append(SeqRecord(Seq(seq_str), id=seq_id, description=""))

    SeqIO.write(records, args.output_fasta, "fasta")
    print(f"✅ FASTA file successfully written to: {args.output_fasta}")

if __name__ == "__main__":
    main()
