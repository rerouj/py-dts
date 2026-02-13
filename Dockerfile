FROM python:3.11-slim

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