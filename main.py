#!/usr/bin/env python3
"""
SynOmix AI - Production Server (Optimized for Large Files)
Fast processing with vectorized operations
"""

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from typing import List, Dict
import pandas as pd
import numpy as np
import io
import gzip
from datetime import datetime
import os

app = FastAPI(title="SynOmix AI", version="3.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
experiments = {}

# Databases
PATHWAYS = {
    "PI3K-AKT": {"genes": ["PIK3CA", "AKT1", "MTOR", "PTEN", "PIK3R1"], "drugs": ["Alpelisib", "Everolimus"]},
    "HER2/ERBB": {"genes": ["ERBB2", "ERBB3", "EGFR", "GRB7"], "drugs": ["Trastuzumab", "Pertuzumab", "T-DM1"]},
    "Cell Cycle": {"genes": ["CCND1", "CDK4", "CDK6", "RB1", "CDKN2A"], "drugs": ["Palbociclib", "Ribociclib"]},
    "p53 Pathway": {"genes": ["TP53", "MDM2", "MDM4", "ATM", "CHEK2"], "drugs": []},
    "Estrogen Receptor": {"genes": ["ESR1", "PGR", "FOXA1", "GATA3"], "drugs": ["Tamoxifen", "Fulvestrant"]},
    "DNA Repair": {"genes": ["BRCA1", "BRCA2", "ATM", "PALB2", "RAD51"], "drugs": ["Olaparib", "Talazoparib"]},
    "Angiogenesis": {"genes": ["VEGFA", "VEGFB", "HIF1A", "KDR"], "drugs": ["Bevacizumab"]},
    "MAPK": {"genes": ["KRAS", "NRAS", "BRAF", "MAP2K1"], "drugs": ["Trametinib", "Vemurafenib"]},
}

BIOMARKERS = {
    "ERBB2": {"role": "Oncogene (HER2)", "drugs": ["Trastuzumab", "Pertuzumab"]},
    "ESR1": {"role": "Hormone receptor", "drugs": ["Tamoxifen", "Fulvestrant"]},
    "TP53": {"role": "Tumor suppressor", "drugs": []},
    "PIK3CA": {"role": "Oncogene", "drugs": ["Alpelisib"]},
    "BRCA1": {"role": "DNA repair", "drugs": ["Olaparib", "Talazoparib"]},
    "BRCA2": {"role": "DNA repair", "drugs": ["Olaparib", "Talazoparib"]},
    "PTEN": {"role": "Tumor suppressor", "drugs": []},
    "MKI67": {"role": "Proliferation marker", "drugs": []},
    "CDK4": {"role": "Cell cycle", "drugs": ["Palbociclib"]},
    "CDK6": {"role": "Cell cycle", "drugs": ["Palbociclib"]},
    "CCND1": {"role": "Cell cycle", "drugs": ["Palbociclib"]},
    "VEGFA": {"role": "Angiogenesis", "drugs": ["Bevacizumab"]},
    "EGFR": {"role": "Oncogene", "drugs": ["Erlotinib", "Gefitinib"]},
    "KRAS": {"role": "Oncogene", "drugs": ["Sotorasib"]},
    "BRAF": {"role": "Oncogene", "drugs": ["Vemurafenib"]},
    "GRB7": {"role": "HER2 co-amplified", "drugs": []},
    "FOXA1": {"role": "Transcription factor", "drugs": []},
    "GATA3": {"role": "Transcription factor", "drugs": []},
    "PGR": {"role": "Hormone receptor", "drugs": ["Tamoxifen"]},
    "ATM": {"role": "DNA damage response", "drugs": []},
    "PALB2": {"role": "DNA repair", "drugs": ["Olaparib"]},
    "AKT1": {"role": "Oncogene", "drugs": ["Capivasertib"]},
    "MTOR": {"role": "Cell growth", "drugs": ["Everolimus"]},
}

BIOMARKER_SET = set(BIOMARKERS.keys())

# Cancer-specific subtypes and markers
CANCER_SUBTYPES = {
    "breast": {
        "name": "Breast Cancer",
        "subtypes": {
            "Luminal A": {
                "markers": {"ESR1": "high", "PGR": "high", "ERBB2": "low", "MKI67": "low"},
                "description": "Hormone receptor positive, slow-growing, best prognosis",
                "treatment": "Endocrine therapy (Tamoxifen, Aromatase inhibitors)"
            },
            "Luminal B": {
                "markers": {"ESR1": "high", "PGR": "variable", "ERBB2": "variable", "MKI67": "high"},
                "description": "Hormone receptor positive but more aggressive, may need chemo",
                "treatment": "Endocrine therapy + chemotherapy"
            },
            "HER2-enriched": {
                "markers": {"ESR1": "low", "PGR": "low", "ERBB2": "high", "MKI67": "high"},
                "description": "HER2-driven, aggressive but responds well to targeted therapy",
                "treatment": "Trastuzumab, Pertuzumab, T-DM1"
            },
            "Basal-like": {
                "markers": {"ESR1": "low", "PGR": "low", "ERBB2": "low", "MKI67": "high"},
                "description": "Triple-negative, most aggressive, limited targeted options",
                "treatment": "Chemotherapy, PARP inhibitors if BRCA mutated"
            }
        }
    },
    "lung": {
        "name": "Lung Cancer (NSCLC)",
        "subtypes": {
            "EGFR-mutant": {
                "markers": {"EGFR": "mutated", "ALK": "normal", "KRAS": "normal"},
                "description": "EGFR-driven, common in non-smokers and Asian populations",
                "treatment": "Osimertinib, Erlotinib, Gefitinib"
            },
            "ALK-rearranged": {
                "markers": {"ALK": "rearranged", "EGFR": "normal", "KRAS": "normal"},
                "description": "ALK fusion positive, excellent response to ALK inhibitors",
                "treatment": "Alectinib, Crizotinib, Lorlatinib"
            },
            "KRAS-mutant": {
                "markers": {"KRAS": "mutated", "EGFR": "normal", "STK11": "variable"},
                "description": "KRAS-driven, historically undruggable but new options emerging",
                "treatment": "Sotorasib (G12C), Adagrasib"
            },
            "PD-L1 high": {
                "markers": {"CD274": "high", "EGFR": "normal", "ALK": "normal"},
                "description": "High PD-L1 expression, responds to immunotherapy",
                "treatment": "Pembrolizumab, Nivolumab, Atezolizumab"
            },
            "SCLC": {
                "markers": {"RB1": "low", "TP53": "mutated", "ASCL1": "high"},
                "description": "Small cell lung cancer, aggressive neuroendocrine tumor",
                "treatment": "Platinum-etoposide + immunotherapy"
            }
        }
    },
    "colorectal": {
        "name": "Colorectal Cancer",
        "subtypes": {
            "CMS1 (MSI-H)": {
                "markers": {"MLH1": "low", "MSH2": "variable", "BRAF": "mutated"},
                "description": "Microsatellite unstable, high immune infiltration, good prognosis",
                "treatment": "Pembrolizumab, Nivolumab (immunotherapy)"
            },
            "CMS2 (Canonical)": {
                "markers": {"APC": "mutated", "TP53": "mutated", "KRAS": "normal"},
                "description": "WNT/MYC activated, chromosomally unstable, most common",
                "treatment": "FOLFOX, FOLFIRI, Cetuximab if RAS wild-type"
            },
            "CMS3 (Metabolic)": {
                "markers": {"KRAS": "mutated", "PIK3CA": "variable"},
                "description": "Metabolic dysregulation, mixed features",
                "treatment": "FOLFOX, FOLFIRI"
            },
            "CMS4 (Mesenchymal)": {
                "markers": {"TGFB1": "high", "NOTCH1": "variable"},
                "description": "Stromal infiltration, EMT activated, worst prognosis",
                "treatment": "FOLFOXIRI, clinical trials"
            }
        }
    },
    "prostate": {
        "name": "Prostate Cancer",
        "subtypes": {
            "Luminal A": {
                "markers": {"AR": "high", "FOXA1": "high", "SPINK1": "low"},
                "description": "Androgen-driven, well-differentiated, good prognosis",
                "treatment": "Active surveillance or ADT"
            },
            "Luminal B": {
                "markers": {"AR": "high", "FOXA1": "high", "MKI67": "high"},
                "description": "Androgen-driven but more proliferative",
                "treatment": "ADT + Abiraterone or Enzalutamide"
            },
            "ERG-fusion": {
                "markers": {"ERG": "high", "TMPRSS2": "rearranged"},
                "description": "TMPRSS2-ERG fusion, most common genomic alteration",
                "treatment": "ADT, PARP inhibitors if HRD"
            },
            "BRCA-mutant": {
                "markers": {"BRCA2": "mutated", "BRCA1": "variable", "ATM": "variable"},
                "description": "DNA repair deficient, sensitive to PARP inhibitors",
                "treatment": "Olaparib, Rucaparib"
            },
            "Neuroendocrine": {
                "markers": {"AR": "low", "SYP": "high", "CHGA": "high", "RB1": "low"},
                "description": "AR-independent, aggressive, poor prognosis",
                "treatment": "Platinum-based chemotherapy"
            }
        }
    },
    "ovarian": {
        "name": "Ovarian Cancer",
        "subtypes": {
            "High-grade Serous": {
                "markers": {"TP53": "mutated", "BRCA1": "variable", "BRCA2": "variable"},
                "description": "Most common type, often BRCA-associated",
                "treatment": "Platinum + PARP inhibitors"
            },
            "Endometrioid": {
                "markers": {"CTNNB1": "mutated", "PIK3CA": "variable", "ARID1A": "variable"},
                "description": "Often associated with endometriosis",
                "treatment": "Platinum-based chemotherapy"
            },
            "Clear Cell": {
                "markers": {"ARID1A": "mutated", "PIK3CA": "mutated", "HNF1B": "high"},
                "description": "Chemoresistant, associated with endometriosis",
                "treatment": "Platinum, immunotherapy trials"
            },
            "Mucinous": {
                "markers": {"KRAS": "mutated", "ERBB2": "variable"},
                "description": "Rare, behaves like GI tumors",
                "treatment": "GI-type chemotherapy regimens"
            }
        }
    },
    "melanoma": {
        "name": "Melanoma",
        "subtypes": {
            "BRAF-mutant": {
                "markers": {"BRAF": "mutated", "NRAS": "normal"},
                "description": "BRAF V600E/K mutation, ~50% of melanomas",
                "treatment": "Dabrafenib + Trametinib, Vemurafenib + Cobimetinib"
            },
            "NRAS-mutant": {
                "markers": {"NRAS": "mutated", "BRAF": "normal"},
                "description": "NRAS-driven, limited targeted options",
                "treatment": "Immunotherapy (Pembrolizumab, Nivolumab)"
            },
            "Triple Wild-type": {
                "markers": {"BRAF": "normal", "NRAS": "normal", "KIT": "normal"},
                "description": "No common driver mutations",
                "treatment": "Immunotherapy"
            },
            "KIT-mutant": {
                "markers": {"KIT": "mutated", "BRAF": "normal"},
                "description": "Common in acral and mucosal melanoma",
                "treatment": "Imatinib, Nilotinib"
            },
            "Uveal": {
                "markers": {"GNAQ": "mutated", "GNA11": "mutated", "BAP1": "variable"},
                "description": "Eye melanoma, distinct biology",
                "treatment": "Tebentafusp, clinical trials"
            }
        }
    },
    "glioma": {
        "name": "Glioma (Brain Cancer)",
        "subtypes": {
            "IDH-mutant Astrocytoma": {
                "markers": {"IDH1": "mutated", "ATRX": "mutated", "TP53": "mutated"},
                "description": "Better prognosis, younger patients",
                "treatment": "Temozolomide, Vorasidenib (IDH inhibitor)"
            },
            "IDH-mutant Oligodendroglioma": {
                "markers": {"IDH1": "mutated", "TERT": "mutated"},
                "description": "1p/19q co-deleted, best prognosis among gliomas",
                "treatment": "PCV chemotherapy, Temozolomide"
            },
            "IDH-wildtype Glioblastoma": {
                "markers": {"IDH1": "normal", "EGFR": "amplified", "TERT": "mutated", "PTEN": "deleted"},
                "description": "Most aggressive, poor prognosis",
                "treatment": "Temozolomide + radiation, Bevacizumab"
            },
            "H3K27M-mutant": {
                "markers": {"H3F3A": "mutated"},
                "description": "Diffuse midline glioma, pediatric/young adult",
                "treatment": "ONC201, clinical trials"
            }
        }
    },
    "pancreatic": {
        "name": "Pancreatic Cancer",
        "subtypes": {
            "Classical": {
                "markers": {"GATA6": "high", "KRAS": "mutated", "SMAD4": "variable"},
                "description": "Better differentiated, slightly better prognosis",
                "treatment": "FOLFIRINOX, Gemcitabine + nab-Paclitaxel"
            },
            "Basal-like": {
                "markers": {"GATA6": "low", "KRT5": "high", "TP63": "high"},
                "description": "Squamous features, worst prognosis",
                "treatment": "FOLFIRINOX, clinical trials"
            },
            "BRCA-mutant": {
                "markers": {"BRCA1": "mutated", "BRCA2": "mutated"},
                "description": "DNA repair deficient, ~5-7% of cases",
                "treatment": "Platinum-based therapy, Olaparib maintenance"
            }
        }
    },
    "liver": {
        "name": "Hepatocellular Carcinoma (HCC)",
        "subtypes": {
            "Proliferative": {
                "markers": {"AFP": "high", "MKI67": "high", "TP53": "mutated"},
                "description": "Aggressive, AFP-elevated, poor prognosis",
                "treatment": "Atezolizumab + Bevacizumab, Sorafenib"
            },
            "Non-proliferative": {
                "markers": {"CTNNB1": "mutated", "AFP": "normal"},
                "description": "WNT-activated, less aggressive",
                "treatment": "Atezolizumab + Bevacizumab, Lenvatinib"
            },
            "Immune-active": {
                "markers": {"CD274": "high", "IFNG": "high"},
                "description": "High immune infiltration, responds to immunotherapy",
                "treatment": "Pembrolizumab, Nivolumab"
            }
        }
    },
    "gastric": {
        "name": "Gastric Cancer",
        "subtypes": {
            "EBV-positive": {
                "markers": {"PIK3CA": "mutated", "CD274": "high"},
                "description": "Epstein-Barr virus associated, high PD-L1",
                "treatment": "Immunotherapy + chemotherapy"
            },
            "MSI-high": {
                "markers": {"MLH1": "low"},
                "description": "Microsatellite unstable, good immunotherapy response",
                "treatment": "Pembrolizumab"
            },
            "HER2-positive": {
                "markers": {"ERBB2": "amplified"},
                "description": "HER2 amplified, ~15-20% of cases",
                "treatment": "Trastuzumab + chemotherapy"
            },
            "Diffuse": {
                "markers": {"CDH1": "mutated", "RHOA": "variable"},
                "description": "Loss of E-cadherin, poor prognosis",
                "treatment": "FLOT chemotherapy"
            }
        }
    }
}

# Add more biomarkers for new cancer types
BIOMARKERS.update({
    "ALK": {"role": "Oncogene (fusion)", "drugs": ["Alectinib", "Crizotinib", "Lorlatinib"]},
    "ROS1": {"role": "Oncogene (fusion)", "drugs": ["Crizotinib", "Entrectinib"]},
    "RET": {"role": "Oncogene", "drugs": ["Selpercatinib", "Pralsetinib"]},
    "MET": {"role": "Oncogene", "drugs": ["Capmatinib", "Tepotinib"]},
    "NTRK1": {"role": "Oncogene (fusion)", "drugs": ["Larotrectinib", "Entrectinib"]},
    "CD274": {"role": "PD-L1", "drugs": ["Pembrolizumab", "Nivolumab", "Atezolizumab"]},
    "IDH1": {"role": "Metabolic enzyme", "drugs": ["Ivosidenib", "Vorasidenib"]},
    "IDH2": {"role": "Metabolic enzyme", "drugs": ["Enasidenib"]},
    "FGFR2": {"role": "Oncogene", "drugs": ["Pemigatinib", "Erdafitinib"]},
    "FGFR3": {"role": "Oncogene", "drugs": ["Erdafitinib"]},
    "AR": {"role": "Androgen receptor", "drugs": ["Enzalutamide", "Abiraterone", "Darolutamide"]},
    "NRAS": {"role": "Oncogene", "drugs": []},
    "GNAQ": {"role": "Oncogene (uveal)", "drugs": []},
    "GNA11": {"role": "Oncogene (uveal)", "drugs": []},
    "BAP1": {"role": "Tumor suppressor", "drugs": []},
    "ARID1A": {"role": "Tumor suppressor", "drugs": []},
    "MLH1": {"role": "DNA mismatch repair", "drugs": ["Pembrolizumab"]},
    "MSH2": {"role": "DNA mismatch repair", "drugs": ["Pembrolizumab"]},
    "SMAD4": {"role": "Tumor suppressor", "drugs": []},
    "CTNNB1": {"role": "WNT pathway", "drugs": []},
    "APC": {"role": "Tumor suppressor", "drugs": []},
    "RB1": {"role": "Tumor suppressor", "drugs": []},
    "CDH1": {"role": "E-cadherin", "drugs": []},
    "STK11": {"role": "Tumor suppressor", "drugs": []},
    "TERT": {"role": "Telomerase", "drugs": []},
    "ATRX": {"role": "Chromatin remodeling", "drugs": []},
})

BIOMARKER_SET = set(BIOMARKERS.keys())

# ============================================================
# DRUG DATABASE - FDA-approved targeted therapies
# ============================================================
DRUG_DATABASE = {
    "ERBB2": {"drugs": ["Trastuzumab", "Pertuzumab", "T-DM1"], "indication": "HER2+ cancers", "fda_approved": True, "evidence": "1A"},
    "EGFR": {"drugs": ["Osimertinib", "Erlotinib", "Gefitinib"], "indication": "EGFR-mutant NSCLC", "fda_approved": True, "evidence": "1A"},
    "BRAF": {"drugs": ["Dabrafenib+Trametinib", "Encorafenib+Binimetinib"], "indication": "BRAF V600 mutant", "fda_approved": True, "evidence": "1A"},
    "ALK": {"drugs": ["Alectinib", "Lorlatinib", "Brigatinib"], "indication": "ALK+ NSCLC", "fda_approved": True, "evidence": "1A"},
    "BRCA1": {"drugs": ["Olaparib", "Rucaparib", "Niraparib"], "indication": "BRCA-mutant cancers", "fda_approved": True, "evidence": "1A"},
    "BRCA2": {"drugs": ["Olaparib", "Rucaparib", "Niraparib"], "indication": "BRCA-mutant cancers", "fda_approved": True, "evidence": "1A"},
    "PIK3CA": {"drugs": ["Alpelisib"], "indication": "PIK3CA-mutant HR+ breast", "fda_approved": True, "evidence": "1A"},
    "KRAS": {"drugs": ["Sotorasib", "Adagrasib"], "indication": "KRAS G12C", "fda_approved": True, "evidence": "1A"},
    "NTRK1": {"drugs": ["Larotrectinib", "Entrectinib"], "indication": "NTRK fusion+", "fda_approved": True, "evidence": "1A"},
    "RET": {"drugs": ["Selpercatinib", "Pralsetinib"], "indication": "RET fusion+", "fda_approved": True, "evidence": "1A"},
    "MET": {"drugs": ["Capmatinib", "Tepotinib"], "indication": "MET exon 14 skip", "fda_approved": True, "evidence": "1A"},
    "ROS1": {"drugs": ["Crizotinib", "Entrectinib"], "indication": "ROS1+ NSCLC", "fda_approved": True, "evidence": "1A"},
    "ESR1": {"drugs": ["Tamoxifen", "Fulvestrant", "Elacestrant"], "indication": "ER+ breast", "fda_approved": True, "evidence": "1A"},
    "AR": {"drugs": ["Enzalutamide", "Abiraterone", "Darolutamide"], "indication": "AR+ prostate", "fda_approved": True, "evidence": "1A"},
    "CDK4": {"drugs": ["Palbociclib", "Ribociclib", "Abemaciclib"], "indication": "HR+ breast", "fda_approved": True, "evidence": "1A"},
    "CDK6": {"drugs": ["Palbociclib", "Ribociclib", "Abemaciclib"], "indication": "HR+ breast", "fda_approved": True, "evidence": "1A"},
    "PD-L1": {"drugs": ["Pembrolizumab", "Nivolumab", "Atezolizumab"], "indication": "PD-L1+ tumors", "fda_approved": True, "evidence": "1A"},
    "TP53": {"drugs": ["Clinical trials (APR-246)"], "indication": "TP53-mutant", "fda_approved": False, "evidence": "3"},
    "AKT1": {"drugs": ["Capivasertib"], "indication": "AKT1-mutant", "fda_approved": True, "evidence": "1A"},
    "FGFR2": {"drugs": ["Pemigatinib", "Futibatinib"], "indication": "FGFR2 fusion", "fda_approved": True, "evidence": "1A"},
    "FGFR3": {"drugs": ["Erdafitinib"], "indication": "FGFR3-mutant bladder", "fda_approved": True, "evidence": "1A"},
}

# Prognostic gene signatures
PROGNOSTIC_SIGNATURES = {
    "proliferation": {"genes": ["MKI67", "PCNA", "TOP2A", "MCM2", "CCNB1", "AURKA"], "high_risk": "high", "weight": 2.0},
    "immune": {"genes": ["CD8A", "CD8B", "GZMA", "GZMB", "PRF1", "IFNG"], "high_risk": "low", "weight": 1.5},
    "stemness": {"genes": ["SOX2", "NANOG", "ALDH1A1", "CD44", "PROM1"], "high_risk": "high", "weight": 1.8},
    "invasion": {"genes": ["MMP2", "MMP9", "TWIST1", "SNAI1", "VIM"], "high_risk": "high", "weight": 1.5},
}

def calculate_survival_score(layer_results: Dict) -> Dict:
    """Calculate prognostic survival score"""
    if 'expression' not in layer_results:
        return {"risk_score": 50, "risk_group": "Unknown", "five_year_survival": "N/A", "risk_factors": [], "protective_factors": []}
    
    expr_data = layer_results['expression']
    expr_genes = {}
    for g in expr_data.get('top_variable', []) + expr_data.get('biomarkers_found', []):
        expr_genes[g['gene']] = float(g.get('mean', 0))
    
    risk_score = 50.0
    risk_factors = []
    protective_factors = []
    
    for sig_name, sig_data in PROGNOSTIC_SIGNATURES.items():
        sig_genes = [g for g in sig_data['genes'] if g in expr_genes]
        if len(sig_genes) >= 2:
            avg_expr = sum(expr_genes[g] for g in sig_genes) / len(sig_genes)
            if sig_data['high_risk'] == 'high' and avg_expr > 5:
                risk_score += 8 * sig_data['weight']
                risk_factors.append(f"High {sig_name}")
            elif sig_data['high_risk'] == 'low' and avg_expr < 3:
                risk_score += 8 * sig_data['weight']
                risk_factors.append(f"Low {sig_name}")
            elif sig_data['high_risk'] == 'high' and avg_expr < 3:
                risk_score -= 5
                protective_factors.append(f"Low {sig_name}")
            elif sig_data['high_risk'] == 'low' and avg_expr > 5:
                risk_score -= 5
                protective_factors.append(f"High {sig_name}")
    
    # Check mutations
    if 'mutation' in layer_results:
        mut_genes = [g['gene'] for g in layer_results['mutation'].get('frequently_mutated', [])]
        if 'TP53' in mut_genes:
            risk_score += 12
            risk_factors.append("TP53 mutation")
        if 'BRCA1' in mut_genes or 'BRCA2' in mut_genes:
            protective_factors.append("BRCA (PARP eligible)")
    
    risk_score = int(max(10, min(95, risk_score)))
    
    if risk_score < 35:
        risk_group, survival = "Low", "85-95%"
    elif risk_score < 55:
        risk_group, survival = "Intermediate-Low", "70-85%"
    elif risk_score < 70:
        risk_group, survival = "Intermediate-High", "50-70%"
    else:
        risk_group, survival = "High", "30-50%"
    
    return {
        "risk_score": risk_score,
        "risk_group": risk_group,
        "five_year_survival": survival,
        "risk_factors": risk_factors[:4],
        "protective_factors": protective_factors[:3]
    }

def get_drug_recommendations(layer_results: Dict) -> List[Dict]:
    """Get actionable drug recommendations"""
    recommendations = []
    seen_genes = set()
    
    # Check expression
    if 'expression' in layer_results:
        for g in layer_results['expression'].get('biomarkers_found', []):
            gene = g['gene']
            if gene in DRUG_DATABASE and gene not in seen_genes and float(g.get('mean', 0)) > 5:
                seen_genes.add(gene)
                info = DRUG_DATABASE[gene]
                recommendations.append({
                    "gene": gene, "alteration": "High expression",
                    "drugs": info['drugs'], "indication": info['indication'],
                    "fda_approved": info['fda_approved'], "evidence": info['evidence']
                })
    
    # Check mutations
    if 'mutation' in layer_results:
        for g in layer_results['mutation'].get('frequently_mutated', []):
            gene = g['gene']
            if gene in DRUG_DATABASE and gene not in seen_genes:
                seen_genes.add(gene)
                info = DRUG_DATABASE[gene]
                recommendations.append({
                    "gene": gene, "alteration": f"Mutated ({g.get('percent', 'N/A')}%)",
                    "drugs": info['drugs'], "indication": info['indication'],
                    "fda_approved": info['fda_approved'], "evidence": info['evidence']
                })
    
    # Check CNV
    if 'cnv' in layer_results:
        for g in layer_results['cnv'].get('amplified', []):
            gene = g['gene']
            if gene in DRUG_DATABASE and gene not in seen_genes:
                seen_genes.add(gene)
                info = DRUG_DATABASE[gene]
                recommendations.append({
                    "gene": gene, "alteration": "Amplified",
                    "drugs": info['drugs'], "indication": info['indication'],
                    "fda_approved": info['fda_approved'], "evidence": info['evidence']
                })
    
    return sorted(recommendations, key=lambda x: (not x['fda_approved'], x['evidence']))[:8]



# Cell-type marker signatures for deconvolution (based on literature)
CELL_TYPE_SIGNATURES = {
    "Tumor_Epithelial": ["EPCAM", "KRT8", "KRT18", "KRT19", "MUC1", "CDH1", "CLDN4", "CLDN7"],
    "CD8_T_Cells": ["CD8A", "CD8B", "GZMA", "GZMB", "PRF1", "IFNG", "CXCR3", "CCL5"],
    "CD4_T_Cells": ["CD4", "IL7R", "CCR7", "LEF1", "TCF7", "SELL", "CD40LG"],
    "Tregs": ["FOXP3", "IL2RA", "CTLA4", "IKZF2", "CCR8", "TNFRSF18"],
    "B_Cells": ["CD19", "CD79A", "CD79B", "MS4A1", "PAX5", "BANK1", "BLK"],
    "NK_Cells": ["NCAM1", "NKG7", "KLRD1", "KLRF1", "GNLY", "FCGR3A", "NCR1"],
    "Macrophages": ["CD68", "CD163", "CSF1R", "MARCO", "MSR1", "MRC1", "CD14"],
    "Dendritic_Cells": ["ITGAX", "CD1C", "CLEC9A", "FLT3", "BATF3", "IRF8"],
    "Fibroblasts": ["FAP", "PDGFRA", "PDGFRB", "COL1A1", "COL1A2", "ACTA2", "THY1"],
    "Endothelial": ["PECAM1", "VWF", "CDH5", "ENG", "KDR", "FLT1", "MCAM"],
}

def deconvolve_cell_types(df: pd.DataFrame) -> Dict:
    """Estimate cell-type proportions from bulk expression using signature scoring"""
    gene_index = set(df.index.str.upper())
    
    # Calculate signature scores for each cell type
    cell_scores = {}
    for cell_type, markers in CELL_TYPE_SIGNATURES.items():
        present_markers = [m for m in markers if m in gene_index]
        if len(present_markers) >= 2:
            marker_expr = []
            for m in present_markers:
                if m in df.index:
                    marker_expr.append(float(df.loc[m].mean()))
                elif m.upper() in df.index:
                    marker_expr.append(float(df.loc[m.upper()].mean()))
            if marker_expr:
                cell_scores[cell_type] = float(np.mean(marker_expr))
            else:
                cell_scores[cell_type] = 0.0
        else:
            cell_scores[cell_type] = 0.0
    
    # Normalize to proportions
    total = float(sum(max(s, 0.01) for s in cell_scores.values()))
    if total > 0:
        cell_fractions = {k: float(round(max(float(v), 0.01) / total * 100, 1)) for k, v in cell_scores.items()}
    else:
        cell_fractions = {k: 10.0 for k in cell_scores.keys()}
    
    # Calculate immunotherapy-relevant metrics
    immune_infiltration = float(cell_fractions.get("CD8_T_Cells", 0) + cell_fractions.get("NK_Cells", 0))
    immunosuppressive = float(cell_fractions.get("Tregs", 0) + cell_fractions.get("Macrophages", 0) * 0.3)
    
    # Generate insights
    insights = []
    if cell_fractions.get("CD8_T_Cells", 0) > 15:
        insights.append({"type": "positive", "text": "High CD8+ T cell infiltration suggests potential immunotherapy responsiveness"})
    if cell_fractions.get("Tregs", 0) > 10:
        insights.append({"type": "warning", "text": "Elevated Tregs may indicate immunosuppressive microenvironment"})
    if cell_fractions.get("Fibroblasts", 0) > 20:
        insights.append({"type": "warning", "text": "High fibroblast content suggests stromal-rich tumor, possible therapy resistance"})
    if immune_infiltration > 25:
        insights.append({"type": "positive", "text": "Strong immune infiltration - consider checkpoint inhibitor therapy"})
    
    itx_score = int(min(100, max(0, immune_infiltration * 2 - immunosuppressive + 30)))
    
    return {
        "cell_fractions": cell_fractions,
        "immune_infiltration": float(round(immune_infiltration, 1)),
        "immunosuppressive_score": float(round(immunosuppressive, 1)),
        "immunotherapy_score": itx_score,
        "insights": insights,
        "markers_detected": {ct: len([m for m in markers if m in gene_index]) for ct, markers in CELL_TYPE_SIGNATURES.items()}
    }



def detect_layer_type(filename: str) -> str:
    f = filename.lower()
    if any(x in f for x in ['rnaseq', 'rna', 'expression', 'rsem', 'rpkm', 'fpkm', 'tpm']):
        return 'expression'
    if any(x in f for x in ['mutation', 'mutsig', 'maf', 'snv']) or f.endswith('.vcf') or f.endswith('.cbt'):
        return 'mutation'
    if any(x in f for x in ['methyl', 'meth450', 'meth27']):
        return 'methylation'
    if any(x in f for x in ['cnv', 'scnv', 'gistic', 'copy']):
        return 'cnv'
    if any(x in f for x in ['rppa', 'protein']):
        return 'protein'
    return 'expression'


def parse_file(contents: bytes, filename: str) -> pd.DataFrame:
    """Parse file - process ALL data (requires adequate server memory)"""
    if filename.endswith('.gz'):
        contents = gzip.decompress(contents)
        filename = filename[:-3]
    
    text = contents.decode('utf-8') if isinstance(contents, bytes) else contents
    sep = '\t' if '\t' in text[:2000] else ','
    
    # Read full file
    df = pd.read_csv(io.StringIO(text), sep=sep, index_col=0, low_memory=False)
    df.columns = df.columns.astype(str).str.strip()
    df.index = df.index.astype(str).str.strip().str.split('|').str[0]
    
    # Convert to numeric (float32 to save memory)
    df = df.apply(pd.to_numeric, errors='coerce').astype('float32')
    
    return df


def analyze_expression_fast(df: pd.DataFrame) -> Dict:
    """FAST expression analysis"""
    means = df.mean(axis=1)
    variances = df.var(axis=1)
    
    results_df = pd.DataFrame({
        'gene': df.index,
        'mean': means.round(3),
        'variance': variances.round(3),
    })
    
    results_df['is_biomarker'] = results_df['gene'].isin(BIOMARKER_SET)
    results_df = results_df.dropna().sort_values('variance', ascending=False)
    
    return {
        "type": "expression",
        "total_genes": len(results_df),
        "top_variable": results_df.head(50).to_dict('records'),
        "biomarkers_found": results_df[results_df['is_biomarker']].to_dict('records')
    }


def analyze_mutations_fast(df: pd.DataFrame) -> Dict:
    """FAST mutation analysis"""
    mut_counts = (df != 0).sum(axis=1)
    total_samples = df.notna().sum(axis=1)
    frequencies = (mut_counts / total_samples).fillna(0)
    
    results_df = pd.DataFrame({
        'gene': df.index,
        'mutation_count': mut_counts.astype(int),
        'total_samples': total_samples.astype(int),
        'frequency': frequencies.round(4),
        'percent': (frequencies * 100).round(1)
    })
    
    results_df['is_biomarker'] = results_df['gene'].isin(BIOMARKER_SET)
    results_df = results_df.sort_values('frequency', ascending=False)
    
    return {
        "type": "mutation",
        "total_genes": len(results_df),
        "top_mutated": results_df.head(50).to_dict('records'),
        "frequently_mutated": results_df[results_df['frequency'] > 0.02].head(30).to_dict('records')
    }


def analyze_methylation_fast(df: pd.DataFrame) -> Dict:
    """FAST methylation analysis"""
    means = df.mean(axis=1)
    
    results_df = pd.DataFrame({
        'gene': df.index,
        'mean_beta': means.round(4),
    })
    
    results_df['status'] = 'intermediate'
    results_df.loc[results_df['mean_beta'] > 0.7, 'status'] = 'hypermethylated'
    results_df.loc[results_df['mean_beta'] < 0.3, 'status'] = 'hypomethylated'
    results_df['is_biomarker'] = results_df['gene'].isin(BIOMARKER_SET)
    
    return {
        "type": "methylation",
        "total_genes": len(results_df),
        "hypermethylated": results_df[results_df['status'] == 'hypermethylated'].head(30).to_dict('records'),
        "hypomethylated": results_df[results_df['status'] == 'hypomethylated'].head(30).to_dict('records'),
        "biomarkers_found": results_df[results_df['is_biomarker']].to_dict('records')
    }


def analyze_cnv_fast(df: pd.DataFrame) -> Dict:
    """FAST CNV analysis"""
    means = df.mean(axis=1)
    
    results_df = pd.DataFrame({
        'gene': df.index,
        'mean_log2': means.round(4),
    })
    
    results_df['status'] = 'neutral'
    results_df.loc[results_df['mean_log2'] > 0.3, 'status'] = 'amplified'
    results_df.loc[results_df['mean_log2'] < -0.3, 'status'] = 'deleted'
    results_df['is_biomarker'] = results_df['gene'].isin(BIOMARKER_SET)
    results_df = results_df.sort_values('mean_log2', ascending=False)
    
    return {
        "type": "cnv",
        "total_genes": len(results_df),
        "amplified": results_df[results_df['status'] == 'amplified'].head(30).to_dict('records'),
        "deleted": results_df[results_df['status'] == 'deleted'].head(30).to_dict('records'),
        "biomarkers_found": results_df[results_df['is_biomarker']].to_dict('records')
    }


def integrate_multi_omics(layer_results: Dict) -> List[Dict]:
    """Integrate findings across layers"""
    gene_evidence = {}
    
    if 'expression' in layer_results:
        for g in layer_results['expression'].get('top_variable', [])[:100]:
            gene = g['gene']
            if gene not in gene_evidence:
                gene_evidence[gene] = {'layers': [], 'findings': [], 'score': 0}
            gene_evidence[gene]['layers'].append('expression')
            gene_evidence[gene]['findings'].append(f"High variance")
            gene_evidence[gene]['score'] += 1
    
    if 'mutation' in layer_results:
        for g in layer_results['mutation'].get('frequently_mutated', []):
            gene = g['gene']
            if gene not in gene_evidence:
                gene_evidence[gene] = {'layers': [], 'findings': [], 'score': 0}
            gene_evidence[gene]['layers'].append('mutation')
            gene_evidence[gene]['findings'].append(f"Mutated {g['percent']}%")
            gene_evidence[gene]['score'] += 2
    
    if 'methylation' in layer_results:
        for g in layer_results['methylation'].get('hypermethylated', []) + layer_results['methylation'].get('hypomethylated', []):
            gene = g['gene']
            if gene not in gene_evidence:
                gene_evidence[gene] = {'layers': [], 'findings': [], 'score': 0}
            gene_evidence[gene]['layers'].append('methylation')
            gene_evidence[gene]['findings'].append(g['status'])
            gene_evidence[gene]['score'] += 1
    
    if 'cnv' in layer_results:
        for g in layer_results['cnv'].get('amplified', []) + layer_results['cnv'].get('deleted', []):
            gene = g['gene']
            if gene not in gene_evidence:
                gene_evidence[gene] = {'layers': [], 'findings': [], 'score': 0}
            gene_evidence[gene]['layers'].append('cnv')
            gene_evidence[gene]['findings'].append(g['status'])
            gene_evidence[gene]['score'] += 1
    
    integrated = []
    for gene, evidence in gene_evidence.items():
        if len(evidence['layers']) >= 2 or gene in BIOMARKER_SET:
            integrated.append({
                'gene': gene,
                'layers': list(set(evidence['layers'])),
                'findings': evidence['findings'],
                'evidence_score': evidence['score'] + (2 if gene in BIOMARKER_SET else 0),
                'is_biomarker': gene in BIOMARKER_SET,
                'role': BIOMARKERS.get(gene, {}).get('role', ''),
                'drugs': BIOMARKERS.get(gene, {}).get('drugs', []),
                'actionable': len(BIOMARKERS.get(gene, {}).get('drugs', [])) > 0
            })
    
    return sorted(integrated, key=lambda x: -x['evidence_score'])[:20]


def pathway_enrichment(layer_results: Dict) -> List[Dict]:
    """Find enriched pathways"""
    altered_genes = set()
    
    if 'expression' in layer_results:
        altered_genes.update([g['gene'] for g in layer_results['expression'].get('top_variable', [])[:50]])
    if 'mutation' in layer_results:
        altered_genes.update([g['gene'] for g in layer_results['mutation'].get('frequently_mutated', [])])
    if 'cnv' in layer_results:
        altered_genes.update([g['gene'] for g in layer_results['cnv'].get('amplified', [])])
        altered_genes.update([g['gene'] for g in layer_results['cnv'].get('deleted', [])])
    
    enriched = []
    for name, info in PATHWAYS.items():
        genes = set(info['genes'])
        overlap = altered_genes & genes
        if overlap:
            enriched.append({
                'pathway': name,
                'genes_affected': len(overlap),
                'genes_total': len(genes),
                'overlap_genes': list(overlap),
                'score': round(len(overlap) / len(genes), 3),
                'drugs': info.get('drugs', []),
                'status': 'ACTIVATED' if len(overlap) / len(genes) > 0.3 else 'ALTERED'
            })
    
    return sorted(enriched, key=lambda x: -x['score'])


def predict_subtype(layer_results: Dict, cancer_type: str = 'breast') -> Dict:
    """Predict cancer subtype based on cancer type"""
    
    # Get expression and mutation data
    expr_genes = {}
    mut_genes = set()
    
    if 'expression' in layer_results:
        for g in layer_results['expression'].get('biomarkers_found', []):
            expr_genes[g['gene']] = g['mean']
        for g in layer_results['expression'].get('top_variable', [])[:100]:
            if g['gene'] not in expr_genes:
                expr_genes[g['gene']] = g['mean']
    
    if 'mutation' in layer_results:
        for g in layer_results['mutation'].get('frequently_mutated', []):
            if g['frequency'] > 0.05:
                mut_genes.add(g['gene'])
        for g in layer_results['mutation'].get('top_mutated', [])[:50]:
            mut_genes.add(g['gene'])
    
    # Get cancer-specific subtypes
    cancer_info = CANCER_SUBTYPES.get(cancer_type, CANCER_SUBTYPES['breast'])
    subtypes = cancer_info['subtypes']
    
    best_match = "Unknown"
    best_score = 0
    best_description = ""
    best_treatment = ""
    evidence = []
    all_scores = {}
    
    for subtype_name, info in subtypes.items():
        score = 0
        subtype_evidence = []
        
        for marker, expected in info['markers'].items():
            # Check expression
            if marker in expr_genes:
                val = expr_genes[marker]
                if expected == "high" and val > 5:
                    score += 2
                    subtype_evidence.append(f"{marker}: high ✓")
                elif expected == "low" and val <= 5:
                    score += 2
                    subtype_evidence.append(f"{marker}: low ✓")
                elif expected == "variable":
                    score += 1
                    subtype_evidence.append(f"{marker}: detected")
            
            # Check mutations
            if expected in ["mutated", "rearranged"] and marker in mut_genes:
                score += 3
                subtype_evidence.append(f"{marker}: mutated ✓")
            elif expected == "normal" and marker not in mut_genes:
                score += 1
            
            # Check if marker is deleted/amplified
            if 'cnv' in layer_results:
                for g in layer_results['cnv'].get('amplified', []):
                    if g['gene'] == marker and expected in ["high", "amplified"]:
                        score += 2
                        subtype_evidence.append(f"{marker}: amplified ✓")
                for g in layer_results['cnv'].get('deleted', []):
                    if g['gene'] == marker and expected in ["low", "deleted"]:
                        score += 2
                        subtype_evidence.append(f"{marker}: deleted ✓")
        
        all_scores[subtype_name] = score
        
        if score > best_score:
            best_score = score
            best_match = subtype_name
            best_description = info.get('description', '')
            best_treatment = info.get('treatment', '')
            evidence = subtype_evidence
    
    # Calculate confidence
    total_markers = len(subtypes.get(best_match, {}).get('markers', {}))
    confidence = min(int((best_score / max(total_markers * 2, 1)) * 100), 95) if best_score > 0 else 30
    
    return {
        'predicted': best_match,
        'confidence': max(confidence, 40),
        'evidence': evidence[:6],
        'description': best_description,
        'treatment': best_treatment,
        'prognosis': f"{best_match} - {best_description}",
        'cancer_type': cancer_info['name'],
        'all_subtypes': {k: {'score': v, 'info': subtypes[k]} for k, v in all_scores.items()}
    }


# API ENDPOINTS

@app.get("/api")
def api_root():
    return {"api": "SynOmix AI", "version": "7.0.0"}


@app.post("/api/experiment/create")
async def create_experiment(name: str = Form("My Experiment"), cancer_type: str = Form("breast")):
    exp_id = f"exp_{len(experiments)+1}_{datetime.now().strftime('%H%M%S')}"
    experiments[exp_id] = {"id": exp_id, "name": name, "cancer_type": cancer_type, "layers": {}, "layer_info": {}}
    return {"success": True, "experiment_id": exp_id}


@app.post("/api/experiment/{exp_id}/upload")
async def upload_layer(exp_id: str, file: UploadFile = File(...), layer_type: str = Form(None)):
    if exp_id not in experiments:
        raise HTTPException(404, "Experiment not found")
    
    contents = await file.read()
    detected_type = layer_type or detect_layer_type(file.filename)
    df = parse_file(contents, file.filename)
    
    experiments[exp_id]["layers"][detected_type] = df
    experiments[exp_id]["layer_info"][detected_type] = {"filename": file.filename, "genes": df.shape[0], "samples": df.shape[1]}
    
    return {"success": True, "layer_type": detected_type, "filename": file.filename, "genes": df.shape[0], "samples": df.shape[1], "total_layers": len(experiments[exp_id]["layers"])}


@app.post("/api/experiment/{exp_id}/analyze")
async def analyze_experiment(exp_id: str):
    if exp_id not in experiments:
        raise HTTPException(404, "Experiment not found")
    
    exp = experiments[exp_id]
    layers = exp["layers"]
    
    if not layers:
        raise HTTPException(400, "No layers")
    
    start = datetime.now()
    layer_results = {}
    
    for layer_type, df in layers.items():
        if layer_type == 'expression':
            layer_results['expression'] = analyze_expression_fast(df)
            # Run cell-type deconvolution on expression data
            layer_results['deconvolution'] = deconvolve_cell_types(df)
        elif layer_type == 'mutation':
            layer_results['mutation'] = analyze_mutations_fast(df)
        elif layer_type == 'methylation':
            layer_results['methylation'] = analyze_methylation_fast(df)
        elif layer_type == 'cnv':
            layer_results['cnv'] = analyze_cnv_fast(df)
        elif layer_type == 'protein':
            layer_results['protein'] = analyze_expression_fast(df)
    
    integrated = integrate_multi_omics(layer_results)
    pathways = pathway_enrichment(layer_results)
    subtype = predict_subtype(layer_results, exp.get('cancer_type', 'breast'))
    
    return {
        "success": True,
        "experiment_id": exp_id,
        "experiment_name": exp["name"],
        "processing_time": round((datetime.now() - start).total_seconds(), 2),
        "layers_analyzed": list(layer_results.keys()),
        "summary": {
            "total_layers": len(layers),
            "multi_omics_hits": len(integrated),
            "actionable_targets": len([i for i in integrated if i.get('actionable')]),
            "pathways_enriched": len(pathways),
            "predicted_subtype": subtype["predicted"],
            "immune_score": layer_results.get("deconvolution", {}).get("immunotherapy_score", 0),
            "confidence": subtype["confidence"]
        },
        "layer_results": layer_results,
        "integrated": integrated,
        "pathways": pathways,
        "subtype": subtype,
        "survival": calculate_survival_score(layer_results),
        "drug_recommendations": get_drug_recommendations(layer_results)
    }


@app.get("/api/experiments")
def list_experiments():
    return {"experiments": list(experiments.keys())}


# Serve frontend
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    index_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse("<h1>SynOmix AI</h1><p>API running</p>")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))

