import cv2
import pytesseract
import re
from sympy import sympify

# If on Windows specify path like:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text(image_path):
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.threshold(gray,150,255,cv2.THRESH_BINARY)[1]
    text = pytesseract.image_to_string(gray)
    return text

def parse_problems(text):
    pattern = r'(\d+\s*[\+\-]\s*\d+)\s*=\s*(\d+)'
    matches = re.findall(pattern,text)

    problems = []
    for expr,answer in matches:
        problems.append((expr.replace(" ",""),int(answer)))

    return problems

def grade(problems):
    correct = 0
    results = []

    for expr,student_answer in problems:
        try:
            correct_answer = int(sympify(expr))

            if student_answer == correct_answer:
                results.append((expr,student_answer,correct_answer,True))
                correct += 1
            else:
                results.append((expr,student_answer,correct_answer,False))

        except:
            continue

    return results,correct

def print_report(results,correct):
    total = len(results)
    print("\nWorksheet Report\n")

    for expr,student,correct_answer,is_correct in results:
        mark = "✔" if is_correct else "✘"
        print(f"{expr} = {student} {mark} (correct: {correct_answer})")

    if total > 0:
        print("\nScore:",correct,"/",total)
        print("Percent:",round((correct/total)*100,2),"%")
    else:
        print("No problems detected. Try improving the image quality.")

def grade_worksheet(image_path):
    text = extract_text(image_path)
    problems = parse_problems(text)
    results,correct = grade(problems)
    print_report(results,correct)

if __name__ == "__main__":
    grade_worksheet("worksheet.jpg")
