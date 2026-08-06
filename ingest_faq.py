import os
from datasets import load_dataset
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

COLLECTION_NAME = "teknonet_sss"

# 1. Qdrant ve Embedding Model Kurulumu (Yerel Disk Modu)
qdrant_client = QdrantClient(path="./qdrant_db")
embedder = SentenceTransformer("intfloat/multilingual-e5-base")

# 2. Qdrant Koleksiyonunu Oluştur (Yoksa)
# Deprecated uyarısını önlemek için get_embedding_dimension() kullanıyoruz
vector_size = embedder.get_embedding_dimension()
collections = [c.name for c in qdrant_client.get_collections().collections]

if COLLECTION_NAME not in collections:
  qdrant_client.create_collection(
      collection_name=COLLECTION_NAME,
      vectors_config=VectorParams(
          size=vector_size, distance=Distance.COSINE
      ),
  )
  print(f"'{COLLECTION_NAME}' koleksiyonu oluşturuldu.")


# 3. SSS Verilerini Getir
def get_faq_data():
  return [
      {
          "id": 1,
          "question": "Faturama nasıl itiraz edebilirim?",
          "answer": (
              "Faturanıza itiraz etmek için mobil uygulamamızdan 'Fatura"
              " İşlemleri > İtiraz' adımlarını takip edebilir veya müşteri"
              " hizmetlerine bağlanarak kayıt oluşturabilirsiniz."
          ),
      },
      {
          "id": 2,
          "question": "Taahhüdüm bitince ne olur?",
          "answer": (
              "Taahhüt süreniz dolduğunda paketiniz standart tarife üzerinden"
              " ücretlendirilmeye devam eder. Cezai şart ödemeden yeni bir"
              " kampanyaya geçebilirsiniz."
          ),
      },
      {
          "id": 3,
          "question": "İnternet hızım düşük, ne yapmalıyım?",
          "answer": (
              "Modeminizi 30 saniye kapatıp açarak resetleyebilirsiniz. Sorun"
              " devam ederse hat değerlerinizin kontrolü için arıza kaydı"
              " bırakabilirsiniz."
          ),
      },
  ]


# 4. Vektörleştirme ve Qdrant'a Yükleme (Ingestion)
def run_ingestion():
  faqs = get_faq_data()
  points = []

  for item in faqs:
    text_to_embed = f"Soru: {item['question']} Yanıt: {item['answer']}"
    vector = embedder.encode(text_to_embed).tolist()

    point = PointStruct(
        id=item["id"],
        vector=vector,
        payload={
            "question": item["question"],
            "answer": item["answer"],
            "category": "SSS",
        },
    )
    points.append(point)

  qdrant_client.upsert(collection_name=COLLECTION_NAME, points=points)
  print(f"{len(points)} adet SSS verisi Qdrant'a başarıyla indekslendi.")


if __name__ == "__main__":
  try:
    run_ingestion()
  finally:
    # Kapanış hatasını engellemek için istemciyi açıkça kapatıyoruz
    qdrant_client.close()