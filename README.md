# cBioPortal Case Summarizer
Uses OpenAI to create a summary for a patient

## Development
To set up the development environment, install the development dependencies:

```sh
poetry install
```

Run:
```bash
poetry run summarize-case --model gpt-4o --openai-api-key YOUR_OPENAPI_KEY data/data_clinical_patient.txt data/data_clinical_sample.txt data/data_mutations.txt data/data_timeline_specimen.txt data/data_timeline_status.txt  data/data_timeline_surgery.txt data/data_timeline_treatment.txt data/nihms-569639.pdf > export/P04.json
```

Currently only generates data for one case

## TODO
- [ ] Use cBioPortal datahub directly (rather than files downloaded per case)
- [ ] Add Deployment Preview for frontend
