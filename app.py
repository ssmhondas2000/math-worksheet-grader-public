
import streamlit as st
import pytesseract
import cv2
import numpy as np
from sympy import sympify
from PIL import Image
from io import BytesIO

def parse_equation(text):
    if '=' in text:
        left, right = text.split('=')
        expr = left.strip()
        student_answer = right.strip()
        return expr, student_answer
    return text.strip(), None

def solve_expression(expr):
    try:
        result = str(sympify(expr))
        return result
    except Exception:
        return None

def grade_and_overlay(image_pil):
    image_cv = np.array(image_pil.convert('RGB'))
    results_img = image_cv.copy()
    data = pytesseract.image_to_data(image_cv, config='--psm 6', output_type=pytesseract.Output.DICT)
    
    n_boxes = len(data['level'])
    total = 0
    correct = 0

    for i in range(n_boxes):
        text = data['text'][i].strip()
        if any(c.isdigit() for c in text) and '=' in text:
            expr, student_answer = parse_equation(text)
            expected = solve_expression(expr)
            if expected is not None:
                total += 1
                is_correct = expected == student_answer
                if is_correct:
                    correct += 1
                    color = (0, 180, 0)
                    tag = "✓"
                else:
                    color = (0, 0, 255)
                    tag = f"✗ ({expected})"

                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                cv2.putText(results_img, tag, (x + w + 10, y + h - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

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
    st.image(image, caption="Original Worksheet", use_column_width=True)

    with st.spinner("Grading worksheet..."):
        result_img, score = grade_and_overlay(image)
        st.subheader(f"Score: {score} / 100")
        st.image(result_img, channels="RGB", use_column_width=True)

        # Download Button
        st.subheader("Download Graded Worksheet")
        downloadable = convert_to_downloadable(result_img)
        st.download_button("Download Image", downloadable, file_name="graded_worksheet.png", mime="image/png")
