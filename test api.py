# from google import genai


# client = genai.Client(api_key="AIzaSyAkkVYdqAJTc8UiR8KrkuMe07skBlF0Nb4")

# response = client.models.generate_content(
#     model="gemini-2.5-flash",
#     contents=input().strip()
# )
# print(response.text, end=" ", flush=True)

from google import genai
from google.genai import types


client = genai.Client(api_key="AIzaSyAkkVYdqAJTc8UiR8KrkuMe07skBlF0Nb4")

prompt = input("Enter your prompt: ")

try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            #max_output_tokens=200,
            temperature=0.5,
        )
    )
    print("\n--- Response ---\n")
    print(response.text)

except Exception as e:
    print("\n❌ Error occurred:")
    print(e)

# from openai import OpenAI

# client = OpenAI(
#     api_key="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",
#     base_url="https://api.groq.com/openai/v1",
# )

# response = client.responses.create(
#     input=input().strip(),
#     model="openai/gpt-oss-120b",
# )
# print(response.output_text)
'''


# '''
# from groq import Groq
# AIzaSyAkkVYdqAJTc8UiR8KrkuMe07skBlF0Nb4
# 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
# client = Groq(api_key="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")

# resp = client.chat.completions.create(
#     model="meta-llama/llama-guard-4-12b",
#     messages=[{"role": "user", "content": input().strip()}]
# )

# print(resp.choices[0].message["content"])

# '''
# import os
# print("Key:", os.getenv("GROQ_API_KEY"))

