from typing import Annotated, Any, Dict, Generator, Sequence, TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from tools import ALL_TOOLS

# Ollama Model Kurulumu
llm = ChatOllama(
    model="llama3.2:3b",
    temperature=0.1,
)

llm_with_tools = llm.bind_tools(ALL_TOOLS)

SYSTEM_PROMPT = """Sen TeknoNet Telekomünikasyon şirketinin otonom müşteri hizmetleri asistanısın.

Sıkı Kurallar ve Uygulama Adımları:

1. MÜŞTERİ ID TESPİTİ (EN YÜKSEK ÖNCELİK):
   - Kullanıcı mesajında 'U1001', 'U1002' gibi bir müşteri ID'si geçtiğinde VEYA sadece 'U1001' gibi bir numara yazıldığında; HİÇBİR ŞEY SORMADAN DERHAL `get_user_info(user_id)` aracını çalıştır.
   - Dönen sonuçtaki Müşteri Adı, Mevcut Paket, Ödeme Durumu ve Fatura Borcu bilgilerini kullanıcıya anlaşılır şekilde raporla. Tekrar müşteri numarası isteme!

2. SELAMLAŞMA:
   - Kullanıcı 'merhaba', 'selam' dediğinde nazikçe karşıla ve 'Müşteri numaranızı (Örn: U1001) iletirseniz fatura ve paket bilgilerinizi hemen kontrol edebilirim' de.

3. FATURA VE ÖDEME:
   - Fatura/ödeme sorulduğunda Müşteri ID yoksa ID talep et.

4. PAKET VE KAMPANYA:
   - Müşteri ID ile paket sorulursa `get_available_packages` aracını çalıştır.

5. GENEL SOHBET VE DİĞER KONULAR:
   - Şirket dışı konularda nazikçe cevap ver, sistemin kapanmasını engelle.
"""


class AgentState(TypedDict):
  messages: Annotated[Sequence[BaseMessage], add_messages]


def call_model(state: AgentState):
  messages = state["messages"]

  if not isinstance(messages[0], SystemMessage):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + list(messages)

  response = llm_with_tools.invoke(messages)
  return {"messages": [response]}


builder = StateGraph(AgentState)
builder.add_node("agent", call_model)
builder.add_node("tools", ToolNode(ALL_TOOLS))

builder.set_entry_point("agent")
builder.add_conditional_edges(
    "agent", tools_condition, {"tools": "tools", END: END}
)
builder.add_edge("tools", "agent")

memory = MemorySaver()
app = builder.compile(checkpointer=memory)