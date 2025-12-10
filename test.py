# # import requests
# # import json

# # def ask_ollama():
# #     url = "http://localhost:11434/api/generate"
# #     headers = {"Content-Type": "application/json"}

# #     # ----- Dynamic user inputs -----
# #     model = input("Enter model name (e.g., llama3): ")
# #     prompt = input("Enter your prompt: ")

# #     payload = {
# #         "model": model,
# #         "prompt": prompt
# #     }

# #     response = requests.post(url, headers=headers, data=json.dumps(payload))

# #     print("\n--- Response ---")
# #     print(json.dumps(response.json(), indent=4))

# # if __name__ == "__main__":
# #     ask_ollama()

# import requests
# import json

# def ask_ollama():
#     url = "http://localhost:11434/api/generate"
#     headers = {"Content-Type": "application/json"}

#     model = input("Enter model name (e.g., llama3): ")
#     prompt = input("Enter your prompt: ")

#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": False
#     }

#     response = requests.post(url, headers=headers, data=json.dumps(payload))

#     data = response.json()

#     # Print ONLY the "response" field
#     print("\nAI Response:")
#     print(data.get("response"))

# if __name__ == "__main__":
#     ask_ollama()

#!/usr/bin/env python3
"""
Streamed request to Ollama-like local API and print progressive content.

Requires: requests
    pip install requests
"""

from openai import OpenAI
import requests
import json
from json import JSONDecodeError

API_URL = "http://localhost:11434/api/generate"
HEADERS = {"Content-Type": "application/json"}


def stream_generate(model: str, prompt: str):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": True
    }

    # Make streaming POST request
    with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as resp:
        resp.raise_for_status()

        full_text = []
        try:
            # iter_lines yields each line (separated by newline) from the stream
            for raw_line in resp.iter_lines(decode_unicode=True):
                if not raw_line:
                    continue  # skip keep-alive/newline frames

                line = raw_line.strip()
                # Some servers may send multiple JSON objects concatenated or
                # an event format; attempt to parse each line as JSON.
                try:
                    obj = json.loads(line)
                except JSONDecodeError:
                    # If it's not valid JSON, skip it (or print for debug)
                    # print(f"[DEBUG] non-json chunk: {line}")
                    continue

                # Extract text from the known shapes:
                chunk_text = None
                if "message" in obj and isinstance(obj["message"], dict):
                    chunk_text = obj["message"].get("content")
                elif "response" in obj:  # older / alternate format
                    chunk_text = obj.get("response")

                # Print chunk progressively (no extra newline)
                if chunk_text:
                    print(chunk_text, end="", flush=True)
                    full_text.append(chunk_text)

                # If the server indicates completion, break out
                if obj.get("done") is True:
                    # If final chunk had done true and maybe had other fields (like done_reason)
                    break

        except KeyboardInterrupt:
            print("\n[Interrupted by user]")

        print()  # final newline after progressive printing
        return "".join(full_text)

prompt = input("Enter your prompt: ").strip()
MODEL_OPTIONS = ["gpt-oss-120b", "llama3", "deepseek-r1"]
option = input(f"Enter model name {MODEL_OPTIONS}: ").strip()
if option not in MODEL_OPTIONS:
    print("Invalid model name. Please choose from the available options.")
else:
    if option == "gpt-oss-120b":

        client = OpenAI(
            api_key="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",
            base_url="https://api.groq.com/openai/v1",
        )

        response = client.responses.create(
            input=prompt,
            model="openai/gpt-oss-120b",
            stream=True
        )
        for event in response:
    # If event has .delta and it's an object with .text
            if hasattr(event, "delta"):
                delta = event.delta

                # Case 1: delta is an object with .text attribute
                if hasattr(delta, "text") and delta.text:
                    print(delta.text, end="", flush=True)

                # Case 2: delta itself *is* a string
                elif isinstance(delta, str):
                    print(delta, end="", flush=True)

            # Some models send raw text directly
            elif isinstance(event, str):
                print(event, end="", flush=True)

        # print(response.output_text)
    else:
        print("\n--- Streaming response (press Ctrl+C to stop) ---\n")
        full_response = stream_generate(option, prompt)

        print("\n--- Full accumulated response ---")
        print(full_response)
            

# import requests
# import json
# from json import JSONDecodeError

# API_URL = "http://localhost:11434/api/generate"
# HEADERS = {"Content-Type": "application/json"}


# def stream_generate(model: str, prompt: str):
#     payload = {
#         "model": model,
#         "prompt": prompt,
#         "stream": True
#     }

#     # Make streaming POST request
#     with requests.post(API_URL, headers=HEADERS, json=payload, stream=True) as resp:
#         resp.raise_for_status()

#         full_text = []
#         try:
#             # iter_lines yields each line (separated by newline) from the stream
#             for raw_line in resp.iter_lines(decode_unicode=True):
#                 if not raw_line:
#                     continue  # skip keep-alive/newline frames

#                 line = raw_line.strip()
#                 # Some servers may send multiple JSON objects concatenated or
#                 # an event format; attempt to parse each line as JSON.
#                 try:
#                     obj = json.loads(line)
#                 except JSONDecodeError:
#                     # If it's not valid JSON, skip it (or print for debug)
#                     # print(f"[DEBUG] non-json chunk: {line}")
#                     continue

#                 # Extract text from the known shapes:
#                 chunk_text = None
#                 if "message" in obj and isinstance(obj["message"], dict):
#                     chunk_text = obj["message"].get("content")
#                 elif "response" in obj:  # older / alternate format
#                     chunk_text = obj.get("response")

#                 # Print chunk progressively (no extra newline)
#                 if chunk_text:
#                     print(chunk_text, end="", flush=True)
#                     full_text.append(chunk_text)

#                 # If the server indicates completion, break out
#                 if obj.get("done") is True:
#                     # If final chunk had done true and maybe had other fields (like done_reason)
#                     break

#         except KeyboardInterrupt:
#             print("\n[Interrupted by user]")

#         print()  # final newline after progressive printing
#         return "".join(full_text)


# def main():
#     model = input("Enter model name (e.g., llama3): ").strip() or "llama3"
#     prompt = input("Enter your prompt: ").strip() or "Hello"

#     print("\n--- Streaming response (press Ctrl+C to stop) ---\n")
#     full_response = stream_generate(model, prompt)

#     print("\n--- Full accumulated response ---")
#     print(full_response)


# if __name__ == "__main__":
#     main()
