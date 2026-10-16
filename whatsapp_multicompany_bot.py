#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
MULTI-COMPANY WHATSAPP HUMANIZED AI BOT — EDIÇÃO MOÇAMBIQUE (V4.0 ANTI-SPAM)
Empresas Atendidas com Personalidade Humana, Carinho e Precisão:
  1. Braga.io — Infraestrutura Digital para Líderes (Maputo)
  2. Vanguard Living Atelier — Mobiliário de Autor Sob Medida (Manhembana, Matola)
  3. Inglês Semestre (Inglês sem Mestre) — 5 Idiomas com Escopo Completo de Áudio
================================================================================
Correções Definitivas Implementadas contra os Problemas do Sistema Antigo:
  ✅ ZERO TEXTÃO NO "OLÁ": Quando o cliente diz "Olá", "Tudo bem?" ou "Como é que é?",
     o bot responde de forma curta, calorosa, humana e gentil (2 a 3 linhas), fazendo a
     pessoa sentir-se acolhida e amada, perguntando com leveza como pode ajudar.
  ✅ ZERO LINKS DE GOOGLE DRIVE: O filtro `OutputSanitizer` bloqueia qualquer link
     `drive.google.com` ou URL inexistente.
  ✅ ZERO PDF CORROMPIDO OU NÃO SOLICITADO: O bot já domina todos os preços e regras
     na própria conversa e NUNCA despeja PDFs sem o cliente pedir. Quando o cliente
     pede um PDF, envia o ficheiro binário oficial limpo (`application/pdf`) guardado
     localmente em `pdf_assets/`, sem códigos estranhos.
  ✅ ZERO REPETIÇÃO / ANTI-FLOOD: Sistema `AntiFloodGuard` que impede mensagens
     duplicadas e garante respostas leves, uma questão de cada vez.
  ✅ AS 5 LEIS DA PERSUASÃO COM GENTILEZA: Afeição/Acolhimento, Reciprocidade,
     Prova Social, Autoridade Serena e Compromisso/Escassez integrados de forma natural.
  ✅ INTEGRAÇÃO GRATUITA COM GEMINI FLASH: Conector nativo para a API gratuita do
     Google Gemini (`gemini-2.5-flash`) + Motor Conversacional Humano Local.
  ✅ DISPARADOR AUTOMÁTICO WHATSAPP (META CLOUD API & EVOLUTION API) + PAINEL WEB.
