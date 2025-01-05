import pandas as pd
import numpy as np
import streamlit as st
import easyocr
from PIL import Image, ImageDraw
import re

st.title("Fiş Bilgisi Çıkartma ve Ayrıştırma")
st.markdown("## EasyOCR ile Fiş Bilgisi İşleme")

# Resim yükleme
file = st.file_uploader(label="Fiş resmini yükleyin", type=['png', 'jpg', 'jpeg'])
if file is not None:
    image = Image.open(file)
    st.image(image)  # Resmi göster

    # EasyOCR kullanımı
    reader = easyocr.Reader(['tr', 'en'], gpu=False)
    result = reader.readtext(np.array(image))

    # Verileri listeye kaydetme ve index atama
    extracted_data = []
    for idx, (bbox, text, confidence) in enumerate(result):
        extracted_data.append({"index": idx, "text": text, "confidence": confidence, "bbox": bbox})

    # OCR sonuçlarını ekrana yazdır
    st.write("OCR Sonuçları:")
    for item in extracted_data:
        st.write(f"Index: {item['index']} - Metin: {item['text']}")

    # Fiş bilgilerini işleme
    unvan = None
    fis_tarihi = None
    fis_no = None
    toplam_degeri = None
    topkdv_degeri = None

    # Tarih formatı için regex
    tarih_pattern = r"\b\d{2}[./-]\d{2}[./-]\d{4}\b"  # Tarih formatı: dd.mm.yyyy

    for idx, item in enumerate(extracted_data):
        text = item['text'].lower()

        # Unvan bilgisini bulma (en üstteki metin)
        if idx == 0:
            unvan = item['text']

        # Tarihi bulma
        if not fis_tarihi:
            match = re.search(tarih_pattern, text)
            if match:
                fis_tarihi = match.group(0)

        # Fiş No bilgisini bulma: "no" kelimesi var ve altındaki metin tamamen sayısal ise
        if "no" in text:
            fis_no_index = item['index'] + 1  # "No" metninden sonraki index
            if fis_no_index < len(extracted_data):
                next_item = extracted_data[fis_no_index]
                if re.match(r"^\d+$", next_item['text']):  # Metin tamamen sayısal mı?
                    fis_no = next_item['text']

        # Toplam kelimesini ve değerini bulma
        if "toplam" in text and idx + 1 < len(extracted_data):
            toplam_degeri = extracted_data[idx + 1]['text']  # Toplamdan bir sonraki metni al

        # Topkdv kelimesini ve değerini bulma
        if "topkdv" in text:
            topkdv_bbox = item['bbox']
            topkdv_degeri = ""

            # Aynı satırda bulunan değerleri birleştir
            for next_item in extracted_data:
                next_bbox = next_item['bbox']
                # Eğer aynı yatay satırdaysa ve sağında yer alıyorsa
                if abs(next_bbox[0][1] - topkdv_bbox[0][1]) < 10 and next_bbox[0][0] > topkdv_bbox[1][0]:
                    topkdv_degeri += next_item['text']

            # * işareti ile başlayan değeri ve ardından gelen sayıyı birleştir
            for idx, item in enumerate(extracted_data):
                if '*' in item['text']:  # '*' ile başlayan metni bul
                    topkdv_degeri = item['text']  # *19, kısmı
                    # *19, kısmından sonra gelen sayıyı alalım
                    if idx + 1 < len(extracted_data):
                        next_item = extracted_data[idx + 1]
                        # Virgülle ayrılmış sayıyı kontrol et
                        if re.match(r"^\d+,\d{2}$", next_item['text']):  # Virgülle ayrılmış sayıyı kontrol et
                            # *19, ve 78'i birleştir
                            topkdv_degeri += next_item['text']  # *19,78 şeklinde birleştir

    # İşlenmiş verileri tabloya aktarma
    processed_data = {
        "Unvan": unvan or "Bulunamadı",
        "Fiş Tarihi": fis_tarihi or "Bulunamadı",
        "Fiş No": fis_no or "Bulunamadı",  # Fiş No'yu ekleyin
        "Toplam Değeri": toplam_degeri or "Bulunamadı",
        "Toplam KDV Değeri": topkdv_degeri or "Bulunamadı"  # Tam değer alınır
    }

    df = pd.DataFrame.from_dict(processed_data, orient="index", columns=["Değer"])
    st.table(df)

    # Dikdörtgen çizimi
    def rectangle(image, result):
        draw = ImageDraw.Draw(image)
        for res in result:
            top_left = tuple(res[0][0])
            bottom_right = tuple(res[0][2])
            draw.rectangle((top_left, bottom_right), outline="blue", width=2)
        st.image(image)

    rectangle(image, result)