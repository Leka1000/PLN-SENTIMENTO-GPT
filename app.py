Aqui está o código atualizado. Foram removidos os campos da barra lateral para preenchimento manual e as credenciais (`minha_chave`, `meu_endpoint` e `meu_modelo`) foram inseridas diretamente no código conforme solicitado.

```python
"""
MIT License

Copyright (c) 2026
"""

import json
import streamlit as st
from openai import AzureOpenAI

# ==============================================================================
# 1. CONFIGURAÇÃO DA PÁGINA E ESTILIZAÇÃO CSS
# ==============================================================================
st.set_page_config(
    page_title="Extrator Super Colorido 🌈",
    page_icon="🎨",
    layout="centered",
)

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
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
# 2. CREDENCIAIS DEFINIDAS DIRETAMENTE NO CÓDIGO
# ==============================================================================
minha_chave = "1gsyJYiGIr1rIjIm6heIq96VWJI5gMgXeXCaYCHx5WeeWGm3AMYvJQQJ99CJACHYHv6XJ3w3AAAAACOGUF3S"
meu_endpoint = "https://marcelomaffeis-7430-resource.services.ai.azure.com/openai/v1"
meu_modelo = "gpt-4.1-mini"

# ==============================================================================
# 3. FUNÇÃO DE PROCESSAMENTO DE IA
# ==============================================================================
def analisar_texto_com_ia(texto: str, chave: str, endpoint: str, modelo: str) -> dict:
    endpoint_limpo = endpoint.replace("&quot;", "").strip()
    
    client_azure = AzureOpenAI(
        api_key=chave.strip(),
        api_version="2024-08-01-preview",
        azure_endpoint=endpoint_limpo,
    )

    system_prompt = (
        "Você é um assistente especialista em extração de dados e análise de texto. "
        "Sua tarefa é analisar o texto fornecido pelo usuário e retornar EXATAMENTE "
        "um objeto JSON válido (sem blocos de código markdown adicionais, sem texto "
        "extra antes ou depois), contendo as seguintes chaves:\n"
        "1. 'sentimento': string indicando o sentimento geral (ex: Positivo, Negativo, Neutro, Animado, etc.).\n"
        "2. 'porcentagem_sentimento': número inteiro de 0 a 100 indicando a intensidade ou grau de certeza daquele sentimento.\n"
        "3. 'assunto_principal': string resumindo o tema central do texto.\n"
        "4. 'pessoas_citadas': lista de strings contendo os nomes das pessoas mencionadas no texto (se houver, senão lista vazia []).\n"
        "5. 'nivel_de_urgencia': string estritamente com um destes três valores: 'Baixo', 'Medio' ou 'Alto'."
    )

    response = client_azure.chat.completions.create(
        model=modelo.strip(),
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": texto}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)

# ==============================================================================
# 4. INTERFACE DO USUÁRIO (UI)
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

if "dados_json" not in st.session_state:
    st.session_state.dados_json = None

texto_usuario = st.text_area(
    "💬 **Cole ou digite sua história/mensagem abaixo:**",
    placeholder="Ex: A Ana e o Carlos vibraram muito com o lançamento do novo projeto incrível na empresa hoje!",
    height=150,
)

col_esq, col_centro, col_dir = st.columns([1, 2, 1])
with col_centro:
    botao_processar = st.button("🪄 Processar com Magia!", use_container_width=True, type="primary")

if botao_processar:
    if not texto_usuario.strip():
        st.warning("⚠️ Opa! Escreva alguma coisa legal antes de clicar no botão!")
    else:
        with st.spinner("🦄 Mágica acontecendo nos servidores da Microsoft..."):
            try:
                st.session_state.dados_json = analisar_texto_com_ia(
                    texto_usuario, minha_chave, meu_endpoint, meu_modelo
                )
                st.success("🎉 ¡Tcha-ram! Análise concluída com sucesso!")
                st.balloons()
            except Exception as e:
                st.error("Ops! Algo deu errado na comunicação com a API do Azure OpenAI. 😢 Verifique se as credenciais estão corretas.")
                st.exception(e)

# ==============================================================================
# 5. EXIBIÇÃO DOS RESULTADOS
# ==============================================================================
if st.session_state.dados_json:
    st.divider()
    st.subheader("🌟 Resultados Extraídos")

    dados = st.session_state.dados_json

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(label="🌈 Sentimento", value=dados.get("sentimento", "N/A"))

    with col2:
        porcentagem = dados.get("porcentagem_sentimento", 0)
        st.metric(label="⚡ Intensidade", value=f"{porcentagem}%")

    with col3:
        urgencia = dados.get("nivel_de_urgencia", "Baixo")
        st.metric(label="🔥 Urgência", value=urgencia)

    st.markdown("### 🎯 Assunto Principal")
    st.info(dados.get("assunto_principal", "Não identificado"))

    st.markdown("### 👥 Pessoas Mencionadas")
    pessoas = dados.get("pessoas_citadas", [])
    if pessoas:
        for pessoa in pessoas:
            st.success(f"⭐ {pessoa}")
    else:
        st.write("Nenhuma pessoa específica foi citada no texto.")

    with st.expander("🔍 Ver Detalhes Técnicos (JSON Bruto)"):
        st.json(dados)

```
