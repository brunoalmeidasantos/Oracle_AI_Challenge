"""Configurações do assistente BimBam Buy. Edite aqui (ou use as variáveis de ambiente indicadas)."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

# Pasta com os documentos (PDF, DOCX, TXT, MD, CSV). Para trocar, altere esta linha ou defina BIMBAM_DOCUMENTOS.
PASTA_DOCUMENTOS = Path(os.getenv(
    "BIMBAM_DOCUMENTOS",
    r"D:\bruno\Cursos_e_Materiais\Curso_ALURA_ONE_IA\Challenge_Documentos\BimBam Buy Documentos",
))
# Se a pasta acima não existir (ex.: outro computador), usa a pasta "documentos" ao lado do código.
PASTA_DOCUMENTOS_RESERVA = BASE_DIR / "documentos"

# Ollama e modelo de IA local.
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODELO = os.getenv("BIMBAM_MODELO", "qwen2.5:7b")  # se o PC for fraco, tente "qwen2.5:3b"

# Contatos do SAC (fictício: troque pelo número oficial e email).
WHATSAPP_SAC = "+55 11 99999-9999"
Email = "sac@bimbambuy.com.br"
MENSAGEM_NAO_ENCONTRADO = f"Informação não encontrada. Entre em contato com nosso SAC pelo WhatsApp: {WHATSAPP_SAC} ou envie um email para: {Email}."

EXTENSOES_SUPORTADAS = {".pdf", ".docx", ".txt", ".md", ".csv"}

# Busca de trechos
TAMANHO_MAX_TRECHO = 800    # caracteres por trecho
QTD_TRECHOS = 7             # trechos enviados à IA
COBERTURA_MINIMA = 0.40     # fração (ponderada) dos termos da pergunta que o trecho precisa conter

# Sinônimos: ajudam a busca por palavras a achar o mesmo assunto escrito de outro jeito nos documentos.
# Formato: "palavra da pergunta": "palavras equivalentes nos documentos". Acrescente os seus à vontade.
SINONIMOS = {
    "prazo": "horas dias",
    "comunicar": "relatar informar avisar registrar",
    "comunicacao": "relato registro",
    "modalidades": "tipos",
    "condicoes": "cobertura exclusoes",
    "aceita": "disponiveis aceitar",
    "valor": "custo preco",
    "custo": "valor preco",
}

# Modelo
TEMPO_LIMITE_SEGUNDOS = 300
CONTEXTO_TOKENS = 4096
