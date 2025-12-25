# SynOmix AI v6.0

**Multi-Omics Biomarker Discovery Platform with AI-Powered Insights**

🔬 Live Demo: [https://synomix.ai](https://synomix.ai)

---

## Overview

SynOmix is a web-based platform for integrating and analyzing multi-omics cancer data. Upload your TCGA or custom datasets and get AI-powered biomarker discovery, subtype prediction, and therapy recommendations in seconds.

---

## Features

### 🧬 Multi-Omics Integration
- **Gene Expression** (RNA-seq, microarray)
- **Mutations** (MAF, MutSig)
- **Methylation** (450K, 27K arrays)
- **Copy Number Variation** (GISTIC)
- **Proteomics** (RPPA)

### 🔬 Tumor Microenvironment Analysis (NEW in v6.0)
- Cell-type deconvolution from bulk expression data
- 10 cell populations: Tumor, CD8+ T, CD4+ T, Tregs, B cells, NK, Macrophages, Dendritic, Fibroblasts, Endothelial
- **Immunotherapy Score** prediction
- AI-generated clinical insights

### 🎯 Cancer Subtype Prediction
- Breast cancer: Luminal A, Luminal B, HER2+, Basal-like, Triple Negative
- Evidence-based classification with confidence scores
- Treatment recommendations

### 🤖 AI Assistant (Streaming)
- Real-time streaming responses for faster interaction
- Context-aware Q&A about your analysis results
- Powered by Claude AI

### 📊 Analysis & Export
- Multi-omics convergence analysis
- Pathway enrichment
- Hypothesis generation
- PDF export

---

## Quick Start

### Using the Demo
1. Visit [synomix.ai](https://synomix.ai)
2. Click "Or try with demo TCGA breast cancer data"
3. View results instantly

### Upload Your Data
1. Create a new experiment
2. Upload TCGA files (.cct, .cbt, .txt, .csv, .tsv)
3. Select cancer type
4. Click "Analyze"

---

## Supported File Formats

| Data Type | Formats | Example |
|-----------|---------|---------|
| Expression | .cct, .csv, .tsv, .txt | RSEM, log2 normalized |
| Mutations | .cbt, .maf, .csv | MutSig2CV output |
| Methylation | .cct, .csv | Beta values |
| CNV | .cct, .csv | GISTIC2 output |
| Proteomics | .cct, .csv | RPPA data |

**Note:** TCGA-style gene IDs (`GENE|ENTREZID`) are automatically parsed.

---

## Tech Stack

- **Frontend:** React, Tailwind CSS, Recharts
- **Backend:** FastAPI, Python
- **AI:** Anthropic Claude API (streaming)
- **Analysis:** NumPy, Pandas

---

## Version History

### v6.0 (Current)
- ✨ Cell-type deconvolution & Tumor Microenvironment analysis
- ✨ Immunotherapy score prediction
- ✨ Streaming AI chat responses
- 🐛 Fixed TCGA gene ID parsing

### v5.0
- Multi-omics integration
- Cancer subtype prediction
- AI assistant

---

## Local Development
```bash
# Clone
git clone https://github.com/kadamrohit2010-prog/synomix.git
cd synomix

# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
echo "ANTHROPIC_API_KEY=your_key" > .env

# Run
uvicorn main:app --reload
```

---

## License

MIT License - see LICENSE file

---

## Author

**Rohit Kadam**
- GitHub: [@kadamrohit2010-prog](https://github.com/kadamrohit2010-prog)

---

*Built for cancer researchers and bioinformaticians to accelerate biomarker discovery.*
