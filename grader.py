
import pytesseract
import cv2
import numpy as np
from sympy import sympify

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
    except:
        return None

def is_answer_correct(expected, student_answer):
    try:
        return sympify(expected) == sympify(student_answer)
    except:
        return False

def preprocess_image(image_path):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)
    _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh

def grade_worksheet(image_path):
    image = preprocess_image(image_path)
    custom_config = r'--oem 3 --psm 6'
    raw_text = pytesseract.image_to_string(image, config=custom_config)

    print("=== OCR RAW OUTPUT ===")
    print(raw_text)
    print("\n=== ANALYZED MATH PROBLEMS ===")

    total = 0
    correct = 0

    for line in raw_text.splitlines():
        line = line.strip()
        if '=' in line and any(c.isdigit() for c in line):
            expr, student_answer = parse_equation(line)
            expected = solve_expression(expr)
            if expected and student_answer:
                total += 1
                is_correct = is_answer_correct(expected, student_answer)
                correct += int(is_correct)
                print(f"Read: {line}")
                print(f" → Interpreted: {expr} = {student_answer}")
                print(f" → Expected: {expected} | {'✓' if is_correct else '✗'}\n")

    grade = int((correct / total) * 100) if total > 0 else 0
    print(f"Final Grade: {grade}/100")

# Example usage
grade_worksheet("IMG_9738.jpg")  # Change this to your image filename