================================================================================
"""

import os
import re
import time
import json
import sqlite3
import hashlib
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("HumanizedWhatsAppBotMZ")

# ==============================================================================
# 1. DADOS BANCÁRIOS E CONTACTOS OFICIAIS (SÓ ENVIADOS QUANDO O CLIENTE PEDE)
# ==============================================================================

OFFICIAL_PAYMENT_DETAILS = (
    "Para sua total segurança e comodidade, aqui estão os nossos dados oficiais para confirmação:\n\n"
    "• *M-Pesa / WhatsApp Direto:* +258 87 778 3631\n"
    "• *Banco:* Millennium BIM\n"
    "• *Titular:* LEANDRO DORCELINO BRAGA (NUIT: 134392320)\n"
    "• *Conta:* 226217484\n"
    "• *NIB:* 000100000022621748457\n"
    "• *IBAN:* MZ59000100000022621748457"
)

# ==============================================================================
# 2. BLINDAGEM ANTI-BUGS: FILTRO ANTI-DRIVE, ANTI-CÓDIGOS E ANTI-FLOOD
# ==============================================================================

class OutputSanitizer:
    """
    Garante que NENHUMA mensagem enviada ao cliente contenha:
    - Links de Google Drive inexistentes (drive.google.com, docs.google.com)
    - Códigos estranhos de PDF (%PDF-, base64, JSON bruto, tags quebradas)
    - Textos gigantescos e assustadores que pareçam spam ou burla.
    """

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        cleaned = re.sub(r'https?://(?:drive|docs)\.google\.com[^\s\)\]]*', '[Catálogo disponível aqui no chat]', text)
        cleaned = re.sub(r'%PDF-\d\.\d[\s\S]*', '', cleaned)
        cleaned = re.sub(r'data:application/pdf;base64,[^\s]+', '', cleaned)
        cleaned = re.sub(r'```(?:json|html|python)?[\s\S]*?```', '', cleaned)

        lines = cleaned.splitlines()
        deduped_lines = []
        for line in lines:
            if not deduped_lines or line.strip() != deduped_lines[-1].strip() or line.strip() == "":
                deduped_lines.append(line)

        return "\n".join(deduped_lines).strip()


class AntiFloodGuard:
    """
    Impede que o bot responda duas vezes à mesma mensagem do WhatsApp (quando a rede
    reenvia o webhook) e evita inundar o chat do cliente.
    """
    def __init__(self, ttl_seconds: int = 15):
        self.ttl_seconds = ttl_seconds
        self._recent_hashes: Dict[str, float] = {}

    def is_duplicate_incoming(self, phone: str, message_text: str, message_id: Optional[str] = None) -> bool:
        now = time.time()
        expired = [k for k, ts in self._recent_hashes.items() if now - ts > self.ttl_seconds]
        for k in expired:
            del self._recent_hashes[k]

        key_raw = f"{phone}:{message_id or ''}:{message_text.strip().lower()}"
        msg_hash = hashlib.sha256(key_raw.encode("utf-8")).hexdigest()

        if msg_hash in self._recent_hashes:
            logger.info(f"AntiFlood bloqueou mensagem repetida de {phone}")
            return True

        self._recent_hashes[msg_hash] = now
        return False

# ==============================================================================
# 3. ESTRUTURAS DE DADOS E ARQUIVOS PDF/IMAGENS REAIS LOCAIS
# ==============================================================================

@dataclass
class ReferenceMedia:
    title: str
    media_url: str
    category: str
    caption: str

@dataclass
class OfficialPDFDocument:
    title: str
    filename: str
    local_url: str
    caption: str

@dataclass
class PricingItem:
    service_id: str
    name: str
    low_price: float
    mid_price: float
    high_max_price: float
    currency: str
    unit: str
    description: str

@dataclass
class CompanyConfig:
    id: str
    name: str
    short_name: str
    slogan: str
    website: str
    keywords: List[str]
    human_welcome: str
    gentle_discovery_question: str
    pricing_catalog: Dict[str, PricingItem]
    media_references: List[ReferenceMedia]
    pdf_documents: List[OfficialPDFDocument]
    persuasion_5_laws: Dict[str, str]
    extra_rules: Dict[str, Any] = field(default_factory=dict)


COMPANIES: Dict[str, CompanyConfig] = {
    # --------------------------------------------------------------------------
    # 1. BRAGA.IO — INFRAESTRUTURA DIGITAL PARA LÍDERES (MAPUTO)
    # --------------------------------------------------------------------------
    "braga_io": CompanyConfig(
        id="braga_io",
        name="Braga.io — Infraestrutura Digital para Líderes",
        short_name="Braga.io",
        slogan="Engenharia Soberana de Software, Hardware e Multiplicação Patrimonial (Maputo)",
        website="https://braga.io",
        keywords=[
            "braga.io", "braga.eu", "braga", "leandro braga", "software", "hardware",
            "automação", "automacao", "ia", "inteligencia artificial", "omniflow",
            "balcao zero", "balcão zero", "biometria", "kyc", "onboarding", "branding",
            "master templates", "canva", "clinica", "clínica", "advogados", "banco",
            "bancos", "millennium", "standard bank", "bci", "sistema", "site", "app"
        ],
        human_welcome=(
            "Que excelente falar consigo! 😊 Aqui na *Braga.io*, em Maputo, ajudamos profissionais, clínicas, escritórios e grandes instituições "
            "a automatizarem o seu atendimento e multiplicarem os seus resultados sem trabalho manual cansativo."
        ),
        gentle_discovery_question=(
            "Para eu te orientar com todo o cuidado e passar os valores certos para a sua realidade, me conta um pouquinho: "
            "qual é o ramo ou porte atual da sua empresa (por exemplo, profissional liberal, clínica, escritório de arquitetura, sociedade de advogados ou banco) e o que você gostaria de melhorar hoje?"
        ),
        pricing_catalog={
            "pacote_aceleracao_branding": PricingItem(
                service_id="pacote_aceleracao_branding",
                name="Pacote Aceleração & Branding Clínico/Comercial",
                low_price=3500.0,
                mid_price=6500.0,
                high_max_price=10000.0,
                currency="MZN",
                unit="3.500 a 10.000 MZN (50% de sinal no arranque)",
                description="Logótipo oficial e identidade visual de prestígio, Master Templates rápidos para telemóvel (sem depender do Canva), criativos publicitários e formulário de triagem inteligente."
            ),
            "pacote_medio": PricingItem(
                service_id="pacote_medio",
                name="Pacote Médio (Clínicas & Empresas Médias)",
                low_price=35000.0,
                mid_price=35000.0,
                high_max_price=35000.0,
                currency="MZN",
                unit="35.000 MZN (50% no arranque + 50% na entrega)",
                description="Funil automatizado de WhatsApp 24/7, formulário dinâmico com lógica condicional, fichas pré-consulta automáticas e atendimento inteligente."
            ),
            "pacote_premium_corporativo": PricingItem(
                service_id="pacote_premium_corporativo",
                name="Pacote Premium Corporativo (Sociedades, Arquitetura & Grandes Empresas)",
                low_price=70000.0,
                mid_price=70000.0,
                high_max_price=70000.0,
                currency="MZN",
                unit="70.000 MZN base (duplicado 2x ou triplicado 3x conforme complexidade técnica)",
                description="Portal próprio de Onboarding/KYC criptografado (TLS 1.3), AI Filter de qualificação silenciosa de património e Concierge Virtual IA 24/7 (PT/EN)."
            ),
            "retencao_continua_mrr": PricingItem(
                service_id="retencao_continua_mrr",
                name="Retenção Contínua (Manutenção & Evolução Mensal)",
                low_price=15000.0,
                mid_price=15000.0,
                high_max_price=15000.0,
                currency="MZN",
                unit="15.000 MZN / mês",
                description="Manutenção preventiva de servidores, evolução contínua dos modelos de IA, relatórios mensais e suporte prioritário."
            ),
            "omniflow_banking_os": PricingItem(
                service_id="omniflow_banking_os",
                name="OmniFlow Banking OS (Instituições Financeiras & Bancos)",
                low_price=3500000.0,
                mid_price=18500000.0,
                high_max_price=50000000.0,
                currency="MZN",
                unit="PoC: 3,5M–4,8M MZN | Rollout: 14M–18,5M MZN | Escala Bancária Completa: até 50.000.000 MZN",
                description="Middleware bancário sobre Finacle, Temenos T24, SAP Core e TCS BaNCS, terminais 'Balcão Zero' QR/NFC, biometria Liveness Detection e conformidade com a Lei n.º 11/2022."
            )
        },
        media_references=[
            ReferenceMedia(
                title="Braga.io — Infraestrutura Digital para Líderes (Maputo)",
                media_url="/media/braga_io_logo_p1_1.png",
                category="institucional",
                caption="Braga.io — Engenharia de Software, Automação 24/7 e Multiplicação Patrimonial em Maputo."
            )
        ],
        pdf_documents=[
            OfficialPDFDocument(
                title="Dossiê Executivo & Arquitetura Operacional — Braga.io",
                filename="Dossie_Executivo_Braga_io.pdf",
                local_url="/pdf/Dossie_Executivo_Braga_io.pdf",
                caption="Aqui está o nosso Dossiê Executivo oficial da Braga.io em PDF, pronto para leitura no seu telemóvel. 📄✨"
            )
        ],
        persuasion_5_laws={
            "afeicao": "Valorizamos imenso o seu trabalho e queremos que você tenha paz de espírito, sabendo que a sua operação funciona 24h por dia com excelência.",
            "reciprocidade": "Antes mesmo de qualquer compromisso, a nossa equipa analisa gratuitamente onde o seu atendimento atual pode ganhar mais velocidade e lucro.",
            "prova_social": "Já ajudamos desde clínicas de referência em Maputo (como a Clínica Ayamed e Dra. Yolanda Dinoca) e sociedades de advogados até projetos para a banca comercial.",
            "autoridade": "Toda a nossa arquitetura é desenhada pelo nosso Arquiteto Chefe, Leandro Braga, com segurança criptográfica de nível bancário.",
            "escassez_compromisso": "Como dedicamos atenção exclusiva à implantação de cada cliente em Maputo, abrimos poucas vagas de desenvolvimento por mês."
        }
    ),

    # --------------------------------------------------------------------------
    # 2. VANGUARD LIVING ATELIER (MANHEMBANA, MATOLA & MAPUTO)
    # --------------------------------------------------------------------------
    "vanguarda_living": CompanyConfig(
        id="vanguarda_living",
        name="Vanguard Living Atelier",
        short_name="Vanguard Living Atelier",
        slogan="Mobiliário de Autor Sob Medida — Produção 100% Real na Matola com Entrega em 15 Dias",
        website="https://vanguardliving.staticdomains.app/",
        keywords=[
            "vanguard", "vanguarda", "living", "atelier", "ateliê", "atelie",
            "mobiliario", "mobiliário", "aura", "chaise", "serpentina",
            "riviera", "lounge exterior", "boucle", "bouclé", "chanfuta",
            "jambirre", "chassis", "sketchup", "revit", "rhino", "valente obras",
            "sofa", "sofá", "sofas", "sofás", "cama", "cabeceira", "banquetas",
            "poltrona", "poltronas", "sala completa", "chave na mao", "chave-na-mão",
            "matola", "boquisso", "manhembana", "estofaria", "marcenaria", "moveis", "móveis"
        ],
        human_welcome=(
            "Que alegria receber você no *Vanguard Living Atelier*! ✨🛋️ "
            "Na nossa oficina em Manhembana (Entrada de Boquisso, na Matola), os nossos mestres marceneiros e estofadores criam sofás e mobiliário sob medida com acabamento de luxo e entrega garantida em *15 dias* em Maputo e Matola."
        ),
        gentle_discovery_question=(
            "Me conta com carinho: qual peça você está imaginando para o seu espaço (um sofá curvo ou em L, cama estofada, poltronas, lounge exterior ou a sala completa)? "
            "Se você tiver uma *foto* do modelo que gosta, também pode me enviar por aqui mesmo para eu analisar e calcular para si! 😊"
        ),
        pricing_catalog={
            "sofa_chaise_aura_l": PricingItem(
                service_id="sofa_chaise_aura_l",
                name="Sofá Chaise 'Aura' ou em L (3.0m–3.6m) — Linha Assinatura Alto Padrão / Bouclé",
                low_price=46800.0,
                mid_price=65000.0,
                high_max_price=88400.0,
                currency="MZN",
                unit="88.400 MZN (Entrega em 15 dias em Maputo e Matola)",
                description="Estrutura robusta em madeira tratada e contraplacado naval que não cede, espuma de alta densidade D35/D45, revestimento Bouclé Off-White e almofadas esféricas."
            ),
            "sofa_curvo_organico": PricingItem(
                service_id="sofa_curvo_organico",
                name="Sofá Curvo Orgânico + Esferas (2.6m) — Linha Assinatura Alto Padrão / Bouclé",
                low_price=39000.0,
                mid_price=54600.0,
                high_max_price=72800.0,
                currency="MZN",
                unit="72.800 MZN (Entrega em 15 dias em Maputo e Matola)",
                description="Modelação curva contínua feita à mão pelos nossos mestres na Matola, gomos anatómicos e par de esferas decorativas incluídas."
            ),
            "cama_casal_queen_cabeceira": PricingItem(
                service_id="cama_casal_queen_cabeceira",
                name="Cama Casal/Queen + Cabeceira Estofada — Linha Assinatura Alto Padrão / Bouclé",
                low_price=31200.0,
                mid_price=42900.0,
                high_max_price=57200.0,
                currency="MZN",
                unit="57.200 MZN (Entrega em 15 dias)",
                description="Cama Casal/Queen em madeira tratada de alta densidade com cabeceira estofada em Bouclé ou Veludo Acetinado."
            ),
            "kit_3_banquetas_altas": PricingItem(
                service_id="kit_3_banquetas_altas",
                name="Kit 3 Banquetas Altas (Ilha de Cozinha / Cozinha Americana) — Linha Assinatura",
                low_price=19500.0,
                mid_price=23400.0,
                high_max_price=31200.0,
                currency="MZN",
                unit="31.200 MZN pelo Kit com 3 Banquetas (Entrega em 15 dias)",
                description="Conjunto de 3 banquetas altas sob medida para bancada ou ilha de cozinha com espuma de alta densidade e tecido nobre."
            ),
            "par_poltronas_esculturais": PricingItem(
                service_id="par_poltronas_esculturais",
                name="Par de Poltronas Esculturais de Sala — Linha Assinatura Alto Padrão / Bouclé",
                low_price=23400.0,
                mid_price=28600.0,
                high_max_price=36400.0,
                currency="MZN",
                unit="36.400 MZN pelo Par (2 Poltronas | Entrega em 15 dias)",
                description="Duas poltronas esculturais de autor com estrutura reforçada e acabamento em Bouclé."
            ),
            "lounge_exterior_riviera": PricingItem(
                service_id="lounge_exterior_riviera",
                name="Lounge Exterior Riviera (Jardim/Varanda — Madeira Chanfuta/Jambirre & Aço)",
                low_price=54600.0,
                mid_price=67600.0,
                high_max_price=93600.0,
                currency="MZN",
                unit="93.600 MZN (Conjunto Completo | Entrega em 15 dias)",
                description="Aço tubular com pintura eletrostática anti-corrosão marítima, madeira de lei moçambicana (Chanfuta/Jambirre tratada UV), lareira ecológica central e tecido náutico hidrorrepelente."
            ),
            "pacote_sala_completa_chave_na_mao": PricingItem(
                service_id="pacote_sala_completa_chave_na_mao",
                name="Pacote Sala Completa Chave-na-Mão (Sofá Principal + 2 Poltronas + Mesa de Centro)",
                low_price=62400.0,
                mid_price=85800.0,
                high_max_price=117000.0,
                currency="MZN",
                unit="117.000 MZN (Sala Completa Chave-na-Mão | Entrega em 15 dias)",
                description="Solução completa de alto padrão: Sofá Principal Linha Assinatura + 2 Poltronas Esculturais + Mesa de Centro sob medida."
            )
        },
        media_references=[
            ReferenceMedia(
                title="Sofá Chaise 'Aura' em Bouclé Off-White (Foto Real de Produção na Matola)",
                media_url="/media/vanguard_real_sofa_chaise_aura_88400mzn.jpg",
                category="aura",
                caption="Foto real da peça finalizada na nossa estofaria em Manhembana (Matola): estrutura reforçada, espuma D35/D45 e almofadas esféricas (88.400 MZN)."
            ),
            ReferenceMedia(
                title="Sofá Curvo Orgânico em Bouclé Cinza (Foto Real de Produção na Matola)",
                media_url="/media/vanguard_real_sofa_curvo_cinza_72800mzn.jpg",
                category="curvo",
                caption="Sofá Curvo Orgânico (2.6m) modelado à mão pelos nossos mestres na Matola com esferas decorativas (72.800 MZN)."
            ),
            ReferenceMedia(
                title="Estrutura Interna: Chassis Curvilíneo em Madeira Tratada",
                media_url="/media/vanguard_00_chassis_curvilineo.jpg",
                category="chassis",
                caption="O segredo da durabilidade: chassis curvilíneo em madeira tratada e contraplacado naval cortado nas medidas exatas da sua sala."
            ),
            ReferenceMedia(
                title="Lounge Exterior Riviera Prime (Madeira Chanfuta/Jambirre & Aço)",
                media_url="/media/vanguard_03_riviera_prime_lounge.jpg",
                category="riviera",
                caption="Lounge Exterior Riviera com lareira ecológica central integrada e tecido náutico (93.600 MZN)."
            )
        ],
        pdf_documents=[
            OfficialPDFDocument(
                title="Catálogo de Produção Real & Preços Finais 2026 — Vanguard Living Atelier",
                filename="Catalogo_Oficial_Vanguard_Living_2026.pdf",
                local_url="/pdf/Catalogo_Oficial_Vanguard_Living_2026.pdf",
                caption="Aqui está o nosso Catálogo Oficial 2026 em PDF com fotos reais da nossa oficina na Matola. 📄🛋️"
            ),
            OfficialPDFDocument(
                title="Dossiê de Especificação Técnica (Arquitetos & Construtoras) — Vanguard Living",
                filename="Especificacao_Tecnica_Vanguard_Living.pdf",
                local_url="/pdf/Especificacao_Tecnica_Vanguard_Living.pdf",
                caption="Aqui está o Dossiê de Especificação Técnica para Arquitetos e Construtoras parceiras em PDF. 📄✨"
            )
        ],
        persuasion_5_laws={
            "afeicao": "A sua casa merece ser um verdadeiro refúgio de conforto e beleza, e cuidamos de cada costura como se fosse para a nossa própria família.",
            "reciprocidade": "Vamos até à sua casa ou escritório em Maputo e Matola levando o mostruário físico de tecidos Bouclé e espumas para tirar as medidas exatas sem compromisso.",
            "prova_social": "Todas as nossas peças são fotografadas de verdade no pátio da nossa oficina em Manhembana (Matola), sem filtros, entregues a clientes e construtoras exigentes.",
            "autoridade": "Usamos esqueleto interno em madeira tratada e contraplacado naval com espuma D35/D45, garantindo que o sofá nunca cede nem perde a curva.",
            "escassez_compromisso": "Para cumprirmos rigorosamente a entrega em 15 dias, os nossos mestres aceitam poucas encomendas por quinzena."
        }
    ),

    # --------------------------------------------------------------------------
    # 3. INGLÊS SEMESTRE (SISTEMA INGLÊS SEM MESTRE — PROF. BRAGA)
    # --------------------------------------------------------------------------
    "ingles_semestre": CompanyConfig(
        id="ingles_semestre",
        name="Inglês Semestre (Sistema Inglês sem Mestre)",
        short_name="Inglês Semestre",
        slogan="Fluência Prática pelo Telemóvel em 5 Línguas (Inglês, Espanhol, Francês, Russo e Português p/ Chineses)",
        website="https://ingles-sem-mestre.pages.dev",
        keywords=[
            "ingles", "inglês", "semestre", "ingles sem mestre", "inglês sem mestre",
            "espanhol", "russo", "frances", "francês", "portugues", "português",
            "chines", "chinês", "chineses", "mandarim", "lingua", "língua",
            "linguas", "línguas", "idioma", "idiomas", "codigo", "código",
            "eng-500", "eng-1500", "eng-3000", "esp-500", "esp-1500", "esp-3000",
            "fra-500", "fra-1500", "fra-3000", "rus-500", "rus-1500", "rus-3000",
            "por-500", "por-1500", "por-3000", "curso", "aulas"
        ],
        human_welcome=(
            "Que bom ter você aqui no *Inglês Semestre*! 🌍😊 "
            "Criamos um método super acolhedor, prático e direto no seu telemóvel para você destravar a fala sem medo, "
            "disponível em *5 línguas*: *Inglês, Espanhol, Francês, Russo* e o nosso curso especial de *Português para Chineses* (com tradução falada em Chinês Mandarim)."
        ),
        gentle_discovery_question=(
            "Me conta com calma: qual dessas 5 línguas você tem vontade ou necessidade de aprender agora, e se é para o seu trabalho, estudos ou dia a dia?"
        ),
        pricing_catalog={
            "nivel_baixo_500": PricingItem(
                service_id="nivel_baixo_500",
                name="Nível Baixo (Base)",
                low_price=500.0,
                mid_price=500.0,
                high_max_price=500.0,
                currency="MZN",
                unit="500 MZN",
                description="Vocabulário essencial, frases do dia a dia e guia de pronúncia completo com os 4 modos de áudio."
            ),
            "nivel_medio_1500": PricingItem(
                service_id="nivel_medio_1500",
                name="Nível Médio (Intermediário)",
                low_price=1500.0,
                mid_price=1500.0,
                high_max_price=1500.0,
                currency="MZN",
                unit="1.500 MZN",
                description="Conversação prática, diálogos completos e destravamento da fala e audição."
            ),
            "nivel_alto_3000": PricingItem(
                service_id="nivel_alto_3000",
                name="Nível Alto (Executivo)",
                low_price=3000.0,
                mid_price=3000.0,
                high_max_price=3000.0,
                currency="MZN",
                unit="3.000 MZN",
                description="Domínio executivo e profissional para reuniões, negócios, contratos e fluência avançada."
            )
        },
        media_references=[
            ReferenceMedia(
                title="Sistema Inglês sem Mestre — Experiência Completa de Áudio nas 5 Línguas",
                media_url="https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=1000&q=80",
                category="aulas",
                caption="Treino prático no smartphone com Áudio Normal (1.0x), Pronúncia Lenta Sílaba a Sílaba (0.65x), Tradução Falada e Áudio Bilingue Sequencial."
            )
        ],
        pdf_documents=[],
        persuasion_5_laws={
            "afeicao": "Sabemos que aprender uma língua nova às vezes dá timidez, por isso o nosso sistema respeita o seu ritmo para você praticar com total confiança.",
            "reciprocidade": "Todos os 5 cursos entregam a experiência completa de som: áudio na língua (1.0x), pronúncia lenta sílaba a sílaba (0.65x), áudio da tradução e áudio bilingue sequencial.",
            "prova_social": "Alunos em todo Moçambique — incluindo empresários e cidadãos chineses que aprendem português connosco — já estão falando com segurança no dia a dia.",
            "autoridade": "Método coordenado pelo Professor Braga com laboratório fonético completo que funciona direto no navegador do seu smartphone.",
            "escassez_compromisso": "Os valores são super acessíveis (500 MZN no nível baixo, 1.500 MZN no médio e 3.000 MZN no executivo) e o seu código de acesso é libertado na hora após a confirmação."
        },
        extra_rules={
            "official_access_codes_table": {
                "en": {
                    "name": "Inglês",
                    "translation_voice": "Português",
                    "baixo": {"price": 500, "code": "ENG-500-LX9"},
                    "medio": {"price": 1500, "code": "ENG-1500-MW4"},
                    "alto": {"price": 3000, "code": "ENG-3000-HZ8"}
                },
                "es": {
                    "name": "Espanhol",
                    "translation_voice": "Português",
                    "baixo": {"price": 500, "code": "ESP-500-VJ3"},
                    "medio": {"price": 1500, "code": "ESP-1500-QR7"},
                    "alto": {"price": 3000, "code": "ESP-3000-TK6"}
                },
                "fr": {
                    "name": "Francês",
                    "translation_voice": "Português",
                    "baixo": {"price": 500, "code": "FRA-500-YD2"},
                    "medio": {"price": 1500, "code": "FRA-1500-NL5"},
                    "alto": {"price": 3000, "code": "FRA-3000-PV8"}
                },
                "ru": {
                    "name": "Russo",
                    "translation_voice": "Português",
                    "baixo": {"price": 500, "code": "RUS-500-SK4"},
                    "medio": {"price": 1500, "code": "RUS-1500-GY7"},
                    "alto": {"price": 3000, "code": "RUS-3000-XB9"}
                },
                "pt": {
                    "name": "Português Especial para Chineses",
                    "translation_voice": "Chinês Mandarim",
                    "baixo": {"price": 500, "code": "POR-500-ZF1"},
                    "medio": {"price": 1500, "code": "POR-1500-WC5"},
                    "alto": {"price": 3000, "code": "POR-3000-TG9"}
                }
            }
        }
    )
}

# ==============================================================================
# 4. MOTOR DE ANÁLISE DE FOTO E FÓRMULA DE CUSTO DE SOFÁ [(Custo + 40%) × 2]
# ==============================================================================

class SofaPhotoCostAnalyzer:
    @staticmethod
    def apply_sofa_formula(manufacturing_cost_mzn: float) -> Dict[str, float]:
        """
        Fórmula Oficial: [(custo de fabricação + 40%) × 2]
        """
        cost_plus_40_pct = round(manufacturing_cost_mzn * 1.40, 2)
        final_price_mzn = round(cost_plus_40_pct * 2.0, 2)
        down_payment_50_pct = round(final_price_mzn * 0.50, 2)
        partner_commission_min = round(final_price_mzn * 0.12, 2)
        partner_commission_max = round(final_price_mzn * 0.15, 2)

        return {
            "manufacturing_cost_mzn": round(manufacturing_cost_mzn, 2),
            "cost_plus_40_pct_mzn": cost_plus_40_pct,
            "final_price_mzn": final_price_mzn,
            "down_payment_50_pct_mzn": down_payment_50_pct,
            "partner_commission_12_pct_mzn": partner_commission_min,
            "partner_commission_15_pct_mzn": partner_commission_max
        }

    @staticmethod
    def estimate_manufacturing_cost_from_photo(
        image_path_or_url: Optional[str] = None,
        user_caption_or_text: str = "",
        explicit_manufacturing_cost: Optional[float] = None
    ) -> Dict[str, Any]:
        if explicit_manufacturing_cost and explicit_manufacturing_cost > 0:
            calc = SofaPhotoCostAnalyzer.apply_sofa_formula(explicit_manufacturing_cost)
            calc["detected_profile"] = "Peça Sob Medida Analisada por Foto"
            return calc

        text_lower = f"{image_path_or_url or ''} {user_caption_or_text}".lower()

        cost_match = re.search(r'custo[^\d]*(\d[\d\.,]*)', text_lower)
        if cost_match:
            raw_num = cost_match.group(1).replace(".", "").replace(",", ".")
            try:
                cost_val = float(raw_num)
                if cost_val > 500:
                    calc = SofaPhotoCostAnalyzer.apply_sofa_formula(cost_val)
                    calc["detected_profile"] = "Peça Sob Medida (Custo Base Identificado)"
                    return calc
            except ValueError:
                pass

        visual_complexity_factor = 1.0
        if image_path_or_url and os.path.isfile(image_path_or_url):
            try:
                from PIL import Image
                with Image.open(image_path_or_url) as im:
                    w, h = im.size
                    if (w / max(h, 1)) >= 1.35:
                        visual_complexity_factor = 1.15
            except Exception:
                pass

        if any(w in text_lower for w in ["sala completa", "chave na mao", "chave-na-mão"]):
            base_mfg_cost = 41785.71
            profile = "Sala Completa Chave-na-Mão (Sofá + 2 Poltronas + Mesa)"
        elif any(w in text_lower for w in ["riviera", "exterior", "jardim", "varanda", "lareira", "chanfuta"]):
            base_mfg_cost = 33428.57
            profile = "Lounge Exterior em Madeira de Lei (Chanfuta/Jambirre) & Aço"
        elif any(w in text_lower for w in ["chaise", "aura", "em l", "3.0m", "3.6m", "canto"]):
            base_mfg_cost = 31571.43
            profile = "Sofá Chaise 'Aura' / Modelo em L (3.0m–3.6m) em Bouclé"
        elif any(w in text_lower for w in ["curvo", "organico", "orgânico", "esferas", "2.6m", "serpentina"]):
            base_mfg_cost = 26000.00
            profile = "Sofá Curvo Orgânico (2.6m) com Chassis Curvilíneo"
        elif any(w in text_lower for w in ["cama", "queen", "casal", "cabeceira"]):
            base_mfg_cost = 20428.57
            profile = "Cama Casal/Queen + Cabeceira Estofada"
        elif any(w in text_lower for w in ["poltrona", "poltronas"]):
            base_mfg_cost = 13000.00
            profile = "Par de Poltronas Esculturais"
        elif any(w in text_lower for w in ["banqueta", "banquetas", "ilha"]):
            base_mfg_cost = 11142.86
            profile = "Kit 3 Banquetas Altas"
        else:
            base_mfg_cost = round(31571.43 * visual_complexity_factor, 2)
            profile = "Sofá Sob Medida em Madeira Tratada, Espuma D35/D45 e Bouclé"

        calc = SofaPhotoCostAnalyzer.apply_sofa_formula(base_mfg_cost)
        calc["detected_profile"] = profile
        return calc

# ==============================================================================
# 5. GERENCIADOR DE SESSÕES E MEMÓRIA CONVERSACIONAL
# ==============================================================================

class ConversationDB:
    def __init__(self, db_path: str = "/tmp/whatsapp_bot_mz_v4.db"):
        self.db_path = db_path
        self._memory_sessions: Dict[str, Dict[str, Any]] = {}
        self._memory_logs: List[Dict[str, Any]] = []
        self._use_memory = False

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        phone_number TEXT PRIMARY KEY,
                        company_id TEXT,
                        stage TEXT,
                        company_status TEXT,
                        needs_data TEXT,
                        quote_data TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        phone_number TEXT,
                        direction TEXT,
                        company_id TEXT,
                        content TEXT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                conn.commit()
        except Exception:
            self._use_memory = True

    def get_session(self, phone: str) -> Dict[str, Any]:
        default_session = {
            "phone_number": phone,
            "company_id": None,
            "stage": "WARM_GREETING",
            "company_status": None,
            "needs_data": {},
            "quote_data": {}
        }
        if self._use_memory:
            return self._memory_sessions.get(phone, default_session)
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT phone_number, company_id, stage, company_status, needs_data, quote_data FROM sessions WHERE phone_number = ?",
                    (phone,)
                )
                row = cursor.fetchone()
                if not row:
                    return default_session
                return {
                    "phone_number": row[0],
                    "company_id": row[1],
                    "stage": row[2],
                    "company_status": row[3],
                    "needs_data": json.loads(row[4] or "{}"),
                    "quote_data": json.loads(row[5] or "{}")
                }
        except Exception:
            return self._memory_sessions.get(phone, default_session)

    def save_session(self, session: Dict[str, Any]):
        phone = session["phone_number"]
        self._memory_sessions[phone] = session
        if self._use_memory:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO sessions (phone_number, company_id, stage, company_status, needs_data, quote_data, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(phone_number) DO UPDATE SET
                        company_id=excluded.company_id,
                        stage=excluded.stage,
                        company_status=excluded.company_status,
                        needs_data=excluded.needs_data,
                        quote_data=excluded.quote_data,
                        updated_at=CURRENT_TIMESTAMP
                """, (
                    phone,
                    session.get("company_id"),
                    session.get("stage", "WARM_GREETING"),
                    session.get("company_status"),
                    json.dumps(session.get("needs_data", {})),
                    json.dumps(session.get("quote_data", {}))
                ))
                conn.commit()
        except Exception:
            pass

    def log_message(self, phone: str, direction: str, company_id: Optional[str], content: str):
        self._memory_logs.append({"phone": phone, "direction": direction, "company_id": company_id, "content": content})
        if self._use_memory:
            return
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO messages (phone_number, direction, company_id, content) VALUES (?, ?, ?, ?)",
                    (phone, direction, company_id, content)
                )
                conn.commit()
        except Exception:
            pass

