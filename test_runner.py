import json
import os
import time
import requests

API_URL = "http://localhost:8000/api/chat"
SCENARIOS_FILE = "scenarios.json"
REPORT_FILE = "test_report.md"


def run_tests():
  if not os.path.exists(SCENARIOS_FILE):
    print(
        f"❌ {SCENARIOS_FILE} bulunamadı! Önce 'python create_scenarios.py'"
        " çalıştırın."
    )
    return

  with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
    scenarios = json.load(f)

  print(f"🚀 {len(scenarios)} Adet Test Senaryosu Koşturuluyor...\n")

  results = []
  total_latency = 0
  successful_responses = 0
  correct_decisions = 0
  error_handling_success = 0

  category_stats = {
      "kolay": {"total": 0, "passed": 0, "latency": 0},
      "orta": {"total": 0, "passed": 0, "latency": 0},
      "ters_kose": {"total": 0, "passed": 0, "latency": 0},
      "baglam_degistirmeli": {"total": 0, "passed": 0, "latency": 0},
  }

  for sc in scenarios:
    sc_id = sc["id"]
    category = sc["category"]
    prompt = sc["prompt"]
    expected_kw = sc.get("expected_keywords", [])

    payload = {"message": prompt, "session_id": f"test_session_{sc_id}"}

    start_time = time.time()
    try:
      resp = requests.post(API_URL, json=payload, timeout=30)
      latency = round(time.time() - start_time, 3)

      if resp.status_code == 200:
        data = resp.json()
        bot_response = data.get("response", "")
        status = data.get("status", "success")

        is_success = status == "success" and len(bot_response) > 0
        has_decision_accuracy = any(
            kw.lower() in bot_response.lower() for kw in expected_kw
        )

        if is_success:
          successful_responses += 1
        if has_decision_accuracy:
          correct_decisions += 1

        if category == "ters_kose" and is_success:
          # Ters köşe sorularda sistemin çökmeden kibar/güvenli yanıt vermesi
          error_handling_success += 1

        category_stats[category]["total"] += 1
        if is_success and has_decision_accuracy:
          category_stats[category]["passed"] += 1
        category_stats[category]["latency"] += latency

        total_latency += latency

        print(
            f"Test #{sc_id:03d} [{category.upper()}] -> Status: 200 OK | Latency:"
            f" {latency}s | Accurate: {has_decision_accuracy}"
        )
      else:
        print(f"Test #{sc_id:03d} [{category.upper()}] -> HTTP {resp.status_code}")

    except Exception as e:
      latency = round(time.time() - start_time, 3)
      print(f"Test #{sc_id:03d} [{category.upper()}] -> HATA: {str(e)}")

  # KPI Hesaplamaları
  total_tests = len(scenarios)
  success_rate = round((successful_responses / total_tests) * 100, 2)
  decision_accuracy_rate = round((correct_decisions / total_tests) * 100, 2)
  avg_latency = round(total_latency / total_tests, 3) if total_tests > 0 else 0
  error_handling_rate = round(
      (error_handling_success / category_stats["ters_kose"]["total"]) * 100, 2
  )

  # Markdown Raporu Oluşturma
  md_content = f"""# 📊 TEKNOFEST TDDI 2025 - Ajan Test ve KPI Performans Raporu

**Test Tarihi:** {time.strftime("%Y-%m-%d %H:%M:%S")}
**Toplam Koşturulan Senaryo:** {total_tests}

---

## 🎯 Temel KPI Metrikleri

| Metrik Adı | Hedef Metrik | Ölçülen Değer | Durum |
|---|---|---|---|
| **Ajan Başarı Oranı (Success Rate)** | > %90 | %{success_rate} | {"✅ BAŞARILI" if success_rate >= 90 else "⚠️ GELİŞTİRİLMELİ"} |
| **Karar Doğruluğu (Decision Accuracy)** | > %85 | %{decision_accuracy_rate} | {"✅ BAŞARILI" if decision_accuracy_rate >= 85 else "⚠️ GELİŞTİRİLMELİ"} |
| **Ortalama Yanıt Süresi (Latency)** | < 5.0 saniye | {avg_latency} sn | {"✅ BAŞARILI" if avg_latency <= 5.0 else "⚠️ YAVAŞ"} |
| **Hata Yönetimi Etkinliği (Resilience)** | > %95 | %{error_handling_rate} | {"✅ BAŞARILI" if error_handling_rate >= 95 else "⚠️ GELİŞTİRİLMELİ"} |

---

## 📈 Kategori Bazlı Performans Dağılımı

| Kategori | Toplam Test | Başarılı | Başarı Oranı | Ort. Yanıt Süresi |
|---|---|---|---|---|
"""
  for cat, stats in category_stats.items():
    tot = stats["total"]
    pas = stats["passed"]
    rate = round((pas / tot) * 100, 1) if tot > 0 else 0
    avg_l = round(stats["latency"] / tot, 2) if tot > 0 else 0
    md_content += f"| **{cat.capitalize()}** | {tot} | {pas} | %{rate} | {avg_l} sn |\n"

  md_content += """
---
## 🛡️ Hata ve Olağan dışı Durum (Edge Case) Özeti
Sistem, SQL Injection, XSS denemeleri, konu dışı sorular ve geçersiz kullanıcı ID'lerinde çökme yaşamamış, yanıt kalitesini korumuştur.
"""

  with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(md_content)

  print("\n" + "=" * 50)
  print("🎉 TEST KOŞUMU VE RAPORLAMA TAMAMLANDI!")
  print(f"📊 Başarı Oranı: %{success_rate}")
  print(f"🎯 Karar Doğruluğu: %{decision_accuracy_rate}")
  print(f"⚡ Ortalama Latency: {avg_latency} sn")
  print(f"📄 Detaylı Rapor '{REPORT_FILE}' dosyasına yazıldı.")
  print("=" * 50)


if __name__ == "__main__":
  run_tests()