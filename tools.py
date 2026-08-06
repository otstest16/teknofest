import json
import os
import requests
from langchain_core.tools import tool

API_BASE_URL = "http://localhost:8000/api"


@tool
def get_user_info(user_id: str) -> str:
  """Kullanıcının profil bilgilerini, mevcut paketini ve fatura/ödeme durumunu sorgular.

  Parametre: user_id (Örn: 'U1001')
  """
  try:
    response = requests.get(f"{API_BASE_URL}/getUserInfo/{user_id}", timeout=5)
    if response.status_code == 200:
      return json.dumps(response.json(), ensure_ascii=False)
    return f"Hata: Kullanıcı bulunamadı (Kod: {response.status_code})"
  except Exception as e:
    return f"API Bağlantı Hatası: {str(e)}"


@tool
def get_available_packages(user_id: str) -> str:
  """Kullanıcının geçebileceği uygun tarifeleri ve paket detaylarını listeler.

  Parametre: user_id (Örn: 'U1001')
  """
  try:
    response = requests.get(
        f"{API_BASE_URL}/getAvailablePackages/{user_id}", timeout=5
    )
    if response.status_code == 200:
      return json.dumps(response.json(), ensure_ascii=False)
    return f"Hata: Paketler getirilemedi (Kod: {response.status_code})"
  except Exception as e:
    return f"API Bağlantı Hatası: {str(e)}"


@tool
def initiate_package_change(user_id: str, package_id: str) -> str:
  """Kullanıcının mevcut paketini yeni bir paket ile değiştirmek için talep oluşturur.

  Parametreler: user_id (Örn: 'U1001'), package_id (Örn: 'P102')
  """
  try:
    payload = {"user_id": user_id, "package_id": package_id}
    response = requests.post(
        f"{API_BASE_URL}/initiatePackageChange", json=payload, timeout=5
    )
    if response.status_code == 200:
      return json.dumps(response.json(), ensure_ascii=False)
    return f"Hata: Paket değişikliği başarısız (Kod: {response.status_code})"
  except Exception as e:
    return f"API Bağlantı Hatası: {str(e)}"


@tool
def search_faq(query: str) -> str:
  """İnternet hızı, fatura itirazı, taahhüt durumları gibi genel bilgi ve SSS sorularını arar.

  Parametre: query (Kullanıcının sorduğu soru metni)
  """
  try:
    # PyTorch C++ çökmesini önlemek için doğrudan faq.json metin araması yapılır
    faq_path = "faq.json"
    if os.path.exists(faq_path):
      with open(faq_path, "r", encoding="utf-8") as f:
        faqs = json.load(f)

      words = [w.lower() for w in query.split() if len(w) > 2]
      matched = []
      for item in faqs:
        q = item.get("question", "").lower()
        if any(w in q for w in words):
          matched.append(
              f"Soru: {item.get('question')}\nYanıt: {item.get('answer')}"
          )

      if matched:
        return "\n---\n".join(matched[:2])

    return (
        "TeknoNet SSS: Fatura ödemeleri, paket değişikliği ve teknik destek"
        " hakkında detaylı bilgi için müşteri temsilcimizle görüşebilirsiniz."
    )
  except Exception as e:
    return f"SSS Arama Hatası: {str(e)}"


ALL_TOOLS = [
    get_user_info,
    get_available_packages,
    initiate_package_change,
    search_faq,
]