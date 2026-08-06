from typing import Annotated, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from tools import ALL_TOOLS

# 1. Ollama Model Kurulumu
# Not: Yerel ortamınızda 'ollama run cosmos-turkish-gemma-9b' veya 'ollama run gemma2' yüklü olmalıdır.
llm = ChatOllama(
    model="llama3.2:3b",  # veya 'gemma2', 'gemma:7b'
    temperature=0,
)

# LLM'e araçları bağlıyoruz
llm_with_tools = llm.bind_tools(ALL_TOOLS)

# 2. Sistem Yönergesi (System Prompt)
SYSTEM_PROMPT = """Sen TeknoNet Telekomünikasyon şirketinin otonom çağrı merkezi asistanısın.
Görevin müşterilere paket değişikliği, abonelik sorgulama ve genel bilgi süreçlerinde yardımcı olmaktır.

Kurallar:
1. Nazik, profesyonel ve çözüm odaklı konuş.
2. İşlem yapmadan önce mutlaka müşteri bilgilerini (getUserInfo) kontrol et.
3. Faturası 'Gecikmede' görünen müşterilerin paket değişim taleplerini 'initiatePackageChange' aracını çağırarak doğrula ve dönen hata mesajını nazikçe ilet.
4. Müşteri aniden farklı bir konuya geçerse (örn: paket değiştirirken faturaya itiraz sorması), durumu kaybetmeden yeni soruya cevap ver, ardından yarım kalan işleme dönmek isteyip istemediğini sor.
5. Bilmediğin bilgileri uydurma, 'search_faq' aracını kullanarak yanıtla.
"""


# 3. LangGraph Durum Yapısı (State)
class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]


# 4. Düğüm (Node) Fonksiyonları
def call_model(state: AgentState):
  messages = state["messages"]

  # Konuşmanın en başına sistem mesajını ekle (Yoksa)
  if not isinstance(messages[0], SystemMessage):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

  response = llm_with_tools.invoke(messages)
  return {"messages": [response]}


# 5. Graph Tasarımı
builder = StateGraph(AgentState)

# Düğümleri ekle
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(ALL_TOOLS))

# Başlangıç noktası
builder.set_entry_point("agent")

# Koşullu Kenarlar (Conditional Edges): Araç mı çağrılacak yoksa kullanıcıya yanıt mı verilecek?
builder.add_conditional_edges(
    "agent", tools_condition, {"tools": "tools", END: END}
)

# Tool çalıştıktan sonra tekrar ajana dön
builder.add_edge("tools", "agent")

# Hafıza Raporlayıcı (Memory Saver) - Oturum bazlı konuşma takibi için
memory = MemorySaver()
app = builder.compile(checkpointer=memory)


def run_agent_session(
    user_input: str, thread_id: str = "default_session"
) -> str:
  """Ajanı bir girdi ile tetikler ve son yanıtı döner."""
  config = {"configurable": {"thread_id": thread_id}}
  input_message = {"messages": [("user", user_input)]}

  events = app.stream(input_message, config, stream_mode="values")
  last_event = None
  for event in events:
    last_event = event

  if last_event and "messages" in last_event:
    return last_event["messages"][-1].content
  return "Bir hata oluştu, yanıt üretilemedi."