# Claude AI Chat Endpoint
import anthropic
from pydantic import BaseModel
from dotenv import load_dotenv


# Claude AI Chat Endpoint
import anthropic
from pydantic import BaseModel

class ChatRequest(BaseModel):
    query: str
    results: dict = {}


from fastapi.responses import StreamingResponse

@app.post("/api/chat")
async def chat_with_claude(request: ChatRequest):
    async def generate():
        try:
            api_key = None
            with open("/var/www/synomix/.env") as f:
                for line in f:
                    if line.startswith("ANTHROPIC_API_KEY="):
                        api_key = line.strip().split("=", 1)[1]
                        break
            
            if not api_key:
                yield "data: AI service not configured.\n\n"
                return
            
            client = anthropic.Anthropic(api_key=api_key)
            
            context = f"""You are an AI assistant for SynOmix, a multi-omics biomarker discovery platform.

The user has run an analysis with these results:
- Subtype: {request.results.get('subtype', {}).get('predicted', 'Unknown')}
- Confidence: {request.results.get('subtype', {}).get('confidence', 0)}%
- Top findings: {[f.get('gene', '') for f in request.results.get('findings', [])[:5]]}
- Pathways affected: {[p.get('name', '') for p in request.results.get('pathways', [])[:5]]}

Answer questions about their cancer biomarker analysis. Be helpful, scientific, and concise.
Remind users this is for research purposes only, not clinical advice."""

            with client.messages.stream(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": f"{context}\n\nUser question: {request.query}"}]
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {text}\n\n"
            
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/event-stream")
