from app.processing.extractor import extract_fields, identify_document_type
from app.processing.validator import validate_fields
from app.processing.risk import calculate_confidence, calculate_risk


sample_text = """
SAMPLE KYC DOCUMENT
FOR OCR / SOFTWARE TESTING ONLY — NOT A REAL IDENTITY DOCUMENT

KYC FIELD SAMPLE VALUE

Full Name RAHUL SHARMA
Date of Birth 15/08/1998
Gender MALE
Father's Name RAJESH SHARMA
Nationality INDIAN
PAN Number ABCDE1234F
Aadhaar Number XXXX XXXX 1234
Mobile Number +91 98765 43210
Email rahul.sharma@example.com
Address 123 MG Road, Andheri East, Mumbai, Maharashtra - 400069
Document Type KYC / Identity Proof
Document Number KYC-SAMPLE-2026-001
"""


document_type = identify_document_type(sample_text)

fields = extract_fields(sample_text)

validation = validate_fields(fields)

confidence = calculate_confidence(
    fields,
    validation,
)

risk = calculate_risk(
    confidence,
    validation,
)


print("\n========== PROCESSING RESULT ==========")

print("Document Type :", document_type)
print("Name          :", fields["name"])
print("Document No   :", fields["document_number"])
print("DOB           :", fields["date_of_birth"])

print("\nValidation:")
print(validation)

print("\nConfidence    :", confidence)
print("Risk Level    :", risk["risk_level"])
print("Risk Reasons  :", risk["reasons"])

print("========================================\n")