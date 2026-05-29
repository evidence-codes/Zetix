# Zetix server — Phase 1 API. Docker-deployable on 2-vCPU / 4GB RAM min (NFR-C3).
FROM python:3.11-slim

WORKDIR /app

# Install the project (foundation deps only; ML/store extras added in EPIC-1).
COPY pyproject.toml ./
COPY api ./api
COPY embedding ./embedding
RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "zetix_api.main:app", "--host", "0.0.0.0", "--port", "8000", "--app-dir", "api"]
