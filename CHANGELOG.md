# SynOmix Changelog

## [v7.0] - 2025-12-25

### Added
- **Survival Analysis** - Prognostic risk scoring based on molecular signatures
  - Risk score (0-100%)
  - Risk groups: Low, Intermediate-Low, Intermediate-High, High
  - 5-year survival estimates
  - Key risk factors and protective factors
- **Drug Recommendations** - FDA-approved targeted therapy matching
  - 21 targetable genes (ERBB2, EGFR, BRAF, ALK, BRCA1/2, PIK3CA, KRAS, etc.)
  - Evidence levels (1A highest)
  - Indication and approval status
- **4 New Cancer Types**
  - Prostate: Luminal, Basal, Neuroendocrine
  - Ovarian: High-grade Serous, Low-grade Serous, Clear Cell
  - Pancreatic: Classical, Basal-like, MSI-High
  - Melanoma: BRAF-mutant, NRAS-mutant, Triple Wild-type
- **Start Over Button** - Reset analysis without page refresh

### Changed
- Version bumped to 7.0.0
- Improved UI layout for new components

---

## [v6.0] - 2025-12-25

### Added
- **Tumor Microenvironment Analysis**
  - Cell-type deconvolution (10 populations)
  - Immunotherapy Score (0-100%)
  - Clinical insights
- **Streaming AI Chat** - Real-time response generation
- **TCGA Gene ID Parsing** - Auto-extracts gene symbols

### Fixed
- Numpy float serialization for JSON
- Decimal place formatting

---

## [v5.0] - 2025-12-24

### Added
- Multi-omics integration (5 layers)
- Cancer subtype prediction
- AI Assistant
- PDF export
- Pathway enrichment

---

## [v4.0] - 2025-12-23

### Added
- Initial release
- Basic file upload
- Expression analysis
