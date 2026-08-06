import json
from typing import Optional
from langchain_core.tools import tool
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests

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
  """İnternet hızı, fatura itirazı, taahhüt durumları gibi genel bilgi ve SSS sorularını Qdrant vektör veritabanında arar.

  Parametre: query (Kullanıcının sorduğu soru metni)
  """
  try:
    client = QdrantClient(path="./qdrant_db")
    embedder = SentenceTransformer("intfloat/multilingual-e5-base")

    query_vector = embedder.encode(f"query: {query}").tolist()
    results = client.search(
        collection_name="teknonet_sss", query_vector=query_vector, limit=2
    )
    client.close()

    if not results:
      return "İlgili SSS bilgisi bulunamadı."

    faq_results = [
        f"Soru: {hit.payload['question']}\nYanıt: {hit.payload['answer']}"
        for hit.payload in [r.payload for r in results]
    ]
    return "\n---\n".join(faq_results)
  except Exception as e:
    return f"Vektör Arama Hatası: {str(e)}"


# Ajanın erişimine sunulacak tüm araçlar
ALL_TOOLS = [
    get_user_info,
    get_available_packages,
    initiate_package_change,
    search_faq,
]