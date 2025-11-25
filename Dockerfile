# =============================================================================
# HLA Imputation Analyst - Production Docker Image
# Multi-stage build for minimal, secure container
# =============================================================================

# Stage 1: Build stage
FROM python:3.11-slim-bookworm AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY pyproject.toml ./
COPY src/ ./src/
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir .

# Stage 2: Production image
FROM python:3.11-slim-bookworm AS production

LABEL maintainer="Ugur Tuna <ugur.tuna@example.com>"
LABEL description="Enterprise-grade HLA Imputation Pipeline Analyst"
LABEL version="1.0.0"
LABEL org.opencontainers.image.source="https://github.com/dsugurtuna/hla-imputation-analyst"

# Create non-root user for security
RUN groupadd --gid 1000 hla \
    && useradd --uid 1000 --gid 1000 --shell /bin/bash --create-home hla

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    coreutils \
    grep \
    gawk \
    diffutils \
    findutils \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application scripts
COPY --chown=hla:hla scripts/ /app/scripts/
COPY --chown=hla:hla config/ /app/config/

WORKDIR /app

# Set up directories
RUN mkdir -p /data /output /logs \
    && chown -R hla:hla /data /output /logs /app

# Switch to non-root user
USER hla

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD hla-analyst --version || exit 1

# Default entrypoint
ENTRYPOINT ["hla-analyst"]
CMD ["--help"]

# =============================================================================
# Usage Examples:
# 
# Build:
#   docker build -t hla-analyst:latest .
#
# Run Analysis:
#   docker run --rm -v /path/to/batch:/data hla-analyst analyze /data
#
# Generate Report:
#   docker run --rm -v /path/to/batch:/data -v /path/to/output:/output \
#       hla-analyst analyze /data --format html --output /output/report.html
#
# Interactive Shell:
#   docker run --rm -it -v /path/to/batch:/data --entrypoint /bin/bash hla-analyst
# =============================================================================
