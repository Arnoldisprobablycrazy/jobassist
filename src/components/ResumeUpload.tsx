// src/components/ResumeUpload.tsx
"use client";

import { useState } from 'react';
import { Upload, FileText, X, CheckCircle } from 'lucide-react';

interface ResumeData {
  personal_info: {
    email: string;
    phone: string;
  };
  skills: string[];
  experience: Array<{ description: string }>;
  education: Array<{ institution: string }>;
  contact_info: {
    linkedin: string;
    github: string;
  };
  raw_text: string;
}

interface ResumeUploadProps {
  onResumeParsed: (data: ResumeData) => void;
}

export default function ResumeUpload({ onResumeParsed }: ResumeUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [isParsing, setIsParsing] = useState(false);
  const [parseSuccess, setParseSuccess] = useState(false);
  const [parsedData, setParsedData] = useState<ResumeData | null>(null);

  const handleFileUpload = async (file: File) => {
    setUploadedFile(file);
    setIsParsing(true);
    setParseSuccess(false);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/parse-resume', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();

      if (result.success) {
        setParsedData(result.data);
        setParseSuccess(true);
        // Store the data but don't trigger analysis yet
        // We'll call onResumeParsed to let parent know we have data
        onResumeParsed(result.data);
      } else {
        console.error('Parsing failed:', result.error);
        
        // Provide user-friendly error messages
        let errorMessage = result.error || 'Failed to parse resume';
        
        if (errorMessage.includes('Invalid resume document')) {
          // Extract the specific validation error
          alert('⚠️ Document Validation Failed\n\n' + errorMessage + '\n\nPlease upload a valid resume or CV document.');
        } else if (errorMessage.includes('too short')) {
          alert('⚠️ Invalid Resume\n\nThe uploaded document is too short to be a resume. Please upload a complete resume document.');
        } else {
          alert('Failed to parse resume:\n\n' + errorMessage);
        }
        
        setUploadedFile(null);
      }
    } catch (error) {
      console.error('Upload error:', error);
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      
      if (errorMsg.includes('fetch failed') || errorMsg.includes('ECONNREFUSED')) {
        alert('❌ Connection Error\n\nCannot connect to the backend service.\nPlease ensure the Python backend is running on port 5000.');
      } else {
        alert('Error uploading resume:\n\n' + errorMsg);
      }
      
      setUploadedFile(null);
    } finally {
      setIsParsing(false);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file && (file.type === 'application/pdf' || file.name.endsWith('.docx'))) {
      handleFileUpload(file);
    } else {
      alert('Please upload a PDF or DOCX file');
    }
  };

  const removeFile = () => {
    setUploadedFile(null);
    setParseSuccess(false);
    setParsedData(null);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 h-full flex flex-col">
      <h3 className="text-lg font-semibold mb-4">Upload Resume</h3>
      
      {!uploadedFile ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center flex-1 flex flex-col items-center justify-center">
          <Upload className="w-12 h-12 text-gray-400 mb-4" />
          <p className="text-gray-600 mb-2">
            Upload your resume (PDF or DOCX)
          </p>
          <p className="text-sm text-gray-500 mb-4">
            We'll extract your skills and experience
          </p>
          <input
            type="file"
            accept=".pdf,.docx"
            onChange={handleFileSelect}
            className="hidden"
            id="resume-upload"
          />
          <label
            htmlFor="resume-upload"
            className="bg-primary text-white px-6 py-2 rounded-lg hover:bg-secondary cursor-pointer"
          >
            Choose File
          </label>
        </div>
      ) : (
        <div className="border rounded-lg p-4 flex-1 flex flex-col">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <FileText className="w-8 h-8 text-blue-500" />
              <div>
                <p className="font-medium">{uploadedFile.name}</p>
                <p className="text-sm text-gray-500">
                  {(uploadedFile.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
            </div>
            <button
              onClick={removeFile}
              className="text-gray-400 hover:text-red-500"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          
          {isParsing && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-2"></div>
                <p className="text-sm text-gray-600">Parsing resume...</p>
                <p className="text-xs text-gray-500 mt-1">This may take a few seconds</p>
              </div>
            </div>
          )}

          {parseSuccess && !isParsing && parsedData && (
            <div className="flex-1 flex flex-col justify-center">
              <div className="text-center mb-4">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-2" />
                <p className="text-green-800 font-medium">Resume Parsed Successfully!</p>
                <p className="text-sm text-gray-600 mt-1">Now upload a job description to see matching analysis.</p>
              </div>
              
              {/* Show extracted skills preview */}
              <div className="bg-gray-50 rounded-lg p-3 mt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Skills Detected:</p>
                <div className="flex flex-wrap gap-1">
                  {parsedData.skills.slice(0, 8).map((skill, index) => (
                    <span key={index} className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs">
                      {skill}
                    </span>
                  ))}
                  {parsedData.skills.length > 8 && (
                    <span className="text-gray-500 text-xs">
                      +{parsedData.skills.length - 8} more
                    </span>
                  )}
                </div>
                {parsedData.skills.length === 0 && (
                  <p className="text-gray-500 text-xs">No skills detected in resume</p>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}