# cBioPortal Case Summarizer
Uses OpenAI to create a summary for a patient

## Development
To set up the development environment, install the development dependencies:

```sh
poetry install
```

Run:
```bash
poetry run summarize-case --model gpt-4o --openai-api-key YOUR_OPENAPI_KEY data > export/P04.json
```

Currently only generates data for one case

## TODO
- [ ] Use cBioPortal datahub directly (rather than files downloaded per case)
- [ ] Add Deployment Preview for frontend
