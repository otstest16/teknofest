import time
from agent import run_agent_session


def execute_context_switch_test():
  print("=" * 60)
  print("TEKNOFEST 2. Hafta - LangGraph Ajan & Bağlam Değişimi Testi")
  print("=" * 60)

  # Benzersiz oturum kimliği (Memory test için)
  session_id = "test_user_U1001_session"

  # Çok Adımlı Test Senaryosu
  test_scenario = [
      (
          "1. Adım: Kullanıcı Sorgusu",
          "Merhaba, ben Ali Can. Kullanıcı numaram U1001. Mevcut paketimi ve"
          " durumumu öğrenebilir miyim?",
      ),
      (
          "2. Adım: Paket Değişim İsteği",
          "Hangi üst paketlere geçebilirim? Bana P102 paketini tanımlar mısın?",
      ),
      (
          "3. Adım: BAĞLAM DEĞİŞİMİ (Context Switch)",
          (
              "Tam paket değiştirecektim ama aklıma takıldı; faturama nasıl"
              " itiraz edebilirim?"
          ),
      ),
      (
          "4. Adım: Bağlama Geri Dönüş",
          (
              "Anladım, teşekkürler. Şimdi az önceki işlemimize dönelim,"
              " U1001 kullanıcısı için P102 paket değişikliğini başlatabilir"
              " misin?"
          ),
      ),
  ]

  for step_title, user_message in test_scenario:
    print(f"\n[KULLANICI - {step_title}]:")
    print(f" > {user_message}\n")

    start_time = time.time()
    response = run_agent_session(user_message, thread_id=session_id)
    elapsed_time = time.time() - start_time

    print(f"[AJAN YANITI] ({elapsed_time:.2f} sn):")
    print(f"{response}")
    print("-" * 60)


if __name__ == "__main__":
  # Not: Bu testi çalıştırmadan önce 'python mock_api.py' servisinin açık olduğundan emin olun.
  execute_context_switch_test()