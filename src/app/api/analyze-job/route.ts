// src/app/api/analyze-job/route.ts
import { NextRequest, NextResponse } from 'next/server';

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const { job_description } = await request.json();

    if (!job_description) {
      return NextResponse.json(
        { error: 'Job description is required' },
        { status: 400 }
      );
    }

    console.log('Forwarding job description to Python service...');

    // Forward to Python service
    const response = await fetch(`${PYTHON_SERVICE_URL}/analyze-job`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ job_description }),
    });

    console.log('Python service response status:', response.status);

    if (!response.ok) {
      throw new Error(`Python service returned ${response.status}: ${response.statusText}`);
    }

    const result = await response.json();
    console.log('Python service result:', result);

    return NextResponse.json(result);
  } catch (error) {
    console.error('Job analysis error:', error);
    
    // Provide more specific error messages
    let errorMessage = 'Failed to analyze job description';
    if (error instanceof Error) {
      if (error.message.includes('fetch failed') || error.message.includes('ECONNREFUSED')) {
        errorMessage = 'Cannot connect to analysis service. Please make sure the Python backend is running on port 5000.';
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