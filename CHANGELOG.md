# SynOmix Changelog

All notable changes to SynOmix are documented here.

---

## [v6.0] - 2025-12-25

### Added
- **Tumor Microenvironment Analysis** - Cell-type deconvolution from bulk RNA-seq
  - 10 cell populations: Tumor Epithelial, CD8+ T Cells, CD4+ T Cells, Tregs, B Cells, NK Cells, Macrophages, Dendritic Cells, Fibroblasts, Endothelial
  - Immunotherapy Score (0-100%) prediction
  - Clinical insights (e.g., "High CD8+ T cell infiltration suggests immunotherapy responsiveness")
- **Streaming AI Chat** - Responses appear word-by-word for faster perceived speed
- **Version display** in sidebar (v6.0)

### Fixed
- TCGA gene ID parsing (`GENE|ENTREZID` → `GENE`)
- Numpy float serialization for JSON responses
- Decimal place formatting in UI

### Changed
- Upgraded AI model to Claude Sonnet 4
- Improved error handling in analysis pipeline

---

## [v5.0] - 2025-12-24

### Added
- Multi-omics integration (expression, mutation, methylation, CNV, proteomics)
- Cancer subtype prediction with confidence scores
- AI Assistant for Q&A about results
- PDF export functionality
- Pathway enrichment analysis
- Hypothesis generation

---

## [v4.0] - 2025-12-23

### Added
- Basic file upload functionality
- Expression analysis
- Simple biomarker detection
- Initial UI design

---
