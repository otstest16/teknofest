# TEKNOFEST 2025 TDDİ - Çağrı Merkezi Otonom Ajanı

## Proje Hakkında
Bu proje, TEKNOFEST Türkçe Doğal Dil İşleme Yarışması Senaryo Kategorisi kapsamında geliştirilen otonom çağrı merkezi asistanıdır.

## Kurulum
1. Sanal ortamı oluşturun ve aktif edin:
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate

2. Bağımlılıkları yükleyin:
   pip install -r requirements.txt

## Çalıştırma (1. Hafta Servisleri)
1. Mock API Backend'ini Başlatma:
   python mock_api.py
   (API Dökümantasyonu: http://localhost:8000/docs)

2. Qdrant Vektör Veritabanına SSS Yükleme:
   python ingest_faq.py