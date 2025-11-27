import { NextRequest, NextResponse } from 'next/server';

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const { resume_text, job_text, recommendations } = await request.json();

    if (!resume_text || !job_text) {
      return NextResponse.json(
        { error: 'Resume text and job text are required' },
        { status: 400 }
      );
    }

    // Forward to Python service
    const response = await fetch(`${PYTHON_SERVICE_URL}/enhance-resume`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ 
        resume_text, 
        job_text,
        recommendations: recommendations || {}
      }),
    });

    const result = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: result.error || 'Resume enhancement failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Resume enhancement error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
