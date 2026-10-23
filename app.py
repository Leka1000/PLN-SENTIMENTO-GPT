import json
import streamlit as st
from openai import AzureOpenAI

# ==============================================================================
# 3. FUNÇÃO DE PROCESSAMENTO DE IA (CORRIGIDA)
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
            {"role": "user", "content": texto}
        ],
        response_format={"type": "json_object"},
        temperature=0.2
    )

    return json.loads(response.choices[0].message.content)
