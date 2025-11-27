"""
Agentic Resume Optimizer using ReAct Pattern
Iteratively improves resume through reasoning, action, and reflection
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from job_analyzer import JobAnalyzer, SimilarityCalculator
from resume_parser import ResumeParser


class AgenticResumeOptimizer:
    """
    An autonomous agent that iteratively improves resumes using ReAct pattern:
    1. REASONING: Analyze current state and decide what to improve
    2. ACTION: Apply specific improvements
    3. REFLECTION: Validate if improvement worked, learn from it
    4. RETRY: If failed, try different approach
    """
    
    def __init__(self, ai_service, max_iterations=3, target_score=85):
        self.ai_service = ai_service
        self.job_analyzer = JobAnalyzer()
        self.similarity_calculator = SimilarityCalculator()
        self.resume_parser = ResumeParser()
        self.max_iterations = max_iterations
        self.target_score = target_score
        
        # Agent memory (learns from attempts)
        self.attempt_history = []
        self.successful_strategies = []
        self.failed_strategies = []
    
    def optimize_resume(
        self, 
        resume_text: str, 
        job_text: str, 
        recommendations: Dict = None
    ) -> Dict[str, Any]:
        """
        Main agentic loop: iteratively improve resume until target score or max iterations
        
        Returns:
            {
                'optimized_resume': str,
                'final_score': float,
                'original_score': float,
                'iterations': int,
                'attempt_history': List[Dict],
                'strategy_used': str,
                'reflection': str
            }
        """
        print("\n" + "="*80)
        print(" AGENTIC RESUME OPTIMIZER STARTED")
        print("="*80)
        
        # Initial analysis
        job_analysis = self.job_analyzer.analyze_job_description(job_text)
        original_scores = self.similarity_calculator.calculate_similarity(resume_text, job_text)
        original_score = original_scores.get('overall_score', 0)
        
        print(f"\n Initial Assessment:")
        print(f"   Original Score: {original_score}%")
        print(f"   Target Score: {self.target_score}%")
        print(f"   Gap to Close: {self.target_score - original_score}%")
        
        if original_score >= self.target_score:
            print(f" Already at target! No optimization needed.")
            return {
                'optimized_resume': resume_text,
                'final_score': original_score,
                'original_score': original_score,
                'iterations': 0,
                'attempt_history': [],
                'strategy_used': 'none',
                'reflection': 'Resume already meets target score'
            }
        
        # Initialize agent state
        current_resume = resume_text
        current_score = original_score
        iteration = 0
        
        # AGENTIC LOOP
        while iteration < self.max_iterations and current_score < self.target_score:
            iteration += 1
            
            print(f"\n{'='*80}")
            print(f" ITERATION {iteration}/{self.max_iterations}")
            print(f"{'='*80}")
            
            # STEP 1: REASONING - Analyze and plan
            strategy = self._reason_and_plan(
                current_resume, 
                job_analysis, 
                current_score, 
                iteration
            )
            
            print(f"\n Agent Reasoning:")
            print(f"   Strategy: {strategy['name']}")
            print(f"   Focus: {strategy['focus']}")
            print(f"   Expected Impact: +{strategy['expected_improvement']}%")
            
            # STEP 2: ACTION - Apply improvement
            improved_resume = self._apply_strategy(
                current_resume,
                job_text,
                job_analysis,
                strategy
            )
            
            if not improved_resume:
                print(f" Action failed, skipping iteration")
                self.failed_strategies.append(strategy['name'])
                continue
            
            # STEP 3: REFLECTION - Validate improvement
            new_scores = self.similarity_calculator.calculate_similarity(improved_resume, job_text)
            new_score = new_scores.get('overall_score', 0)
            actual_improvement = new_score - current_score
            
            print(f"\n Results:")
            print(f"   Previous: {current_score}%")
            print(f"   New: {new_score}%")
            print(f"   Actual Change: {actual_improvement:+.1f}%")
            
            # STEP 4: REFLECTION & LEARNING
            reflection = self._reflect_on_attempt(
                strategy,
                actual_improvement,
                strategy['expected_improvement']
            )
            
            print(f"\n Agent Reflection:")
            print(f"   {reflection['assessment']}")
            print(f"   Learning: {reflection['learning']}")
            
            # Record attempt
            attempt_record = {
                'iteration': iteration,
                'strategy': strategy['name'],
                'previous_score': current_score,
                'new_score': new_score,
                'improvement': actual_improvement,
                'reflection': reflection
            }
            self.attempt_history.append(attempt_record)
            
            # DECISION: Keep improvement or revert?
            if actual_improvement > -1:  # Keep if not significantly worse
                current_resume = improved_resume
                current_score = new_score
                
                if actual_improvement > 0:
                    self.successful_strategies.append(strategy['name'])
                    print(f" Keeping improvement")
                else:
                    print(f"  Marginal change, keeping for next iteration")
            else:
                self.failed_strategies.append(strategy['name'])
                print(f" Reverting changes (score decreased too much)")
            
            # Check if target reached
            if current_score >= self.target_score:
                print(f"\n TARGET ACHIEVED! {current_score}% >= {self.target_score}%")
                break
        
        # Final summary
        final_improvement = current_score - original_score
        
        print(f"\n{'='*80}")
        print(f" OPTIMIZATION COMPLETE")
        print(f"{'='*80}")
        print(f"   Iterations Used: {iteration}/{self.max_iterations}")
        print(f"   Original Score: {original_score}%")
        print(f"   Final Score: {current_score}%")
        print(f"   Total Improvement: {final_improvement:+.1f}%")
        print(f"   Successful Strategies: {', '.join(self.successful_strategies) or 'None'}")
        print(f"   Failed Strategies: {', '.join(self.failed_strategies) or 'None'}")
        print(f"{'='*80}\n")
        
        return {
            'optimized_resume': current_resume,
            'final_score': current_score,
            'original_score': original_score,
            'improvement': final_improvement,
            'iterations_used': iteration,
            'max_iterations': self.max_iterations,
            'target_reached': current_score >= self.target_score,
            'attempt_history': self.attempt_history,
            'successful_strategies': self.successful_strategies,
            'failed_strategies': self.failed_strategies,
            'final_reflection': self._generate_final_reflection(original_score, current_score)
        }
    
    def _reason_and_plan(
        self, 
        resume: str, 
        job_analysis: Dict, 
        current_score: float,
        iteration: int
    ) -> Dict[str, Any]:
        """
        REASONING phase: Agent analyzes situation and decides strategy
        """
        # Extract current resume skills
        current_skills = self.resume_parser.extract_skills_dynamically(resume)
        required_skills = job_analysis.get('required_skills', [])
        missing_skills = [s for s in required_skills if s.lower() not in [cs.lower() for cs in current_skills]]
        
        # Analyze what's been tried before
        tried_strategies = [attempt['strategy'] for attempt in self.attempt_history]
        
        # Agent reasoning prompt
        reasoning_prompt = f"""You are an intelligent resume optimization agent. Analyze the situation and decide the BEST strategy for this iteration.

