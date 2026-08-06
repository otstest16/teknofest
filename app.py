import requests
import streamlit as st

st.set_page_config(
    page_title="TeknoNet - Otonom Müşteri Asistanı",
    page_icon="🤖",
    layout="wide",
)

API_CHAT_URL = "http://localhost:8000/api/chat"

# Sidebar
with st.sidebar:
  st.title("🤖 TeknoNet Asistanı")
  st.caption("TEKNOFEST TDDI 2025 - LangGraph Ajan Demosu")
  st.divider()

  session_id = st.text_input("Oturum / Müşteri ID:", value="U1001_session")

  if st.button("💬 Sohbeti Temizle", use_container_width=True):
    st.session_state.messages = []
    st.rerun()

  st.divider()
  st.markdown("""
    **Sistem Durumu:**
    - ⚡ **Backend API:** `http://localhost:8000`
    - 🧠 **Model:** `Llama 3.2 / Qwen 2.5`
    - 🗄️ **Vector DB:** `Qdrant Local`
    """)

st.title("📞 TeknoNet Müşteri Hizmetleri")
st.subheader("Otonom Çağrı Merkezi Ajan Arayüzü")

if "messages" not in st.session_state:
  st.session_state.messages = [
      {
          "role": "assistant",
          "content": (
              "Merhaba! Ben TeknoNet dijital asistanıyım. Size paket"
              " değişiklikleri, fatura işlemleri ve teknik konularda nasıl"
              " yardımcı olabilirim?"
          ),
      }
  ]

for msg in st.session_state.messages:
  with st.chat_message(msg["role"]):
    st.markdown(msg["content"])

if user_input := st.chat_input("Mesajınızı yazın... (Örn: Merhaba / U1001 faturam nasıl?)"):
  st.session_state.messages.append({"role": "user", "content": user_input})
  with st.chat_message("user"):
    st.markdown(user_input)

  with st.chat_message("assistant"):
    with st.spinner("🧠 Ajan yanıt veriyor..."):
      try:
        resp = requests.post(
            API_CHAT_URL,
            json={"message": user_input, "session_id": session_id},
            timeout=60,
        )
        if resp.status_code == 200:
          final_response = resp.json().get("response", "Yanıt alınamadı.")
        else:
          final_response = (
              f"Backend Hatası ({resp.status_code}): {resp.text}"
          )
      except Exception as e:
        final_response = (
            f"Bağlantı Kurulamadı: {str(e)}\n\nLütfen `python mock_api.py`"
            " servisinin açık olduğundan emin olun."
        )

      st.markdown(final_response)
      st.session_state.messages.append(
          {"role": "assistant", "content": final_response}
      )