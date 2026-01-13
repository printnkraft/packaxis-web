FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps for WeasyPrint and Postgres
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    libxml2 \
    libxslt1.1 \
    libxrender1 \
    libfontconfig1 \
    libjpeg62-turbo \
    shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . /app

EXPOSE 8000

CMD ["gunicorn", "printaxis.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]