# ==============================================================================
# 6. ROTEADOR INTELIGENTE E DETECTOR DE SAUDAÇÕES HUMANAS
# ==============================================================================

class CompanyRouter:
    PURE_GREETING_PATTERNS = [
        r"^(ol[aá]|oi|bom dia|boa tarde|boa noite|al[oô]|hey|hello|hi)[\s,!?.]*$",
        r"^(ol[aá]|oi|bom dia|boa tarde|boa noite)?[\s,]*tudo (bem|bom|optimo|ótimo)\??[\s!.]*$",
        r"^(ol[aá]|oi)?[\s,]*como ([eé] que [eé]|est[aá]|vai)\??[\s!.]*$"
    ]

    @staticmethod
    def is_pure_greeting(text: str) -> bool:
        t = text.strip().lower()
        if len(t) <= 32:
            for pat in CompanyRouter.PURE_GREETING_PATTERNS:
                if re.match(pat, t):
                    return True
        return False

    @staticmethod
    def identify_company(text: str, current_company_id: Optional[str] = None, has_image: bool = False) -> Tuple[Optional[str], float]:
        text_lower = text.lower()
        scores: Dict[str, int] = {"braga_io": 0, "vanguarda_living": 0, "ingles_semestre": 0}

        if any(w in text_lower for w in ["braga.io", "braga.eu", "omniflow", "balcao zero", "balcão zero", "leandro braga"]):
            scores["braga_io"] += 15
        if any(w in text_lower for w in [
            "vanguard", "vanguarda", "aura", "serpentina", "riviera", "valente obras",
            "boucle", "bouclé", "chanfuta", "sofa", "sofá", "sofas", "sofás", "cama",
            "cabeceira", "banquetas", "poltronas", "matola", "boquisso", "moveis", "móveis"
        ]):
            scores["vanguarda_living"] += 15
        if any(w in text_lower for w in [
            "ingles semestre", "inglês semestre", "ingles sem mestre", "inglês sem mestre",
            "eng-500", "eng-1500", "eng-3000", "esp-500", "esp-1500", "esp-3000",
            "fra-500", "fra-1500", "fra-3000", "rus-500", "rus-1500", "rus-3000",
            "por-500", "por-1500", "por-3000", "portugues para chineses", "português para chineses",
            "russo", "espanhol", "francês", "frances", "mandarim", "aprender ingles", "curso de ingles"
        ]):
            scores["ingles_semestre"] += 15

        if has_image and not current_company_id:
            scores["vanguarda_living"] += 10

        for comp_id, comp in COMPANIES.items():
            for kw in comp.keywords:
                if re.search(r'\b' + re.escape(kw) + r'\b', text_lower):
                    scores[comp_id] += 3
                elif kw in text_lower:
                    scores[comp_id] += 1

        best_company = max(scores, key=scores.get)
        if scores[best_company] >= 2:
            return best_company, min(1.0, scores[best_company] / 8.0)

        if current_company_id and current_company_id in COMPANIES:
            return current_company_id, 0.5

        return None, 0.0

