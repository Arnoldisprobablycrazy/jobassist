// src/app/api/generate-cover-letter/route.ts
import { NextRequest, NextResponse } from 'next/server';

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const { resume_data, job_data, tone = 'professional', preferences = {} } = await request.json();

    if (!resume_data || !job_data) {
      return NextResponse.json(
        { error: 'Resume data and job data are required' },
        { status: 400 }
      );
    }

    console.log('Generating cover letter...');
    console.log('Job:', job_data.title || 'Unknown');
    console.log('Tone:', tone);

    // Merge tone into preferences
    const enhancedPreferences = {
      ...preferences,
      tone: tone
    };

    // Try AI endpoint first (if available), then fallback to basic
    let response = await fetch(`${PYTHON_SERVICE_URL}/generate-cover-letter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        resume_data, 
        job_data, 
        tone,
        preferences: enhancedPreferences 
      }),
    });

    console.log('Python service response status:', response.status);

    if (!response.ok) {
      const errorData = await response.json();
      console.error('Cover letter generation failed:', errorData);
      
      // Provide helpful error message
      let errorMessage = errorData.error || 'Cover letter generation failed';
      if (errorMessage.includes('ECONNREFUSED') || errorMessage.includes('fetch failed')) {
        errorMessage = 'Cannot connect to AI service. Please ensure the Python backend is running on port 5000.';
      }
      
      return NextResponse.json(
        { 
          success: false,
          error: errorMessage 
        },
        { status: response.status }
      );
    }

    const result = await response.json();
    console.log('Cover letter generated successfully');

    // Ensure we have the expected response structure
    if (result.success) {
      return NextResponse.json(result);
    } else {
      return NextResponse.json({
        success: false,
        error: result.error || 'Unknown error during generation'
      }, { status: 500 });
    }
    
  } catch (error) {
    console.error('Cover letter generation error:', error);
    
    let errorMessage = 'Failed to generate cover letter';
    if (error instanceof Error) {
      if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
        errorMessage = 'Cannot connect to AI service. Please ensure the Python backend is running on port 5000.';
      } else {
        errorMessage = error.message;
      }
    }
    
    return NextResponse.json(
      { 
        success: false,
        error: errorMessage 
      },
      { status: 500 }
    );
  }
}