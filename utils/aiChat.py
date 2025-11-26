"""
AI Chat Utility Module
Handles DeepSeek API integration for AI chat functionality
"""

import os
from openai import OpenAI

# DeepSeek API configuration - read directly from environment variables
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
DEEPSEEK_BASE_URL = 'https://api.deepseek.com'
DEEPSEEK_MODEL = 'deepseek-chat'

# System prompt for Hong Kong history context
SYSTEM_PROMPT = """You are a helpful AI assistant specializing in Hong Kong's history, culture, and historic places. 
You help users explore and learn about Hong Kong's rich heritage, including:
- Historic streets and buildings
- Cultural landmarks and their significance
- Historical events and transformations
- Architectural heritage
- Local stories and memories

Be conversational, informative, and engaging. If you don't know something specific, acknowledge it and provide general context when possible.
Always respond in a friendly and helpful manner."""


def get_ai_response(user_message: str, conversation_history: list = None) -> dict:
    """
    Send a message to DeepSeek API and get AI response.
    
    Parameters:
        user_message (str): The user's message
        conversation_history (list): List of previous messages in format:
            [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    
    Returns:
        dict: Response dictionary with keys:
            - "success" (bool): Whether the request was successful
            - "message" (str): AI response message or error message
            - "error" (str, optional): Error details if success is False
    """
    if not DEEPSEEK_API_KEY:
        return {
            "success": False,
            "message": "AI chat is not configured. Please set DEEPSEEK_API_KEY environment variable.",
            "error": "Missing API key"
        }
    
    try:
        # Initialize OpenAI client with DeepSeek endpoint
        client = OpenAI(
            api_key=DEEPSEEK_API_KEY,
            base_url=DEEPSEEK_BASE_URL
        )
        
        # Build messages list
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add conversation history if provided
        if conversation_history:
            # Limit to last 10 messages to manage context window
            recent_history = conversation_history[-10:] if len(conversation_history) > 10 else conversation_history
            messages.extend(recent_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Make API request
        response = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=messages,
            temperature=1.0,
            max_tokens=1000
        )
        
        # Extract AI response
        ai_message = response.choices[0].message.content
        
        return {
            "success": True,
            "message": ai_message
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Sorry, I encountered an error: {str(e)}",
            "error": str(e)
        }

