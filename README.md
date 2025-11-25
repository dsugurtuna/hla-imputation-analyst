# HLA Imputation Analyst 🧬

[![CI/CD Pipeline](https://github.com/dsugurtuna/hla-imputation-analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/dsugurtuna/hla-imputation-analyst/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Enterprise-grade Quality Control & Forensic Analysis for HLA Imputation Pipelines.**

> **Note:** This repository contains a sanitized, professionalized version of tools developed for high-throughput immunogenetics workflows. It demonstrates modern software engineering practices including **Python package structure**, **Docker containerization**, **CI/CD**, and **automated testing**.

---

## 🚀 Key Features

*   **🔍 Deep Forensic Analysis**: Automatically reconstructs execution commands from logs to ensure reproducibility.
*   **📊 Multi-Format Reporting**: Generates detailed reports in **Console**, **JSON**, and **HTML** formats.
*   **🐳 Containerized**: Fully Dockerized for consistent execution across environments.
*   **🛡️ Robust Validation**: Validates input file integrity and checks for critical workflow artifacts.
*   **🔄 Batch Comparison**: Diffing engine to detect unauthorized changes in processing scripts between batches.

## 🛠️ Installation

### Option 1: Docker (Recommended)

No installation required. Run directly using the pre-built image:

```bash
# Build the image
docker build -t hla-analyst .

# Run analysis
docker run --rm -v $(pwd)/data:/data hla-analyst analyze /data/sample_batch
```

### Option 2: Python Package

```bash
# Clone the repository
git clone https://github.com/dsugurtuna/hla-imputation-analyst.git
cd hla-imputation-analyst

# Install with pip
pip install .

# Verify installation
hla-analyst --help
```

## 📖 Usage

### 1. Analyze a Batch
Run a comprehensive health check on an imputation batch:

```bash
hla-analyst analyze ./data/sample_batch
```

**Output:**
```text
Analyzing Batch: ./data/sample_batch
Status: SUCCESS

Reconstructed Command:
  java -Xmx16g -jar beagle.jar unphased=input.QC.bgl out=output
```

### 2. Generate HTML Report
Create a shareable HTML report for stakeholders:

```bash
hla-analyst analyze ./data/sample_batch --format html --output report.html
```

### 3. Compare Batches
Debug a failed batch by comparing it against a known good reference:

```bash
hla-analyst analyze ./data/failed_batch --compare ./data/good_batch
```

### 4. CI/CD Integration
Use the validation command in your pipeline to fail builds on bad data:

```bash
hla-analyst validate ./data/new_batch || echo "Batch Failed QC!"
```

## 🏗️ Architecture

The project is structured as a modern Python application:

```text
.
├── src/hla_analyst/       # 📦 Core package
│   ├── cli.py             # CLI entry point (Typer)
│   ├── core.py            # Business logic
│   ├── parsers.py         # Log & script parsers
│   └── report.py          # Report generation engine
├── tests/                 # 🧪 Comprehensive test suite
├── Dockerfile             # 🐳 Multi-stage Docker build
├── docker-compose.yml     # 🐙 Orchestration config
├── pyproject.toml         # 🐍 Project metadata & dependencies
└── .github/workflows/     # 🤖 CI/CD pipelines
```

## 🧪 Development

We use `make` to manage common development tasks:

```bash
make install        # Install dependencies
make test           # Run unit tests
make lint           # Run linters (Ruff, Black, MyPy)
make docker-build   # Build Docker image
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---
*Developed by Ugur Tuna to demonstrate senior-level software engineering capabilities in bioinformatics.*