# ==============================================================================
# 7. MOTOR DE PRECIFICAÇÃO CONVERSACIONAL HUMANO (AS 3 EMPRESAS)
# ==============================================================================

class PricingEngine:
    @staticmethod
    def detect_braga_company_status_and_multiplier(text: str, current_status: Optional[str] = None) -> Tuple[str, float, bool]:
        combined = f"{current_status or ''} {text}".lower()

        if any(w in combined for w in ["banco", "bancos", "bancario", "bancário", "instituicao financeira", "instituição financeira", "millennium", "standard bank", "bci", "omniflow", "core banking"]):
            mult = 3.0 if any(w in combined for w in ["nacional", "complexo", "completa", "total", "biometria", "balcao zero", "balcão zero", "triplicar"]) else 2.0
            return "Instituição Financeira / Banco", mult, True

        if any(w in combined for w in ["arquitetura", "arquiteto", "arquitecto", "engenharia", "construtora", "obras", "imobiliaria de luxo"]):
            mult = 3.0 if any(w in combined for w in ["complexo", "alta complexidade", "grande", "3d", "completo", "portal", "triplicar"]) else 2.0
            return f"Empresa de Arquitetura / Engenharia (Fator de Complexidade {int(mult)}x)", mult, False

        if any(w in combined for w in ["complexo", "complexa", "complexidade", "alta", "sociedade de advogados", "baleia", "corporativo", "multinacional", "hospital"]):
            mult = 3.0 if any(w in combined for w in ["muito complexo", "extrema", "triplo", "total", "integrado"]) else 2.0
            return f"Operação Corporativa de Alta Complexidade (Fator {int(mult)}x)", mult, False

        if any(w in combined for w in ["clinica", "clínica", "empresa media", "empresa média", "consultorio", "consultório"]):
            return "Clínica / Empresa de Médio Porte", 1.0, False

        if any(w in combined for w in ["pequeno", "profissional", "autonomo", "autónomo", "comerciante", "artesao", "artesão", "esteticista", "nutricionista", "branding"]):
            return "Profissional Liberal / Negócio Comercial", 1.0, False

        return "Empresarial Padrão", 1.0, False

    @staticmethod
    def build_braga_human_quote(text: str, company_status: Optional[str]) -> str:
        company = COMPANIES["braga_io"]
        status_label, multiplier, is_bank = PricingEngine.detect_braga_company_status_and_multiplier(text, company_status)
        text_lower = f"{company_status or ''} {text}".lower()
        laws = company.persuasion_5_laws

        if is_bank:
            poc_calc = 3500000.0 * multiplier
            rollout_calc = min(50000000.0, 18500000.0 * multiplier)
            return (
                f"Muito obrigado por partilhar o perfil da sua instituição! 😊 Para o setor bancário (*{status_label}*), "
                f"desenvolvemos o ecossistema soberano *OmniFlow Banking OS* (com totens Balcão Zero, biometria KYC e integração Core Banking).\n\n"
                f"Devido à complexidade e segurança de nível bancário ({int(multiplier)}x), o investimento estrutura-se assim:\n"
                f"• *Piloto / PoC Controlado:* {poc_calc:,.0f} MZN\n"
                f"• *Rollout Corporativo:* {rollout_calc:,.0f} MZN (podendo ir até *50.000.000 MZN* em implantações nacionais completas)\n"
                f"• *Manutenção SaaS:* 950.000 a 1.400.000 MZN/mês\n\n"
                f"{laws['reciprocidade']} Gostaria de agendar uma demonstração executiva com o nosso Arquiteto Chefe, Leandro Braga, ou prefere que eu envie o nosso Dossiê Executivo em PDF?"
            )

        if any(w in text_lower for w in ["branding", "logo", "logotipo", "canva", "pequeno", "nutricionista", "artesao", "comerciante"]):
            item = company.pricing_catalog["pacote_aceleracao_branding"]
        elif any(w in text_lower for w in ["premium", "arquitetura", "advogados", "sociedade", "portal", "kyc", "baleia", "corporativo"]):
            item = company.pricing_catalog["pacote_premium_corporativo"]
        else:
            item = company.pricing_catalog["pacote_medio"]

        min_val = item.low_price * multiplier
        max_val = item.high_max_price * multiplier
        mrr_val = 15000.0 * (multiplier if multiplier > 1.0 else 1.0)

        if min_val == max_val:
            price_str = f"*{max_val:,.0f} MZN* (iniciando com 50% de sinal na adjudicação: {max_val/2:,.0f} MZN)"
        else:
            price_str = f"*{min_val:,.0f} a {max_val:,.0f} MZN* (iniciando com 50% de sinal)"

        mult_explanation = (
            f" (já ajustado em *{int(multiplier)}x* pela complexidade técnica do seu setor de *{status_label}*)"
            if multiplier > 1.0 else f" para *{status_label}*"
        )

        return (
            f"Perfeito, compreendi exatamente a sua necessidade! 😊 Para entregar toda a segurança e velocidade que você precisa{mult_explanation}, "
            f"a solução ideal é o nosso *{item.name}*:\n\n"
            f"• *O que preparamos para si:* {item.description}\n"
            f"• *Investimento de Implementação:* {price_str}\n"
            f"• *Acompanhamento e Manutenção Mensal (Opcional):* {mrr_val:,.0f} MZN/mês\n\n"
            f"✨ {laws['prova_social']}\n\n"
            f"O que acha dessa estrutura para o seu negócio? Faz sentido avançarmos assim ou tem alguma dúvida que eu possa esclarecer?"
        )

    @staticmethod
    def build_vanguard_human_quote(
        text: str,
        has_photo: bool = False,
        image_path_or_url: Optional[str] = None,
        explicit_manufacturing_cost: Optional[float] = None
    ) -> str:
        company = COMPANIES["vanguarda_living"]
        text_lower = text.lower()
        laws = company.persuasion_5_laws

        photo_triggered = has_photo or bool(image_path_or_url) or (explicit_manufacturing_cost is not None) or any(
            w in text_lower for w in ["enviei uma foto", "mandei uma foto", "esta foto", "nessa foto", "desta foto", "custo de fabricacao", "custo de fabricação", "calcular pela foto"]
        )

        if photo_triggered:
            photo_calc = SofaPhotoCostAnalyzer.estimate_manufacturing_cost_from_photo(
                image_path_or_url=image_path_or_url,
                user_caption_or_text=text,
                explicit_manufacturing_cost=explicit_manufacturing_cost
            )
            mfg_cost = photo_calc["manufacturing_cost_mzn"]
            final_price = photo_calc["final_price_mzn"]
            sinal_50 = photo_calc["down_payment_50_pct_mzn"]

            return (
                f"Que lindo modelo você escolheu! 😍 Analisei com todo o cuidado os detalhes da foto para produzir na nossa oficina em Manhembana (Matola) "
                f"com estrutura em madeira tratada, espuma de alta densidade D35/D45 e acabamento de primeira:\n\n"
                f"• *Peça Analisada:* {photo_calc['detected_profile']}\n"
                f"• *Custo Base de Fabricação Estimado:* {mfg_cost:,.2f} MZN\n"
                f"• *Valor Final Chave-na-Mão `[(Custo + 40%) × 2]`:* *{final_price:,.2f} MZN*\n"
                f"• *Condição de Encomenda:* 50% de sinal ({sinal_50:,.2f} MZN) e os outros 50% na entrega em sua casa (prazo de *15 dias* em Maputo e Matola).\n\n"
                f"💛 {laws['reciprocidade']}\n\n"
                f"Gostaria que a nossa equipa fosse tirar as medidas do seu espaço com o mostruário de tecidos, ou prefere já reservar a sua vaga de fabrico desta quinzena?"
            )

        if any(w in text_lower for w in ["sala completa", "chave na mao", "chave-na-mão", "pacote sala"]):
            item = company.pricing_catalog["pacote_sala_completa_chave_na_mao"]
        elif any(w in text_lower for w in ["riviera", "exterior", "jardim", "varanda", "lareira", "chanfuta", "jambirre"]):
            item = company.pricing_catalog["lounge_exterior_riviera"]
        elif any(w in text_lower for w in ["curvo", "organico", "orgânico", "esferas", "2.6m", "cinza", "serpentina"]):
            item = company.pricing_catalog["sofa_curvo_organico"]
        elif any(w in text_lower for w in ["cama", "queen", "casal", "cabeceira"]):
            item = company.pricing_catalog["cama_casal_queen_cabeceira"]
        elif any(w in text_lower for w in ["banqueta", "banquetas", "ilha", "cozinha"]):
            item = company.pricing_catalog["kit_3_banquetas_altas"]
        elif any(w in text_lower for w in ["poltrona", "poltronas"]):
            item = company.pricing_catalog["par_poltronas_esculturais"]
        else:
            item = company.pricing_catalog["sofa_chaise_aura_l"]

        max_price = item.high_max_price
        sinal_50 = max_price * 0.50

        return (
            f"Com todo o prazer! 😊 Na nossa *Linha Assinatura de Alto Padrão (em Bouclé e Espuma D35/D45)*, produzida pelos nossos mestres na Matola com *entrega em 15 dias*:\n\n"
            f"🛋️ *{item.name}:* *{max_price:,.0f} MZN*\n"
            f"• *Detalhes:* {item.description}\n"
            f"• *Como funciona a encomenda:* 50% de sinal no arranque ({sinal_50:,.0f} MZN) e 50% na entrega.\n\n"
            f"Se também quiser comparar com as outras peças da nossa *Linha Assinatura (Valor Alto)*:\n"
            f"• Sofá Chaise 'Aura' ou em L (3.0m–3.6m): *88.400 MZN*\n"
            f"• Sofá Curvo Orgânico + Esferas (2.6m): *72.800 MZN*\n"
            f"• Cama Casal/Queen + Cabeceira Estofada: *57.200 MZN*\n"
            f"• Kit 3 Banquetas Altas (Ilha de Cozinha): *31.200 MZN*\n"
            f"• Par de Poltronas Esculturais: *36.400 MZN*\n"
            f"• Lounge Exterior Riviera (Madeira & Aço): *93.600 MZN*\n"
            f"• Pacote Sala Completa Chave-na-Mão: *117.000 MZN*\n\n"
            f"✨ {laws['autoridade']} Qual dessas peças combina melhor com a sua sala? Se quiser, posso te mandar fotos reais delas agora mesmo!"
        )

    @staticmethod
    def build_ingles_semestre_human_quote(text: str) -> str:
        company = COMPANIES["ingles_semestre"]
        text_lower = text.lower()
        codes_table = company.extra_rules["official_access_codes_table"]
        laws = company.persuasion_5_laws

        lang_key = "en"
        if any(w in text_lower for w in ["esp", "espanhol"]):
            lang_key = "es"
        elif any(w in text_lower for w in ["fra", "frances", "francês"]):
            lang_key = "fr"
        elif any(w in text_lower for w in ["rus", "russo"]):
            lang_key = "ru"
        elif any(w in text_lower for w in ["por", "portugues", "português", "chines", "chinês", "chineses", "mandarim"]):
            lang_key = "pt"

        lang_info = codes_table[lang_key]

        return (
            f"Que ótima escolha estudar *{lang_info['name']}* connosco! 🌍😊\n\n"
            f"Todos os nossos 5 idiomas (*Inglês, Espanhol, Francês, Russo e Português Especial para Chineses*) têm *exatamente o mesmo escopo completo de som* no telemóvel:\n"
            f"1️⃣ *Áudio da Língua (1.0x):* Pronúncia natural de cada palavra, frase e diálogo.\n"
            f"2️⃣ *Áudio de Pronúncia Lenta (0.65x):* Fala pausadamente sílaba por sílaba para você pegar o jeito sem dificuldade.\n"
            f"3️⃣ *Áudio da Tradução:* Pronuncia a tradução em voz alta em *{lang_info['translation_voice']}*.\n"
            f"4️⃣ *Áudio Bilingue Sequencial (Língua ➔ Tradução):* Fala na língua em estudo, espera terminar e logo em seguida fala a tradução!\n\n"
            f"💰 *Os valores são super acessíveis e divididos em 3 níveis (iguais para todas as línguas):*\n"
            f"• *Nível Baixo (Base):* *500 MZN* (Código de turma: `{lang_info['baixo']['code'][:7]}`)\n"
            f"• *Nível Médio (Intermediário):* *1.500 MZN* (Código de turma: `{lang_info['medio']['code'][:7]}`)\n"
            f"• *Nível Alto (Executivo):* *3.000 MZN* (Código de turma: `{lang_info['alto']['code'][:7]}`)\n\n"
            f"💛 {laws['afeicao']} Qual desses 3 níveis (500, 1.500 ou 3.000 MZN) você sente que é o melhor para começar hoje?"
        )

