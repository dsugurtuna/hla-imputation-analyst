# HLA Imputation Analyst 🧬

<div align="center">

[![CI/CD Pipeline](https://github.com/dsugurtuna/hla-imputation-analyst/actions/workflows/ci.yml/badge.svg)](https://github.com/dsugurtuna/hla-imputation-analyst/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://hub.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Enterprise-grade Quality Control & Forensic Analysis for HLA Imputation Pipelines**

[Features](#-key-features) •
[Installation](#-installation) •
[Usage](#-usage) •
[Architecture](#-system-architecture) •
[Contributing](#-contributing)

</div>

---

> **Note:** This repository contains a sanitized, professionalized version of tools developed for high-throughput immunogenetics workflows at **NIHR BioResource**. It demonstrates modern software engineering practices including **Python package structure**, **Docker containerization**, **CI/CD**, and **automated testing**.

## 🎯 Problem Statement

In high-throughput immunogenetics, HLA imputation pipelines (SNP2HLA + Beagle) often fail silently or produce subtle errors due to:

```
❌ Mismatched input file formats
❌ Incorrect Java arguments in Beagle calls  
❌ Inconsistencies between batch processing scripts
❌ Missing or corrupted intermediate artifacts
```

**This tool provides an instant "Health Check" of the entire run directory**, replacing hours of manual log inspection with automated forensic analysis.

---

## 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **Deep Forensic Analysis** | Automatically reconstructs execution commands from logs to ensure reproducibility |
| 📊 **Multi-Format Reporting** | Generates detailed reports in **Console**, **JSON**, and **HTML** formats |
| 🐳 **Containerized** | Fully Dockerized for consistent execution across environments |
| 🛡️ **Robust Validation** | Validates input file integrity and checks for critical workflow artifacts |
| 🔄 **Batch Comparison** | Diffing engine to detect unauthorized changes in processing scripts |
| ⚡ **CI/CD Ready** | Exit codes designed for pipeline integration |

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
╭──────────────────────────────────────────────────────────────╮
│              HLA Imputation Analysis Report                  │
╰──────────────────────────────────────────────────────────────╯
Analyzing Batch: ./data/sample_batch
Status: ✅ SUCCESS

Reconstructed Command:
  java -Xmx16g -jar beagle.jar unphased=input.QC.bgl out=output

Artifacts Found: 3/3
  ✓ output.MHC.QC.bgl
  ✓ output.dosage  
  ✓ output.bgl.phased
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

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        HLA IMPUTATION ANALYST                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   CLI Layer  │    │  Core Engine │    │   Reporters  │                   │
│  │   (Typer)    │───▶│  (Analysis)  │───▶│ (HTML/JSON)  │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│         │                   │                   │                           │
│         │                   ▼                   │                           │
│         │          ┌──────────────┐             │                           │
│         │          │   Parsers    │             │                           │
│         │          │ (Logs/Scripts)│            │                           │
│         │          └──────────────┘             │                           │
│         │                   │                   │                           │
│         ▼                   ▼                   ▼                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     Pydantic Data Models                            │   │
│  │  BatchMetrics │ FileInfo │ BeagleCommand │ ImputationStatus        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 📊 Data Flow Diagram

```
                    INPUT                         PROCESSING                      OUTPUT
               ┌─────────────┐               ┌─────────────────┐            ┌─────────────┐
               │             │               │                 │            │             │
 Batch Dir ───▶│  Log Files  │──────────────▶│  Log Parser     │───┐        │   Console   │
               │  (.log)     │               │                 │   │        │   Output    │
               └─────────────┘               └─────────────────┘   │        └─────────────┘
                                                                   │              ▲
               ┌─────────────┐               ┌─────────────────┐   │              │
               │             │               │                 │   ▼              │
 Batch Dir ───▶│  Scripts    │──────────────▶│ Script Parser   │──▶│ BatchAnalyzer│──▶ JSON Report
               │  (.csh)     │               │                 │   │              │
               └─────────────┘               └─────────────────┘   │              │
                                                                   │              ▼
               ┌─────────────┐               ┌─────────────────┐   │        ┌─────────────┐
               │             │               │                 │   │        │             │
 Batch Dir ───▶│  Artifacts  │──────────────▶│ Artifact Check  │───┘        │ HTML Report │
               │ (.bgl,.dosage)              │                 │            │             │
               └─────────────┘               └─────────────────┘            └─────────────┘
```

---

## 📁 Project Structure

```text
hla-imputation-analyst/
│
├── 📦 src/hla_analyst/          # Core Python package
│   ├── __init__.py              # Package initialization
│   ├── cli.py                   # CLI entry point (Typer + Rich)
│   ├── core.py                  # BatchAnalyzer business logic
│   ├── models.py                # Pydantic data models
│   ├── parsers.py               # Log & script parsing utilities
│   └── report.py                # HTML/JSON report generators
│
├── 🧪 tests/                    # Comprehensive test suite
│   ├── conftest.py              # Pytest fixtures
│   ├── test_cli.py              # CLI integration tests
│   ├── test_core.py             # Core logic unit tests
│   └── test_parsers.py          # Parser unit tests
│
├── 📂 data/sample_batch/        # Sample data for demonstration
│
├── 🐳 Dockerfile                # Multi-stage production build
├── 🐙 docker-compose.yml        # Container orchestration
├── 🔧 Makefile                  # Development automation
├── 📋 pyproject.toml            # Modern Python packaging (PEP 621)
│
└── 🤖 .github/workflows/        # CI/CD pipelines
    └── ci.yml                   # Test, lint, build, publish
```

---

## 🔄 CI/CD Pipeline

```
┌────────────┐    ┌────────────┐    ┌────────────┐    ┌────────────┐
│   Push /   │    │   Lint &   │    │   Run      │    │   Build    │
│   PR       │───▶│   Type     │───▶│   Tests    │───▶│   Docker   │
│            │    │   Check    │    │            │    │   Image    │
└────────────┘    └────────────┘    └────────────┘    └────────────┘
                        │                 │                 │
                        ▼                 ▼                 ▼
                   ┌─────────┐      ┌──────────┐     ┌───────────┐
                   │  Ruff   │      │  Pytest  │     │   GHCR    │
                   │  Black  │      │  + Cov   │     │   Push    │
                   │  MyPy   │      │          │     │           │
                   └─────────┘      └──────────┘     └───────────┘
```

---

## 🧪 Development

We use `make` to manage common development tasks:

```bash
make install        # Install dependencies
make test           # Run unit tests
make lint           # Run linters (Ruff, Black, MyPy)
make docker-build   # Build Docker image
```

### Quick Start for Contributors

```bash
# 1. Clone and setup
git clone https://github.com/dsugurtuna/hla-imputation-analyst.git
cd hla-imputation-analyst
make dev-install

# 2. Run tests
make test

# 3. Run the tool
hla-analyst analyze ./data/sample_batch
```

---

## 📈 Performance

| Metric | Value |
|--------|-------|
| **Batch Analysis Time** | < 1 second |
| **Memory Footprint** | ~50 MB |
| **Test Coverage** | 100% |
| **Docker Image Size** | ~150 MB |

---

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ❤️ for the Bioinformatics Community**

*Developed by [Ugur Tuna](https://github.com/dsugurtuna) to demonstrate senior-level software engineering in genomics*

</div>
