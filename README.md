# SynOmix AI v7.0

**Multi-Omics Biomarker Discovery Platform with AI-Powered Clinical Insights**

🔬 **Live Demo:** [https://synomix.ai](https://synomix.ai)

---

## What's New in v7.0

- 📈 **Survival Analysis** - Prognostic risk scoring with 5-year survival estimates
- 💊 **Drug Recommendations** - 21 FDA-approved targeted therapies matched to your biomarkers
- 🧬 **More Cancer Types** - Now supports 7 cancers: breast, lung, colorectal, prostate, ovarian, pancreatic, melanoma
- ↺ **Start Over Button** - Easy reset to analyze new samples

---

## Features

### 🧬 Multi-Omics Integration (5 Data Layers)
| Data Type | Formats | Analysis |
|-----------|---------|----------|
| Gene Expression | .cct, .csv, .tsv | Differential expression, variance |
| Mutations | .cbt, .maf | Mutation frequency, driver detection |
| Methylation | .cct, .csv | Hyper/hypomethylation |
| Copy Number | .cct (GISTIC) | Amplifications, deletions |
| Proteomics | .cct (RPPA) | Protein abundance |

### 🔬 Tumor Microenvironment (v6.0+)
- Cell-type deconvolution (10 populations)
- Immunotherapy score prediction
- AI-generated clinical insights

### 📈 Survival Analysis (v7.0)
- Risk score calculation
- 5-year survival estimates
- Prognostic signature analysis (proliferation, immune, stemness, invasion)

### 💊 Drug Recommendations (v7.0)
- 21 targetable genes with FDA-approved therapies
- Evidence levels (1A = highest)
- Matched to mutations, amplifications, and expression

### 🎯 Cancer Subtype Prediction
| Cancer | Subtypes |
|--------|----------|
| Breast | Luminal A, Luminal B, HER2+, Basal-like |
| Lung | EGFR, ALK, KRAS, PD-L1 high, SCLC |
| Colorectal | CMS1-4 |
| Prostate | Luminal, Basal, Neuroendocrine |
| Ovarian | High-grade Serous, Low-grade, Clear Cell |
| Pancreatic | Classical, Basal-like, MSI-High |
| Melanoma | BRAF, NRAS, Triple WT |

### 🤖 AI Assistant
- Streaming responses (Claude AI)
- Context-aware Q&A about your results
- Clinical interpretation help

---

## Quick Start

### Option 1: Demo Data
1. Visit [synomix.ai](https://synomix.ai)
2. Click **"Or try with demo TCGA breast cancer data"**
3. View instant results

### Option 2: Upload Your Data
1. Click **Upload Data**
2. Drag & drop TCGA files
3. Select cancer type
4. Click **Analyze**

---

## Tech Stack

- **Frontend:** React 18, Tailwind CSS, Recharts
- **Backend:** FastAPI, Python 3.12
- **AI:** Anthropic Claude (streaming)
- **Analysis:** NumPy, Pandas

---

## Local Development
```bash
git clone https://github.com/kadamrohit2010-prog/synomix.git
cd synomix
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
echo "ANTHROPIC_API_KEY=your_key" > .env
uvicorn main:app --reload
```

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| v7.0 | Dec 25, 2024 | Survival analysis, drug recommendations, 4 new cancer types |
| v6.0 | Dec 25, 2024 | Cell deconvolution, immunotherapy score, streaming chat |
| v5.0 | Dec 24, 2024 | Multi-omics integration, subtype prediction |

---

## Author

**Rohit Kadam** - [@kadamrohit2010-prog](https://github.com/kadamrohit2010-prog)

---

## License

MIT License
