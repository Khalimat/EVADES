#!/usr/bin/env python3
"""Add the genome (nucleotide) accession of each protein in a TSV, using NCBI Entrez.

WHAT IT DOES
    For every protein ID in one column of a TSV, asks NCBI (Entrez elink protein ->
    nuccore, then esummary) for the linked GenBank nucleotide record and appends its
    versioned accession (e.g. NC_045512.2) as a new column `nucleotide_accession`.
    Missing IDs, proteins without a linked record, and failed requests get "NA".

INPUT   TSV with a column of protein accessions (e.g. the `sseqid` hits from the BLAST
        homolog search in adp_homologs_all.sh).
OUTPUT  Same TSV plus `nucleotide_accession`; default name <input>_with_genome.tsv.

USAGE
    python3 add_genome_id.py hits.tsv sseqid --email you@example.org [--output out.tsv] [--sleep 0.3]

NOTES
    NCBI asks for a real contact email and limits request rates: keep --sleep >= 0.34 s
    without an API key. One elink + one esummary request is made per protein, so large
    tables take a while.
"""
import argparse
import pandas as pd
from Bio import Entrez
from time import sleep
import sys

def get_genome_accession(protein_id, email):
    """Get the GenBank nucleotide accession (e.g. NC_045512.2) linked to a protein ID.

    Returns "NA" if no link exists or the request fails (the error is printed to stderr)."""
    try:
        Entrez.email = email
        handle = Entrez.elink(dbfrom="protein", db="nuccore", id=protein_id, linkname="protein_nuccore")
        record = Entrez.read(handle)
        handle.close()

        if record and record[0].get("LinkSetDb"):
            nuc_id = record[0]["LinkSetDb"][0]["Link"][0]["Id"]
            handle = Entrez.esummary(db="nuccore", id=nuc_id)
            summary = Entrez.read(handle)
            handle.close()
            return summary[0]["AccessionVersion"]
        else:
            return "NA"

    except Exception as e:
        sys.stderr.write(f"⚠️  Error for {protein_id}: {e}\n")
        return "NA"


def main():
    """Parse arguments, look up each protein ID in turn (sleeping between requests), write the augmented TSV."""
    parser = argparse.ArgumentParser(description="Map protein IDs to GenBank nucleotide accessions.")
    parser.add_argument("input_tsv", help="Input TSV file")
    parser.add_argument("column", help="Column name containing protein IDs")
    parser.add_argument("--email", default="your.email@example.com", help="Email for NCBI Entrez (default: your.email@example.com)")
    parser.add_argument("--output", default=None, help="Output TSV (default: input_with_genome.tsv)")
    parser.add_argument("--sleep", type=float, default=0.3, help="Sleep time between requests (default: 0.3s)")
    args = parser.parse_args()

    df = pd.read_csv(args.input_tsv, sep="\t")
    if args.column not in df.columns:
        sys.exit(f"❌ Column '{args.column}' not found in input TSV.")

    accessions = []
    for pid in df[args.column]:
        if pd.isna(pid) or str(pid).strip() == "":
            accessions.append("NA")
            continue
        acc = get_genome_accession(str(pid).strip(), args.email)
        accessions.append(acc)
        sleep(args.sleep)

    df["nucleotide_accession"] = accessions

    output_file = args.output or args.input_tsv.replace(".tsv", "_with_genome.tsv")
    df.to_csv(output_file, sep="\t", index=False)
    print(f"✅ Done. Saved results to: {output_file}")


if __name__ == "__main__":
    main()

