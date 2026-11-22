FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN useradd --create-home --uid 10001 helpdesk

WORKDIR /app

COPY --chown=helpdesk:helpdesk requirements.txt .

RUN pip install --no-cache-dir --disable-pip-version-check -r requirements.txt

COPY --chown=helpdesk:helpdesk app ./app

USER helpdesk

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]