# Why it's built this way

## The problem

A failed SNP2HLA run leaves its evidence spread across a Beagle log, a csh script and a folder of half-written files. Deciding whether a run finished, why it stopped and what changed from the last good run should take seconds, not an afternoon of reading logs.

## Design choices

**Why decide success from SNP2HLA's final outputs?** Because the script's default cleanup deletes the `<OUTPUT>.MHC.*` intermediates. An earlier version required `.MHC.QC.bgl`, which would have reported every correctly completed run as incomplete.

**Why make a missing output an error rather than a warning?** Because a run without `.dosage` or `.bgl.r2` cannot be released. A check that only warns gets ignored in a pipeline.

**Why such a narrow error pattern?** Because a broad one cries wolf. Matching any line containing "error" flags "finished with 0 errors". Whole words plus a short list of fatal messages (`OutOfMemoryError`, `Segmentation fault`, `Killed`) catches real failures without training people to ignore the tool.

**Why check the column count of Beagle input?** Because Beagle 3 expects two columns per sample after two leading columns. An odd count means a sample lost a column during conversion, which Beagle may not report clearly.

**Why compare with a known-good run?** Because most failures are a changed setting or a missing file. Listing the `set` parameters that differ (for example the Beagle window) and the outputs the good run has points straight at the cause.

**Why separate `analyze` and `validate`?** Because people and pipelines want different things. `analyze` explains and always exits 0; `validate` is silent and exits 1 on failure, so a pipeline can stop before a bad batch moves on.

**Why so few dependencies, and no network libraries?** Because this runs on machines that hold genetic data. An earlier version declared an HTTP client it never used; every dependency is something a reviewer has to trust.

## Questions worth asking

**"A run passes this check. Does that mean the imputation is good?"**
No. It means the run completed and produced its outputs. Quality needs the per-marker `.bgl.r2` values (Beagle's estimate of how well each allele was imputed) and, ideally, samples with lab HLA typing to measure accuracy. Summarising `.bgl.r2` for HLA markers is the next item on the roadmap.

**"What if the log format changes between Beagle versions?"**
The command extraction is a best-effort search and returns nothing if it finds no `java ... -jar ...` line; that is reported as "no command found", not as a failure. The error patterns are generic Java and operating-system messages, so they carry over. SNP2HLA uses Beagle 3; newer Beagle versions write different outputs and would need their own artifact list.

**"Why not just check exit codes?"**
Because on a shared cluster you often only have the directory afterwards: the job may have been killed, the exit code lost, or the run started by someone else. The directory is the evidence that is always there.

## What's next

- Summarise `.bgl.r2` for HLA markers and flag alleles below a threshold.
- Check that output sample counts match the input `.fam`.
- Add CookHLA output names.
