/**
 * Home.jsx — Premium Landing + Upload Page
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  FileCheck,
  ShieldCheck,
  Zap,
  Brain,
  ArrowRight,
} from 'lucide-react';

import UploadZone from '../components/UploadZone';
import { uploadFile } from '../api/axios';

const Home = ({ onUploadSuccess, currentSession }) => {
  const navigate = useNavigate();

  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const [uploadDone, setUploadDone] = useState(false);

  const handleUpload = async (file) => {
    setIsLoading(true);
    setError(null);
    setProgress(0);
    setUploadDone(false);

    try {
      const data = await uploadFile(file, (pct) => setProgress(pct));

      setUploadDone(true);
      setProgress(100);

      onUploadSuccess?.(data);

      setTimeout(() => navigate('/chat'), 800);
    } catch (err) {
      setError(err.message || 'Failed to upload contract. Please try again.');
      setIsLoading(false);
      setProgress(0);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">

      {/* Background Decorations */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400/20 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 w-80 h-80 bg-cyan-300/20 rounded-full blur-3xl -translate-x-1/2 -translate-y-1/2" />

      <div className="relative z-10 max-w-5xl mx-auto px-4 py-12">

        {/* Hero Section */}
        <div className="text-center mb-12">

          <div className="inline-flex items-center gap-3 bg-white shadow-lg border border-blue-100 rounded-2xl px-6 py-4 mb-6">
            <div className="bg-gradient-to-r from-blue-600 to-cyan-500 p-3 rounded-xl shadow-md">
              <FileCheck className="h-8 w-8 text-white" />
            </div>

            <h1 className="text-5xl font-extrabold text-slate-900">
              ContractIQ
            </h1>
          </div>

          <div className="flex justify-center mb-4">
            <div className="flex items-center gap-2 bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
              <Zap className="h-4 w-4" />
              AI-Powered Contract Intelligence
            </div>
          </div>

          <p className="text-xl text-slate-700 font-medium mb-3">
            Analyze Legal Contracts in Seconds
          </p>

          <p className="text-slate-500 max-w-2xl mx-auto leading-relaxed">
            Upload your PDF contracts, ask questions in natural language,
            detect risks, understand obligations, and get intelligent answers
            powered by Gemini, LangGraph, and Retrieval-Augmented Generation.
          </p>
        </div>

        {/* Active Session */}
        {currentSession && !uploadDone && (
          <div className="mb-8 bg-white border border-blue-100 rounded-2xl shadow-md p-5 flex flex-col md:flex-row md:items-center md:justify-between gap-4">

            <div>
              <p className="font-semibold text-slate-800">
                Active Session Available
              </p>

              <p className="text-sm text-slate-600 mt-1">
                {currentSession.filename}
              </p>

              <p className="text-xs text-slate-400 mt-1">
                {currentSession.chunkCount} Chunks • {currentSession.pageCount} Pages
              </p>
            </div>

            <button
              onClick={() => navigate('/chat')}
              className="inline-flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl transition-all font-medium"
            >
              Continue Session
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        )}

        {/* Upload Section */}
        <div className="bg-white/80 backdrop-blur-sm border border-white rounded-3xl shadow-xl p-6">
          <UploadZone
            onUpload={handleUpload}
            isLoading={isLoading}
            progress={progress}
            uploadDone={uploadDone}
          />
        </div>

        {/* Progress */}
        {isLoading && progress > 0 && (
          <div className="mt-6 max-w-2xl mx-auto">

            <div className="flex justify-between text-sm text-slate-500 mb-2">
              <span>
                {progress < 100
                  ? 'Uploading Contract...'
                  : 'Processing & Embedding Document...'}
              </span>

              <span>{progress}%</span>
            </div>

            <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-blue-500 via-cyan-400 to-indigo-500 rounded-full transition-all duration-500"
                style={{ width: `${progress}%` }}
              />
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-5 max-w-2xl mx-auto bg-red-50 border border-red-200 text-red-700 px-5 py-4 rounded-xl shadow-sm">
            ⚠ {error}
          </div>
        )}

        {/* Success */}
        {uploadDone && (
          <div className="mt-5 max-w-2xl mx-auto bg-green-50 border border-green-200 text-green-700 px-5 py-4 rounded-xl shadow-sm text-center">
            ✅ Contract processed successfully. Redirecting to AI Assistant...
          </div>
        )}

        {/* Features */}
        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6">

          <FeatureCard
            icon={<Brain className="h-6 w-6 text-blue-600" />}
            title="Smart Analysis"
            description="Automatically understand clauses, obligations, liabilities, deadlines, and legal risks."
          />

          <FeatureCard
            icon={<Zap className="h-6 w-6 text-indigo-600" />}
            title="Instant Answers"
            description="Ask contract-related questions and receive context-aware answers with source references."
          />

          <FeatureCard
            icon={<ShieldCheck className="h-6 w-6 text-green-600" />}
            title="Secure Processing"
            description="Contracts remain tied to your active session with privacy-first document handling."
          />
        </div>

        {/* Footer */}
        <div className="mt-16 text-center">
          <p className="text-slate-500 text-sm">
            Powered by Gemini • LangGraph • ChromaDB • FastAPI • React
          </p>

          <p className="text-slate-400 text-xs mt-2">
            AI Legal Contract Intelligence Platform
          </p>
        </div>
      </div>
    </div>
  );
};

const FeatureCard = ({ icon, title, description }) => (
  <div className="bg-white border border-slate-100 rounded-2xl shadow-md p-6 hover:shadow-xl hover:-translate-y-2 transition-all duration-300">
    <div className="mb-4">
      {icon}
    </div>

    <h3 className="font-bold text-slate-900 mb-2">
      {title}
    </h3>

    <p className="text-slate-500 text-sm leading-relaxed">
      {description}
    </p>
  </div>
);

export default Home;