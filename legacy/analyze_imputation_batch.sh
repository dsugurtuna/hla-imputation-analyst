#!/bin/bash

# ==============================================================================
# Script Name: analyze_imputation_batch.sh
# Author:      Ugur Tuna
# Context:     Developed during tenure at NIHR BioResource (Cambridge).
# Disclaimer:  Sanitized version for educational/portfolio use.
#
# Description: Analyzes the integrity and execution status of HLA imputation 
#              batches (SNP2HLA/Beagle). It checks logs, input formats, and 
#              reconstructs execution commands for QC purposes.
# Usage:       ./analyze_imputation_batch.sh <batch_directory> [comparison_directory]
# ==============================================================================

# --- Configuration ---
BATCH_DIR=$1
COMPARE_DIR=$2

# --- Validation ---
if [ -z "$BATCH_DIR" ]; then
    echo "Usage: $0 <batch_directory> [comparison_directory]"
    echo "Example: $0 ./data/batch_28_hla ./data/batch_26_hla"
    exit 1
fi

if [ ! -d "$BATCH_DIR" ]; then
    echo "Error: Directory '$BATCH_DIR' not found."
    exit 1
fi

echo "========================================================"
echo "HLA Imputation Analysis Tool"
echo "Target Batch: $BATCH_DIR"
if [ ! -z "$COMPARE_DIR" ]; then
    echo "Comparing vs: $COMPARE_DIR"
fi
echo "========================================================"

# 1. Directory Structure Analysis
echo -e "\n[1] Directory Structure Analysis"
echo "--------------------------------"
# Find key batch files (generalized pattern)
find "$BATCH_DIR" -type f -name "*batch*" | sort | head -n 10
echo "... (truncated list)"

# 2. Key Script Analysis (SNP2HLA)
echo -e "\n[2] Key Script Analysis (SNP2HLA.csh)"
echo "-------------------------------------"
SCRIPT_PATH="$BATCH_DIR/SNP2HLA.csh"

if [ -f "$SCRIPT_PATH" ]; then
    echo "Found SNP2HLA.csh script - analyzing key parameters:"
    echo "  > Linkage2Beagle calls:"
    grep -n "linkage2beagle" "$SCRIPT_PATH" | head -3
    echo "  > Beagle JAR usage:"
    grep -n "beagle.jar" "$SCRIPT_PATH" | head -3
    echo "  > Dosage Parsing:"
    grep -n "ParseDosage" "$SCRIPT_PATH" | head -3
else
    echo "Warning: SNP2HLA.csh not found in $BATCH_DIR"
fi

# 3. Log File Analysis
echo -e "\n[3] Log File Analysis"
echo "---------------------"
# Search for common Beagle log patterns
LOG_FILE=$(find "$BATCH_DIR" -name "*.log" | grep "beagle" | head -n 1)

if [ -f "$LOG_FILE" ]; then
    echo "Analyzing Beagle run log: $(basename "$LOG_FILE")"
    grep -n "Beagle" "$LOG_FILE" | head -10
else
    echo "No Beagle log file found."
fi

# 4. Input File Format QC
echo -e "\n[4] Input File Format QC"
echo "------------------------"
# Look for QC'd Beagle input files
INPUT_FILE=$(find "$BATCH_DIR" -name "*.QC.bgl" | head -n 1)

if [ -f "$INPUT_FILE" ]; then
    echo "Analyzing input file format: $(basename "$INPUT_FILE")"
    COL_COUNT=$(head -n 1 "$INPUT_FILE" | wc -w)
    echo "  > Column Count: $COL_COUNT"
    echo "  > Header Preview (first 10 fields):"
    head -n 1 "$INPUT_FILE" | tr ' ' '\n' | head -10 | sed 's/^/    /'
else
    echo "No .QC.bgl input file found."
fi

# 5. Command Reconstruction
echo -e "\n[5] Execution Command Reconstruction"
echo "------------------------------------"
if [ -f "$LOG_FILE" ]; then
    echo "Reconstructing Beagle command from log:"
    # Extract the java command line from the log
    grep -A 5 "java -" "$LOG_FILE" | head -10 | sed 's/^/  /'
fi

# 6. Workflow Artifact Check
echo -e "\n[6] Workflow Artifact Check"
echo "---------------------------"
echo "Checking for intermediate files:"
ls -la "$BATCH_DIR"/*.MHC* 2>/dev/null | awk '{print $9}' | xargs -n 1 basename

# 7. Comparison (Optional)
if [ ! -z "$COMPARE_DIR" ]; then
    echo -e "\n[7] Batch Comparison"
    echo "--------------------"
    if [ ! -d "$COMPARE_DIR" ]; then
        echo "Error: Comparison directory '$COMPARE_DIR' not found."
    else
        echo "Comparing SNP2HLA.csh scripts:"
        if [ -f "$BATCH_DIR/SNP2HLA.csh" ] && [ -f "$COMPARE_DIR/SNP2HLA.csh" ]; then
            DIFF_OUT=$(diff -q "$BATCH_DIR/SNP2HLA.csh" "$COMPARE_DIR/SNP2HLA.csh")
            if [ -z "$DIFF_OUT" ]; then
                echo "  > Scripts are IDENTICAL."
            else
                echo "  > Scripts DIFFER."
            fi
        else
            echo "  > Cannot compare (script missing in one or both dirs)."
        fi
    fi
fi

echo -e "\n========================================================"
echo "Analysis Complete."
echo "========================================================"
