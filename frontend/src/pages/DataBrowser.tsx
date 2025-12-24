import { useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Download, Database, ExternalLink } from 'lucide-react';
import { searchGEO, searchCBioPortal, importGEO, importCBioPortal } from '../services/api';

const DataBrowser = () => {
  const [activeTab, setActiveTab] = useState<'geo' | 'cbioportal'>('geo');
  const [searchQuery, setSearchQuery] = useState('');
  const [organism, setOrganism] = useState('human');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    try {
      if (activeTab === 'geo') {
        const data = await searchGEO(searchQuery, organism);
        setResults(data);
      } else {
        const data = await searchCBioPortal(searchQuery);
        setResults(data);
      }
    } catch (error) {
      console.error('Search failed:', error);
      alert('Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async (id: string, experimentId: string) => {
    try {
      if (activeTab === 'geo') {
        await importGEO(id, experimentId);
      } else {
        await importCBioPortal(id, experimentId);
      }
      alert('Import successful!');
    } catch (error) {
      console.error('Import failed:', error);
      alert('Import failed');
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-6xl mx-auto"
      >
        <h1 className="text-4xl font-bold gradient-text mb-8 text-center">
          Data Browser
        </h1>

        <div className="glass-card p-8 mb-8">
          {/* Tabs */}
          <div className="flex gap-4 mb-6">
            <button
              onClick={() => setActiveTab('geo')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'geo'
                  ? 'bg-purple-600 shadow-lg shadow-purple-500/50'
                  : 'bg-white/5 hover:bg-white/10'
              }`}
            >
              <Database size={20} />
              GEO (Gene Expression Omnibus)
            </button>
            <button
              onClick={() => setActiveTab('cbioportal')}
              className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${
                activeTab === 'cbioportal'
                  ? 'bg-purple-600 shadow-lg shadow-purple-500/50'
                  : 'bg-white/5 hover:bg-white/10'
              }`}
            >
              <Database size={20} />
              cBioPortal
            </button>
          </div>

          {/* Search Bar */}
          <div className="flex gap-4 mb-6">
            <div className="flex-1">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder={
                  activeTab === 'geo'
                    ? 'Search GEO datasets (e.g., breast cancer)'
                    : 'Search cancer types (e.g., brca)'
                }
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              />
            </div>
            {activeTab === 'geo' && (
              <select
                value={organism}
                onChange={(e) => setOrganism(e.target.value)}
                className="px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
              >
                <option value="human">Human</option>
                <option value="mouse">Mouse</option>
                <option value="">All Organisms</option>
              </select>
            )}
            <button
              onClick={handleSearch}
              disabled={!searchQuery || loading}
              className="btn-primary px-8 disabled:opacity-50"
            >
              <Search size={20} />
            </button>
          </div>

          {/* Description */}
          <p className="text-gray-400 text-sm">
            {activeTab === 'geo' ? (
              <>
                Search and import datasets from NCBI's Gene Expression Omnibus.
                Find RNA-seq, microarray, and other genomics data.
              </>
            ) : (
              <>
                Browse cancer genomics studies from cBioPortal.
                Import mutation, CNA, and expression data from published studies.
              </>
            )}
          </p>
        </div>

        {/* Results */}
        {loading && (
          <div className="text-center py-12">
            <div className="inline-block animate-spin w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full" />
            <p className="mt-4 text-gray-400">Searching...</p>
          </div>
        )}

        {!loading && results.length > 0 && (
          <div className="space-y-4">
            {results.map((result, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="glass-card p-6"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <span className="px-3 py-1 bg-purple-600/30 rounded-full text-sm font-semibold">
                        {activeTab === 'geo' ? result.accession : result.studyId}
                      </span>
                      {result.organism && (
                        <span className="text-sm text-gray-400">{result.organism}</span>
                      )}
                      {result.samples_count && (
                        <span className="text-sm text-gray-400">
                          {result.samples_count} samples
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-bold mb-2">{result.title}</h3>
                    <p className="text-gray-400 mb-3">{result.summary || result.description}</p>
                    {result.pubmed_id && (
                      <a
                        href={`https://pubmed.ncbi.nlm.nih.gov/${result.pubmed_id}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-purple-400 hover:text-purple-300 inline-flex items-center gap-1 text-sm"
                      >
                        View Publication <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                  <button
                    onClick={() =>
                      handleImport(
                        activeTab === 'geo' ? result.accession : result.studyId,
                        'new-experiment'
                      )
                    }
                    className="btn-secondary flex items-center gap-2 ml-4"
                  >
                    <Download size={18} />
                    Import
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </motion.div>
    </div>
  );
};

export default DataBrowser;
