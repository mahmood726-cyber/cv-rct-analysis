Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

CV-RCT Analysis: Cardiovascular Trial Landscape Dashboard Integrating Registry and Publication Data

Can an integrated pipeline map the cardiovascular Phase III trial landscape by reconciling registry, bibliometric, and open-access publication data sources? We built an extraction pipeline connecting ClinicalTrials.gov via AACT PostgreSQL, PubMed for publication matching, and OpenAlex for citation metrics covering cardiovascular trials from 2015 to 2022. The system classifies trials into eight cardiovascular sub-domains via keyword matching, performs automated publication reconciliation, and delivers interactive forest and funnel plots through a summaries. Across 87 of 87 automated validation tests (100 percent pass rate) covering extraction and visualization, all passed with complete coverage from database query through statistical aggregation and plot generation. Domain-level summaries revealed differential publication rates and enrollment patterns across heart failure, coronary artery disease, arrhythmia, and additional cardiovascular sub-domains. Multi-source data reconciliation provides a scalable approach to mapping trial landscapes beyond what any single registry captures alone. The limitation of keyword-based domain classification is that multi-label assignment may inflate counts for trials spanning multiple conditions.

Outside Notes

Type: methods
Primary estimand: Publication rate
App: CV-RCT Analysis Dashboard v1.0
Data: AACT, PubMed, OpenAlex; CV Phase III RCTs 2015-2022
Code: https://github.com/mahmood726-cyber/cv-rct-analysis
Version: 1.0
Validation: DRAFT

References

1. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.
2. Higgins JPT, Thompson SG, Deeks JJ, Altman DG. Measuring inconsistency in meta-analyses. BMJ. 2003;327(7414):557-560.
3. Cochrane Handbook for Systematic Reviews of Interventions. Version 6.4. Cochrane; 2023.
