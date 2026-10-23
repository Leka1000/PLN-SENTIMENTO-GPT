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
    /* Personalização da barra lateral */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e0e0e0;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ==============================================================================
# 2. BARRA LATERAL - CONFIGURAÇÕES E CREDENCIAIS DO MICROSOFT FOUNDRY
# ==============================================================================
st.sidebar.title("⚙️ Configurações & Conexão")
st.sidebar.markdown(
    "Insira suas credenciais do Microsoft Foundry com segurança para estabelecer a conexão."
)

minha_chave = st.sidebar.text_input("minha_chave (API Key)", type="password")
meu_endpoint = st.sidebar.text_input(
    "meu_endpoint", 
    placeholder="https://seu-recurso.services.ai.azure.com/"
)
meu_modelo = st.sidebar.text_input(
    "meu_modelo", 
    value="gpt-4.1-mini"
)

# ==============================================================================
# 3. FUNÇÃO DE PROCESSAMENTO DE IA
# ==============================================================================
def analisar_texto_com_ia(texto: str, chave: str, endpoint: str, modelo: str) -> dict:
    """Instancia o cliente AzureOpenAI dinamicamente e retorna o JSON estruturado."""
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
            {"role": "user", "content": texto},
        ],
        response_format={"type": "json_object"},
        temperature=0
