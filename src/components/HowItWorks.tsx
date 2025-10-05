// components/HowItWorks.jsx
'use client';

import { useInView } from 'framer-motion';
import { useRef } from 'react';
import { 
  FileText, 
  ClipboardList, 
  Sparkles, 
  BarChart3, 
  Download,
  User,
  Target,
  CheckCircle,
  Zap,
  LucideIcon
} from 'lucide-react';
import CTA from './CTX'; 

// Define TypeScript interface for step object
interface Step {
  step: string;
  title: string;
  description: string;
  icon: LucideIcon;
}

// Define props interface for StepCard component
interface StepCardProps {
  step: Step;
  index: number;
  totalSteps: number;
}

// Separate component defined outside with proper typing
function StepCard({ step, index, totalSteps }: StepCardProps) {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: '-50px' });

  return (
    <div 
      ref={ref}
      className="relative group"
      style={{
        transform: isInView ? 'none' : 'translateY(50px)',
        opacity: isInView ? 1 : 0,
        transition: `all 0.6s cubic-bezier(0.17, 0.55, 0.55, 1) ${index * 0.1}s`
      }}
    >
      {/* Mobile connecting line */}
      {index < totalSteps - 1 && (
        <div className="md:hidden absolute top-12 left-1/2 w-0.5 h-8 bg-gray-200 transform -translate-x-1/2"></div>
      )}

      <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100 hover:shadow-lg transition-all duration-300 group-hover:transform group-hover:scale-105 group-hover:border-primary/20 h-full flex flex-col items-center text-center">
        {/* Step Number with Gradient */}
        <div className="relative mb-4">
          <div className="w-16 h-16 bg-background-icons text-white rounded-full flex items-center justify-center text-xl font-bold shadow-lg">
            <step.icon className="w-7 h-7" />
          </div>
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-accent text-white rounded-full flex items-center justify-center text-xs font-bold">
            {step.step}
          </div>
        </div>

        {/* Content */}
        <h3 className="text-lg font-semibold text-gray-900 mb-3 leading-tight">
          {step.title}
        </h3>
        <p className="text-gray-600 text-sm leading-relaxed flex-grow">
          {step.description}
        </p>

        {/* Hover Indicator */}
        <div className="w-8 h-1 bg-gradient-to-r from-primary to-secondary rounded-full mt-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
      </div>
    </div>
  );
}

export default function HowItWorks() {
  const steps: Step[] = [
    {
      step: '1',
      title: 'Create Your Profile',
      description: 'Upload your resume and tell us about your skills, experience, and career goals.',
      icon: User 
    },
    {
      step: '2',
      title: 'Upload Job Description',
      description: 'Provide the job description for the position you want to apply for.',
      icon: ClipboardList
    },
    {
      step: '3',
      title: 'AI Optimization',
      description: 'Get AI-powered suggestions to tailor your resume and cover letter.',
      icon: Sparkles
    },
    {
      step: '4',
      title: 'View Match Score',
      description: 'Get a percentage score comparing your resume with the job requirements.',
      icon: BarChart3
    },
    {
      step: '5',
      title: 'Download & Customize',
      description: 'Download your cover letter or regenerate for better results.',
      icon: Download
    }
  ];

  return (
    <section id="how-it-works" className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <span className="inline-block px-4 py-1 bg-blue-100 text-primary rounded-full text-sm font-medium mb-4">
            Simple Process
          </span>
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            How It Works
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Get from job search to job offer in 5 simple steps with our AI-powered assistant
          </p>
        </div>

        <div className="relative">
          {/* Connecting line for desktop */}
          <div className="hidden lg:block absolute top-20 left-0 right-0 h-0.5 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20"></div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-5 gap-8 lg:gap-6">
            {steps.map((step, index) => (
              <StepCard 
                key={index} 
                step={step} 
                index={index} 
                totalSteps={steps.length}
              />
            ))}
          </div>
        </div>
        <div className='mt-16'>
          <CTA/>
        </div>
      </div>
    </section>
  );
}