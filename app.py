
import streamlit as st
import pytesseract
import cv2
import numpy as np
from sympy import sympify
from PIL import Image
from io import BytesIO
import logging

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("debug.log"), logging.StreamHandler()]
)

<<<<<<< HEAD
# Clean up common OCR mistakes
def clean_ocr_text(text):
    logging.debug(f"Raw OCR text before cleanup: {text}")
    replacements = {
        't': '+', 'T': '+',
        's': '5', 'S': '5',
        'l': '1', 'I': '1',
        'O': '0', '|': '1',
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    logging.debug(f"OCR text after cleanup: {text}")
    return text

=======
# Normalize OCR results and compare math expressions more flexibly
>>>>>>> parent of a4bf5a5 (still troubleshooting OCR issues)
def parse_equation(text):
    text = text.replace(' ', '')  # Remove all whitespace
    if '=' in text:
        left, right = text.split('=', 1)
        return left.strip(), right.strip()
    return text.strip(), None

def solve_expression(expr):
    try:
        result = str(sympify(expr))
        return result
    except Exception as e:
        logging.warning(f"Failed to solve expression '{expr}': {e}")
        return None

def is_answer_correct(expected, student_answer):
    try:
        return sympify(expected) == sympify(student_answer)
    except Exception as e:
        logging.warning(f"Error comparing answers: {expected} vs {student_answer}: {e}")
        return False

def grade_and_overlay(image_pil):
    logging.info("Starting grading process.")
    image_cv = np.array(image_pil.convert('RGB'))
    results_img = image_cv.copy()
    data = pytesseract.image_to_data(image_cv, config='--psm 6', output_type=pytesseract.Output.DICT)

    n_boxes = len(data['level'])
    total = 0
    correct = 0

    for i in range(n_boxes):
        text = data['text'][i].strip().replace(' ', '')
        if '=' in text and any(c.isdigit() for c in text):
            logging.debug(f"Equation found: {text}")
            expr, student_answer = parse_equation(text)
            expected = solve_expression(expr)
            if expected is not None and student_answer is not None:
                total += 1
                if is_answer_correct(expected, student_answer):
                    correct += 1
                    color = (0, 180, 0)
                    tag = "✓"
                else:
                    color = (0, 0, 255)
                    tag = f"✗ ({expected})"

                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.putText(results_img, tag, (x + w + 10, y + h - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

<<<<<<< HEAD
                logging.info(f"OCR: '{raw_text}' → Expr: '{expr}' | Student: '{student_answer}' | Expected: '{expected}' | Match: {match}")

=======
>>>>>>> parent of a4bf5a5 (still troubleshooting OCR issues)
    score = int((correct / total) * 100) if total > 0 else 0
    logging.info(f"Grading complete. Score: {score} / 100")
    return results_img, score

def convert_to_downloadable(image_cv):
    img_pil = Image.fromarray(image_cv)
    buf = BytesIO()
    img_pil.save(buf, format="PNG")
    buf.seek(0)
    return buf

# --- Streamlit UI ---
st.title("Graded Math Worksheet Solver with Debug Logging")

uploaded_file = st.file_uploader("Upload a worksheet image (JPG/PNG)", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Original Worksheet", use_container_width=True)

    with st.spinner("Grading worksheet..."):
        result_img, score = grade_and_overlay(image)
        st.subheader(f"Score: {score} / 100")
        st.image(result_img, channels="RGB", use_container_width=True)

        # Download Button
        st.subheader("Download Graded Worksheet")
        downloadable = convert_to_downloadable(result_img)
        st.download_button("Download Image", downloadable, file_name="graded_worksheet.png", mime="image/png")
