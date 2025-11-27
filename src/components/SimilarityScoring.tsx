// src/components/SimilarityScoring.tsx
"use client";

import { useState } from 'react';
import { Target, CheckCircle, XCircle, AlertCircle, TrendingUp, Award, FileText, Zap, Sparkles, Download, Eye } from 'lucide-react';

interface Recommendation {
  category: string;
  item: string;
  impact: string;
}

interface SkillsSummary {
  matched: number;
  missing: number;
  match_percentage: number;
}

interface Recommendations {
  action_items: Recommendation[];
  skill_suggestions: string[];
  content_suggestions: string[];
  formatting_tips: string[];
  graduate_specific?: Recommendation[];
}

interface GraduateStatus {
  is_recent_graduate: boolean;
  graduation_year: number | null;
  has_internship: boolean;
  has_academic_projects: boolean;
  has_limited_experience: boolean;
  years_of_experience: number;
}

interface SimilarityScoringProps {
  resumeData: any;
  jobData: any;
  scores: {
    overall_score: number;
    skill_match_score: number;
    experience_match_score: number;
    keyword_match_score: number;
    matching_skills?: string[];
    missing_skills?: string[];
    recommendations?: Recommendations;
    skills_summary?: SkillsSummary;
    graduate_status?: GraduateStatus;
  };
  resumeText?: string;
  jobText?: string;
}

