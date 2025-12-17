# import tkinter as tk
# from tkinter import filedialog
# import base64
# import requests
# import json

# API_URL = "http://localhost:11434/api/chat"
# MODEL_NAME = "deepseek-ocr:3b"


# def pick_image():
#     root = tk.Tk()
#     root.withdraw()

#     file_path = filedialog.askopenfilename(
#         title="Select an image",
#         filetypes=[
#             ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
#             ("All files", "*.*")
#         ]
#     )
#     return file_path


# def image_to_base64(path):
#     with open(path, "rb") as f:
#         return base64.b64encode(f.read()).decode("utf-8")


# def send_request(prompt,base64_image):
#     payload = {
#         "model": MODEL_NAME,
#         "messages": [
#             {
#                 "role": "user",
#                 "content": prompt,
#                 "images": [base64_image]
#             }
#         ],
#         "stream": False
#     }

#     headers = {"Content-Type": "application/json"}

#     response = requests.post(API_URL, headers=headers, data=json.dumps(payload))
#     response.raise_for_status()
#     return response.json()


# def main():
#     prompt = input("Enter your prompt: ").strip()
#     image_path = pick_image()
#     if not image_path:
#         print("No image selected. Program sulks and exits.")
#         return

#     base64_img = image_to_base64(image_path)
#     result = send_request(prompt,base64_img)

#     # OUTPUT: only the content value
#     print(result["message"]["content"])


# if __name__ == "__main__":
#     main()

import tkinter as tk
from tkinter import filedialog
import base64
import requests
import json

API_URL = "http://localhost:11434/api/chat"
MODEL_NAME = "deepseek-ocr:3b"


def pick_image():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("All files", "*.*")
        ]
    )


def image_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def send_request_stream(prompt, base64_image):
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt,
                "images": [base64_image]
            }
        ],
        "stream": True
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(
        API_URL,
        headers=headers,
        json=payload,
        stream=True
    )
    response.raise_for_status()

    # Stream and print only the assistant content
    for line in response.iter_lines():
        if not line:
            continue

        data = json.loads(line.decode("utf-8"))

        if "message" in data and "content" in data["message"]:
            print(data["message"]["content"], end="", flush=True)

        if data.get("done"):
            break


def main():
    prompt = input("Enter your prompt: ").strip()
    image_path = pick_image()

    if not image_path:
        print("No image selected. Exiting.")
        return

    base64_img = image_to_base64(image_path)
    send_request_stream(prompt, base64_img)


if __name__ == "__main__":
    main()
