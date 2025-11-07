// src/components/CoverLetterGenerator.tsx
"use client";

import { useState } from 'react';
import { FileText, Download, RefreshCw, Copy } from 'lucide-react';

interface CoverLetterGeneratorProps {
  resumeData: any;
  jobData: any;
}

export default function CoverLetterGenerator({ resumeData, jobData }: CoverLetterGeneratorProps) {
  const [coverLetter, setCoverLetter] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [tone, setTone] = useState<'professional' | 'enthusiastic' | 'formal'>('professional');

  const generateCoverLetter = async () => {
    setIsGenerating(true);
    
    try {
      const response = await fetch('/api/generate-cover-letter', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_data: resumeData,
          job_data: jobData,
          tone: tone
        }),
      });

      const result = await response.json();

      if (result.success) {
        setCoverLetter(result.data.cover_letter);
      } else {
        console.error('Generation failed:', result.error);
        alert('Failed to generate cover letter: ' + result.error);
      }
    } catch (error) {
      console.error('Generation error:', error);
      alert('Error generating cover letter');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadCoverLetter = () => {
    const element = document.createElement('a');
    const file = new Blob([coverLetter], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `cover-letter-${jobData.job_title || 'application'}.txt`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(coverLetter);
    alert('Cover letter copied to clipboard!');
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <FileText className="w-5 h-5 mr-2" />
        AI Cover Letter Generator
      </h3>

      <div className="flex items-center justify-between mb-4">
        <div>
          <label className="text-sm font-medium text-gray-700 mr-2">Tone:</label>
          <select
            value={tone}
            onChange={(e) => setTone(e.target.value as any)}
            className="border rounded px-3 py-1 text-sm"
          >
            <option value="professional">Professional</option>
            <option value="enthusiastic">Enthusiastic</option>
            <option value="formal">Formal</option>
          </select>
        </div>
        
        <button
          onClick={generateCoverLetter}
          disabled={isGenerating}
          className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary disabled:opacity-50 flex items-center space-x-2"
        >
          {isGenerating ? (
            <RefreshCw className="w-4 h-4 animate-spin" />
          ) : (
            <FileText className="w-4 h-4" />
          )}
          <span>{isGenerating ? 'Generating...' : 'Generate Letter'}</span>
        </button>
      </div>

      {coverLetter && (
        <div className="space-y-4">
          <div className="border rounded-lg">
            <div className="border-b bg-gray-50 px-4 py-2 flex justify-between items-center">
              <span className="text-sm font-medium">Generated Cover Letter</span>
              <div className="flex space-x-2">
                <button
                  onClick={copyToClipboard}
                  className="flex items-center space-x-1 text-sm text-gray-600 hover:text-gray-800"
                >
                  <Copy className="w-4 h-4" />
                  <span>Copy</span>
                </button>
                <button
                  onClick={downloadCoverLetter}
                  className="flex items-center space-x-1 text-sm text-green-600 hover:text-green-800"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>
            <div className="p-4 max-h-96 overflow-y-auto">
              <pre className="whitespace-pre-wrap font-sans text-sm">
                {coverLetter}
              </pre>
            </div>
          </div>
        </div>
      )}

      {!coverLetter && !isGenerating && (
        <div className="text-center py-8 text-gray-500">
          <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p>Click "Generate Letter" to create a personalized cover letter</p>
          <p className="text-sm mt-1">Based on your resume and the job description</p>
        </div>
      )}
    </div>
  );
}