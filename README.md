# 🚀 TeknoNet - Otonom Müşteri Hizmetleri Yapay Zeka Ajanı

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Topic](https://img.shields.io/badge/TEKNOFEST-BilisimVadisi2025-orange.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10+-green.svg)](#)

TEKNOFEST Türkçe Doğal Dil İşleme Yarışması 2025 kapsamında geliştirilen **TeknoNet Asistanı**, Müşteri Hizmetleri süreçlerinde fatura sorgulama, paket değişimi ve teknik destek süreçlerini otonom araçlar (tools) ve dinamik karar zincirleri ile yöneten otonom bir AI ajanıdır.

---

## 🏗️ Sistem Mimarisi

Sistem, gelen kullanıcı girdilerini niyet analizine (Intent Analysis) tabi tutar, gerekli durumda Qdrant Vektör Veritabanı üzerinden RAG (Retrieval-Augmented Generation) mekanizmasını çalıştırır veya FastAPI üzerinden Müşteri/Fatura API'lerine güvenli araç çağrıları (Tool Calls) gerçekleştirir.