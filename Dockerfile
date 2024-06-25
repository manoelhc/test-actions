# Builder
FROM python@sha256:f6d04873f0a67146854270e5f6513ed5e0165557c1b10689f1a20e9e65c8fe8e AS builder
LABEL org.opencontainers.image.source="https://github.com/docker-library/python"
LABEL org.opencontainers.image.description="Python 3.12.0"
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    rustc=1.63.0+dfsg1-2 \
    libpq-dev=15.6-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY src /app
COPY packages/manocorp /manocorp
COPY requirements.txt /app
WORKDIR /app
ENV PYTHONPATH=/packages
RUN pip install --cache-dir=/tmp -r requirements.txt --target=/packages
RUN pip install --cache-dir=/tmp /manocorp --force-reinstall --target=/packages
RUN python -m compileall .

# Final
FROM python@sha256:f6d04873f0a67146854270e5f6513ed5e0165557c1b10689f1a20e9e65c8fe8e
WORKDIR /app
COPY --from=builder --chown=root:root /packages /packages
COPY --from=builder --chown=root:root /app /app
ENV PYTHONPATH=/packages
USER nobody
HEALTHCHECK --interval=5s --timeout=30s --start-period=2s --retries=3 CMD [ "python", "docker_healthcheck.py" ]
CMD ["python", "/app/app.py"]
