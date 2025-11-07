// src/app/dashboard/page.tsx
"use client";

import { useState, useEffect } from 'react';
import AppBarChart from '@/components/AppBarChart'
import DashboardCards from '@/components/DashboardCards'
import JobDescriptionUpload from '@/components/JobDescriptionUpload'
import ResumeUpload from '@/components/ResumeUpload'
import SimilarityScoring from '@/components/SimilarityScoring'
import CoverLetterGenerator from '@/components/CoverLetterGenerator'

// Define the data types
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

interface JobData {
  required_skills: string[];
  experience_level: string;
  job_title: string;
  key_responsibilities: string[];
  qualifications: string[];
  description?: string;
}

interface SimilarityScores {
  overall_score: number;
  skill_match_score: number;
  experience_match_score: number;
  keyword_match_score: number;
}

const Dashboardpage = () => {
  const [resumeData, setResumeData] = useState<ResumeData | null>(null);
  const [jobData, setJobData] = useState<JobData | null>(null);
  const [similarityScores, setSimilarityScores] = useState<SimilarityScores | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'analysis' | 'cover-letter'>('upload');
  const [isCalculatingSimilarity, setIsCalculatingSimilarity] = useState(false);

  // Handler for when resume is parsed - just store the data
  const handleResumeParsed = (data: ResumeData) => {
    console.log('Resume parsed and stored:', data);
    setResumeData(data);
  };

  // Handler for when job description is parsed
  const handleJobDescriptionParsed = (data: JobData) => {
    console.log('Job description parsed:', data);
    setJobData(data);
    // Now we have both, we can calculate similarity
    if (resumeData) {
      calculateSimilarity(resumeData, data);
    }
  };

  // Calculate similarity only when explicitly called
  const calculateSimilarity = async (resume: ResumeData, job: JobData) => {
    setIsCalculatingSimilarity(true);
    
    try {
      const response = await fetch('/api/calculate-similarity', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resume.raw_text,
          job_text: job.description || JSON.stringify(job)
        }),
      });

      const result = await response.json();
      
      if (result.success) {
        setSimilarityScores(result.data);
        setActiveTab('analysis');
      } else {
        console.error('Similarity calculation failed:', result.error);
        alert('Failed to calculate similarity: ' + result.error);
      }
    } catch (error) {
      console.error('Error calculating similarity:', error);
      alert('Error calculating similarity. Please try again.');
    } finally {
      setIsCalculatingSimilarity(false);
    }
  };

  // Manual trigger for similarity calculation
  const handleCalculateSimilarity = () => {
    if (resumeData && jobData) {
      calculateSimilarity(resumeData, jobData);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-4">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Job Application Assistant</h1>
        <p className="text-gray-600 mt-2">Upload your resume and job description to get started</p>
      </div>

      {/* Navigation Tabs */}
      <div className="mb-6">
        <div className="flex space-x-4 border-b">
          <button
            onClick={() => setActiveTab('upload')}
            className={`pb-2 px-4 font-medium ${
              activeTab === 'upload'
                ? 'border-b-2 border-primary text-primary'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            📄 Upload Documents
          </button>
          <button
            onClick={() => setActiveTab('analysis')}
            disabled={!resumeData || !jobData}
            className={`pb-2 px-4 font-medium ${
              activeTab === 'analysis'
                ? 'border-b-2 border-primary text-primary'
                : 'text-gray-500 hover:text-gray-700 disabled:opacity-50'
            }`}
          >
            📊 Analysis & Scores
          </button>
          <button
            onClick={() => setActiveTab('cover-letter')}
            disabled={!resumeData || !jobData}
            className={`pb-2 px-4 font-medium ${
              activeTab === 'cover-letter'
                ? 'border-b-2 border-primary text-primary'
                : 'text-gray-500 hover:text-gray-700 disabled:opacity-50'
            }`}
          >
            ✍️ Cover Letter
          </button>
        </div>
      </div>

      {/* Upload Tab */}
      {activeTab === 'upload' && (
        <div className='grid grid-cols-1 lg:grid-cols-2 2xl:grid-cols-4 gap-4'>
          {/* Status Banner */}
          {(resumeData || jobData) && (
            <div className="col-span-full bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-blue-900">Upload Status</h3>
                  <div className="flex space-x-4 mt-1 text-sm text-blue-800">
                    {resumeData && <span>✓ Resume Uploaded ({resumeData.skills?.length || 0} skills)</span>}
                    {jobData && <span>✓ Job Description Analyzed</span>}
                    {!resumeData && <span>⏳ Resume Pending</span>}
                    {!jobData && <span>⏳ Job Description Pending</span>}
                  </div>
                </div>
                {resumeData && jobData && !similarityScores && (
                  <button
                    onClick={handleCalculateSimilarity}
                    disabled={isCalculatingSimilarity}
                    className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-secondary disabled:opacity-50"
                  >
                    {isCalculatingSimilarity ? 'Calculating...' : 'Calculate Match Score'}
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Dashboard Cards - REMOVE PROPS */}
          <div className="bg-white p-4 rounded-lg col-span-full shadow-sm border">
            <DashboardCards /> 
          </div>

          {/* Resume and Job Description Upload */}
          <div className="bg-white p-4 rounded-lg col-span-full lg:col-span-2 shadow-sm border">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="min-h-[400px]">
                <ResumeUpload onResumeParsed={handleResumeParsed} />
              </div>
              <div className="min-h-[400px]">
                <JobDescriptionUpload onJobDescriptionParsed={handleJobDescriptionParsed} />
              </div>
            </div>
          </div>

          {/* Quick Stats - REMOVE PROPS */}
          <div className="bg-white p-4 rounded-lg col-span-full lg:col-span-2 2xl:col-span-2 shadow-sm border">
            <AppBarChart />
          </div>
        </div>
      )}

      {/* Analysis Tab */}
      {activeTab === 'analysis' && resumeData && jobData && (
        <div className="space-y-6">
          {similarityScores ? (
            <div className="bg-white p-6 rounded-lg shadow-sm border">
              <SimilarityScoring 
                resumeData={resumeData}
                jobData={jobData}
                scores={similarityScores}
              />
              
              {/* Data Comparison */}
              <div className="mt-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Resume Skills */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-3 text-green-600">✓ Your Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {resumeData.skills.map((skill, index) => (
                      <span key={index} className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Job Required Skills */}
                <div className="border rounded-lg p-4">
                  <h3 className="font-semibold mb-3 text-blue-600">🎯 Job Requirements</h3>
                  <div className="flex flex-wrap gap-2">
                    {jobData.required_skills.map((skill, index) => (
                      <span key={index} className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white p-6 rounded-lg shadow-sm border text-center">
              <p className="text-gray-600">Similarity analysis not calculated yet.</p>
              <button
                onClick={handleCalculateSimilarity}
                disabled={isCalculatingSimilarity}
                className="mt-4 bg-primary text-white px-6 py-2 rounded-lg hover:bg-secondary disabled:opacity-50"
              >
                {isCalculatingSimilarity ? 'Calculating...' : 'Calculate Match Score'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* Cover Letter Tab */}
      {activeTab === 'cover-letter' && resumeData && jobData && (
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <CoverLetterGenerator 
            resumeData={resumeData}
            jobData={jobData}
          />
        </div>
      )}
    </div>
  )
}

export default Dashboardpage