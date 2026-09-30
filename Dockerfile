FROM python:3.11-slim AS builder
WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src/ ./src/
RUN python -m venv /opt/venv && /opt/venv/bin/pip install --no-cache-dir .

FROM python:3.11-slim
LABEL org.opencontainers.image.source="https://github.com/dsugurtuna/hla-imputation-analyst"
RUN groupadd --gid 1000 hla && useradd --uid 1000 --gid 1000 --create-home hla
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
USER hla
WORKDIR /data
ENTRYPOINT ["hla-analyst"]
CMD ["--help"]
