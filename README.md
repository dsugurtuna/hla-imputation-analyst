# HLA Imputation Analyst 🧬

[![Bash](https://img.shields.io/badge/Language-Bash-blue.svg)](https://www.gnu.org/software/bash/)
[![Bioinformatics](https://img.shields.io/badge/Domain-Bioinformatics-green.svg)]()
[![Portfolio](https://img.shields.io/badge/Status-Portfolio_Project-purple.svg)]()

**Automated Quality Control & Forensics for HLA Imputation Pipelines.**

> **Note:** This repository contains sanitized versions of scripts developed during my tenure at **NIHR BioResource**. They are presented here for **educational and portfolio purposes only** to demonstrate proficiency in pipeline debugging and QC. No real patient data or internal infrastructure paths are included.

The **HLA Imputation Analyst** is a forensic tool designed to audit the execution of complex imputation workflows (specifically **SNP2HLA** and **Beagle**). It helps bioinformaticians quickly diagnose why a batch failed or verify that a successful batch was processed correctly.

---

## 🌟 Use Case: Pipeline Debugging

In high-throughput immunogenetics, imputation pipelines often fail silently or produce subtle errors due to:
*   Mismatched input file formats.
*   Incorrect Java arguments in the Beagle call.
*   Inconsistencies between batch processing scripts.

Instead of manually opening dozens of log files, this tool provides an instant "Health Check" of the entire run directory.

## 🚀 Key Features

*   **🕵️ Command Reconstruction**: Parses log files to reconstruct the *exact* Java command used to run Beagle, ensuring reproducibility.
*   **📜 Script Diffing**: Automatically compares the processing script of the current batch against a known "Gold Standard" batch to detect unauthorized changes.
*   **🔍 Input QC**: Validates the structure of `.bgl` input files (column counts, headers) before they hit the imputation engine.
*   **📂 Artifact Verification**: Checks for the presence of critical intermediate files (`.MHC.QC.bgl`, `.dosage`) to confirm workflow completion.

## 📂 Repository Structure

```text
.
├── analyze_imputation_batch.sh  # 🚀 Main Analysis Tool
└── README.md                    # 📖 Documentation
```

## 🛠️ Usage

### Prerequisites
*   Bash shell
*   Standard Unix tools (`grep`, `find`, `diff`, `awk`)

### Running an Analysis

**1. Analyze a Single Batch**
```bash
./analyze_imputation_batch.sh ./data/batch_28_hla
```

**2. Compare Against a Reference Batch**
Debug a failed batch by comparing it to a successful one:
```bash
./analyze_imputation_batch.sh ./data/batch_29_failed ./data/batch_28_success
```

### Sample Output
```text
[1] Directory Structure Analysis
--------------------------------
Found SNP2HLA.csh script - analyzing key parameters:
  > Linkage2Beagle calls: 12
  > Beagle JAR usage: beagle.jar parameter=true

[5] Execution Command Reconstruction
------------------------------------
Reconstructing Beagle command from log:
  java -Xmx16g -jar beagle.jar unphased=input.bgl ...
```

## 🤝 Contributing
Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---
*Developed to ensure the reliability of immunogenetic data processing.*
