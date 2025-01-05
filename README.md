# 🧾 Receipt Information Extraction and Parsing with EasyOCR

This project is a **Streamlit**-based application for extracting and parsing receipt information using the **EasyOCR** library. The goal is to process receipt images, extract relevant details (e.g., company name, receipt number, date, total amount, and VAT), and display the results in a user-friendly interface.

---

## 📋 Features

- 🖼️ **OCR-Based Extraction**: Uses EasyOCR to extract text from receipt images.
- 🔍 **Regex Matching**: Identifies specific fields such as dates, receipt numbers, and monetary values using regular expressions.
- ⚙️ **Dynamic Processing**:
  - Extracts key details like:
    - 🏢 Company name (unvan)
    - 📅 Receipt date
    - 🧾 Receipt number
    - 💰 Total amount
    - 💵 VAT (KDV) amount
  - Highlights detected fields on the receipt image.
- 🌟 **Interactive Interface**:
  - Upload receipt images in PNG, JPG, or JPEG formats.
  - View extracted data in a tabular format.
  - Display processed images with bounding boxes around detected text.

---

## 🛠️ Technologies Used

- 🐍 **Python**: Core programming language.
- 🌐 **Streamlit**: For creating an interactive web application.
- 🔤 **EasyOCR**: Optical Character Recognition (OCR) library for text extraction.
- 🖌️ **Pillow**: For image processing and annotation.
- 🔢 **Regular Expressions (re)**: For extracting specific patterns like dates and monetary values.
- 📊 **Pandas**: For structuring and displaying extracted data.

---

## 🚀 How to Run the Project

1. **📥 Clone the Repository**:
   ```bash
   git clone  https://github.com/Sarizeybekk/easy-ocr.git
