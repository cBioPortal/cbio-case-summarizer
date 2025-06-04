import json
from openai import OpenAI

import typer
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
import PyPDF2

app = typer.Typer()

# Define a Pydantic schema for the structured output
class SampleSummary(BaseModel):
    sample_id: str = Field(..., alias="cBioPortal Sample ID", description="cBioPortal Sample ID, beginning with 'P-'")
class CaseSummary(BaseModel):
    patient_id: str = Field(..., alias="cBioPortal Patient ID", description="cBioPortal Patient ID, beginning with 'P-'")
    sample_ids: List[SampleSummary]
    sample_ids: str= Field(..., alias="cBioPortal Sample ID List", description="List of sequenced cBioPortal Sample IDs, beginning with 'P-'")
    clinical_context: str = Field(..., alias="Clinical context", description="A short overview of the patient and disease.")
    clinical_timeline: str = Field(..., alias="Clinical timeline", description="A short overview of treatments, surgery, and recurrences.")
    molecular_profile: str = Field(..., alias="Molecular profile", description="What mutations were seen, OncoKB levels, and interpretation.")
   # study_context: str = Field(..., alias="Study context", description="Study context")
    patient_in_study: str = Field(..., alias="Patient in study", description="Describe how the patient fits into the cohort based on the publication.")
    scientific_implications: str = Field(..., alias="Scientific implications", description="Explain what this case illustrates biologically or clinically. ")
    resistance_mechanisms: str = Field(..., alias="Mechanisms of resistance", description="Explain potential mechanisms of resistance")
    diagnosis_history: str =  Field(..., alias="Diagnosis history", description="Describe the diagnosis history of the patient")
    mutational_signatures: str = Field(..., alias="Mutational signatures", description="Infer any COSMIC mutational signatures the patient might have")
    epigenomic_remodeling: str = Field(..., alias="Methylation", description="Summary of methylation data, truncal mutations, potential clonal selection, and/or epigenomic remodeling (e.g. G-CIMP erosion) if relevant")
    treatment_history: str =  Field(..., alias="Treatment history", description="Describe the treatment history of the patient")
    patient_history_summary: str= Field(..., alias="Summary", description="Four sentence summary of the patient clinical and genomic history, using the 'clinical_context', 'clinical_timeline', 'molecular_profile', 'patient_in_study', 'scientific_implications', 'resistance_mechanisms', 'diagnosis_history', 'mutational_signatures', 'epigenomic_remodeling' and 'treatment_history' fields ONLY. Only use information that is confirmed about the patient.")
    treatment_recommendation: str = Field(..., alias="Treatment recommendation", description="Based on the patient treatment history, diagnosis history, and molecular profile with mutation information, suggest the most-likely beneficial next treatment for the patient based on your knowledge.")
    clinical_trial_recommendation: str = Field(..., alias="Clinical trial recommendation", description="Based on the patient treatment history, diagnosis history, and molecular profile with mutation information, suggest any clinical trial the patient might be eligible for based on your knowledge.")

    class Config:
        allow_population_by_field_name = True
        
def get_file_names_in_folder(folder_path):
    """
    Returns a list of all file names (not including directories) in the specified folder.
    Args: 
        folder_path (str or Path): The path to the folder.
    Returns:
        list: A list of strings, where each string is the name of a file.
    """
    path = Path(folder_path)
    file_names = []
    for item in path.iterdir():
        if item.is_file():
            #file_names.append(item.name)
            file_names.append(f'{path}/{item.name}')
    return file_names

def pdf_reader(pdf_path='../data/msk_chord.pdf'):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text()
    return text

# Auto-generate JSON schema from the Pydantic model
SCHEMA_JSON = CaseSummary.schema_json(indent=2)
#Build the prompt

@app.command()
def summarize(
    folder_path: Path,
    model: str = "gpt-4o",
    openai_api_key: Optional[str] = typer.Option(None, envvar="OPENAI_API_KEY")
):
    #f"""Summarize patient from clinical and molecular files using OpenAI's GPT API."""
    """Summarize patient P18 from clinical and molecular files using OpenAI's GPT API."""
    client = OpenAI(api_key=openai_api_key)

    # Read in file paths and build system prompt
    file_names= get_file_names_in_folder(folder_path)
    files= {file: Path(file).read_text() for file in file_names if '.txt' in file}
    pdf_files= {file: pdf_reader(file) for file in file_names if '.pdf' in file}
    files.update(pdf_files)
    full_prompt = "\n\n".join(
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
    # parse CaseSummary instance
    parsed: CaseSummary = response.choices[0].message.parsed
    typer.echo(parsed.json(indent=2, by_alias=True))

if __name__ == "__main__":
    app()
