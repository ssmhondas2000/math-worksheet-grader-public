
import streamlit as st
import pytesseract
import cv2
import numpy as np
from sympy import sympify
from PIL import Image
from io import BytesIO

# Clean up common OCR mistakes
def clean_ocr_text(text):
    replacements = {
        't': '+', 'T': '+',
        's': '5', 'S': '5',
        'l': '1', 'I': '1',
        'O': '0', '|': '1',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text

def parse_equation(text):
    text = text.replace(' ', '')
    text = clean_ocr_text(text)
    if '=' in text:
        left, right = text.split('=', 1)
        return left.strip(), right.strip()
    return text.strip(), None

def solve_expression(expr):
    try:
        result = str(sympify(expr))
        return result
    except Exception:
        return None

def is_answer_correct(expected, student_answer):
    try:
        return sympify(expected) == sympify(student_answer)
    except Exception:
        return False

def grade_and_overlay(image_pil):
    image_cv = np.array(image_pil.convert('RGB'))
    results_img = image_cv.copy()
    data = pytesseract.image_to_data(image_cv, config='--psm 5', output_type=pytesseract.Output.DICT)

    n_boxes = len(data['level'])
    total = 0
    correct = 0

    for i in range(n_boxes):
        raw_text = data['text'][i].strip()
        text = clean_ocr_text(raw_text.replace(' ', ''))

        if '=' in text and any(c.isdigit() for c in text):
            expr, student_answer = parse_equation(text)
            expected = solve_expression(expr)
            if expected and student_answer:
                total += 1
                match = is_answer_correct(expected, student_answer)
                correct += int(match)

                color = (0, 180, 0) if match else (255, 0, 0)
                tag = "✓" if match else f"✗ ({expected})"

                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.putText(results_img, tag, (x + w - 300, y + h + 40),
                            cv2.FONT_HERSHEY_SIMPLEX, 2.0, color, 5)

                # Debug: show what was read
                print(f"OCR: '{raw_text}' → Expr: '{expr}' | Student: '{student_answer}' | Expected: '{expected}' | Match: {match}")

    score = int((correct / total) * 100) if total > 0 else 0
    return results_img, score

def convert_to_downloadable(image_cv):
    img_pil = Image.fromarray(image_cv)
    buf = BytesIO()
    img_pil.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- Streamlit UI ---
st.title("Graded Math Worksheet Solver")

uploaded_file = st.file_uploader("Upload a worksheet image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Worksheet", use_container_width=True)

    with st.spinner("Grading worksheet..."):
        result_img, score = grade_and_overlay(image)
        st.subheader(f"Score: {score} / 100")
        st.image(result_img, channels="RGB", use_container_width=True)

        st.subheader("Download Graded Worksheet")
        downloadable = convert_to_downloadable(result_img)
        st.download_button("Download Image", downloadable, file_name="graded_worksheet.png", mime="image/png")
