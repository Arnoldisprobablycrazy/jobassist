// src/components/SimilarityScoring.tsx
"use client";

import { Target, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface SimilarityScoringProps {
  resumeData: any;
  jobData: any;
  scores: {
    overall_score: number;
    skill_match_score: number;
    experience_match_score: number;
    keyword_match_score: number;
  };
}

export default function SimilarityScoring({ resumeData, jobData, scores }: SimilarityScoringProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  const getScoreMessage = (score: number) => {
    if (score >= 80) return 'Excellent match!';
    if (score >= 60) return 'Good match';
    if (score >= 40) return 'Fair match';
    return 'Needs improvement';
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Target className="w-5 h-5 mr-2" />
        Resume Match Score
      </h3>

      {/* Overall Score */}
      <div className="text-center mb-8">
        <div className={`inline-flex items-center justify-center w-24 h-24 rounded-full ${getScoreBgColor(scores.overall_score)} mb-4`}>
          <span className={`text-2xl font-bold ${getScoreColor(scores.overall_score)}`}>
            {scores.overall_score}%
          </span>
        </div>
        <p className="text-gray-600 font-medium">
          {getScoreMessage(scores.overall_score)}
        </p>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center p-4 border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Skills Match</div>
          <div className={`text-lg font-semibold ${getScoreColor(scores.skill_match_score)}`}>
            {scores.skill_match_score}%
          </div>
        </div>
        <div className="text-center p-4 border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Experience</div>
          <div className={`text-lg font-semibold ${getScoreColor(scores.experience_match_score)}`}>
            {scores.experience_match_score}%
          </div>
        </div>
        <div className="text-center p-4 border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Keywords</div>
          <div className={`text-lg font-semibold ${getScoreColor(scores.keyword_match_score)}`}>
            {scores.keyword_match_score}%
          </div>
        </div>
        <div className="text-center p-4 border rounded-lg">
          <div className="text-sm text-gray-600 mb-1">Overall</div>
          <div className={`text-lg font-semibold ${getScoreColor(scores.overall_score)}`}>
            {scores.overall_score}%
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="border-t pt-4">
        <h4 className="font-semibold mb-3 flex items-center">
          <AlertCircle className="w-4 h-4 mr-2 text-blue-500" />
          Recommendations to Improve Your Score
        </h4>
        <ul className="space-y-2">
          {scores.skill_match_score < 70 && (
            <li className="flex items-start space-x-2 text-sm">
              <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span>Add more of the required skills mentioned in the job description to your resume</span>
            </li>
          )}
          {scores.keyword_match_score < 70 && (
            <li className="flex items-start space-x-2 text-sm">
              <XCircle className="w-4 h-4 text-red-500 mt-0.5 flex-shrink-0" />
              <span>Include more industry-specific keywords from the job description</span>
            </li>
          )}
          {scores.overall_score >= 70 && (
            <li className="flex items-start space-x-2 text-sm">
              <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
              <span>Your resume is well-matched! Consider generating a cover letter to complete your application</span>
            </li>
          )}
        </ul>
      </div>
    </div>
  );
}