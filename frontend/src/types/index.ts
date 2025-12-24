export interface Experiment {
  id: string;
  name: string;
  cancer_type: string;
  created_at: string;
  updated_at: string;
  user_id?: string;
  is_public: boolean;
  share_token?: string;
}

export interface Layer {
  type: 'expression' | 'mutation' | 'methylation' | 'cnv' | 'protein' | 'metabolomics' | 'single_cell';
  file_name: string;
  gene_count: number;
  sample_count: number;
  uploaded_at: string;
}

export interface AnalysisResults {
  experiment_id: string;
  metrics: {
    layers_count: number;
    novel_genes_count: number;
    known_alterations_count: number;
    multi_omics_hits: number;
    pathways_count: number;
    hypotheses_count: number;
  };
  novel_findings: NovelFinding[];
  known_genes: KnownGene[];
  pathways: Pathway[];
  subtype_prediction?: SubtypePrediction;
  hypotheses: string[];
  narrative: string;
}

export interface NovelFinding {
  gene: string;
  evidence: string[];
  confidence: 'HIGH' | 'MEDIUM' | 'LOW';
  score: number;
  details: {
    expression?: { mean: number; variance: number };
    mutation?: { frequency: number; samples: number };
    methylation?: { mean_beta: number; status: string };
    cnv?: { log2_ratio: number; status: string };
    protein?: { mean: number; variance: number };
  };
}

export interface KnownGene {
  gene: string;
  role: string;
  drugs: string[];
  actionable: boolean;
  evidence: string[];
}

export interface Pathway {
  name: string;
  genes: string[];
  altered_genes: string[];
  enrichment_score: number;
  drugs: string[];
  description?: string;
}

export interface SubtypePrediction {
  subtype: string;
  confidence: number;
  markers: string[];
  description: string;
  treatment: string;
}

export interface GEODataset {
  accession: string;
  title: string;
  summary: string;
  organism: string;
  samples_count: number;
  platform: string;
  pubmed_id?: string;
}

export interface CancerType {
  id: string;
  name: string;
  description: string;
  subtypes: string[];
}

export interface Team {
  id: string;
  name: string;
  description: string;
  members: TeamMember[];
  created_at: string;
}

export interface TeamMember {
  user_id: string;
  name: string;
  email: string;
  role: 'owner' | 'admin' | 'member';
  joined_at: string;
}

export interface UserSettings {
  theme: 'dark' | 'light';
  notifications: boolean;
  default_cancer_type?: string;
  api_keys: {
    openai?: string;
    anthropic?: string;
  };
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface SurvivalData {
  sample_id: string;
  time: number;
  event: boolean;
  group?: string;
}