export default function SimilarityScoring({ resumeData, jobData, scores, resumeText, jobText }: SimilarityScoringProps) {
  const [isEnhancing, setIsEnhancing] = useState(false);
  const [enhancedResume, setEnhancedResume] = useState<string | null>(null);
  const [newScores, setNewScores] = useState<any>(null);
  const [showEnhancedResume, setShowEnhancedResume] = useState(false);
  const [enhancementError, setEnhancementError] = useState<string | null>(null);

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

  const handleEnhanceResume = async () => {
    if (!resumeText || !jobText) {
      setEnhancementError('Resume or job description text not available');
      return;
    }

    setIsEnhancing(true);
    setEnhancementError(null);

    try {
      const response = await fetch('/api/enhance-resume', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resume_text: resumeText,
          job_text: jobText,
          recommendations: scores.recommendations,
        }),
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.error || 'Failed to enhance resume');
      }

      setEnhancedResume(result.data.enhanced_resume);
      setNewScores(result.data.new_similarity_scores);
      setShowEnhancedResume(true);
    } catch (error: any) {
      console.error('Enhancement error:', error);
      setEnhancementError(error.message || 'Failed to enhance resume');
    } finally {
      setIsEnhancing(false);
    }
  };

  const handleDownloadEnhancedResume = () => {
    if (!enhancedResume) return;

    const blob = new Blob([enhancedResume], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'enhanced-resume.txt';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6">
      <h3 className="text-lg font-semibold mb-4 flex items-center">
        <Target className="w-5 h-5 mr-2" />
        Resume Match Score
      </h3>

      {/* Graduate Status Banner */}
      {scores.graduate_status?.is_recent_graduate && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <Award className="w-5 h-5 text-blue-600 mt-0.5 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-blue-900">🎓 Recent Graduate Profile Detected</h4>
              <p className="text-sm text-blue-800 mt-1">
                Graduated in {scores.graduate_status.graduation_year}
                {scores.graduate_status.has_internship && ' • Has internship experience'}
                {scores.graduate_status.has_academic_projects && ' • Has academic projects'}
              </p>
              <p className="text-xs text-blue-700 mt-2">
                Our scoring considers your graduate status. Employers understand recent graduates have academic knowledge but limited industry experience.
              </p>
            </div>
          </div>
        </div>
      )}

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
        
        {/* Render action items if available */}
        {scores.recommendations?.action_items && scores.recommendations.action_items.length > 0 && (
          <div className="space-y-3 mb-4">
            {scores.recommendations.action_items.map((item: any, index: number) => (
              <div key={index} className="bg-gray-50 p-3 rounded-lg">
                <h5 className="font-semibold text-sm mb-1">{item.title}</h5>
                <p className="text-xs text-gray-600 mb-2">{item.description}</p>
                <p className="text-xs text-blue-600">{item.action}</p>
              </div>
            ))}
          </div>
        )}

        {/* Render skill suggestions if available */}
        {scores.recommendations?.skill_suggestions && scores.recommendations.skill_suggestions.length > 0 && (
          <div className="space-y-3 mb-4">
            <h5 className="font-semibold text-sm">Skill Suggestions:</h5>
            {scores.recommendations.skill_suggestions.map((item: any, index: number) => (
              <div key={index} className="bg-blue-50 p-3 rounded-lg">
                <h6 className="font-semibold text-sm mb-1">{item.title}</h6>
                <p className="text-xs text-gray-600 mb-2">{item.description}</p>
                {item.skills && (
                  <div className="flex flex-wrap gap-1 mb-2">
                    {item.skills.map((skill: string, idx: number) => (
                      <span key={idx} className="bg-blue-200 text-blue-800 px-2 py-0.5 rounded text-xs">
                        {skill}
                      </span>
                    ))}
                  </div>
                )}
                <p className="text-xs text-blue-600">{item.action}</p>
              </div>
            ))}
          </div>
        )}

        {/* Graduate-specific recommendations */}
        {scores.recommendations?.graduate_specific && scores.recommendations.graduate_specific.length > 0 && (
          <div className="space-y-3 mb-4">
            <h5 className="font-semibold text-sm flex items-center">
              <Award className="w-4 h-4 mr-1 text-purple-600" />
              Graduate-Specific Guidance:
            </h5>
            {scores.recommendations.graduate_specific.map((item: any, index: number) => (
              <div key={index} className="bg-purple-50 p-3 rounded-lg border border-purple-200">
                <h6 className="font-semibold text-sm mb-1">{item.title}</h6>
                <p className="text-xs text-gray-600 mb-2">{item.description}</p>
                <p className="text-xs text-purple-600 font-medium">{item.action}</p>
              </div>
            ))}
          </div>
        )}

        {/* Fallback to simple recommendations if detailed ones aren't available */}
        {(!scores.recommendations || 
          (!scores.recommendations.action_items?.length && !scores.recommendations.skill_suggestions?.length)) && (
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
        )}
      </div>

      {/* AI Resume Enhancement Section */}
      {!enhancedResume && resumeText && jobText && scores.overall_score < 80 && (
        <div className="border-t pt-4 mt-4">
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-4 rounded-lg border border-purple-200">
            <div className="flex items-start space-x-3">
              <Sparkles className="w-6 h-6 text-purple-600 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h4 className="font-semibold text-gray-900 mb-2">
                  ✨ AI-Powered Resume Optimization
                </h4>
                <p className="text-sm text-gray-700 mb-3">
                  Let our AI rewrite your resume to better match this job description. We'll <strong>reword your existing experience</strong> using 
                  relevant keywords, improve formatting, and add a professional summary - <strong>without adding false information</strong>. 
                  Your facts stay the same, only the presentation improves!
                </p>
                {enhancementError && (
                  <div className="mb-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
                    {enhancementError}
                  </div>
                )}
                <button
                  onClick={handleEnhanceResume}
                  disabled={isEnhancing}
                  className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {isEnhancing ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      <span>Optimizing Resume...</span>
                    </>
                  ) : (
                    <>
                      <Zap className="w-4 h-4" />
                      <span>Yes, Optimize My Resume</span>
                    </>
                  )}
                </button>
                <p className="text-xs text-gray-600 mt-2 italic">
                  Note: AI will reword your content but keep your actual experience and dates unchanged. Always review before using!
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Enhanced Resume Display */}
      {enhancedResume && newScores && (
        <div className="border-t pt-4 mt-4">
          {/* Warning if score decreased */}
          {newScores.overall_score < scores.overall_score && (
            <div className="bg-yellow-50 p-4 rounded-lg border border-yellow-200 mb-4">
              <div className="flex items-start space-x-2">
                <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 flex-shrink-0" />
                <div>
                  <h5 className="font-semibold text-yellow-900 mb-1">Enhancement May Need Review</h5>
                  <p className="text-sm text-yellow-800">
                    The enhanced resume has a lower match score ({newScores.overall_score}%) compared to your original ({scores.overall_score}%). 
                    This might indicate that some important content was reworded too much. You can still download it and 
                    manually adjust, or keep your original resume.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className={`p-4 rounded-lg border mb-4 ${
            newScores.overall_score >= scores.overall_score 
              ? 'bg-green-50 border-green-200' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                {newScores.overall_score >= scores.overall_score ? (
                  <>
                    <CheckCircle className="w-5 h-5 text-green-600" />
                    <h4 className="font-semibold text-green-900">Resume Enhanced Successfully!</h4>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-5 h-5 text-gray-600" />
                    <h4 className="font-semibold text-gray-900">Resume Enhanced (Review Recommended)</h4>
                  </>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => setShowEnhancedResume(!showEnhancedResume)}
                  className="bg-white hover:bg-gray-50 text-gray-700 px-3 py-1.5 rounded text-sm border flex items-center space-x-1"
                >
                  <Eye className="w-4 h-4" />
                  <span>{showEnhancedResume ? 'Hide' : 'View'} Resume</span>
                </button>
                <button
                  onClick={handleDownloadEnhancedResume}
                  className="bg-green-600 hover:bg-green-700 text-white px-3 py-1.5 rounded text-sm flex items-center space-x-1"
                >
                  <Download className="w-4 h-4" />
                  <span>Download</span>
                </button>
              </div>
            </div>

            {/* Score Comparison */}
            <div className="grid grid-cols-2 gap-4 mb-3">
              <div className="bg-white p-3 rounded border">
                <div className="text-xs text-gray-600 mb-1">Previous Score</div>
                <div className={`text-2xl font-bold ${getScoreColor(scores.overall_score)}`}>
                  {scores.overall_score}%
                </div>
              </div>
              <div className="bg-white p-3 rounded border">
                <div className="text-xs text-gray-600 mb-1">New Score</div>
                <div className={`text-2xl font-bold ${getScoreColor(newScores.overall_score)}`}>
                  {newScores.overall_score}%
                </div>
                {newScores.overall_score > scores.overall_score && (
                  <div className="text-xs text-green-600 font-semibold mt-1">
                    +{(newScores.overall_score - scores.overall_score).toFixed(1)}% improvement! 🎉
                  </div>
                )}
              </div>
            </div>

            {/* Enhanced Score Breakdown */}
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div className="bg-white p-2 rounded">
                <div className="text-gray-600">Skills</div>
                <div className="font-semibold">
                  {scores.skill_match_score}% → {newScores.skill_match_score}%
                </div>
              </div>
              <div className="bg-white p-2 rounded">
                <div className="text-gray-600">Experience</div>
                <div className="font-semibold">
                  {scores.experience_match_score}% → {newScores.experience_match_score}%
                </div>
              </div>
              <div className="bg-white p-2 rounded">
                <div className="text-gray-600">Keywords</div>
                <div className="font-semibold">
                  {scores.keyword_match_score}% → {newScores.keyword_match_score}%
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Resume Content */}
          {showEnhancedResume && (
            <div className="bg-white border rounded-lg p-4 max-h-96 overflow-y-auto">
              <h5 className="font-semibold mb-3 flex items-center">
                <FileText className="w-4 h-4 mr-2" />
                Enhanced Resume
              </h5>
              <pre className="whitespace-pre-wrap text-sm text-gray-700 font-sans">
                {enhancedResume}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}