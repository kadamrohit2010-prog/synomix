import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDropzone } from 'react-dropzone';
import { motion } from 'framer-motion';
import { Upload as UploadIcon, FileText, CheckCircle, Loader, X } from 'lucide-react';
import { createExperiment, uploadFile, analyzeExperiment } from '../services/api';
import ProgressStepper from '../components/ui/ProgressStepper';

const CANCER_TYPES = [
  { id: 'breast', name: 'Breast Cancer' },
  { id: 'lung', name: 'Lung Cancer' },
  { id: 'colorectal', name: 'Colorectal Cancer' },
  { id: 'prostate', name: 'Prostate Cancer' },
  { id: 'ovarian', name: 'Ovarian Cancer' },
  { id: 'melanoma', name: 'Melanoma' },
  { id: 'glioma', name: 'Glioma' },
  { id: 'pancreatic', name: 'Pancreatic Cancer' },
  { id: 'liver', name: 'Liver Cancer' },
  { id: 'gastric', name: 'Gastric Cancer' },
];

const LAYER_TYPES = [
  { id: 'expression', name: 'Expression (RNA-seq)', color: 'bg-blue-500' },
  { id: 'mutation', name: 'Mutations', color: 'bg-red-500' },
  { id: 'methylation', name: 'Methylation', color: 'bg-green-500' },
  { id: 'cnv', name: 'Copy Number Variation', color: 'bg-yellow-500' },
  { id: 'protein', name: 'Proteomics', color: 'bg-purple-500' },
  { id: 'metabolomics', name: 'Metabolomics', color: 'bg-pink-500' },
  { id: 'single_cell', name: 'Single-Cell RNA-seq', color: 'bg-cyan-500' },
];

interface UploadedFile {
  file: File;
  layerType?: string;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  geneCount?: number;
  sampleCount?: number;
  error?: string;
}

