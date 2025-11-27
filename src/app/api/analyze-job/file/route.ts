// src/app/api/analyze-job/file/route.ts
import { NextRequest, NextResponse } from 'next/server';

const PYTHON_SERVICE_URL = process.env.PYTHON_SERVICE_URL || 'http://localhost:5000';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file');

    if (!file || !(file instanceof File)) {
      return NextResponse.json(
        { error: 'No file uploaded' },
        { status: 400 }
      );
    }

    console.log('Received job description file:', file.name, file.type, file.size, 'bytes');

    // Forward file to Python service
    const pythonFormData = new FormData();
    pythonFormData.append('file', file);

    console.log('Forwarding file to Python service...');

    const response = await fetch(`${PYTHON_SERVICE_URL}/analyze-job/file`, {
      method: 'POST',
      body: pythonFormData,
    });

    console.log('Python service response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Python service error:', errorText);
      throw new Error(`Python service returned ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log('Python service result received');

    return NextResponse.json(result);
  } catch (error) {
    console.error('Job file analysis error:', error);
    
    // Provide more specific error messages
    let errorMessage = 'Failed to analyze job description file';
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
