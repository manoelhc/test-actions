# Builder
FROM python@sha256:b4b901d9304f0b4af0157eb021300eb4775a3af8fdbd3e9504dbfd4be16e9ee3 AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential=12.9 \
    rustc=1.63.0+dfsg1-2 \
    libpq-dev=15.6-0+deb12u1 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

COPY . /app
WORKDIR /app
ENV PYTHONPATH=/packages
RUN pip install --cache-dir=/tmp -r requirements.txt --target=/packages
RUN python -m compileall .

# Final
FROM gcr.io/distroless/python3-debian12@sha256:538f54b8d704c29137d337aeac1bfc874afd7db813b163b585366d57ec113e13
WORKDIR /app
COPY --from=builder --chown=root:root /packages /packages
COPY --from=builder --chown=root:root /app/src /app
ENV PYTHONPATH=/packages
USER nonroot
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 CMD [ "docker_healthcheck.py" ]
CMD ["app.py"]
