# math_checker_app_with_ocr_preview.py
import streamlit as st
import pytesseract
import cv2
import numpy as np
from PIL import Image
import re
import io

# Optional: set Tesseract path
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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

def extract_questions(image):
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    ocr_data = pytesseract.image_to_data(img_cv, output_type=pytesseract.Output.DICT)
    ocr_text_raw = pytesseract.image_to_string(img_cv)

    found_items = []
    for i in range(len(ocr_data["text"])):
        text = ocr_data["text"][i].strip()
        if "=" in text:
            question, user_answer = parse_equation(text)
            if question:
                found_items.append({
                    "text": text,
                    "question": question,
                    "user_answer": user_answer,
                    "box": (ocr_data["left"][i], ocr_data["top"][i], ocr_data["width"][i], ocr_data["height"][i])
                })
    return img_cv, found_items, ocr_text_raw

def grade_answers(answer_list):
    graded = []
    correct = 0
    for item in answer_list:
        question = item["question"]
        user_answer = item["user_answer"]
        correct_answer = correct_answers.get(question)
        is_correct = correct_answer == user_answer
        graded.append({**item, "is_correct": is_correct, "correct_answer": correct_answer})
        if is_correct:
            correct += 1
    percent = (correct / len(graded)) * 100 if graded else 0
    return graded, percent

def draw_boxes(img, graded_answers):
    for item in graded_answers:
        x, y, w, h = item["box"]
        color = (0, 255, 0) if item["is_correct"] else (0, 0, 255)
        cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
    return img

# Streamlit UI
st.title("📄 Math Worksheet Grader")
uploaded_file = st.file_uploader("Upload worksheet image", type=["jpg", "jpeg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Worksheet", use_container_width=True)

    with st.spinner("Reading and grading answers..."):
        img_cv, found_items, ocr_text_raw = extract_questions(image)
        graded_list, score = grade_answers(found_items)

    st.markdown(f"### 🧮 Grade: **{score:.2f}%**")

    # ✅ OCR Detected Raw Text
    with st.expander("📄 See OCR Detected Text"):
        st.text(ocr_text_raw)

    # ✅ Manual Review
    st.markdown("### ✏️ Review and Edit Answers")
    updated_items = []
    for idx, item in enumerate(graded_list):
        st.markdown(f"**Q{idx + 1}: {item['question']} = ?**")
        updated_answer = st.text_input("Your Answer", value=item["user_answer"], key=f"answer_{idx}")
        updated_items.append({**item, "user_answer": updated_answer})

    if st.button("✅ Recalculate Grade"):
        graded_list, score = grade_answers(updated_items)
        img_cv = draw_boxes(img_cv, graded_list)
        st.markdown(f"### 🔁 Updated Grade: **{score:.2f}%**")

    # ✅ Display Graded Image
    st.image(cv2.cvtColor(draw_boxes(img_cv, graded_list), cv2.COLOR_BGR2RGB), caption="Graded Worksheet", use_container_width=True)

    # ✅ Download Results
    st.markdown("### 💾 Download Results")
    result_text = f"Math Worksheet Grading Results\nScore: {score:.2f}%\n\n"
    for i, item in enumerate(graded_list):
        status = "✅ Correct" if item["is_correct"] else "❌ Incorrect"
        result_text += f"{i + 1}. {item['question']} = {item['user_answer']} ({status}, Correct: {item['correct_answer']})\n"

    st.download_button(
        label="📥 Download Results as .txt",
        data=result_text,
        file_name="worksheet_results.txt",
        mime="text/plain"
    )
