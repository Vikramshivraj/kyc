from io import BytesIO

import fitz
import pytesseract
from PIL import Image


def extract_text_from_file(
    file_data: bytes,
    content_type: str,
) -> str:

    if content_type.startswith("image/"):
        image = Image.open(BytesIO(file_data))

        return pytesseract.image_to_string(image)

    if content_type == "application/pdf":
        document = fitz.open(
            stream=file_data,
            filetype="pdf",
        )

        text_parts = []

        for page in document:
            text_parts.append(page.get_text())

        document.close()

        return "\n".join(text_parts)

    raise ValueError(
        f"Unsupported OCR content type: {content_type}"
    )