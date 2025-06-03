import json
from openai import OpenAI

import typer
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

app = typer.Typer()

# Define a Pydantic schema for the structured output
class CaseSummary(BaseModel):
    clinical_context: str = Field(..., alias="Clinical context")
    clinical_timeline: str = Field(..., alias="Clinical timeline")
    molecular_profile: str = Field(..., alias="Molecular profile")
    study_context: str = Field(..., alias="Study context")
    patient_in_study: str = Field(..., alias="Patient in study")
    scientific_implications: str = Field(..., alias="Scientific implications")

    class Config:
        allow_population_by_field_name = True

# Auto-generate JSON schema from the Pydantic model
SCHEMA_JSON = CaseSummary.schema_json(indent=2)

# Build the prompt
PROMPT_TEMPLATE = f"""
You are a scientific assistant reading clinical and genomic data from a cancer patient enrolled in a glioma study.
You are provided with the following files:
- patient_info.tsv
- samples_info.tsv
- mutations.tsv
- data_timeline_specimen.txt
- data_timeline_status.txt
- data_timeline_surgery.txt
- data_timeline_treatment.txt
- nihms-569639.pdf (a publication describing the cohort)

Please summarize the information for Patient P04 into the following structured JSON schema. Keep answers succinct:

Clinical context: A short overview of the patient and disease.
Clinical timeline: A short overview of treatments, surgery, and recurrences.
Molecular profile: What mutations were seen, OncoKB levels, and interpretation.
Study context: What is this study about and what is its scientific contribution?
Patient in study: How does patient P04 fit into the cohort?
Scientific implications: Explain what this case illustrates biologically or clinically. Include mechanisms of resistance, tumor evolution, mutational signatures (e.g. COSMIC TMZ induced signature 11), epigenomic remodeling if relevant. Highlight the role of truncal mutations, potential clonal selection, and/or epigenomic remodeling (e.g. G-CIMP erosion) if relevant. Keep it succinct but try to answer each.
"""

@app.command()
def summarize(
    patient_info: Path,
    samples_info: Path,
    mutations: Path,
    specimen: Path,
    status: Path,
    surgery: Path,
    treatment: Path,
    publication: Path,
    model: str = "gpt-4-turbo",
    openai_api_key: Optional[str] = typer.Option(None, envvar="OPENAI_API_KEY")
):
    """Summarize patient P04 from clinical and molecular files using OpenAI's GPT API."""
    client = OpenAI(api_key=openai_api_key)

    # Read in file paths and build system prompt
    files = {
        "patient_info.tsv": patient_info.read_text(),
        "samples_info.tsv": samples_info.read_text(),
        "mutations.tsv": mutations.read_text(),
        "data_timeline_specimen.txt": specimen.read_text(),
        "data_timeline_status.txt": status.read_text(),
        "data_timeline_surgery.txt": surgery.read_text(),
        "data_timeline_treatment.txt": treatment.read_text(),
        "nihms-569639.pdf": "[PDF text omitted for brevity – assume loaded separately]"
    }

    full_prompt = PROMPT_TEMPLATE + "\n\n" + "\n\n".join(
        f"### {name}\n{content[:3000]}..." for name, content in files.items()
    )

    # Query OpenAI with structured output parsing
    response = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {"role": "system", "content": "You are a scientific summarizer."},
            {"role": "user", "content": full_prompt}
        ],
        response_format=CaseSummary,
        temperature=0.3
    )
    # parsed is a CaseSummary instance
    parsed: CaseSummary = response.choices[0].message.parsed
    typer.echo(parsed.json(indent=2, by_alias=True))

if __name__ == "__main__":
    app()
