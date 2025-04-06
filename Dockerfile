FROM python:3.12

RUN apt-get update && apt-get install -y curl gcc libpq-dev build-essential

ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app
COPY pyproject.toml /app/


RUN poetry config virtualenvs.create false \
    && poetry install poetry install --only main --no-interaction --no-ansi


COPY . .


EXPOSE 8000


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

