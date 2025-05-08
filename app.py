# math_checker_app.py
import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re

# Optional: Update path to your tesseract executable
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Sample correct answers
correct_answers = {
    "1 + 1": "2",
    "2 + 2": "4",
    "5 - 3": "2",
    "6 / 2": "3",
    "3 x 3": "9",
    "10 - 7": "3"
}

def parse_equation(text):
    match = re.match(r'(.+?)\s*=\s*(.+)', text)
    if match:
        question = match.group(1).strip()
        answer = match.group(2).strip()
        return question, answer
    return None, None

def grade_image(image):
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    results = pytesseract.image_to_data(img_cv, output_type=pytesseract.Output.DICT)

    correct = 0
    total = 0

    for i in range(len(results["text"])):
        text = results["text"][i].strip()
        if "=" in text:
            question, user_answer = parse_equation(text)
            if question in correct_answers:
                is_correct = user_answer == correct_answers[question]
                total += 1
                if is_correct:
                    correct += 1
                    color = (0, 255, 0)  # Green
                else:
                    color = (0, 0, 255)  # Red

                (x, y, w, h) = (results["left"][i], results["top"][i], results["width"][i], results["height"][i])
                cv2.rectangle(img_cv, (x, y), (x + w, y + h), color, 2)

    percent = (correct / total) * 100 if total else 0
    return img_cv, percent

# Streamlit UI
st.title("Math Worksheet Grader")
uploaded_file = st.file_uploader("Upload worksheet image", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Worksheet", use_container_width=True)

    with st.spinner("Grading..."):
        graded_img, score = grade_image(image)

    st.markdown(f"### 🧮 Grade: **{score:.2f}%**")
    st.image(cv2.cvtColor(graded_img, cv2.COLOR_BGR2RGB), caption="Graded Worksheet", use_container_width=True)
