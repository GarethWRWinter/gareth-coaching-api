from openai import OpenAI
import os
import json

client = OpenAI()

def generate_coach_notes(summary: dict) -> str:
    prompt = f"""
You are a world-class cycling coach. Based on this ride summary, provide coaching feedback:

Ride Summary:
{json.dumps(summary, indent=2)}

Highlight strengths, areas for improvement, and suggest one training focus for next week.
Keep it short, direct, and motivational.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    return response.choices[0].message.content.strip()
