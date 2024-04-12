# Builder
FROM python@sha256:b4b901d9304f0b4af0157eb021300eb4775a3af8fdbd3e9504dbfd4be16e9ee3 AS builder
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
COPY requirements.txt /app
WORKDIR /app
ENV PYTHONPATH=/packages
RUN pip install --cache-dir=/tmp -r requirements.txt --target=/packages
RUN python -m compileall .

# Final
FROM gcr.io/distroless/python3-debian12@sha256:22a48ea7c898642dee832615db15dd3372b652ecd5dfa0b3f795ac3c9312aba2
LABEL org.opencontainers.image.source="https://github.com/GoogleContainerTools/distroless"
LABEL org.opencontainers.image.description="Google Distroless Python3 Debian 12"
WORKDIR /app
COPY --from=builder --chown=root:root /packages /packages
COPY --from=builder --chown=root:root /app /app
ENV PYTHONPATH=/packages
USER nonroot
HEALTHCHECK --interval=5s --timeout=30s --start-period=2s --retries=3 CMD [ "python", "docker_healthcheck.py" ]
CMD ["app.py"]
