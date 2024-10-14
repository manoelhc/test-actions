# Builder
FROM python:3.13.0-slim-bookworm AS builder
LABEL org.opencontainers.image.source="https://github.com/docker-library/python"
LABEL org.opencontainers.image.description="Python 3.13"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    rustc=1.63.0+dfsg1-2 \
    libpq-dev=15.8-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean


COPY packages/manocorp /manocorp
COPY requirements.txt /app
WORKDIR /app
ENV PYTHONPATH=/packages
RUN pip install --cache-dir=/tmp -r requirements.txt --target=/packages
RUN pip install --cache-dir=/tmp /manocorp --force-reinstall --target=/packages
COPY src /app
RUN python -m compileall .

# Final
FROM python:3.13.0-slim-bookworm
WORKDIR /app
COPY --from=builder --chown=root:root /packages /packages
COPY --from=builder --chown=root:root /app /app
ENV PYTHONPATH=/packages
USER nobody
HEALTHCHECK --interval=5s --timeout=30s --start-period=2s --retries=3 CMD [ "python", "docker_healthcheck.py" ]
CMD ["python", "/app/app.py"]