const Upload = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [experimentName, setExperimentName] = useState('');
  const [cancerType, setCancerType] = useState('');
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [experimentId, setExperimentId] = useState('');
  const [analyzing, setAnalyzing] = useState(false);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop: (acceptedFiles) => {
      const newFiles = acceptedFiles.map((file) => ({
        file,
        progress: 0,
        status: 'pending' as const,
      }));
      setFiles((prev) => [...prev, ...newFiles]);
    },
    accept: {
      'text/csv': ['.csv'],
      'text/tab-separated-values': ['.tsv', '.txt'],
      'application/gzip': ['.gz'],
    },
  });

  const handleCreateExperiment = async () => {
    if (!experimentName || !cancerType) return;

    try {
      const experiment = await createExperiment(experimentName, cancerType);
      setExperimentId(experiment.id);
      setStep(2);
    } catch (error) {
      console.error('Failed to create experiment:', error);
      alert('Failed to create experiment');
    }
  };

  const handleUploadFiles = async () => {
    if (files.length === 0) return;

    setStep(3);

    for (let i = 0; i < files.length; i++) {
      const fileData = files[i];
      if (fileData.status !== 'pending') continue;

      setFiles((prev) =>
        prev.map((f, idx) =>
          idx === i ? { ...f, status: 'uploading' } : f
        )
      );

      try {
        const result = await uploadFile(
          experimentId,
          fileData.file,
          fileData.layerType,
          (progress) => {
            setFiles((prev) =>
              prev.map((f, idx) =>
                idx === i ? { ...f, progress } : f
              )
            );
          }
        );

        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? {
                  ...f,
                  status: 'success',
                  layerType: result.layer_type,
                  geneCount: result.gene_count,
                  sampleCount: result.sample_count,
                }
              : f
          )
        );
      } catch (error) {
        setFiles((prev) =>
          prev.map((f, idx) =>
            idx === i
              ? { ...f, status: 'error', error: 'Upload failed' }
              : f
          )
        );
      }
    }

    setStep(4);
  };

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      await analyzeExperiment(experimentId);
      navigate(`/results/${experimentId}`);
    } catch (error) {
      console.error('Analysis failed:', error);
      alert('Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const updateLayerType = (index: number, layerType: string) => {
    setFiles((prev) =>
      prev.map((f, i) => (i === index ? { ...f, layerType } : f))
    );
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto"
      >
        <h1 className="text-4xl font-bold gradient-text mb-8 text-center">
          Create New Analysis
        </h1>

        <ProgressStepper
          steps={[
            { label: 'Experiment Details', completed: step > 1 },
            { label: 'Upload Data', completed: step > 2 },
            { label: 'Processing', completed: step > 3 },
            { label: 'Analyze', completed: false },
          ]}
          currentStep={step}
        />

        {/* Step 1: Experiment Setup */}
        {step === 1 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card p-8 mt-8"
          >
            <h2 className="text-2xl font-bold mb-6">Experiment Details</h2>

            <div className="mb-6">
              <label className="block text-sm font-semibold mb-2">
                Experiment Name
              </label>
              <input
                type="text"
                value={experimentName}
                onChange={(e) => setExperimentName(e.target.value)}
                placeholder="e.g., Breast Cancer Cohort 2024"
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
              />
            </div>

            <div className="mb-8">
              <label className="block text-sm font-semibold mb-2">
                Cancer Type
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {CANCER_TYPES.map((type) => (
                  <button
                    key={type.id}
                    onClick={() => setCancerType(type.id)}
                    className={`p-3 rounded-lg border transition-all ${
                      cancerType === type.id
                        ? 'bg-purple-600 border-purple-500 shadow-lg shadow-purple-500/50'
                        : 'bg-white/5 border-white/10 hover:bg-white/10'
                    }`}
                  >
                    {type.name}
                  </button>
                ))}
              </div>
            </div>

            <button
              onClick={handleCreateExperiment}
              disabled={!experimentName || !cancerType}
              className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Continue to Upload
            </button>
          </motion.div>
        )}

        {/* Step 2: File Upload */}
        {step === 2 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-8"
          >
            <div
              {...getRootProps()}
              className={`glass-card p-12 text-center cursor-pointer transition-all ${
                isDragActive ? 'border-purple-500 bg-purple-500/10' : ''
              }`}
            >
              <input {...getInputProps()} />
              <UploadIcon
                size={64}
                className="mx-auto mb-4 text-purple-400"
              />
              {isDragActive ? (
                <p className="text-xl">Drop files here...</p>
              ) : (
                <>
                  <p className="text-xl mb-2">
                    Drag & drop files here, or click to select
                  </p>
                  <p className="text-gray-400">
                    Supported: CSV, TSV, TXT, GZ
                  </p>
                </>
              )}
            </div>

            {/* Uploaded Files List */}
            {files.length > 0 && (
              <div className="mt-6 space-y-4">
                {files.map((fileData, index) => (
                  <div key={index} className="glass-card p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <FileText size={24} className="text-purple-400" />
                        <div>
                          <p className="font-semibold">{fileData.file.name}</p>
                          <p className="text-sm text-gray-400">
                            {(fileData.file.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(index)}
                        className="text-red-400 hover:text-red-300"
                      >
                        <X size={20} />
                      </button>
                    </div>

                    <div className="mb-2">
                      <label className="block text-sm mb-1">Layer Type</label>
                      <select
                        value={fileData.layerType || ''}
                        onChange={(e) => updateLayerType(index, e.target.value)}
                        className="w-full px-3 py-2 bg-white/5 border border-white/10 rounded-lg focus:border-purple-500 focus:outline-none"
                      >
                        <option value="">Auto-detect</option>
                        {LAYER_TYPES.map((type) => (
                          <option key={type.id} value={type.id}>
                            {type.name}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                ))}

                <button
                  onClick={handleUploadFiles}
                  className="btn-primary w-full"
                >
                  Upload & Process Files
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Step 3: Processing */}
        {step === 3 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card p-8 mt-8"
          >
            <h2 className="text-2xl font-bold mb-6">Processing Files</h2>
            <div className="space-y-4">
              {files.map((fileData, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span>{fileData.file.name}</span>
                    <div className="flex items-center gap-2">
                      {fileData.status === 'uploading' && (
                        <Loader className="animate-spin" size={20} />
                      )}
                      {fileData.status === 'success' && (
                        <CheckCircle className="text-green-500" size={20} />
                      )}
                      <span>{fileData.progress}%</span>
                    </div>
                  </div>
                  <div className="w-full bg-white/10 rounded-full h-2">
                    <div
                      className="bg-gradient-to-r from-purple-500 to-fuchsia-500 h-2 rounded-full transition-all"
                      style={{ width: `${fileData.progress}%` }}
                    />
                  </div>
                  {fileData.status === 'success' && (
                    <div className="text-sm text-gray-400">
                      {fileData.geneCount} genes, {fileData.sampleCount}{' '}
                      samples
                    </div>
                  )}
                </div>
              ))}
            </div>
          </motion.div>
        )}

        {/* Step 4: Ready to Analyze */}
        {step === 4 && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="glass-card p-8 mt-8 text-center"
          >
            <CheckCircle size={64} className="mx-auto mb-4 text-green-500" />
            <h2 className="text-2xl font-bold mb-4">Files Uploaded Successfully!</h2>
            <p className="text-gray-400 mb-8">
              {files.length} file{files.length !== 1 ? 's' : ''} processed and ready for analysis
            </p>

            <button
              onClick={handleAnalyze}
              disabled={analyzing}
              className="btn-primary inline-flex items-center gap-2"
            >
              {analyzing ? (
                <>
                  <Loader className="animate-spin" size={20} />
                  Analyzing...
                </>
              ) : (
                'Start Analysis'
              )}
            </button>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
};

export default Upload;
