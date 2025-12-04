from elevenlabs import ElevenLabs
from rag_pipeline import answer_question
import os
from dotenv import load_dotenv

load_dotenv()

client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

def create_university_agent():
    """
    Creates an ElevenLabs conversational AI agent configured as a university assistant.
    The agent can answer questions about university documents using RAG.
    """
    
    # Define the agent's prompt/personality
    agent_prompt = """You are a helpful university assistant helping students with questions about admissions, fees, exams, courses, and campus life.

When a student asks a question:
1. Be friendly and professional
2. Use the search_university_docs function to find relevant information
3. Provide clear, concise answers based on the documents
4. If you don't find information, politely say so and suggest who they might contact

Keep responses conversational and natural for voice interaction."""

    try:
        # Create the conversational agent
        agent = client.conversational_ai.agents.create(
            name="University Assistant",
            conversationConfig={
                "agent": {
                    "prompt": {
                        "prompt": agent_prompt
                    },
                    "firstMessage": "Hello! I'm your university assistant. How can I help you today?",
                    "language": "en"
                },
                "tts": {
                    "voiceId": "21m00Tcm4TlvDq8ikWAM"  # Rachel voice
                }
            }
        )
        
        print(f"✅ Agent created successfully!")
        print(f"Agent ID: {agent.agent_id}")
        return agent.agent_id
        
    except Exception as e:
        print(f"Error creating agent: {e}")
        return None

if __name__ == "__main__":
    agent_id = create_university_agent()
    if agent_id:
        print(f"\n🎉 Your conversational agent is ready!")
        print(f"Save this Agent ID: {agent_id}")