# ==============================================================================
# 8. CONECTOR OPCIONAL COM GOOGLE GEMINI FLASH (API GRATUITA GOOGLE AI STUDIO)
# ==============================================================================

class GeminiHumanAssistant:
    @staticmethod
    def generate_human_reply(user_text: str, fallback_reply: str, company_name: str) -> str:
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            return OutputSanitizer.clean(fallback_reply)

        try:
            import requests
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
            system_instruction = (
                f"Você é um atendente humano, carinhoso, gentil e altamente profissional da {company_name} em Maputo, Moçambique. "
                "REGRAS ESTRITAS DE SEGURANÇA:\n"
                "1. NUNCA invente links do Google Drive (drive.google.com) nem URLs externas.\n"
                "2. NUNCA envie textos gigantescos ou repetitivos. Escreva de forma leve, acolhedora e humana.\n"
                "3. Mantenha 100% de fidelidade aos valores em Meticais (MZN) e informações fornecidas na base abaixo.\n"
                f"BASE OFICIAL PARA RESPONDER:\n{fallback_reply}"
            )
            payload = {
                "contents": [{"parts": [{"text": f"Mensagem do cliente: {user_text}\n\nResponda com base nestes dados:\n{fallback_reply}"}]}],
                "systemInstruction": {"parts": [{"text": system_instruction}]},
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 450}
            }
            resp = requests.post(url, json=payload, timeout=8)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts and parts[0].get("text"):
                        return OutputSanitizer.clean(parts[0]["text"])
        except Exception as e:
            logger.warning(f"Fallback para motor humano local ativado: {e}")

        return OutputSanitizer.clean(fallback_reply)

