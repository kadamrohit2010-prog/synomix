import { motion } from 'framer-motion';
import { X, ExternalLink } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface GeneDetailModalProps {
  gene: string;
  onClose: () => void;
}

const GeneDetailModal = ({ gene, onClose }: GeneDetailModalProps) => {
  // Mock data
  const expressionData = [
    { sample: 'S1', value: 5.2 },
    { sample: 'S2', value: 8.1 },
    { sample: 'S3', value: 6.5 },
    { sample: 'S4', value: 9.3 },
    { sample: 'S5', value: 7.8 },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.9 }}
        className="glass-card p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
      >
        <div className="flex items-start justify-between mb-6">
          <div>
            <h2 className="text-3xl font-bold gradient-text">{gene}</h2>
            <p className="text-gray-400 mt-1">Gene Details & Multi-Omics Evidence</p>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <X size={24} />
          </button>
        </div>

        {/* Evidence Summary */}
        <div className="grid md:grid-cols-3 gap-4 mb-8">
          {[
            { layer: 'Expression', status: 'Upregulated', color: 'bg-blue-500' },
            { layer: 'Mutation', status: 'Detected', color: 'bg-red-500' },
            { layer: 'Methylation', status: 'Hypomethylated', color: 'bg-green-500' },
          ].map((evidence, index) => (
            <div key={index} className="p-4 bg-white/5 rounded-lg">
              <div className={`w-3 h-3 rounded-full ${evidence.color} mb-2`} />
              <p className="text-sm text-gray-400">{evidence.layer}</p>
              <p className="font-bold">{evidence.status}</p>
            </div>
          ))}
        </div>

        {/* Expression Chart */}
        <div className="mb-8">
          <h3 className="text-xl font-bold mb-4">Expression Levels Across Samples</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={expressionData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
              <XAxis dataKey="sample" stroke="#fff" />
              <YAxis stroke="#fff" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1f2937',
                  border: '1px solid #374151',
                  borderRadius: '8px',
                }}
              />
              <Bar dataKey="value" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Gene Information */}
        <div className="space-y-4">
          <div>
            <h3 className="text-xl font-bold mb-2">Gene Function</h3>
            <p className="text-gray-300">
              This gene encodes a tumor suppressor protein involved in cell cycle regulation,
              DNA repair, and apoptosis. Alterations in this gene are frequently observed in
              various cancers.
            </p>
          </div>

          <div>
            <h3 className="text-xl font-bold mb-2">Clinical Significance</h3>
            <p className="text-gray-300">
              Mutations and expression changes in this gene are associated with poor prognosis
              and may serve as a potential therapeutic target.
            </p>
          </div>

          <div>
            <h3 className="text-xl font-bold mb-2">External Resources</h3>
            <div className="flex flex-wrap gap-3">
              {[
                { name: 'NCBI Gene', url: `https://www.ncbi.nlm.nih.gov/gene?term=${gene}` },
                { name: 'COSMIC', url: `https://cancer.sanger.ac.uk/cosmic/search?q=${gene}` },
                { name: 'cBioPortal', url: `https://www.cbioportal.org/results?gene_list=${gene}` },
              ].map((resource) => (
                <a
                  key={resource.name}
                  href={resource.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-secondary text-sm py-2 px-4 flex items-center gap-2"
                >
                  {resource.name}
                  <ExternalLink size={14} />
                </a>
              ))}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default GeneDetailModal;
