from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

key = os.getenv("OPENAI_API_KEY")
print(f"Key loaded: {key[:10]}...")

try:
    client = OpenAI(api_key=key)
    print("Testing gpt-5-nano...")
    # Using the standard 'chat.completions.create' because 'responses.create' in user prompt
    # might be a hallucination or beta SDK. I will try standard first.
    # If standard fails, I will try exactly what user provided.
    
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[{"role": "user", "content": "write a haiku about ai"}],
        store=True,
    )
    print(response.choices[0].message.content)
    print("✅ Success!")
except Exception as e:
    print(f"❌ Error: {e}")
    
    print("\nAttempting user's exact syntax (responses.create)...")
    try:
        response = client.responses.create(
          model="gpt-5-nano",
          input="write a haiku about ai",
          store=True,
        )
        print(response.output_text)
        print("✅ Success with responses.create!")
    except Exception as e2:
        print(f"❌ Error with responses.create: {e2}")
