# E156 Protocol — `cv-rct-analysis`

This repository is the source code and dashboard backing an E156 micro-paper on the [E156 Student Board](https://mahmood726-cyber.github.io/e156/students.html).

---

## `[43]` CV-RCT Analysis: Cardiovascular Trial Landscape Dashboard Integrating Registry and Publication Data

**Type:** methods  |  ESTIMAND: Publication rate  
**Data:** AACT, PubMed, OpenAlex; CV Phase III RCTs 2015-2022

### 156-word body

Can an integrated pipeline map the cardiovascular Phase III trial landscape by reconciling registry, bibliometric, and open-access publication data sources? We built an extraction pipeline connecting ClinicalTrials.gov via AACT PostgreSQL, PubMed for publication matching, and OpenAlex for citation metrics covering cardiovascular trials from 2015 to 2022. The system classifies trials into eight cardiovascular sub-domains via keyword matching, performs automated publication reconciliation, and delivers interactive forest and funnel plots through a summaries. Across 87 of 87 automated validation tests (100 percent pass rate) covering extraction and visualization, all passed with complete coverage from database query through statistical aggregation and plot generation. Domain-level summaries revealed differential publication rates and enrollment patterns across heart failure, coronary artery disease, arrhythmia, and additional cardiovascular sub-domains. Multi-source data reconciliation provides a scalable approach to mapping trial landscapes beyond what any single registry captures alone. The limitation of keyword-based domain classification is that multi-label assignment may inflate counts for trials spanning multiple conditions.

### Submission metadata

```
Corresponding author: Mahmood Ahmad <mahmood.ahmad2@nhs.net>
ORCID: 0000-0001-9107-3704
Affiliation: Tahir Heart Institute, Rabwah, Pakistan

Links:
  Code:      https://github.com/mahmood726-cyber/cv-rct-analysis
  Protocol:  https://github.com/mahmood726-cyber/cv-rct-analysis/blob/main/E156-PROTOCOL.md
  Dashboard: https://mahmood726-cyber.github.io/cv-rct-analysis/

References (topic pack: publication bias / selection):
  1. Egger M, Davey Smith G, Schneider M, Minder C. 1997. Bias in meta-analysis detected by a simple, graphical test. BMJ. 315(7109):629-634. doi:10.1136/bmj.315.7109.629
  2. Duval S, Tweedie R. 2000. Trim and fill: a simple funnel-plot-based method of testing and adjusting for publication bias in meta-analysis. Biometrics. 56(2):455-463. doi:10.1111/j.0006-341X.2000.00455.x

Data availability: No patient-level data used. Analysis derived exclusively
  from publicly available aggregate records. All source identifiers are in
  the protocol document linked above.

Ethics: Not required. Study uses only publicly available aggregate data; no
  human participants; no patient-identifiable information; no individual-
  participant data. No institutional review board approval sought or required
  under standard research-ethics guidelines for secondary methodological
  research on published literature.

Funding: None.

Competing interests: MA serves on the editorial board of Synthēsis (the
  target journal); MA had no role in editorial decisions on this
  manuscript, which was handled by an independent editor of the journal.

Author contributions (CRediT):
  [STUDENT REWRITER, first author] — Writing – original draft, Writing –
    review & editing, Validation.
  [SUPERVISING FACULTY, last/senior author] — Supervision, Validation,
    Writing – review & editing.
  Mahmood Ahmad (middle author, NOT first or last) — Conceptualization,
    Methodology, Software, Data curation, Formal analysis, Resources.

AI disclosure: Computational tooling (including AI-assisted coding via
  Claude Code [Anthropic]) was used to develop analysis scripts and assist
  with data extraction. The final manuscript was human-written, reviewed,
  and approved by the author; the submitted text is not AI-generated. All
  quantitative claims were verified against source data; cross-validation
  was performed where applicable. The author retains full responsibility for
  the final content.

Preprint: Not preprinted.

Reporting checklist: PRISMA 2020 (methods-paper variant — reports on review corpus).

Target journal: ◆ Synthēsis (https://www.synthesis-medicine.org/index.php/journal)
  Section: Methods Note — submit the 156-word E156 body verbatim as the main text.
  The journal caps main text at ≤400 words; E156's 156-word, 7-sentence
  contract sits well inside that ceiling. Do NOT pad to 400 — the
  micro-paper length is the point of the format.

Manuscript license: CC-BY-4.0.
Code license: MIT.

SUBMITTED: [ ]
```


---

_Auto-generated from the workbook by `C:/E156/scripts/create_missing_protocols.py`. If something is wrong, edit `rewrite-workbook.txt` and re-run the script — it will overwrite this file via the GitHub API._