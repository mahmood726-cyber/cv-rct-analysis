Mahmood Ahmad
Tahir Heart Institute
mahmood.ahmad2@nhs.net

CV-RCT Analysis: Cardiovascular Trial Landscape Dashboard Integrating Registry and Publication Data

Can an integrated pipeline map the cardiovascular Phase III trial landscape by reconciling registry, bibliometric, and open-access publication data sources? We built an extraction pipeline connecting ClinicalTrials.gov via AACT PostgreSQL, PubMed for publication matching, and OpenAlex for citation metrics covering cardiovascular trials from 2015 to 2022. The system classifies trials into eight cardiovascular sub-domains via keyword matching, performs automated publication reconciliation, and delivers interactive forest and funnel plots through a Streamlit dashboard with domain-level statistical summaries. Across 87 automated tests covering extraction, reconciliation, mapping, and visualization, all passed with complete coverage from database query through statistical aggregation and plot generation. Domain-level summaries revealed differential publication rates and enrollment patterns across heart failure, coronary artery disease, arrhythmia, and additional cardiovascular sub-domains. Multi-source data reconciliation provides a scalable approach to mapping trial landscapes beyond what any single registry captures alone. The limitation of keyword-based domain classification is that multi-label assignment may inflate counts for trials spanning multiple conditions.

Outside Notes

Type: methods
Primary estimand: Publication rate
App: CV-RCT Analysis Dashboard v1.0
Data: AACT, PubMed, OpenAlex; CV Phase III RCTs 2015-2022
Code: https://github.com/mahmood726-cyber/cv-rct-analysis
Version: 1.0
Validation: DRAFT

References

1. Marshall IJ, Noel-Storr A, Kuber J, et al. Machine learning for identifying randomized controlled trials: an evaluation and practitioner's guide. Res Synth Methods. 2018;9(4):602-614.
2. Jonnalagadda SR, Goyal P, Huffman MD. Automating data extraction in systematic reviews: a systematic review. Syst Rev. 2015;4:78.
3. Borenstein M, Hedges LV, Higgins JPT, Rothstein HR. Introduction to Meta-Analysis. 2nd ed. Wiley; 2021.

AI Disclosure

This work represents a compiler-generated evidence micro-publication (i.e., a structured, pipeline-based synthesis output). AI is used as a constrained synthesis engine operating on structured inputs and predefined rules, rather than as an autonomous author. Deterministic components of the pipeline, together with versioned, reproducible evidence capsules (TruthCert), are designed to support transparent and auditable outputs. All results and text were reviewed and verified by the author, who takes full responsibility for the content. The workflow operationalises key transparency and reporting principles consistent with CONSORT-AI/SPIRIT-AI, including explicit input specification, predefined schemas, logged human-AI interaction, and reproducible outputs.