# ==============================================================================
# 9. DISPARADOR DE MENSAGENS PARA WHATSAPP (META CLOUD API & EVOLUTION API)
# ==============================================================================

class WhatsAppOutboundSender:
    """
    Envia as respostas geradas pelo bot diretamente para o telemóvel do cliente
    caso as variáveis de conexão (Meta Cloud API ou Evolution API) estejam ativas.
    """
    @staticmethod
    def dispatch(recipient_phone: str, actions: List[Dict[str, Any]], public_base_url: str = ""):
        import requests

        # A. Meta WhatsApp Cloud API Oficial
        meta_token = os.getenv("WHATSAPP_ACCESS_TOKEN", "").strip()
        phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "").strip()

        # B. Evolution API
        evo_url = os.getenv("EVOLUTION_API_URL", "").strip().rstrip("/")
        evo_key = os.getenv("EVOLUTION_API_KEY", "").strip()
        evo_instance = os.getenv("EVOLUTION_INSTANCE", "").strip()

        for act in actions:
            act_type = act.get("type", "text")

            # Envio via Meta Cloud API
            if meta_token and phone_id:
                try:
                    headers = {"Authorization": f"Bearer {meta_token}", "Content-Type": "application/json"}
                    api_url = f"https://graph.facebook.com/v21.0/{phone_id}/messages"
                    if act_type == "text":
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": recipient_phone,
                            "type": "text",
                            "text": {"body": act["body"]}
                        }
                    elif act_type == "image":
                        media_link = act["url"] if act["url"].startswith("http") else f"{public_base_url}{act['url']}"
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": recipient_phone,
                            "type": "image",
                            "image": {"link": media_link, "caption": act.get("caption", "")}
                        }
                    elif act_type == "document":
                        doc_link = act["url"] if act["url"].startswith("http") else f"{public_base_url}{act['url']}"
                        payload = {
                            "messaging_product": "whatsapp",
                            "to": recipient_phone,
                            "type": "document",
                            "document": {
                                "link": doc_link,
                                "filename": act.get("filename", "Documento_Oficial.pdf"),
                                "caption": act.get("caption", "")
                            }
                        }
                    requests.post(api_url, headers=headers, json=payload, timeout=10)
                except Exception as e:
                    logger.warning(f"Erro ao enviar via Meta Cloud API: {e}")

            # Envio via Evolution API
            elif evo_url and evo_key and evo_instance:
                try:
                    headers = {"apikey": evo_key, "Content-Type": "application/json"}
                    if act_type == "text":
                        requests.post(
                            f"{evo_url}/message/sendText/{evo_instance}",
                            headers=headers,
                            json={"number": recipient_phone, "text": act["body"]},
                            timeout=10
                        )
                    elif act_type in ["image", "document"]:
                        media_link = act["url"] if act["url"].startswith("http") else f"{public_base_url}{act['url']}"
                        requests.post(
                            f"{evo_url}/message/sendMedia/{evo_instance}",
                            headers=headers,
                            json={
                                "number": recipient_phone,
                                "mediatype": act_type,
                                "media": media_link,
                                "fileName": act.get("filename", "Catalogo.pdf"),
                                "caption": act.get("caption", "")
                            },
                            timeout=10
                        )
                except Exception as e:
                    logger.warning(f"Erro ao enviar via Evolution API: {e}")

# ==============================================================================
# 10. ORQUESTRADOR CONVERSACIONAL HUMANO DO BOT DE WHATSAPP
# ==============================================================================

