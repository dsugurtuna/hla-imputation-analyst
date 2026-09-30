# Synthetic example runs

All files are invented for the quickstart and tests; nothing comes from a real cohort. `SNP2HLA.csh` here is a stand-in containing only `set` lines, not the real script.

- `sample_batch/`: a complete run (outputs named as SNP2HLA writes them, with the `demo.MHC.QC.bgl` intermediate kept).
- `failed_batch/`: a run that ran out of Java heap: no `.dosage`, `.bgl.gprobs` or `.bgl.r2`, a different Beagle window and a malformed Beagle input file.
