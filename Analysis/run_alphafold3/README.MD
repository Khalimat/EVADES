# run_alphafold3

Scripts for running AlphaFold 3 and scoring its models. They are reused for several analyses in the paper, so they live in this shared folder.

| Script | What it does |
|---|---|
| `create_single_json.py` | Turns a protein FASTA into one AF3 input JSON per protein (single chain, seeds 1-4). |
| `run_af3_cpu_pipeline.slurm` | Stage 1 (CPU): SLURM array job that only builds MSAs/templates for each JSON (`--run_inference=false`). |
| `run_af3_gpu_pipeline.slurm` | Stage 2 (GPU): SLURM array job that runs structure inference from the prepared JSONs. |
| `qDockQ.py` | Computes the pDockQ interface-quality score (and its PPV) for a two-chain AF3 `.cif`. |

Typical order: `create_single_json.py` -> `run_af3_cpu_pipeline.slurm` -> `run_af3_gpu_pipeline.slurm` -> `qDockQ.py`.
Site-specific paths (model weights, databases, Singularity image) are left as `..` placeholders in the SLURM scripts; fill them in before running.
