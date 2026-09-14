import pytesseract
from PIL import Image


image = Image.open("sample-kyc.png")

text = pytesseract.image_to_string(image)

print("OCR RESULT:")
print(text)