#!/usr/bin/env bash
set -euo pipefail

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level warning &
server_pid=$!
trap 'kill "$server_pid" 2>/dev/null || true' EXIT

for _ in {1..20}; do
  if curl --fail --silent http://127.0.0.1:8000/health >/dev/null; then
    break
  fi
  sleep 0.25
done

python -m pytest -q
npx newman run postman/TaskFlow_API_QA.postman_collection.json \
  -e postman/TaskFlow_Local.postman_environment.json \
  -r cli,json \
  --reporter-json-export reports/newman-run.json
