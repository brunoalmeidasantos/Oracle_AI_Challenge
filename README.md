# BimBam Buy – Assistente Inteligente de Atendimento

## 1. Descrição geral
Assistente virtual em Python, executado no terminal, que responde perguntas de clientes **exclusivamente com base nos
documentos da BimBam Buy** (manuais, políticas, FAQs). Ele lê os arquivos de uma pasta local, encontra os trechos
relacionados à pergunta e pede a um modelo de IA **local** (Ollama) que redija a resposta em português, citando o documento de origem.

Regras centrais:
- Não usa conhecimento externo, não inventa prazos, valores ou procedimentos e não faz suposições.
- Se a informação não estiver nos documentos, mostra **somente** a mensagem do SAC (número configurável) e email (configurável).
- Funciona offline, sem APIs pagas, sem nuvem, sem interface gráfica.

## 2. Arquitetura da solução
```
 Usuário (terminal)
        │ pergunta
        ▼
 ┌─────────────────────────── main.py ───────────────────────────┐
 │ 1. Leitura  : PDF · DOCX · TXT · MD · CSV  (pasta configurada) │
 │               recarrega sozinho quando há arquivo novo/alterado│
 │ 2. Trechos  : divisão por seção; sumário descartado            │
 │ 3. Busca    : palavras da pergunta × trechos (sem acento/plural│
 │               + sinônimos + peso por raridade do termo)        │
 │        │                                                       │
 │   nenhum trecho relevante ──────────────► mensagem do SAC      │
 │        │ (a IA nem é consultada)                               │
 │        ▼                                                       │
 │ 4. Ollama local (qwen2.5:7b): responde só com os trechos       │
 │        │                                                       │
 │   "NAO_ENCONTRADO" ─────────────────────► mensagem do SAC      │
 │        ▼                                                       │
 │ 5. Resposta em português + "Fonte: documento" (conferida)      │
 └────────────────────────────────────────────────────────────────┘
        ▲ config.py: pasta, modelo, WhatsApp do SAC, sinônimos
```
Há duas barreiras contra respostas inventadas: (1) sem trecho relevante a IA não é chamada; (2) a IA recebe só os trechos
encontrados e uma regra rígida para responder `NAO_ENCONTRADO` quando eles não bastarem. O nome do documento citado é
conferido contra os documentos realmente usados.

## 3. Tecnologias e ferramentas
| Item | Uso |
|---|---|
| Python 3.10+ | Linguagem do projeto |
| Ollama + `qwen2.5:7b` | Execução local do modelo de IA |
| `pypdf` | Leitura de PDF |
| `python-docx` | Leitura de DOCX |
| `csv` (biblioteca padrão) | Leitura de CSV |
| `requests` | Comunicação com o Ollama (HTTP local) |
| `unittest` | Testes automáticos |

## 4. Estrutura do projeto
```
bimbam-buy-ai/
├── main.py            # assistente: leitura, busca, Ollama e terminal
├── config.py          # pasta dos documentos, modelo, número do SAC, sinônimos
├── testes.py          # testes automáticos (não precisam do Ollama)
├── requirements.txt
├── documentos/        # pasta de reserva com 5 documentos de exemplo
└── README.md
```

## 5. Instruções para executar (Windows)
**1. Python** – instale o Python 3.10+ (python.org/downloads) marcando "Add Python to PATH".

**2. Ollama** – instale em ollama.com/download e deixe o aplicativo aberto.

**3. Modelo** – no Prompt de Comando:
```
ollama pull qwen2.5:7b
```
Computador fraco? Use `ollama pull qwen2.5:3b` e altere `MODELO` no `config.py`.

**4. Projeto** – na pasta `bimbam-buy-ai`:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

