# 🚀 TeknoNet Ajan Mimarisi - Günlük 100K Çağrı Ölçeklenebilirlik ve Donanım Tahmin Raporu

## 1. Yük ve Trafik Analizi
* **Günlük Toplam Çağrı Sayısı:** 100.000 istek/gün
* **Ortalama Çağrı Yoğunluğu (24 Saat):** 
  $$RPS_{ort} = \frac{100.000}{24 \times 3600} \approx 1.16 \text{ İstek/Saniye (RPS)}$$
* **Zirve (Peak) Yük Çarpanı (Mesai Saatleri 09:00 - 18:00):** $4\times$ yoğunluk
* **Zirve Çağrı Yoğunluğu (Peak RPS):** 
  $$RPS_{peak} \approx 5 \text{ ile } 8 \text{ İstek/Saniye (RPS)}$$
* **Ortalama Üretilen Token / İstek:** ~150 Token (Input) + ~200 Token (Output) = 350 Token/çağrı.

---

## 2. Donanım ve Kaynak İhtiyaç Tahmini

Sistemin ortalama 1 saniyenin altında yanıt süresi (Target Latency < 1s) sunabilmesi için vLLM / TensorRT-LLM altyapısı ile ölçeklenmesi gerekmektedir.

### A. Üretken Yapay Zeka (LLM Inference Cluster)
* **Model:** Llama-3.2-3B / Qwen-2.5-7B (FP16 veya INT4 Quantized)
* **Gerekli GPU Sayısı:** 2x NVIDIA A10G (24 GB VRAM) veya 1x NVIDIA L40S (48 GB VRAM)
* **Kapasite:** 1x NVIDIA A10G ekran kartı vLLM motoru ile saniyede ~15-20 paralel çağrıya (RPS) kadar hizmet verebilmektedir (Peak yükün 2.5 katı yedekli).

### B. Uygulama ve Ajan Sunucuları (FastAPI & LangGraph API)
* **CPU:** 8 vCPU (Intel Xeon veya AMD EPYC)
* **RAM:** 16 GB RAM
* **Ölçekleme:** 2x Load Balanced (Nginx / Traefik arkasında) Docker Konteyner

### C. Vektör Veritabanı (Qdrant Cluster)
* **Koleksiyon Boyutu:** 50.000+ SSS Dokümanı
* **RAM:** 8 GB RAM (In-Memory Indexing için)
* **Depolama:** 20 GB NVMe SSD

---

## 3. Önerilen Üretim (Production) Mimarisi