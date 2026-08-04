# API QA and Postman Portfolio - TaskFlow

This repository is a complete, synthetic API QA engagement. It shows how I test a REST API, organize a Postman collection, automate checks with Newman, document defects, and verify fixes.

> Portfolio disclosure: TaskFlow is a fictional QA target created for demonstration. The defects and verification history are seeded examples, not claims about a real client.

## What a client receives

- Importable Postman collection and local environment
- Positive, negative, authentication, validation, and workflow tests
- Newman-ready command-line execution
- Python regression tests with pytest
- Endpoint test matrix
- Prioritized defect report with fix verification
- Executive QA report in PDF
- Docker and local setup instructions

## Tested flows

| Area | Coverage |
| --- | --- |
| Health | Status, version, response time, content type |
| Authentication | Valid login, invalid credentials, missing fields, token capture |
| Authorization | Missing and invalid bearer token checks |
| Users | Pagination, single user, not found, invalid query boundary |
| Tasks | Create, validate response contract, reject invalid data, delete |

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API documentation at `http://127.0.0.1:8000/docs`.

## Run Python regression tests

```bash
python -m pytest -q
```

## Run the Postman suite with Newman

With the API running in another terminal:

```bash
npx newman run postman/TaskFlow_API_QA.postman_collection.json \
  -e postman/TaskFlow_Local.postman_environment.json
```

Or run the API, pytest suite, and Newman evidence together:

```bash
chmod +x scripts/run-evidence.sh
./scripts/run-evidence.sh
```

## Portfolio deliverables

- `postman/TaskFlow_API_QA.postman_collection.json`
- `postman/TaskFlow_Local.postman_environment.json`
- `reports/API_QA_Portfolio_Report.pdf`
- `reports/test-matrix.csv`
- `reports/defect-log.csv`
- `tests/test_api.py`

## Verified demonstration result

- Newman: 13 requests, 44 assertions, 0 failures
- pytest: 11 tests passed

## Skills demonstrated

Postman, REST API testing, HTTP status codes, JSON contract validation, negative testing, bearer authentication, boundary analysis, Newman, pytest, FastAPI, Docker, and release-readiness reporting.

