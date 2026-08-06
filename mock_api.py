import os
import subprocess
import sys
import time
import traceback

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI(title="TeknoNet Mock API & Agent Backend")

USERS_DB = {
    "U1001": {
        "user_id": "U1001",
        "name": "Ahmet Yılmaz",
        "current_package": "Standart 50 Mbps",
        "balance_status": "Düzenli",
        "unpaid_bills": 0,
    },
    "U1002": {
        "user_id": "U1002",
        "name": "Ayşe Kaya",
        "current_package": "Eko 25 Mbps",
        "balance_status": "Gecikmede",
        "unpaid_bills": 250.0,
    },
}

PACKAGES_DB = [
    {
        "package_id": "P101",
        "name": "Hızlı 100 Mbps",
        "price": 299.90,
        "speed": "100 Mbps",
    },
    {
        "package_id": "P102",
        "name": "Ultra 200 Mbps",
        "price": 399.90,
        "speed": "200 Mbps",
    },
    {
        "package_id": "P103",
        "name": "Gamer 500 Mbps",
        "price": 599.90,
        "speed": "500 Mbps",
    },
]


@app.get("/api/getUserInfo/{user_id}")
def get_user_info(user_id: str):
  if user_id in USERS_DB:
    return USERS_DB[user_id]
  raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")


@app.get("/api/getAvailablePackages/{user_id}")
def get_available_packages(user_id: str):
  if user_id in USERS_DB:
    return {"user_id": user_id, "available_packages": PACKAGES_DB}
  raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")


class PackageChangeRequest(BaseModel):
  user_id: str
  package_id: str


@app.post("/api/initiatePackageChange")
def initiate_package_change(req: PackageChangeRequest):
  user = USERS_DB.get(req.user_id)
  if not user:
    raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")
  if user["balance_status"] == "Gecikmede":
    raise HTTPException(
        status_code=400,
        detail="Gecikmiş fatura borcunuz nedeniyle paket değişikliği yapılamaz.",
    )

  selected_pkg = next(
      (p for p in PACKAGES_DB if p["package_id"] == req.package_id), None
  )
  if not selected_pkg:
    raise HTTPException(status_code=404, detail="Geçersiz paket ID")

  user["current_package"] = selected_pkg["name"]
  return {
      "status": "Success",
      "message": f"Paketiniz başarıyla {selected_pkg['name']} olarak değiştirildi.",
      "new_package": selected_pkg["name"],
  }


class ChatRequest(BaseModel):
  message: str
  session_id: str = "default_session"


@app.post("/api/chat")
def chat_endpoint(req: ChatRequest):
  try:
    from agent import app as agent_app

    config = {"configurable": {"thread_id": req.session_id}}
    response_state = agent_app.invoke(
        {"messages": [("user", req.message)]}, config=config
    )
    final_response = response_state["messages"][-1].content
    return {"status": "success", "response": final_response}
  except Exception as e:
    print(f"\n⚠️ Chat Uç Noktası İkazı: {str(e)}")
    traceback.print_exc()

    # Çökme yerine kullanıcıya akışın devam etmesini sağlayan güvenli yanıt
    return {
        "status": "success",
        "response": (
            "Mesajınızı aldım. TeknoNet müşteri hizmetleri olarak size paket,"
            " fatura veya teknik konularda yardımcı olabilirim. Nasıl yardımcı"
            " olmamı istersiniz?"
        ),
    }


if __name__ == "__main__":
  if os.environ.get("MOCK_API_WORKER") != "1":
    print("==================================================")
    print("🛡️ Mock API Otomatik Yeniden Başlatma Koruması Aktif")
    print("==================================================")

    env = os.environ.copy()
    env["MOCK_API_WORKER"] = "1"

    while True:
      try:
        process = subprocess.run([sys.executable] + sys.argv, env=env)
        print(
            "\n⚠️ Mock API süreci durdu veya çöktü (Çıkış Kodu:"
            f" {process.returncode})."
        )
      except KeyboardInterrupt:
        print("\n🛑 Kullanıcı tarafından durduruldu.")
        sys.exit(0)
      except Exception as e:
        print(f"\n❌ Sistem hatası: {e}")

      time.sleep(2)
  else:
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)