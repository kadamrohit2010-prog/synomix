import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { ArrowRight, Zap, Database, BarChart3, Brain, Share2, Download } from 'lucide-react';

const Landing = () => {
  return (
    <div className="container mx-auto px-4 py-12">
      {/* Animated Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="text-center mb-20"
      >
        <motion.div
          className="inline-block mb-6"
          animate={{
            scale: [1, 1.05, 1],
            rotate: [0, 2, -2, 0],
          }}
          transition={{
            duration: 3,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        >
          <h1 className="text-7xl md:text-9xl font-bold gradient-text mb-4">
            60 Seconds
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.8 }}
          className="text-2xl md:text-3xl text-gray-300 mb-8"
        >
          From Multi-Omics Data to Breakthrough Insights
        </motion.p>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5, duration: 0.8 }}
          className="text-lg text-gray-400 max-w-3xl mx-auto mb-12"
        >
          Integrate expression, mutations, methylation, CNV, proteomics, metabolomics, and single-cell data.
          Discover novel biomarkers, predict cancer subtypes, and generate publication-ready hypotheses in under a minute.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7, duration: 0.8 }}
          className="flex gap-4 justify-center"
        >
          <Link to="/upload" className="btn-primary inline-flex items-center gap-2">
            Start Analysis <ArrowRight size={20} />
          </Link>
          <Link to="/browse" className="btn-secondary inline-flex items-center gap-2">
            Browse Public Data <Database size={20} />
          </Link>
        </motion.div>
      </motion.div>

      {/* Feature Cards */}
      <div className="grid md:grid-cols-3 gap-6 mb-20">
        {[
          {
            icon: Zap,
            title: 'Lightning Fast',
            description: 'Complete multi-omics analysis in 60 seconds. Upload your data and get results instantly.',
          },
          {
            icon: Brain,
            title: 'AI-Powered',
            description: 'Real LLM integration for intelligent analysis, contextual insights, and interactive queries.',
          },
          {
            icon: Database,
            title: 'Rich Integrations',
            description: 'Import from GEO, cBioPortal. Support for metabolomics, single-cell RNA-seq, and more.',
          },
          {
            icon: BarChart3,
            title: 'Advanced Analytics',
            description: 'Survival analysis, batch processing, pathway enrichment, and subtype prediction.',
          },
          {
            icon: Share2,
            title: 'Collaborate',
            description: 'Share experiments with teams, create shareable links, and work together seamlessly.',
          },
          {
            icon: Download,
            title: 'Export Everything',
            description: 'Download PDF reports, export figures in multiple formats, and share your findings.',
          },
        ].map((feature, index) => {
          const Icon = feature.icon;
          return (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.9 + index * 0.1, duration: 0.6 }}
              className="glass-card-hover p-6"
            >
              <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-fuchsia-500 rounded-lg flex items-center justify-center mb-4">
                <Icon size={24} className="text-white" />
              </div>
              <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
              <p className="text-gray-400">{feature.description}</p>
            </motion.div>
          );
        })}
      </div>

      {/* Supported Data Types */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.5, duration: 0.8 }}
        className="glass-card p-8 text-center"
      >
        <h2 className="text-3xl font-bold gradient-text mb-6">Supported Data Types</h2>
        <div className="flex flex-wrap justify-center gap-4">
          {[
            'RNA-seq',
            'Mutations',
            'Methylation',
            'Copy Number',
            'Proteomics',
            'Metabolomics',
            'Single-Cell RNA-seq',
          ].map((type, index) => (
            <motion.span
              key={type}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 1.7 + index * 0.1, duration: 0.4 }}
              className="px-6 py-3 bg-gradient-to-r from-purple-600/20 to-fuchsia-600/20 border border-purple-500/30 rounded-full text-purple-300 font-semibold"
            >
              {type}
            </motion.span>
          ))}
        </div>
      </motion.div>

      {/* Cancer Types */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1.8, duration: 0.8 }}
        className="glass-card p-8 text-center mt-6"
      >
        <h2 className="text-3xl font-bold gradient-text mb-6">Multiple Cancer Types</h2>
        <p className="text-gray-400 mb-4">
          Optimized analysis pipelines for 10+ cancer types with cancer-specific biomarkers and subtype prediction
        </p>
        <div className="flex flex-wrap justify-center gap-3">
          {[
            'Breast',
            'Lung',
            'Colorectal',
            'Prostate',
            'Ovarian',
            'Melanoma',
            'Glioma',
            'Pancreatic',
            'Liver',
            'Gastric',
          ].map((cancer, index) => (
            <motion.span
              key={cancer}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 2.0 + index * 0.05, duration: 0.3 }}
              className="px-4 py-2 bg-white/5 rounded-lg text-gray-300"
            >
              {cancer}
            </motion.span>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default Landing;
