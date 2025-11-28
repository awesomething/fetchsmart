import { NextRequest, NextResponse } from 'next/server';

const RECRUITMENT_BACKEND_URL = process.env.RECRUITMENT_BACKEND_URL || 'http://localhost:8100';

export async function POST(request: NextRequest) {
  try {
    const { userId, query, limit = 10 } = await request.json();
    
    // Create A2A session with recruitment_backend
    const sessionResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        state: { topic: 'recruiting' }
      })
    });
    
    if (!sessionResponse.ok) {
      throw new Error('Failed to create session');
    }
    
    const session = await sessionResponse.json();
    
    // Send query to agent (or default to show first candidates)
    const message = query || `Show me the first ${limit} candidates from the database`;
    
    const agentResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/agent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        session_id: session.id,
        new_message: {
          role: 'user',
          parts: [{ text: message }]
        },
        streaming: false
      })
    });
    
    if (!agentResponse.ok) {
      throw new Error('Failed to get agent response');
    }
    
    const agentData = await agentResponse.json();
    
    // Extract response text and parse candidate data
    const responseText = agentData.events?.[0]?.parts?.[0]?.text || '';
    
    return NextResponse.json({
      success: true,
      data: agentData,
      response_text: responseText,
      session_id: session.id
    });
    
  } catch (error) {
    console.error('Recruitment API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}

