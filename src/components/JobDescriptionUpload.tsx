// src/components/JobDescriptionUpload.tsx
"use client";

import { useState } from 'react';
import { Upload, FileText, X, Copy, Loader, AlertCircle } from 'lucide-react';

interface JobDescriptionUploadProps {
  onJobDescriptionParsed: (data: any) => void;
}

export default function JobDescriptionUpload({ onJobDescriptionParsed }: JobDescriptionUploadProps) {
  const [method, setMethod] = useState<'upload' | 'paste'>('paste');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [pastedText, setPastedText] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleJobAnalysis = async (jobText: string) => {
    if (!jobText.trim()) {
      setError('Please enter a job description');
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      console.log('Sending job description to API...', jobText.substring(0, 100));

      const response = await fetch('/api/analyze-job', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ job_description: jobText }),
      });

      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('API response:', result);

      if (result.success) {
        onJobDescriptionParsed(result.data);
      } else {
        throw new Error(result.error || 'Analysis failed');
      }
    } catch (error) {
      console.error('Analysis error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      setError(`Failed to analyze job description: ${errorMessage}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePasteSubmit = () => {
    handleJobAnalysis(pastedText);
  };

  const handlePasteFromClipboard = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setPastedText(text);
      setError(null);
    } catch (error) {
      console.error('Failed to read clipboard:', error);
      setError('Unable to access clipboard. Please paste manually.');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setError('File upload selected. Please use the paste method for now.');
    }
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Job Description</h3>
      
      {/* Error Display */}
      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-start space-x-2">
          <AlertCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
          <div className="flex-1">
            <p className="text-red-800 text-sm">{error}</p>
            <button 
              onClick={clearError}
              className="text-red-600 hover:text-red-800 text-xs mt-1"
            >
              Dismiss
            </button>
          </div>
        </div>
      )}

      <div className="flex space-x-2 mb-4">
        <button
          onClick={() => setMethod('upload')}
          className={`flex-1 px-3 py-2 rounded-lg text-sm ${
            method === 'upload' 
              ? 'bg-primary text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Upload File
        </button>
        <button
          onClick={() => setMethod('paste')}
          className={`flex-1 px-3 py-2 rounded-lg text-sm ${
            method === 'paste' 
              ? 'bg-primary text-white' 
              : 'bg-gray-100 text-gray-700'
          }`}
        >
          Paste Text
        </button>
      </div>

      <div className="flex-1">
        {method === 'upload' ? (
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center h-48 flex flex-col items-center justify-center">
            <Upload className="w-10 h-10 text-gray-400 mb-3" />
            <p className="text-gray-600 mb-2 text-sm">
              Upload job description document
            </p>
            <p className="text-xs text-gray-500 mb-4">
              Supports PDF, DOC, DOCX, TXT
            </p>
            <input
              type="file"
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileUpload}
              className="hidden"
              id="jd-upload"
            />
            <label
              htmlFor="jd-upload"
              className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary cursor-pointer text-sm"
            >
              Upload File
            </label>
          </div>
        ) : (
          <div className="space-y-4 h-full flex flex-col">
            <div className="flex-1">
              <textarea
                value={pastedText}
                onChange={(e) => {
                  setPastedText(e.target.value);
                  setError(null);
                }}
                placeholder="Paste the job description here...&#10;&#10;Example:&#10;We are looking for a Senior Frontend Developer with 5+ years of experience in React and TypeScript. The ideal candidate should have experience with modern web technologies and a strong understanding of software engineering principles."
                className="w-full h-full min-h-[200px] p-3 border border-gray-300 rounded-lg resize-none text-sm focus:border-primary focus:ring-1 focus:ring-primary"
              />
            </div>
            <div className="flex justify-between items-center pt-2">
              <button
                onClick={handlePasteFromClipboard}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-800 text-sm"
              >
                <Copy className="w-4 h-4" />
                <span>Paste from clipboard</span>
              </button>
              <button
                onClick={handlePasteSubmit}
                disabled={!pastedText.trim() || isAnalyzing}
                className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 text-sm"
              >
                {isAnalyzing ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <span>Analyze Job Description</span>
                )}
              </button>
            </div>
          </div>
        )}

        {uploadedFile && (
          <div className="mt-4 border rounded-lg p-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <FileText className="w-6 h-6 text-green-500" />
                <div>
                  <p className="font-medium text-sm">{uploadedFile.name}</p>
                  <p className="text-xs text-gray-500">Ready for analysis</p>
                </div>
              </div>
              <button
                onClick={() => setUploadedFile(null)}
                className="text-gray-400 hover:text-red-500"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}