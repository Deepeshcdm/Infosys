import tkinter as tk
from tkinter import filedialog
import base64

def pick_image_and_convert():
    root = tk.Tk()
    root.withdraw()  # hide the useless empty window

    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[
            ("Image files", "*.png *.jpg *.jpeg *.webp *.bmp"),
            ("All files", "*.*")
        ]
    )

    if not file_path:
        return None  # user chickened out

    with open(file_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode("utf-8")

    return encoded

# usage
b64_image = pick_image_and_convert()
print(b64_image)
