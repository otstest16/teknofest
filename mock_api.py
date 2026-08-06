from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Telekom Mock Core Backend",
    description="TEKNOFEST TDDİ Mock API Services",
)


# Pydantic Modelleri
class UserInfoResponse(BaseModel):
  user_id: str
  name: str
  surname: str
  current_package: str
  contract_end_date: str
  payment_status: str


class PackageItem(BaseModel):
  id: str
  name: str
  price: str
  details: str


class PackageChangeRequest(BaseModel):
  user_id: str
  package_id: str


class PackageChangeResponse(BaseModel):
  success: bool
  message: Optional[str] = None
  error: Optional[str] = None


# Mock Veri Deposu (DB Bağlantısı Olmadığı Durumlar İçin İzolasyon)
MOCK_USERS = {
    "U1001": {
        "name": "Ali",
        "surname": "Can",
        "current_package": "SüperNet 50",
        "contract_end_date": "2026-08-01",
        "payment_status": "Odendi",
    },
    "U1002": {
        "name": "Ayşe",
        "surname": "Yılmaz",
        "current_package": "EkoPaket 25",
        "contract_end_date": "2025-12-01",
        "payment_status": "Gecikmede",
    },
}

MOCK_PACKAGES = [
    {
        "id": "P101",
        "name": "SüperNet 50",
        "price": "250 TL",
        "details": "50Mbps limitsiz internet, 1000 dk konuşma",
    },
    {
        "id": "P102",
        "name": "MegaPaket 100",
        "price": "350 TL",
        "details": "100Mbps limitsiz internet, 2000 dk konuşma",
    },
    {
        "id": "P103",
        "name": "EkoPaket 25",
        "price": "180 TL",
        "details": "25Mbps internet, 10GB mobil kota",
    },
]


@app.get("/api/getUserInfo/{user_id}", response_model=UserInfoResponse)
def get_user_info(user_id: str):
  """Kullanıcı profilini ve mevcut sözleşmesini getirir."""
  user = MOCK_USERS.get(user_id)
  if not user:
    raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")

  return UserInfoResponse(
      user_id=user_id,
      name=user["name"],
      surname=user["surname"],
      current_package=user["current_package"],
      contract_end_date=user["contract_end_date"],
      payment_status=user["payment_status"],
  )


@app.get(
    "/api/getAvailablePackages/{user_id}", response_model=List[PackageItem]
)
def get_available_packages(user_id: str):
  """Kullanıcının geçebileceği uygun paketlerin listesini döner."""
  if user_id not in MOCK_USERS:
    raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı.")
  return [
      PackageItem(**pkg)
      for pkg in MOCK_PACKAGES
      if pkg["name"] != MOCK_USERS[user_id]["current_package"]
  ]


@app.post("/api/initiatePackageChange", response_model=PackageChangeResponse)
def initiate_package_change(req: PackageChangeRequest):
  """Paket değişikliği işlemini başlatır."""
  user = MOCK_USERS.get(req.user_id)
  if not user:
    return PackageChangeResponse(
        success=False, error="Kullanıcı kaydı bulunamadı."
    )

  if user["payment_status"] == "Gecikmede":
    return PackageChangeResponse(
        success=False,
        error=(
            "Gecikmiş faturanız bulunmaktadır. Paket değişikliği yapabilmek"
            " için önce ödemenizi tamamlamalısınız."
        ),
    )

  target_package = next(
      (p for p in MOCK_PACKAGES if p["id"] == req.package_id), None
  )
  if not target_package:
    return PackageChangeResponse(
        success=False, error="Geçersiz paket seçimi."
    )

  # Başarılı işlem simülasyonu
  user["current_package"] = target_package["name"]
  return PackageChangeResponse(
      success=True,
      message=(
          f"Paket değişikliği talebiniz alınmıştır. Yeni paketiniz:"
          f" {target_package['name']}"
      ),
  )


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=8000)