CURRENT SITUATION:
- Current Score: {current_score}%
- Target Score: {self.target_score}%
- Gap: {self.target_score - current_score}%
- Iteration: {iteration}
- Previous Strategies Tried: {', '.join(tried_strategies) if tried_strategies else 'None'}
- Successful Strategies: {', '.join(self.successful_strategies) if self.successful_strategies else 'None'}
- Failed Strategies: {', '.join(self.failed_strategies) if self.failed_strategies else 'None'}

JOB REQUIREMENTS:
- Position: {job_analysis.get('job_title', 'N/A')}
- Required Skills: {', '.join(required_skills[:15])}
- Missing Skills: {', '.join(missing_skills[:10])}

AVAILABLE STRATEGIES:
1. keyword_optimization - Rewrite experience bullets using job keywords
2. skills_emphasis - Reorganize to highlight matching skills
3. professional_summary - Add/improve summary section
4. ats_formatting - Improve structure and formatting
5. experience_expansion - Elaborate on relevant experiences

INSTRUCTIONS:
Based on the gap, previous attempts, and job requirements, choose ONE strategy that will be most effective NOW.

Respond in JSON format:
{{
    "strategy_name": "chosen_strategy",
    "focus_area": "specific aspect to improve",
    "expected_improvement": estimated_percentage_points,
    "reasoning": "why this strategy now"
}}"""

        try:
            response = self.ai_service.llm.complete(reasoning_prompt)
            plan = json.loads(str(response))
            
            return {
                'name': plan.get('strategy_name', 'keyword_optimization'),
                'focus': plan.get('focus_area', 'general improvement'),
                'expected_improvement': plan.get('expected_improvement', 5),
                'reasoning': plan.get('reasoning', 'Default strategy')
            }
        except Exception as e:
            print(f"  Reasoning failed, using default strategy: {e}")
            # Fallback to simple strategy selection
            if iteration == 1:
                return {
                    'name': 'keyword_optimization',
                    'focus': 'experience rewording',
                    'expected_improvement': 8,
                    'reasoning': 'First iteration - optimize keywords'
                }
            elif 'keyword_optimization' in self.successful_strategies:
                return {
                    'name': 'professional_summary',
                    'focus': 'summary creation',
                    'expected_improvement': 5,
                    'reasoning': 'Keywords worked, now add summary'
                }
            else:
                return {
                    'name': 'skills_emphasis',
                    'focus': 'skills reorganization',
                    'expected_improvement': 6,
                    'reasoning': 'Emphasize matching skills'
                }
    
    def _apply_strategy(
        self,
        resume: str,
        job_text: str,
        job_analysis: Dict,
        strategy: Dict
    ) -> Optional[str]:
        """
        ACTION phase: Apply the chosen strategy
        """
        strategy_name = strategy['name']
        
        # Strategy-specific prompts
        if strategy_name == 'keyword_optimization':
            action_prompt = f"""Rewrite this resume to use more keywords from the job description.

