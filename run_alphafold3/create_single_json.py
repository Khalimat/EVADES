import os
import json
import argparse
from pathlib import Path
from Bio import SeqIO


def generate_jsons_from_fasta(input_fasta, output_dir):
    """
    Create AF3 input json files for
    entries in a fasta file

    :param input_fasta: str, path to the input dir
    :param output_dir: str, path to the output dir
    """
    input_fasta = Path(input_fasta)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_seeds = [1, 2, 3, 4]
    dialect = "alphafold3"
    version = 3

    for record in SeqIO.parse(input_fasta, "fasta"):
        json_content = {
            "name": record.id,
            "modelSeeds": model_seeds,
            "sequences": [
                {
                    "protein": {
                        "id": "A",
                        "sequence": str(record.seq)
                    }
                }
            ],
            "dialect": dialect,
            "version": version
        }

        json_filename = output_dir / f"{record.id}.json"
        with open(json_filename, "w") as json_file:
            json.dump(json_content, json_file, indent=2)

    print(f"Created JSON files for all entries in: {output_dir.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert FASTA entries to JSON for MSA input.")
    parser.add_argument("--input", "-i", required=True,
                        help="Path to input FASTA file")

    parser.add_argument("--output", "-o", required=True,
                        help="Directory to save JSON files")

    args = parser.parse_args()
    generate_jsons_from_fasta(args.input, args.output)
