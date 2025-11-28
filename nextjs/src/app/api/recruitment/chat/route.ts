import { NextRequest, NextResponse } from 'next/server';

const RECRUITMENT_BACKEND_URL = process.env.RECRUITMENT_BACKEND_URL || 'http://localhost:8100';

export async function POST(request: NextRequest) {
  try {
    const { userId, message, sessionId } = await request.json();
    
    let currentSessionId = sessionId;
    
    // Create session if needed
    if (!currentSessionId) {
      const sessionResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/sessions`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          app_name: 'recruitment_system',
          user_id: userId || 'recruiter_1',
          state: { topic: 'recruiting' }
        })
      });
      
      const session = await sessionResponse.json();
      currentSessionId = session.id;
    }
    
    // Send message to agent
    const agentResponse = await fetch(`${RECRUITMENT_BACKEND_URL}/agent`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_name: 'recruitment_system',
        user_id: userId || 'recruiter_1',
        session_id: currentSessionId,
        new_message: {
          role: 'user',
          parts: [{ text: message }]
        },
        streaming: false
      })
    });
    
    const agentData = await agentResponse.json();
    
    // Extract text response from agent
    const responseText = agentData.events?.[0]?.parts?.[0]?.text || 'No response';
    
    return NextResponse.json({
      response: responseText,
      session_id: currentSessionId
    });
    
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: error instanceof Error ? error.message : 'Internal server error' },
      { status: 500 }
    );
  }
}

