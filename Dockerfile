FROM python:3.11-slim

ENV STORAGE=local
ENV INDEXER=standard
ENV BASE_PATH="tests/dummy/local-storage-data/database"
ENV METADATA_PATH="metadata.json"
ENV TEI_NS='http://www.tei-c.org/ns/1.0'
ENV APP_NAME="MY DTS API"

WORKDIR /app

# Copy dependency files
COPY pyproject.toml poetry.lock README.md ./

# Install dependencies only (without the project)
RUN pip install poetry && \
    poetry config virtualenvs.create false

# Copy source code
COPY . ./

# Install the project
RUN poetry install --no-interaction

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]