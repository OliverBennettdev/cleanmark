FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    CLEANMARK_HOST=0.0.0.0 \
    CLEANMARK_PORT=8765

RUN apt-get update \
    && apt-get install -y --no-install-recommends libimage-exiftool-perl qpdf \
    && rm -rf /var/lib/apt/lists/* \
    && useradd --create-home --uid 10001 cleanmark

WORKDIR /app
COPY services/cleaner/cleaner ./cleaner

USER cleanmark
EXPOSE 8765
CMD ["python", "-m", "cleaner.app"]
