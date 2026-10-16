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
# CONFIGURAÇÃO DE SEGREDOS (.streamlit/secrets.toml)
# ==============================================================================
# Para que este aplicativo funcione localmente, crie uma pasta chamada '.streamlit'
# na mesma pasta raiz onde este arquivo 'app.py' está salvo. Dentro de '.streamlit',
# crie um arquivo chamado 'secrets.toml' contendo as suas credenciais no formato:
#
# [azure_openai]
# endpoint = "https://seu-recurso.services.ai.azure.com/"
# api_key = "sua_chave_de_api_aqui"
# deployment_name = "gpt-4.1-mini"
#
# Em ambiente de produção (Streamlit Community Cloud), você pode configurar
# essas mesmas variáveis na seção "Secrets" do painel de administração do app.
# ==============================================================================

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Extrator de Dados Inteligente | Azure OpenAI",
    page_icon="🧠",
    layout="centered",
)


# Função para carregar as credenciais de forma segura do st.secrets
def carregar_credenciais():
  try:
    endpoint = st.secrets["azure_openai"]["endpoint"]
    api_key = st.secrets["azure_openai"]["api_key"]
    deployment_name = st.secrets["azure_openai"]["deployment_name"]
    return endpoint, api_key, deployment_name
  except Exception:
    # Fallback didático caso o secrets.toml ainda não tenha sido configurado pelo aluno
    # (Utilizando os dados fornecidos no escopo da instrução)
    return (
        "https://marcelomaffeis-05082026-resource.services.ai.azure.com/",
        "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os",
        "gpt-4.1-mini",
    )


ENDPOINT, API_KEY, DEPLOYMENT_NAME = carregar_credenciais()

# Limpando possíveis caracteres indesejados na URL do endpoint (como &quot;)
ENDPOINT = ENDPOINT.replace("&quot;", "").strip()

# Inicialização do cliente AzureOpenAI oficial
client = AzureOpenAI(
    api_key=API_KEY,
    api_version="2024-08-01-preview",  # Versão recomendada para endpoints modernos do Foundry/Azure OpenAI
    azure_endpoint=ENDPOINT,
)

# ==============================================================================
# INTERFACE DO USUÁRIO (UI)
# ==============================================================================
st.title("🧠 Extrator de Dados Inteligente")
st.markdown(
    "Utilizando infraestrutura **Microsoft Azure OpenAI** para análise semântica"
    " avançada."
)

st.divider()

# Campo de texto para entrada
texto_usuario = st.text_area(
    "Digite ou cole o texto que deseja analisar:",
    placeholder=(
        "Ex: O cliente João Silva ligou extremamente irritado cobrando a entrega"
        " do pedido #4589 até amanhã às 14h."
    ),
    height=150,
)

# Botão de processamento
if st.button("Processar Texto", type="primary", use_container_width=True):
  if not texto_usuario.strip():
    st.warning("Por favor, digite algum texto antes de clicar em Processar.")
  else:
    with st.spinner(
        "Analisando texto com o modelo Azure OpenAI (GPT-4.1-mini)..."
    ):
      try:
        # Prompt de Sistema rígido exigindo formato estrito em JSON
        system_prompt = (
            "Você é um assistente especialista em extração de dados e análise"
            " de texto. Sua tarefa é analisar o texto fornecido pelo usuário e"
            " retornar EXATAMENTE um objeto JSON válido (sem blocos de código"
            " markdown adicionais, sem texto extra antes ou depois), contendo"
            " as seguintes chaves:\n"
            "1. 'sentimento': string indicando o sentimento geral (ex: Positivo,"
            " Negativo, Neutro, etc.).\n"
            "2. 'porcentagem_sentimento': número inteiro de 0 a 100 indicando a"
            " intensidade ou grau de certeza daquele sentimento.\n"
            "3. 'assunto_principal': string resumindo o tema central do texto.\n"
            "4. 'pessoas_citadas': lista de strings contendo os nomes das"
            " pessoas mencionadas no texto (se houver, senão lista vazia []).\n"
            "5. 'nivel_de_urgencia': string estritamente com um destes três"
            " valores: 'Baixo', 'Medio' ou 'Alto'."
        )

        # Chamada à API utilizando a biblioteca oficial do OpenAI configurada para Azure
        response = client.chat.completions.create(
            model=DEPLOYMENT_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": texto_usuario},
            ],
            response_format={"type": "json_object"},  # Força resposta em JSON
            temperature=0.1,  # Baixa temperatura para respostas determinísticas
        )

        # Extração do conteúdo JSON retornado pela API
        resposta_bruta = response.choices[0].message.content
        dados_json = json.loads(resposta_bruta)

        st.success("Análise concluída com sucesso!")
        st.divider()

        # ======================================================================
        # EXIBIÇÃO ESTRUTURADA NA TELA
        # ======================================================================
        st.subheader("📊 Resultados da Análise")

        # Exibição usando st.metric para destaque visual
        col1, col2, col3 = st.columns(3)

        with col1:
          st.metric(
              label="Sentimento",
              value=dados_json.get("sentimento", "N/A"),
          )

        with col2:
          porcentagem = dados_json.get("porcentagem_sentimento", 0)
          st.metric(label="Intensidade", value=f"{porcentagem}%")

        with col3:
          urgencia = dados_json.get("nivel_de_urgencia", "Baixo")
          # Cores visuais dinâmicas baseadas na urgência (apenas estética complementar)
          st.metric(label="Nível de Urgência", value=urgencia)

        # Assunto Principal e Pessoas Citadas
        st.markdown(f"**📌 Assunto Principal:**")
        st.info(dados_json.get("assunto_principal", "Não identificado"))

        st.markdown(f"**👥 Pessoas Citadas:**")
        pessoas = dados_json.get("pessoas_citadas", [])
        if pessoas:
          for pessoa in pessoas:
            st.markdown(f"- {pessoa}")
        else:
          st.write("Nenhuma pessoa citada no texto.")

        # Exibição do JSON bruto completo colapsável para auditoria técnica
        with st.expander("Ver JSON Bruto Retornado pela API"):
          st.json(dados_json)

      except Exception as e:
        st.error(
            "Ocorreu um erro ao processar a requisição com o Azure OpenAI."
        )
        st.exception(e)
