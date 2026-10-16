"""
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import json
import streamlit as st
from openai import AzureOpenAI

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA (TEMA ALEGRE E COLORIDO)
# ==============================================================================
st.set_page_config(
    page_title="Extrator Super Colorido 🌈",
    page_icon="🎨",
    layout="centered",
)

# Injeção de CSS personalizado para deixar o visual mais divertido, com gradientes e cartões coloridos
st.markdown(
    """
    <style>
    /* Fundo geral suave */
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Cabeçalho com gradiente vibrante */
    .header-box {
        background: linear-gradient(90deg, #FF4B2B 0%, #FF416C 50%, #7F00FF 100%);
        padding: 25px;
        border-radius: 20px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    }
    .header-box h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .header-box p {
        margin-top: 10px;
        font-size: 1.1rem;
        font-weight: 500;
    }

    /* Estilização dos botões principais */
    .stButton>button {
        background: linear-gradient(90deg, #00C9FF 0%, #92FE9D 100%);
        color: #0d1b2a;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        box-shadow: 0 4px 10px rgba(0,201,255,0.3);
        transition: 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(0,201,255,0.5);
    }

    /* Estilização customizada das caixas de métricas */
    div[data-testid="stMetric"] {
        background: white;
        padding: 15px;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        border-left: 5px solid #FF416C;
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ==============================================================================
# CARREGAMENTO DE CREDENCIAIS (SECRETS OU FALLBACK)
# ==============================================================================
def carregar_credenciais():
  try:
    endpoint = st.secrets["azure_openai"]["endpoint"]
    api_key = st.secrets["azure_openai"]["api_key"]
    deployment_name = st.secrets["azure_openai"]["deployment_name"]
    return endpoint, api_key, deployment_name
  except Exception:
    return (
        "https://marcelomaffeis-05082026-resource.services.ai.azure.com/",
        "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os",
        "gpt-4.1-mini",
    )


ENDPOINT, API_KEY, DEPLOYMENT_NAME = carregar_credenciais()
ENDPOINT = ENDPOINT.replace("&quot;", "").strip()

# Inicialização do cliente AzureOpenAI oficial
client = AzureOpenAI(
    api_key=API_KEY,
    api_version="2024-08-01-preview",
    azure_endpoint=ENDPOINT,
)

# ==============================================================================
# INTERFACE DO USUÁRIO (VISUAL DIVERTIDO)
# ==============================================================================
st.markdown(
    """
    <div class="header-box">
        <h1>🎨 Extrator Super Colorido 🚀</h1>
        <p>Transformando textos em insights mágicos com Azure OpenAI! ✨</p>
    </div>
""",
    unsafe_allow_html=True,
)

# Campo de texto super amigável
texto_usuario = st.text_area(
    "💬 **Cole ou digite sua história/mensagem abaixo:**",
    placeholder=(
        "Ex: A Ana e o Carlos vibraram muito com o lançamento do novo projeto"
        " incrível na empresa hoje!"
    ),
    height=150,
)

# Botão centralizado / destacado
col_esq, col_centro, col_dir = st.columns([1, 2, 1])
with col_centro:
  processar = st.button(
      "🪄 Processar com Magia!", use_container_width=True, type="primary"
  )

if processar:
  if not texto_usuario.strip():
    st.warning("⚠️ Opa! Escreva alguma coisa legal antes de clicar no botão!")
  else:
    with st.spinner("🦄 Mágica acontecendo nos servidores da Microsoft..."):
      try:
        system_prompt = (
            "Você é um assistente especialista em extração de dados e análise"
            " de texto. Sua tarefa é analisar o texto fornecido pelo usuário e"
            " retornar EXATAMENTE um objeto JSON válido (sem blocos de código"
            " markdown adicionais, sem texto extra antes ou depois), contendo"
            " as seguintes chaves:\n"
            "1. 'sentimento': string indicando o sentimento geral (ex: Positivo,"
            " Negativo, Neutro, Animado, etc.).\n"
            "2. 'porcentagem_sentimento': número inteiro de 0 a 100 indicando a"
            " intensidade ou grau de certeza daquele sentimento.\n"
            "3. 'assunto_principal': string resumindo o tema central do texto.\n"
            "4. 'pessoas_citadas': lista de strings contendo os nomes das"
            " pessoas mencionadas no texto (se houver, senão lista vazia []).\n"
            "5. 'nivel_de_urgencia': string estritamente com um destes três"
            " valores: 'Baixo', 'Medio' ou 'Alto'."
        )

        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto_usuario},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        resposta_bruta = response.choices[0].message.content
        dados_json = json.loads(resposta_bruta)

        st.success("🎉 ¡Tcha-ram! Análise concluída com sucesso!")
        st.balloons()  # Efeito visual de balões subindo na tela

        st.divider()

        # ======================================================================
        # EXIBIÇÃO COLORIDA DOS RESULTADOS
        # ======================================================================
        st.subheader("🌟 Resultados Extraídos")

        col1, col2, col3 = st.columns(3)

        with col1:
          st.metric(
              label="🌈 Sentimento",
              value=dados_json.get("sentimento", "N/A"),
          )

        with col2:
          porcentagem = dados_json.get("porcentagem_sentimento", 0)
          st.metric(label="⚡ Intensidade", value=f"{porcentagem}%")

        with col3:
          urgencia = dados_json.get("nivel_de_urgencia", "Baixo")
          st.metric(label="🔥 Urgência", value=urgencia)

        # Assunto Principal com estilo amigável
        st.markdown("### 🎯 Assunto Principal")
        st.info(dados_json.get("assunto_principal", "Não identificado"))

        # Pessoas Citadas
        st.markdown("### 👥 Pessoas Mencionadas")
        pessoas = dados_json.get("pessoas_citadas", [])
        if pessoas:
          for pessoa in pessoas:
            st.success(f"⭐ {pessoa}")
        else:
          st.write("Nenhuma pessoa específica foi citada no texto.")

        # JSON bruto colapsável
        with st.expander("🔍 Ver Detalhes Técnicos (JSON Bruto)"):
          st.json(dados_json)

      except Exception as e:
        st.error(
            "Ops! Algo deu errado na comunicação com a API do Azure OpenAI.
