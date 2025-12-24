import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  BarChart3,
  FileText,
  Brain,
  Share2,
  Download,
  MessageSquare,
} from 'lucide-react';
import { getExperiment, shareExperiment, exportPDF } from '../services/api';
import type { Experiment, AnalysisResults } from '../types';
import VennDiagram from '../components/visualizations/VennDiagram';
import NetworkGraph from '../components/visualizations/NetworkGraph';
import GeneDetailModal from '../components/ui/GeneDetailModal';
import AIChat from '../components/ui/AIChat';

const Results = () => {
  const { experimentId, shareToken } = useParams();
  const [experiment, setExperiment] = useState<Experiment | null>(null);
  const [_results, _setResults] = useState<AnalysisResults | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'findings' | 'pathways' | 'hypotheses'>('overview');
  const [selectedGene, setSelectedGene] = useState<string | null>(null);
  const [showChat, setShowChat] = useState(false);
  const [_shareUrl, setShareUrl] = useState('');

  useEffect(() => {
    loadExperiment();
  }, [experimentId, shareToken]);

  const loadExperiment = async () => {
    try {
      const id = experimentId || shareToken;
      if (!id) return;

      const data = await getExperiment(id);
      setExperiment(data);
      // Assume results are embedded or fetched separately
      // setResults(data.results);
    } catch (error) {
      console.error('Failed to load experiment:', error);
    }
  };

  const handleShare = async () => {
    if (!experimentId) return;
    try {
      const result = await shareExperiment(experimentId);
      setShareUrl(result.share_url);
      navigator.clipboard.writeText(result.share_url);
      alert('Share link copied to clipboard!');
    } catch (error) {
      console.error('Failed to share:', error);
      alert('Failed to create share link');
    }
  };

  const handleExportPDF = async () => {
    if (!experimentId) return;
    try {
      const blob = await exportPDF(experimentId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `synomix-${experimentId}.pdf`;
      a.click();
    } catch (error) {
      console.error('Failed to export PDF:', error);
      alert('Failed to export PDF');
    }
  };

  // Mock data for demonstration
  const mockMetrics = {
    layers_count: 5,
    novel_genes_count: 23,
    known_alterations_count: 18,
    multi_omics_hits: 12,
    pathways_count: 8,
    hypotheses_count: 5,
  };

  const mockNovelFindings = [
    { gene: 'GENE1', confidence: 'HIGH', score: 0.95, evidence: ['expression', 'mutation'] },
    { gene: 'GENE2', confidence: 'HIGH', score: 0.88, evidence: ['methylation', 'cnv'] },
    { gene: 'GENE3', confidence: 'MEDIUM', score: 0.75, evidence: ['expression', 'protein'] },
  ];

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold gradient-text">{experiment?.name || 'Analysis Results'}</h1>
            <p className="text-gray-400 mt-1">{experiment?.cancer_type} • {new Date().toLocaleDateString()}</p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={() => setShowChat(!showChat)}
              className="btn-secondary flex items-center gap-2"
            >
              <MessageSquare size={20} />
              AI Chat
            </button>
            <button
              onClick={handleShare}
              className="btn-secondary flex items-center gap-2"
            >
              <Share2 size={20} />
              Share
            </button>
            <button
              onClick={handleExportPDF}
              className="btn-primary flex items-center gap-2"
            >
              <Download size={20} />
              Export PDF
            </button>
          </div>
        </div>

        {/* Metrics Dashboard */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-8">
          {[
            { label: 'Layers', value: mockMetrics.layers_count, icon: BarChart3, color: 'blue' },
            { label: 'Novel Genes', value: mockMetrics.novel_genes_count, icon: FileText, color: 'purple' },
            { label: 'Known Alterations', value: mockMetrics.known_alterations_count, icon: Brain, color: 'green' },
            { label: 'Multi-Omics Hits', value: mockMetrics.multi_omics_hits, icon: BarChart3, color: 'yellow' },
            { label: 'Pathways', value: mockMetrics.pathways_count, icon: FileText, color: 'pink' },
            { label: 'Hypotheses', value: mockMetrics.hypotheses_count, icon: Brain, color: 'cyan' },
          ].map((metric, index) => {
            const Icon = metric.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-6 text-center"
              >
                <Icon size={32} className={`mx-auto mb-2 text-${metric.color}-400`} />
                <p className="text-3xl font-bold mb-1">{metric.value}</p>
                <p className="text-sm text-gray-400">{metric.label}</p>
              </motion.div>
            );
          })}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6">
          {[
            { id: 'overview', label: 'Overview', icon: BarChart3 },
            { id: 'findings', label: 'Novel Findings', icon: FileText },
            { id: 'pathways', label: 'Pathways', icon: Brain },
            { id: 'hypotheses', label: 'Hypotheses', icon: Brain },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                  activeTab === tab.id
                    ? 'bg-purple-600 shadow-lg shadow-purple-500/50'
                    : 'bg-white/5 hover:bg-white/10'
                }`}
              >
                <Icon size={20} />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <div className="glass-card p-8">
              <h2 className="text-2xl font-bold mb-6">Multi-Omics Overview</h2>
              <VennDiagram />
            </div>

            <div className="glass-card p-8">
              <h2 className="text-2xl font-bold mb-6">Pathway Interaction Network</h2>
              <NetworkGraph />
            </div>
          </div>
        )}

        {activeTab === 'findings' && (
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold mb-6">Novel Gene Discoveries</h2>
            <div className="space-y-4">
              {mockNovelFindings.map((finding, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer transition-all"
                  onClick={() => setSelectedGene(finding.gene)}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="font-mono font-bold text-lg">{finding.gene}</div>
                      <span
                        className={`px-3 py-1 rounded-full text-sm font-semibold ${
                          finding.confidence === 'HIGH'
                            ? 'bg-green-600/30 text-green-300'
                            : 'bg-yellow-600/30 text-yellow-300'
                        }`}
                      >
                        {finding.confidence}
                      </span>
                    </div>
                    <div className="text-right">
                      <p className="text-2xl font-bold">{(finding.score * 100).toFixed(0)}%</p>
                      <p className="text-sm text-gray-400">Confidence</p>
                    </div>
                  </div>
                  <div className="mt-2 flex gap-2">
                    {finding.evidence.map((ev) => (
                      <span
                        key={ev}
                        className="px-2 py-1 bg-purple-600/20 rounded text-xs"
                      >
                        {ev}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'pathways' && (
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold mb-6">Pathway Enrichment</h2>
            <p className="text-gray-400">Pathway analysis visualization coming soon...</p>
          </div>
        )}

        {activeTab === 'hypotheses' && (
          <div className="glass-card p-8">
            <h2 className="text-2xl font-bold mb-6">Research Hypotheses</h2>
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <div key={i} className="p-4 bg-white/5 rounded-lg">
                  <h3 className="font-bold mb-2">Hypothesis {i}</h3>
                  <p className="text-gray-300">
                    Based on multi-omics evidence, this gene shows significant alterations
                    across multiple layers suggesting a novel biomarker for {experiment?.cancer_type}.
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Gene Detail Modal */}
        {selectedGene && (
          <GeneDetailModal
            gene={selectedGene}
            onClose={() => setSelectedGene(null)}
          />
        )}

        {/* AI Chat Sidebar */}
        {showChat && experimentId && (
          <AIChat
            experimentId={experimentId}
            onClose={() => setShowChat(false)}
          />
        )}
      </motion.div>
    </div>
  );
};

export default Results;
