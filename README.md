# BimBam Buy – Assistente Virtual (terminal)

Responde perguntas **somente** com base nos documentos da pasta configurada. Sem site, sem nuvem, sem APIs pagas:
roda no seu computador com o modelo `qwen2.5:7b` do Ollama.
Se a informação não estiver nos documentos, mostra **apenas**:
`Informação não encontrada. Entre em contato com nosso SAC pelo WhatsApp: +55 11 99999-9999 ou envie um email para: sac@bimbambuy.com.br.`

## Estrutura
```
bimbam-buy-ai/
├── main.py            # o assistente (leitura, busca, Ollama, terminal)
├── config.py          # pasta, modelo, número do SAC, sinônimos
├── testes.py          # testes automáticos (não precisam do Ollama)
├── requirements.txt
├── documentos/        # pasta de reserva (5 documentos de exemplo da BimBam Buy, em .txt)
└── README.md
```

## Instalação (Windows)
1. **Python 3.10+**: https://www.python.org/downloads/ (marque "Add Python to PATH").
2. **Ollama**: https://ollama.com/download → instale e deixe aberto (ícone na bandeja).
3. Baixe o modelo (vários GB, uma vez só). No Prompt de Comando:
   ```
   ollama pull qwen2.5:7b
   ```
   Computador fraco (menos de ~8 GB de RAM livre) ou muito lento? Use `ollama pull qwen2.5:3b` e troque `MODELO` no `config.py`.
4. Na pasta do projeto:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

## Configuração (`config.py`)
| O que | Onde |
|---|---|
| Pasta dos documentos | `PASTA_DOCUMENTOS` (já aponta para `D:\bruno\Cursos_e_Materiais\Curso_ALURA_ONE_IA\Challenge_Documentos\BimBam Buy Documentos`). Se essa pasta não existir, usa `documentos\` ao lado do código. |
| Modelo | `MODELO` (ou variável `BIMBAM_MODELO`) |
| WhatsApp do SAC | `WHATSAPP_SAC` (hoje fictício: troque pelo oficial) |
| Email do SAC | `Email` (hoje fictício: troque pelo oficial) |
| Palavras equivalentes | `SINONIMOS` (ex.: "comunicar" ↔ "relatar") |

## Executar
```
python main.py
```
```
BimBam Buy - Assistente Virtual

Digite sua pergunta (ou SAIR para encerrar):
> Qual é o prazo para comunicar um produto danificado?

Resposta:
O caso deve ser relatado dentro de 48 horas após o recebimento.

Fonte: Manual_de_Garantia_de_Produtos_da_BimBam_Buy.txt
```
(texto ilustrativo: a redação exata vem do modelo, mas o conteúdo vem do documento).
Para adicionar documentos, copie PDF/DOCX/TXT/MD/CSV para a pasta: são detectados na próxima pergunta, sem reiniciar nem mexer no código.
Um arquivo ilegível (corrompido, PDF escaneado) gera um aviso e é ignorado; os demais continuam funcionando.

## Testes
```
python testes.py
```
Cobrem as quatro perguntas do enunciado, perguntas sem resposta (devem dar exatamente a mensagem do SAC **sem chamar o modelo**),
formato/fonte da resposta e leitura de TXT, MD, CSV, DOCX e PDF. O modelo é simulado; a qualidade do texto do `qwen2.5:7b` real só se vê rodando `main.py`.

## Como funciona e limites
1. Lê os documentos e divide em trechos por seção.
2. Procura os trechos com mais palavras da pergunta (ignorando acentos e variações como plural; com sinônimos configuráveis).
3. Sem trecho suficiente → mensagem do SAC (a IA nem é consultada). Com trechos → envia só eles ao modelo, com regras rígidas.
4. Se o modelo responder `NAO_ENCONTRADO`, mostra a mensagem do SAC. A fonte citada é conferida contra os documentos reais.

**Limite importante:** a busca é por palavras, não por significado. Se a pergunta usa termos bem diferentes dos documentos
(ex.: "avisar" × "relatar"), ela pode não achar o trecho e dará a mensagem do SAC mesmo havendo resposta. Solução simples: acrescentar o par em `SINONIMOS`.
Se isso acontecer muito, o próximo passo seria busca semântica com embeddings (modelo `bge-m3` do Ollama), a um custo maior de complexidade.
PDFs escaneados (imagem) não são lidos (sem OCR). Perguntas sobre vários assuntos ao mesmo tempo podem trazer só parte dos trechos (limite `QTD_TRECHOS`).
