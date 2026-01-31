import { NextRequest, NextResponse } from 'next/server';

const BACKEND_URL = process.env.BACKEND_URL || 'http://127.0.0.1:5000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    console.log('[Land Registry API] Fetching from:', `${BACKEND_URL}/api/land-registry`);
    console.log('[Land Registry API] Request body:', JSON.stringify(body));
    
    // Forward request to Flask backend
    const response = await fetch(`${BACKEND_URL}/api/land-registry`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });
    
    console.log('[Land Registry API] Response status:', response.status);
    
    if (!response.ok) {
      console.error('[Land Registry API] Backend returned non-OK status:', response.status);
      return NextResponse.json({
        success: false,
        error: `Backend service returned ${response.status}`,
        transactions: [],
        statistics: {}
      });
    }
    
    const data = await response.json();
    console.log('[Land Registry API] Response data:', JSON.stringify(data).substring(0, 200));
    return NextResponse.json(data);
    
  } catch (error) {
    console.error('[Land Registry API] Error:', error);
    return NextResponse.json({
      success: false,
      error: 'Failed to fetch Land Registry data',
      transactions: [],
      statistics: {}
    });
  }
}
