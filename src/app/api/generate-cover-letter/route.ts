// src/app/api/generate-cover-letter/route.ts
import { NextRequest, NextResponse } from 'next/server';

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const { resume_data, job_data, tone = 'professional' } = await request.json();

    if (!resume_data || !job_data) {
      return NextResponse.json(
        { error: 'Resume data and job data are required' },
        { status: 400 }
      );
    }

    const response = await fetch(`${PYTHON_SERVICE_URL}/generate-cover-letter`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ resume_data, job_data, tone }),
    });

    const result = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: result.error || 'Cover letter generation failed' },
        { status: response.status }
      );
    }

    return NextResponse.json(result);
  } catch (error) {
    console.error('Cover letter generation error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}