RESUME:
{resume}

JOB KEYWORDS: {', '.join(job_analysis.get('required_skills', [])[:20])}

INSTRUCTIONS:
- Reword experience bullets to include job keywords
- Keep all facts unchanged (companies, dates, education)
- Use action verbs from job description
- Do NOT add fake information

Return ONLY the rewritten resume."""

        elif strategy_name == 'professional_summary':
            action_prompt = f"""Add or improve the professional summary section at the top of this resume.

RESUME:
{resume}

TARGET JOB: {job_analysis.get('job_title', 'Position')}
KEY SKILLS: {', '.join(job_analysis.get('required_skills', [])[:10])}

INSTRUCTIONS:
- Add 2-3 sentence professional summary highlighting relevant experience
- Keep all other content unchanged
- Focus on match to target role

Return ONLY the resume with improved summary."""

        elif strategy_name == 'skills_emphasis':
            action_prompt = f"""Reorganize skills section to emphasize job-relevant skills.

RESUME:
{resume}

REQUIRED SKILLS: {', '.join(job_analysis.get('required_skills', [])[:15])}

INSTRUCTIONS:
- Move matching skills to top of skills section
- Group related skills together
- Keep all facts unchanged

Return ONLY the reorganized resume."""

        elif strategy_name == 'ats_formatting':
            action_prompt = f"""Improve ATS-friendly formatting of this resume.

RESUME:
{resume}

INSTRUCTIONS:
- Use clear section headers (EXPERIENCE, EDUCATION, SKILLS)
- Remove any complex formatting
- Use bullet points consistently
- Keep content unchanged

Return ONLY the reformatted resume."""

        else:  # experience_expansion
            action_prompt = f"""Expand on experiences most relevant to the target job.

RESUME:
{resume}

TARGET JOB: {job_analysis.get('job_title', 'Position')}

INSTRUCTIONS:
- Elaborate on job-relevant experiences with more detail
- Keep facts unchanged, just add more context
- Use keywords from job description

Return ONLY the expanded resume."""

        try:
            response = self.ai_service.llm.complete(action_prompt)
            improved_resume = str(response).strip()
            
            if len(improved_resume) < 100:
                return None
                
            return improved_resume
            
        except Exception as e:
            print(f" Strategy execution failed: {e}")
            return None
    
    def _reflect_on_attempt(
        self,
        strategy: Dict,
        actual_improvement: float,
        expected_improvement: float
    ) -> Dict[str, str]:
        """
        REFLECTION phase: Agent learns from the attempt
        """
        if actual_improvement >= expected_improvement:
            assessment = f" Success! Strategy exceeded expectations"
            learning = f"{strategy['name']} is effective for this type of resume/job match"
        elif actual_improvement > 0:
            assessment = f"  Partial success. Improved but less than expected"
            learning = f"{strategy['name']} has limited impact, may need combination with other strategies"
        elif actual_improvement > -2:
            assessment = f" Minimal impact. Score barely changed"
            learning = f"{strategy['name']} may not be relevant for this job/resume combination"
        else:
            assessment = f" Strategy backfired. Score decreased"
            learning = f"Avoid {strategy['name']} in similar situations"
        
        return {
            'assessment': assessment,
            'learning': learning,
            'success': actual_improvement > 0
        }
    
    def _generate_final_reflection(self, original_score: float, final_score: float) -> str:
        """Generate final reflection on the optimization process"""
        improvement = final_score - original_score
        
        if improvement >= 15:
            return f" Excellent optimization! Improved {improvement:.1f}% through strategic iterations. Successful strategies: {', '.join(self.successful_strategies)}"
        elif improvement >= 5:
            return f" Good optimization. Improved {improvement:.1f}% through careful adjustments. Some strategies worked better than others."
        elif improvement > 0:
            return f"  Modest improvement of {improvement:.1f}%. This resume may already be well-optimized, or the job requirements are very specific."
        else:
            return f"  No improvement achieved. The original resume may already be optimal for this job, or different strategies are needed."
