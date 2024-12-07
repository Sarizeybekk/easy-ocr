import pandas as pd
import numpy as np
import streamlit as st
import easyocr
from PIL import Image, ImageDraw, ImageEnhance
from matplotlib import pyplot as plt
import time

# Başlık ve Açıklama
st.title("Get Text from Image with EasyOCR")
st.markdown("## EasyOCR with Streamlit")

# Dil Seçimi
languages = st.multiselect(
    "Select languages for OCR",
    options=['en', 'tr', 'fr', 'de', 'es', 'it'],
    default=['en', 'tr']
)

if languages:
    reader = easyocr.Reader(languages, gpu=False)

    # Dosya Yükleme
    file = st.file_uploader(label="Upload your image", type=['png', 'jpg', 'jpeg'])
    if file is not None:
        image = Image.open(file)  # Resmi Oku
        st.image(image, caption="Uploaded Image")  # Resmi Göster

        # Görüntü Boyutlandırma
        max_size = st.slider("Max image size (pixels)", 500, 2000, 1000)
        image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        # Görüntü Ön İşleme
        preprocess = st.radio("Preprocess image before OCR", ["None", "Grayscale", "Increase Contrast"])
        if preprocess == "Grayscale":
            image = image.convert("L")
        elif preprocess == "Increase Contrast":
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2)

        # OCR İşlemi ve Süre Ölçümü
        start_time = time.time()
        result = reader.readtext(np.array(image))
        end_time = time.time()
        st.info(f"Processing time: {end_time - start_time:.2f} seconds")

        # Güven Seviyesi Filtresi
        min_confidence = st.slider("Minimum confidence threshold", 0.0, 1.0, 0.5)
        filtered_result = [res for res in result if res[2] >= min_confidence]

        # Sonuçları Tablo Olarak Göster
        if filtered_result:
            textdic_easyocr = {
                res[1]: {"pred_confidence": res[2]} for res in filtered_result
            }
            df = pd.DataFrame.from_dict(textdic_easyocr).T
            st.table(df)

            # CSV İndir
            csv = df.to_csv().encode('utf-8')
            st.download_button(
                label="Download results as CSV",
                data=csv,
                file_name='ocr_results.csv',
                mime='text/csv',
            )

            # Görüntü Üzerine Çizim Fonksiyonları
            def rectangle(image, result):
                draw = ImageDraw.Draw(image)
                for res in result:
                    top_left = tuple(res[0][0])
                    bottom_right = tuple(res[0][2])
                    draw.rectangle((top_left, bottom_right), outline="blue", width=2)
                return image

            def overlay_text(image, result):
                draw = ImageDraw.Draw(image)
                for res in result:
                    top_left = tuple(res[0][0])
                    pred_text = res[1]
                    draw.text(top_left, pred_text, fill="red")
                return image

            # Kullanıcıya Seçenek Sunma
            show_boxes = st.checkbox("Show bounding boxes", value=True)
            overlay_option = st.checkbox("Overlay text on image")

            if show_boxes:
                image_with_boxes = rectangle(image.copy(), filtered_result)
                st.image(image_with_boxes, caption="Image with Bounding Boxes")

            if overlay_option:
                image_with_overlay = overlay_text(image.copy(), filtered_result)
                st.image(image_with_overlay, caption="Image with Overlayed Text")

            # Güven Seviyesi Dağılım Grafiği
            confidences = [res[2] for res in filtered_result]
            if confidences:
                plt.figure(figsize=(8, 4))
                plt.hist(confidences, bins=10, color='blue', alpha=0.7)
                plt.title("Confidence Distribution")
                plt.xlabel("Confidence")
                plt.ylabel("Frequency")
                st.pyplot(plt)

        else:
            st.warning("No text found with the selected confidence threshold.")
