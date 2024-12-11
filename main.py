import pandas as pd
import numpy as np
import streamlit as st
import easyocr
from PIL import Image
import re
import cv2

# Streamlit Başlığı
st.title("Extract and Categorize Receipt Details with EasyOCR")

# Dil Seçimi
languages = st.multiselect(
    "Select languages for OCR",
    options=['en', 'tr'],
    default=['en', 'tr']
)

if languages:
    reader = easyocr.Reader(languages, gpu=False)

    # Fatura Görselleri Yükleme
    uploaded_files = st.file_uploader(
        label="Upload your receipt images",
        type=['png', 'jpg', 'jpeg'],
        accept_multiple_files=True
    )

    if uploaded_files:
        receipt_data = []

        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image")

            # Görüntü İşleme
            def preprocess_image(image):
                image_np = np.array(image)
                gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
                _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
                contrast = cv2.convertScaleAbs(binary, alpha=1.5, beta=20)
                return contrast

            processed_image = preprocess_image(image)
            st.image(processed_image, caption="Processed Image", clamp=True)

            # OCR İşlemi
            results = reader.readtext(processed_image, detail=1)
            extracted_text = [res[1] for res in results]
            st.text_area("Extracted Full Text", "\n".join(extracted_text))

            # Tüm metni analiz et ve kategorilere ayır
            def categorize_text(text_lines):
                details = {
                    "Fiş No": None,
                    "Firma Unvanı": None,
                    "Fiş Tarihi": None,
                    "KDV Oranları": {},
                    "TOPKDV": None,
                    "Toplam Tutar": None,
                    "Ham Metin": "\n".join(text_lines)
                }

                # Firma Adını İlk Satırlardan Bulma
                for i, line in enumerate(text_lines[:5]):  # İlk 5 satırda ara
                    if re.search(r"(TİC\.|SAN\.|LTD\.|A\.Ş\.)", line.upper()):
                        details["Firma Unvanı"] = line.strip()
                        break
                if not details["Firma Unvanı"]:  # Eğer "TİC., A.Ş." bulamazsa
                    details["Firma Unvanı"] = text_lines[0].strip()  # İlk satırı al

                # Fiş No, Tarih, TOPKDV ve TOPLAM Yakalama
                for line in text_lines:
                    # Fiş No
                    receipt_no_match = re.search(r"(FİŞ NO|NO FİŞ|FATURA NO|FİŞ[:\s]+)(\d+)", line, re.IGNORECASE)
                    if receipt_no_match:
                        details["Fiş No"] = receipt_no_match.group(2)

                    # Fiş Tarihi
                    date_match = re.search(r"(\b\d{1,2}[/.\-]\d{1,2}[/.\-]\d{2,4}\b)", line)
                    if date_match:
                        details["Fiş Tarihi"] = date_match.group(1)

                    # TOPKDV
                    if "TOPKDV" in line.upper():
                        try:
                            topkdv_value = re.findall(r"[\d.,]+", line)
                            if topkdv_value:
                                details["TOPKDV"] = float(topkdv_value[-1].replace(",", "."))
                        except:
                            pass

                    # TOPLAM
                    if "TOPLAM" in line.upper():
                        try:
                            toplam_value = re.findall(r"[\d.,]+", line)
                            if toplam_value:
                                details["Toplam Tutar"] = float(toplam_value[-1].replace(",", "."))
                        except:
                            pass

                    # KDV Oranları
                    if re.search(r"%\d+", line):
                        try:
                            match = re.search(r"%(\d+)[^\d]*(\d+,\d+)", line)
                            if match:
                                kdv_rate = match.group(1)
                                amount = float(match.group(2).replace(",", "."))
                                details["KDV Oranları"][kdv_rate] = details["KDV Oranları"].get(kdv_rate, 0) + amount
                        except:
                            pass

                return details

            # Kategorilere ayır
            categorized_details = categorize_text(extracted_text)
            categorized_details["Dosya Adı"] = uploaded_file.name

            # Fiş Detaylarını Göster
            st.write("### Receipt Details")
            st.write(f"**Fiş No:** {categorized_details['Fiş No']}")
            st.write(f"**Firma Unvanı:** {categorized_details['Firma Unvanı']}")
            st.write(f"**Fiş Tarihi:** {categorized_details['Fiş Tarihi']}")
            st.write(f"**TOPKDV:** {categorized_details['TOPKDV']}")
            st.write(f"**Toplam Tutar:** {categorized_details['Toplam Tutar']}")

            receipt_data.append(categorized_details)

        # Sonuçları DataFrame'e dönüştür
        df_receipts = pd.DataFrame(receipt_data)

        # KDV oranlarını ayrıştır ve gruplandır
        def process_kdv(row):
            if row["KDV Oranları"]:
                return ", ".join([f"%{key}: {value:.2f}" for key, value in row["KDV Oranları"].items()])
            return None

        df_receipts["KDV Detayları"] = df_receipts.apply(process_kdv, axis=1)
        df_receipts = df_receipts.drop(columns=["KDV Oranları"])

        # Detayları tablo olarak göster
        st.dataframe(df_receipts)

        # Excel çıktısı oluşturma
        output_file = "receipt_details.xlsx"
        df_receipts.to_excel(output_file, index=False)

        with open(output_file, "rb") as file:
            st.download_button(
                label="Download Receipt Details as Excel",
                data=file,
                file_name=output_file,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )