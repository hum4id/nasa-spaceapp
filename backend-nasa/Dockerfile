FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

WORKDIR /app

# Optional extras per module, e.g. --build-arg EXTRAS=db,cache,ml
ARG EXTRAS=""

# Dependencies first for layer caching
COPY pyproject.toml README.md ./
RUN mkdir -p app && touch app/__init__.py \
    && pip install --no-cache-dir ".${EXTRAS:+[$EXTRAS]}"

COPY app ./app
COPY scripts ./scripts
COPY models ./models
COPY datasets ./datasets
COPY configs ./configs
RUN pip install --no-cache-dir --no-deps .

# Run as non-root
RUN useradd --create-home --uid 10001 app && chown -R app /app
USER app

EXPOSE 8000
HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# --proxy-headers: trust X-Forwarded-For only from FORWARDED_ALLOW_IPS (set it to the proxy IP)
ENV FORWARDED_ALLOW_IPS=127.0.0.1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