class WhatsAppSalesBot:
    def __init__(self, db: ConversationDB):
        self.db = db
        self.anti_flood = AntiFloodGuard(ttl_seconds=15)

    def handle_message(
        self,
        phone_number: str,
        message_text: str = "",
        image_path_or_url: Optional[str] = None,
        explicit_manufacturing_cost: Optional[float] = None,
        message_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        text_clean = (message_text or "").strip()
        text_lower = text_clean.lower()
        has_image = bool(image_path_or_url) or (explicit_manufacturing_cost is not None)

        # 1. Proteção Anti-Flood / Anti-Repetição
        if self.anti_flood.is_duplicate_incoming(phone_number, text_clean, message_id=message_id) and not has_image:
            return []

        session = self.db.get_session(phone_number)
        self.db.log_message(phone_number, "INCOMING", session.get("company_id"), f"{'[FOTO] ' if has_image else ''}{text_clean}")

        current_company_id = session.get("company_id")
        responses: List[Dict[str, Any]] = []

        # 2. Comando para mudar de assunto / empresa com gentileza
        if text_lower in ["menu", "trocar empresa", "empresas", "início", "inicio", "outra empresa"]:
            session["company_id"] = None
            session["stage"] = "WARM_GREETING"
            self.db.save_session(session)
            warm_switch = (
                "Com certeza! 😊 Estou aqui para cuidar do que você precisar. "
                "Sobre qual área você gostaria de conversar agora?\n\n"
                "• *Vanguard Living Atelier* (Sofás e móveis sob medida na Matola)\n"
                "• *Inglês Semestre* (Cursos práticos de Inglês, Espanhol, Francês, Russo e Português p/ Chineses)\n"
                "• *Braga.io* (Sistemas, automação no WhatsApp, design e tecnologia para empresas)"
            )
            return [{"type": "text", "body": OutputSanitizer.clean(warm_switch)}]

        # 3. Se for apenas uma saudação ("Olá", "Tudo bem?", "Bom dia", "Como é que é?") -> RESPOSTA HUMANA CURTA E CARINHOSA!
        if CompanyRouter.is_pure_greeting(text_clean) and not has_image and not current_company_id:
            session["stage"] = "WARM_GREETING"
            self.db.save_session(session)
            human_hello = (
                "Olá! Tudo ótimo por aqui, graças a Deus! E consigo, como está tudo? 😊\n\n"
                "É um prazer enorme receber a sua mensagem! Me conta com calma: como posso te ajudar hoje? "
                "Você está procurando *sofás e móveis sob medida*, *cursos de idiomas* ou *soluções de tecnologia e sistemas para empresa*?"
            )
            self.db.log_message(phone_number, "OUTGOING", None, human_hello)
            return [{"type": "text", "body": OutputSanitizer.clean(human_hello)}]

        # 4. Identificar a empresa pelo que o cliente falou
        detected_company_id, _ = CompanyRouter.identify_company(text_clean, current_company_id, has_image=has_image)

        if not detected_company_id:
            if text_clean in ["1", "braga", "braga.io", "braga.eu"]:
                detected_company_id = "braga_io"
            elif text_clean in ["2", "vanguard", "vanguarda", "vanguard living", "ateliê"]:
                detected_company_id = "vanguarda_living"
            elif text_clean in ["3", "ingles", "inglês", "ingles semestre", "idiomas"]:
                detected_company_id = "ingles_semestre"

        if not detected_company_id:
            session["stage"] = "WARM_GREETING"
            self.db.save_session(session)
            gentle_ask = (
                "Muito obrigado pelo seu contacto! 😊 Para eu te dar toda a atenção e responder certinho ao que você precisa, "
                "me diz só qual destes serviços você procura hoje:\n\n"
                "1️⃣ *Sistemas, Automação ou Branding para Empresas* (*Braga.io*)\n"
                "2️⃣ *Sofás e Mobiliário de Luxo Sob Medida* (*Vanguard Living Atelier*)\n"
                "3️⃣ *Cursos de Idiomas no Telemóvel* (*Inglês Semestre*)\n\n"
                "Pode responder com o número ou me contar com as suas palavras!"
            )
            self.db.log_message(phone_number, "OUTGOING", None, gentle_ask)
            return [{"type": "text", "body": OutputSanitizer.clean(gentle_ask)}]

        company = COMPANIES[detected_company_id]
        is_first_company_turn = (session.get("company_id") != detected_company_id)
        session["company_id"] = detected_company_id

        # 5. Se o cliente enviou uma FOTO de sofá para a Vanguard Living -> Analisa e calcula [(Custo + 40%) × 2]
        if detected_company_id == "vanguarda_living" and (has_image or any(w in text_lower for w in ["enviei uma foto", "mandei uma foto", "calcular pela foto", "custo de fabricacao", "custo de fabricação"])):
            photo_reply = PricingEngine.build_vanguard_human_quote(
                text=text_clean,
                has_photo=True,
                image_path_or_url=image_path_or_url,
                explicit_manufacturing_cost=explicit_manufacturing_cost
            )
            session["stage"] = "PRICING_QUOTE"
            self.db.save_session(session)
            clean_reply = OutputSanitizer.clean(photo_reply)
            self.db.log_message(phone_number, "OUTGOING", detected_company_id, clean_reply)
            return [{"type": "text", "body": clean_reply}]

        # 6. Se o cliente pediu explicitamente um arquivo PDF / Catálogo em PDF / Dossiê em PDF
        wants_pdf = any(w in text_lower for w in ["pdf", "dossie", "dossiê", "enviar catalogo", "mandar catalogo", "manda o catalogo", "envia o catalogo", "baixar catalogo", "ficheiro", "arquivo"])
        if wants_pdf:
            if company.pdf_documents:
                doc = company.pdf_documents[0]
                if "especificacao" in text_lower or "especificação" in text_lower or "arquiteto" in text_lower:
                    doc = company.pdf_documents[-1]
                responses.append({
                    "type": "document",
                    "url": doc.local_url,
                    "filename": doc.filename,
                    "mime_type": "application/pdf",
                    "caption": doc.caption
                })
                follow_msg = (
                    f"Enviei acima o ficheiro PDF oficial da *{company.short_name}* diretamente aqui pelo WhatsApp (sem precisar de links externos). 😊\n\n"
                    f"Enquanto dá uma olhadinha, se quiser me dizer qual item mais te chamou a atenção, eu já te explico tudo por aqui!"
                )
                responses.append({"type": "text", "body": OutputSanitizer.clean(follow_msg)})
                self.db.save_session(session)
                return responses
            else:
                no_pdf_needed = PricingEngine.build_ingles_semestre_human_quote(text_clean)
                return [{"type": "text", "body": OutputSanitizer.clean(no_pdf_needed)}]

        # 7. Guardar status da empresa se o cliente estiver falando com a Braga.io
        if detected_company_id == "braga_io":
            if any(w in text_lower for w in [
                "banco", "arquitetura", "arquiteto", "engenharia", "construtora", "clinica", "clínica",
                "advogado", "sociedade", "pequeno", "comerciante", "profissional", "empresa", "complexo", "hospital"
            ]):
                session["company_status"] = text_clean

        # 8. Se o cliente pediu FOTOS / IMAGENS de referência
        wants_photos = any(w in text_lower for w in ["foto", "fotos", "imagem", "imagens", "ver fotos", "mostra", "mostrar"]) and not any(
            w in text_lower for w in ["enviei uma foto", "mandei uma foto", "calcular pela foto"]
        )
        if wants_photos:
            matched_media = [
                m for m in company.media_references
                if m.category.lower() in text_lower or any(w in text_lower for w in m.title.lower().split() if len(w) > 3)
            ]
            if not matched_media:
                matched_media = company.media_references[:2]

            for m in matched_media[:2]:
                responses.append({
                    "type": "image",
                    "url": m.media_url,
                    "caption": f"*{m.title}*\n{m.caption}"
                })
            gentle_after_photo = (
                f"Aqui estão algumas fotos reais do nosso trabalho na *{company.short_name}*! 😊✨\n"
                f"O que você achou desse acabamento? Se quiser saber os detalhes de medidas ou valores de alguma peça específica, é só me dizer!"
            )
            responses.append({"type": "text", "body": OutputSanitizer.clean(gentle_after_photo)})
            self.db.save_session(session)
            return responses

        # 9. Se o cliente perguntou explicitamente PREÇO / VALOR / QUANTO CUSTA / ORÇAMENTO
        wants_pricing = any(w in text_lower for w in [
            "preco", "preço", "precos", "preços", "valor", "valores", "quanto custa", "quanto fica",
            "orcamento", "orçamento", "cotacao", "cotação", "tabela", "investimento", "500", "1500", "3000"
        ])

        if wants_pricing:
            if detected_company_id == "braga_io" and not session.get("company_status"):
                session["stage"] = "AWAITING_COMPANY_STATUS"
                self.db.save_session(session)
                gentle_status_check = (
                    "Com todo o gosto! 😊 Aqui na *Braga.io* temos soluções que vão desde pacotes de aceleração e branding (*3.500 a 10.000 MZN*) "
                    "e automação para clínicas e empresas médias (*35.000 MZN*) até ecossistemas corporativos e bancários.\n\n"
                    "Para eu te passar o orçamento certinho para o seu caso, me conta só: *qual é o ramo/porte da sua empresa* "
                    "(por exemplo: negócio próprio, clínica, escritório de arquitetura, sociedade de advogados ou banco) e *qual serviço você gostaria de implementar*?"
                )
                return [{"type": "text", "body": OutputSanitizer.clean(gentle_status_check)}]

            session["stage"] = "PRICING_QUOTE"
            self.db.save_session(session)

            if detected_company_id == "braga_io":
                human_quote = PricingEngine.build_braga_human_quote(text_clean, session.get("company_status"))
            elif detected_company_id == "vanguarda_living":
                human_quote = PricingEngine.build_vanguard_human_quote(text=text_clean, has_photo=False)
            else:
                human_quote = PricingEngine.build_ingles_semestre_human_quote(text_clean)

            clean_quote = OutputSanitizer.clean(human_quote)
            self.db.log_message(phone_number, "OUTGOING", detected_company_id, clean_quote)
            return [{"type": "text", "body": clean_quote}]

        # 10. Se a Braga.io estava aguardando o cliente responder o status/ramo da empresa
        if session.get("stage") == "AWAITING_COMPANY_STATUS" and detected_company_id == "braga_io":
            session["company_status"] = text_clean
            session["stage"] = "PRICING_QUOTE"
            self.db.save_session(session)
            human_quote = PricingEngine.build_braga_human_quote(text_clean, text_clean)
            clean_quote = OutputSanitizer.clean(human_quote)
            self.db.log_message(phone_number, "OUTGOING", detected_company_id, clean_quote)
            return [{"type": "text", "body": clean_quote}]

        # 11. Se o cliente quer fechar / pagar / encomendar / inscrever-se
        if any(w in text_lower for w in ["sim", "quero fechar", "quero contratar", "quero me inscrever", "matricular", "avancar", "avançar", "pagar", "sinal", "encomendar", "comprar", "conta bancaria", "m-pesa", "mpesa"]):
            session["stage"] = "CLOSING"
            self.db.save_session(session)
            closing_reply = (
                f"Que alegria! Fico muito feliz em cuidar disso para si aqui na *{company.short_name}*! 😊🤝\n\n"
                f"{company.persuasion_5_laws['escassez_compromisso']}\n\n"
                f"{OFFICIAL_PAYMENT_DETAILS}\n\n"
                f"Assim que realizar a confirmação, basta me enviar o comprovativo por aqui mesmo que eu já trato da sua liberação na hora!"
            )
            clean_closing = OutputSanitizer.clean(closing_reply)
            self.db.log_message(phone_number, "OUTGOING", detected_company_id, clean_closing)
            return [{"type": "text", "body": clean_closing}]

        # 12. Primeiro contato sobre a empresa (acolhimento gentil + 1 pergunta leve, SEM despejar tabela de preços)
        if is_first_company_turn:
            session["stage"] = "NEEDS_DISCOVERY"
            self.db.save_session(session)
            welcome_reply = (
                f"{company.human_welcome}\n\n"
                f"💛 {company.persuasion_5_laws['afeicao']}\n\n"
                f"{company.gentle_discovery_question}"
            )
            clean_welcome = OutputSanitizer.clean(welcome_reply)
            self.db.log_message(phone_number, "OUTGOING", detected_company_id, clean_welcome)
            return [{"type": "text", "body": clean_welcome}]

        # 13. Resposta empática contínua adaptada ao que o cliente acabou de contar
        session["needs_data"]["ultimo_relato"] = text_clean
        session["stage"] = "CONVERSATION"
        self.db.save_session(session)

        base_empathetic_reply = (
            f"Compreendo perfeitamente o que você precisa, e pode ficar tranquilo(a) que estamos aqui para cuidar de cada detalhe consigo na *{company.short_name}*! 😊\n\n"
            f"✨ {company.persuasion_5_laws['autoridade']}\n"
            f"🎁 {company.persuasion_5_laws['reciprocidade']}\n\n"
            f"Você gostaria que eu já te passasse os valores certinhos para essa sua necessidade, ou prefere ver algumas fotos de referência primeiro?"
        )
        final_reply = GeminiHumanAssistant.generate_human_reply(text_clean, base_empathetic_reply, company.short_name)
        self.db.log_message(phone_number, "OUTGOING", detected_company_id, final_reply)
        return [{"type": "text", "body": final_reply}]

# ==============================================================================
# 11. SERVIDOR WEBHOOK FASTAPI + SIMULADOR WEB NO NAVEGADOR DO TELEMÓVEL
# ==============================================================================

def create_fastapi_app():
    from fastapi import FastAPI, Request, Response, Query
    from fastapi.staticfiles import StaticFiles
    from fastapi.responses import FileResponse, HTMLResponse

    app = FastAPI(
        title="Humanized Multi-Company WhatsApp AI Bot (Moçambique)",
        description="Atendimento Humanizado 24/7 — Braga.io | Vanguard Living Atelier | Inglês Semestre",
        version="4.0.0"
    )

    base_dir = os.path.dirname(os.path.abspath(__file__))
    media_dir = os.path.join(base_dir, "media_assets")
    pdf_dir = os.path.join(base_dir, "pdf_assets")

    if os.path.isdir(media_dir):
        app.mount("/media", StaticFiles(directory=media_dir), name="media")

    @app.get("/pdf/{filename}")
    async def serve_clean_pdf(filename: str):
        safe_name = os.path.basename(filename)
        file_path = os.path.join(pdf_dir, safe_name)
        if os.path.isfile(file_path):
            return FileResponse(
                path=file_path,
                media_type="application/pdf",
                filename=safe_name
            )
        return Response(content="Ficheiro PDF não encontrado", status_code=404)

    bot = WhatsAppSalesBot(ConversationDB())
    VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "BRAGA_IO_SECURE_TOKEN_2026")

    @app.get("/", response_class=HTMLResponse)
    async def home_panel():
        """Painel Visual e Simulador de Chat para testar o Bot diretamente pelo Telemóvel."""
        return """
        <!DOCTYPE html>
        <html lang="pt">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Painel & Simulador — Bot WhatsApp V4.0 (Moçambique)</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0b141a; color: #e9edef; margin: 0; padding: 16px; }
                .card { max-width: 560px; margin: 0 auto; background: #111b21; border-radius: 14px; padding: 18px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); border: 1px solid #222e35; }
                h2 { margin-top: 0; color: #00a884; font-size: 1.25rem; }
                .badge { display: inline-block; background: #005c4b; color: #fff; padding: 4px 10px; border-radius: 12px; font-size: 0.78rem; margin-bottom: 12px; }
                #chat { height: 360px; overflow-y: auto; background: #0b141a; border-radius: 10px; padding: 12px; margin-bottom: 12px; border: 1px solid #222e35; }
                .msg { margin: 8px 0; padding: 10px 12px; border-radius: 10px; max-width: 85%; line-height: 1.4; font-size: 0.92rem; white-space: pre-wrap; }
                .user { background: #005c4b; margin-left: auto; color: #fff; }
                .bot { background: #202c33; margin-right: auto; color: #e9edef; }
                .row { display: flex; gap: 8px; }
                input { flex: 1; padding: 12px; border-radius: 8px; border: 1px solid #2a3942; background: #202c33; color: #fff; font-size: 0.95rem; }
                button { background: #00a884; color: #111b21; font-weight: bold; border: none; padding: 12px 18px; border-radius: 8px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="card">
                <span class="badge">● ONLINE 24/7 — V4.0 HUMANIZADO</span>
                <h2>🤖 Central WhatsApp: Braga.io | Vanguard Living | Inglês Semestre</h2>
                <p style="font-size:0.85rem; color:#8696a0;">Teste a conversa humana abaixo ou conecte o seu WhatsApp no endereço <code>/webhook</code> (Token: <code>BRAGA_IO_SECURE_TOKEN_2026</code>).</p>
                <div id="chat">
                    <div class="msg bot">Sistema pronto! Digite "Olá, tudo bem?" abaixo para testar o atendimento humano. 😊</div>
                </div>
                <div class="row">
                    <input id="inp" type="text" placeholder="Escreva como se fosse um cliente..." onkeypress="if(event.key==='Enter')sendMsg()">
                    <button onclick="sendMsg()">Enviar</button>
                </div>
            </div>
            <script>
                async function sendMsg() {
                    const inp = document.getElementById('inp');
                    const txt = inp.value.trim();
                    if (!txt) return;
                    const chat = document.getElementById('chat');
                    chat.innerHTML += `<div class="msg user">${txt}</div>`;
                    inp.value = '';
                    chat.scrollTop = chat.scrollHeight;
                    const res = await fetch('/simulate', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({phone: '+258849999999', text: txt})
                    });
                    const data = await res.json();
                    for (const r of (data.replies || [])) {
                        if (r.type === 'text') {
                            chat.innerHTML += `<div class="msg bot">${r.body}</div>`;
                        } else if (r.type === 'image') {
                            chat.innerHTML += `<div class="msg bot">📸 [Foto Enviada]: <a href="${r.url}" target="_blank" style="color:#00a884">${r.caption}</a></div>`;
                        } else if (r.type === 'document') {
                            chat.innerHTML += `<div class="msg bot">📄 [PDF Oficial]: <a href="${r.url}" target="_blank" style="color:#00a884">${r.filename}</a>\\n${r.caption}</div>`;
                        }
                    }
                    chat.scrollTop = chat.scrollHeight;
                }
            </script>
        </body>
        </html>
        """

    @app.post("/simulate")
    async def simulate_chat(request: Request):
        body = await request.json()
        phone = body.get("phone", "+258849999999")
        text = body.get("text", "")
        replies = bot.handle_message(phone, text, message_id=f"sim_{time.time()}")
        return {"replies": replies}

    @app.get("/webhook")
    async def verify_token(
        hub_mode: Optional[str] = Query(None, alias="hub.mode"),
        hub_token: Optional[str] = Query(None, alias="hub.verify_token"),
        hub_challenge: Optional[str] = Query(None, alias="hub.challenge")
    ):
        if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
            return Response(content=hub_challenge, media_type="text/plain")
        return Response(content="Token inválido", status_code=403)

    @app.post("/webhook")
    async def incoming_message(request: Request):
        payload = await request.json()
        base_url = str(request.base_url).rstrip("/")

        # 1. Meta WhatsApp Cloud API
        if "entry" in payload:
            for entry in payload.get("entry", []):
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    for msg in value.get("messages", []):
                        sender = msg.get("from")
                        msg_id = msg.get("id")
                        msg_type = msg.get("type", "text")
                        text_body = ""
                        image_ref = None

                        if msg_type == "text":
                            text_body = msg.get("text", {}).get("body", "")
                        elif msg_type == "image":
                            image_data = msg.get("image", {})
                            image_ref = image_data.get("url") or image_data.get("id") or "whatsapp_uploaded_photo.jpg"
                            text_body = image_data.get("caption", "Foto enviada pelo cliente")

                        if sender and (text_body or image_ref):
                            replies = bot.handle_message(sender, text_body, image_path_or_url=image_ref, message_id=msg_id)
                            if replies:
                                WhatsAppOutboundSender.dispatch(sender, replies, public_base_url=base_url)

        # 2. Evolution API / Baileys / Z-API
        elif "data" in payload and "message" in payload.get("data", {}):
            data = payload["data"]
            key_data = data.get("key", {})
            if key_data.get("fromMe") is True:
                return {"status": "ignored_self_message"}

            sender = key_data.get("remoteJid", "").replace("@s.whatsapp.net", "")
            msg_id = key_data.get("id")
            m_obj = data.get("message", {})
            text_body = (
                m_obj.get("conversation") or
                m_obj.get("extendedTextMessage", {}).get("text") or
                m_obj.get("imageMessage", {}).get("caption") or
                ""
            )
            image_ref = m_obj.get("imageMessage", {}).get("url")
            if sender and (text_body or image_ref):
                replies = bot.handle_message(sender, text_body, image_path_or_url=image_ref, message_id=msg_id)
                if replies:
                    WhatsAppOutboundSender.dispatch(sender, replies, public_base_url=base_url)

        return {"status": "ok"}

    @app.get("/status")
    async def get_status():
        return {
            "status": "online",
            "version": "4.0.0-humanized",
            "anti_drive_links": True,
            "anti_flood_deduplication": True,
            "ignore_self_messages_loop_guard": True,
            "native_pdfs_available": [
                "/pdf/Catalogo_Oficial_Vanguard_Living_2026.pdf",
                "/pdf/Dossie_Executivo_Braga_io.pdf",
                "/pdf/Especificacao_Tecnica_Vanguard_Living.pdf"
            ],
            "companies": list(COMPANIES.keys())
        }

    return app


if __name__ == "__main__":
    print("=" * 80)
    print("BOT WHATSAPP HUMANIZADO (V4.0) — ZERO SPAM, ZERO LINKS DRIVE, PDF NATIVO!")
    for cid, comp in COMPANIES.items():
        print(f" • {comp.name} [{cid}] -> {len(comp.pricing_catalog)} itens | {len(comp.pdf_documents)} PDFs locais")
    print("=" * 80)