**5. Configuração (`config.py`)**
| O que | Variável |
|---|---|
| Pasta dos documentos | `PASTA_DOCUMENTOS` (já aponta para `D:\bruno\Cursos_e_Materiais\Curso_ALURA_ONE_IA\Challenge_Documentos\BimBam Buy Documentos`; se não existir, usa `documentos\`) |
| Modelo de IA | `MODELO` (ou variável de ambiente `BIMBAM_MODELO`) |
| Email da empresa | `Email` (hoje fictício: troque pelo oficial) |
| WhatsApp do SAC | `WHATSAPP_SAC` (hoje fictício: troque pelo oficial) |
| Palavras equivalentes | `SINONIMOS` |

**6. Testes (opcional)** – `python testes.py` (14 testes; o modelo é simulado).

**7. Executar** – `python main.py`. Digite a pergunta; `SAIR` encerra.
Para incluir novos documentos, copie o arquivo (PDF, DOCX, TXT, MD ou CSV) para a pasta: ele é lido na pergunta seguinte, sem mexer no código.

## 6. Exemplos de perguntas que o agente consegue responder
(com base nos documentos de exemplo da BimBam Buy)
- Qual é o prazo para comunicar um produto danificado?
- Quais são as condições de garantia?
- Quais são as modalidades de envio?
- A empresa aceita pagamento por boleto?
- Quanto tempo demora um reembolso aprovado?
- Qual o prazo para solicitar devolução por arrependimento?

## 7. Exemplos de respostas geradas
> A redação exata é gerada pelo modelo e pode variar um pouco a cada execução; o conteúdo vem sempre dos documentos.
> Os exemplos abaixo mostram o formato esperado e o conteúdo documentado em cada caso.

```text
BimBam Buy - Assistente Virtual

Digite sua pergunta (ou SAIR para encerrar):
> Qual é o prazo para comunicar um produto danificado?

Resposta:
Se o produto chegou danificado, o caso deve ser relatado dentro de 48 horas após o recebimento.

Fonte: Manual_de_Garantia_de_Produtos_da_BimBam_Buy.txt
```
```text
> Quais são as condições de garantia?

Resposta:
A garantia pode cobrir falha ao ligar, mau funcionamento de componentes, defeitos de montagem e problemas de
fabricação não causados pelo cliente. Não cobre danos por golpes ou quedas, umidade, água, calor excessivo ou fogo,
manipulação por terceiros não autorizados, entre outras exclusões. O prazo de garantia varia conforme o produto e o
país, e é o informado na ficha do produto ou na confirmação de compra.

Fonte: Manual_de_Garantia_de_Produtos_da_BimBam_Buy.txt
```
```text
> Quais são as modalidades de envio?

Resposta:
Os tipos de envio são: envio padrão, envio expresso (apenas em áreas e categorias habilitadas), envio agendado,
retirada em ponto autorizado (onde habilitada), reenvio por incidência e coleta de devolução.

Fonte: Guia_de_Prazos_e_Custos_de_Envio_da_BimBam_Buy.txt
```
```text
> A empresa aceita pagamento por boleto?

Resposta:
Sim. O boleto está entre os métodos de pagamento que a BimBam Buy pode aceitar, mas a disponibilidade
varia conforme o país, a categoria e o valor da compra.

Fonte: Perguntas_frequentes_sobre_metodos_de_pagamento.txt
```

## 8. Resposta quando a pergunta não tem resposta nos documentos
Resposta **exata e única** (esta é fixa no código, não depende do modelo):
```text
> Qual a cor do uniforme dos entregadores?

Resposta:
Informação não encontrada. Entre em contato com nosso SAC pelo WhatsApp: +55 11 99999-9999 ou nos envie um Email para sac@bimbambuy.com.br.
```
Isso ocorre quando nenhum trecho dos documentos é relevante para a pergunta (a IA nem é consultada) ou quando a IA
conclui que os trechos não respondem. O número é fictício e é alterado em `WHATSAPP_SAC` no `config.py`.

## 9. Testes realizados
`python testes.py` verifica, entre outros pontos:
- as 4 perguntas do enunciado encontram os trechos corretos (seções "13. Garantia e danos em trânsito", "6. Cobertura geral", "4. Tipos de envio", "3. Métodos de pagamento disponíveis");
- 4 perguntas sem resposta (cor do uniforme, loja física, CEO, horário do SAC) devolvem exatamente a mensagem do SAC **sem chamar a IA**;
- a fonte citada é sempre um documento real; fonte inventada pelo modelo é substituída;
- leitura de TXT, MD, CSV, DOCX e PDF; arquivo corrompido ou vazio gera aviso e não derruba os demais;
- detecção de documento novo sem alterar o código.

Nos testes automáticos o modelo é simulado. A qualidade do texto do `qwen2.5:7b` só é verificada rodando `python main.py` no seu computador.

## 10. Limitações
- A busca é por **palavras**, não por significado: se a pergunta usar termos muito diferentes dos documentos ("avisar" × "relatar"), pode não achar o trecho e responder com a mensagem do SAC. Acrescente o par em `SINONIMOS`.
- Perguntas que misturam vários assuntos podem trazer só parte dos trechos (limite `QTD_TRECHOS`).
- PDFs escaneados (imagem) não são lidos (sem OCR).
- Os documentos de exemplo apresentam pequenas variações entre si (ex.: 48 horas "após a entrega" na política de devoluções e "após o recebimento" no manual de garantia); o assistente não resolve conflitos entre documentos.
