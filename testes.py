"""Testes automáticos (não precisam do Ollama: o modelo é simulado).
Rodar:  python testes.py
Validam: leitura de arquivos, busca dos trechos, mensagem do SAC e formato da resposta.
NÃO validam a qualidade do texto gerado pelo qwen2.5:7b real: para isso, use o terminal (python main.py)."""
import tempfile
import unittest
from pathlib import Path

import config
import main

SAC = config.MENSAGEM_NAO_ENCONTRADO
DOCS, TRECHOS = None, None


def base():
    global DOCS, TRECHOS
    if TRECHOS is None:
        DOCS, TRECHOS, _ = main.montar_base(config.PASTA_DOCUMENTOS_RESERVA)
    return TRECHOS


def titulos(pergunta):
    return [texto.splitlines()[0] for _, texto in main.buscar_trechos(pergunta, base())]


class ModeloFalso:
    """Simula o Ollama e guarda o que recebeu."""
    def __init__(self, resposta):
        self.resposta, self.chamadas = resposta, []

    def __call__(self, pergunta, trechos):
        self.chamadas.append((pergunta, trechos))
        return self.resposta


class PerguntasComResposta(unittest.TestCase):
    def test_prazo_produto_danificado(self):
        self.assertTrue(any(t.startswith("13. Garantia e danos em trânsito") for t in titulos(
            "Qual é o prazo para comunicar um produto danificado?")))
        # o trecho recuperado contém o prazo documentado
        trechos = main.buscar_trechos("Qual é o prazo para comunicar um produto danificado?", base())
        self.assertTrue(any("48 horas" in texto for _, texto in trechos))

    def test_condicoes_de_garantia(self):
        self.assertIn("6. Cobertura geral", titulos("Quais são as condições de garantia?"))

    def test_modalidades_de_envio(self):
        self.assertIn("4. Tipos de envio", titulos("Quais são as modalidades de envio?"))

    def test_pagamento_por_boleto(self):
        trechos = main.buscar_trechos("A empresa aceita pagamento por boleto?", base())
        self.assertTrue(any("Boleto" in texto for _, texto in trechos))


class PerguntasSemResposta(unittest.TestCase):
    PERGUNTAS = ["Qual a cor do uniforme dos entregadores?", "A empresa tem loja física em Curitiba?",
                 "Quem é o CEO da BimBam Buy?", "Qual o horário de funcionamento do SAC?"]

    def test_mensagem_exata_do_sac_e_modelo_nao_chamado(self):
        for pergunta in self.PERGUNTAS:
            modelo = ModeloFalso("qualquer coisa")
            self.assertEqual(main.responder(pergunta, base(), modelo), SAC, pergunta)
            self.assertEqual(modelo.chamadas, [], f"o modelo não deveria ser chamado: {pergunta}")

    def test_modelo_diz_que_nao_sabe(self):
        modelo = ModeloFalso("NAO_ENCONTRADO")
        resposta = main.responder("Qual é o prazo para comunicar um produto danificado?", base(), modelo)
        self.assertEqual(resposta, SAC)
        self.assertEqual(len(modelo.chamadas), 1)

    def test_mensagem_configuravel(self):
        self.assertIn(config.WHATSAPP_SAC, SAC)
        self.assertTrue(SAC.startswith("Informação não encontrada. Entre em contato com nosso SAC pelo WhatsApp:"))


class FormatoDaResposta(unittest.TestCase):
    def test_fonte_real_e_mantida(self):
        pergunta = "Qual é o prazo para comunicar um produto danificado?"
        nomes = {n for n, _ in main.buscar_trechos(pergunta, base())}
        nome = sorted(nomes)[0]
        resposta = main.responder(pergunta, base(), ModeloFalso(f"O prazo é de 48 horas.\nFonte: {nome}"))
        self.assertEqual(resposta, f"O prazo é de 48 horas.\n\nFonte: {nome}")

    def test_fonte_inventada_e_trocada_por_documento_real(self):
        resposta = main.responder("A empresa aceita pagamento por boleto?", base(),
                                  ModeloFalso("Sim, boleto.\nFonte: documento_que_nao_existe.pdf"))
        self.assertIn("Fonte: Perguntas_frequentes_sobre_metodos_de_pagamento.txt", resposta)
        self.assertNotIn("nao_existe", resposta)

    def test_resposta_sem_linha_de_fonte_ganha_uma(self):
        resposta = main.responder("A empresa aceita pagamento por boleto?", base(), ModeloFalso("Sim, boleto."))
        self.assertTrue(resposta.startswith("Sim, boleto.\n\nFonte: "))


class LeituraDeArquivos(unittest.TestCase):
    def setUp(self):
        self._t = tempfile.TemporaryDirectory()
        self.pasta = Path(self._t.name)

    def tearDown(self):
        self._t.cleanup()

    def test_txt_md_csv_docx(self):
        (self.pasta / "a.txt").write_text("1. Troca\nTroca em 7 dias.", encoding="utf-8")
        (self.pasta / "b.md").write_text("# Frete\nFrete grátis acima de 200.", encoding="utf-8")
        (self.pasta / "c.csv").write_text("produto;prazo\nTênis;5 dias\n", encoding="utf-8")
        from docx import Document
        doc = Document()
        doc.add_paragraph("Garantia de 90 dias.")
        doc.save(str(self.pasta / "d.docx"))
        documentos, avisos = main.carregar_documentos(self.pasta)
        textos = {nome: texto for nome, texto in documentos}
        self.assertEqual(avisos, [])
        self.assertIn("produto: Tênis | prazo: 5 dias", textos["c.csv"])
        self.assertIn("Garantia de 90 dias.", textos["d.docx"])
        self.assertEqual(len(documentos), 4)

    def test_arquivo_com_problema_nao_derruba_os_outros(self):
        (self.pasta / "quebrado.pdf").write_bytes(b"isto nao e pdf")
        (self.pasta / "ok.txt").write_text("Texto válido sobre trocas.", encoding="utf-8")
        (self.pasta / "vazio.txt").write_text("   ", encoding="utf-8")
        (self.pasta / "ignorado.exe").write_bytes(b"MZ")
        documentos, avisos = main.carregar_documentos(self.pasta)
        self.assertEqual([n for n, _ in documentos], ["ok.txt"])
        self.assertEqual(len(avisos), 2)
        self.assertTrue(any("quebrado.pdf" in a for a in avisos))

    def test_pdf_real(self):
        try:
            from reportlab.pdfgen import canvas
        except ImportError:
            self.skipTest("reportlab não instalado (opcional, só para este teste)")
        pdf = canvas.Canvas(str(self.pasta / "p.pdf"))
        pdf.drawString(50, 750, "Prazo de troca: 7 dias corridos.")
        pdf.save()
        documentos, _ = main.carregar_documentos(self.pasta)
        self.assertIn("Prazo de troca", documentos[0][1])

    def test_novo_documento_e_detectado_sem_mudar_codigo(self):
        antes = main.assinatura_pasta(self.pasta)
        (self.pasta / "novo.txt").write_text("Novo documento.", encoding="utf-8")
        self.assertNotEqual(antes, main.assinatura_pasta(self.pasta))


if __name__ == "__main__":
    unittest.main(verbosity=2)
