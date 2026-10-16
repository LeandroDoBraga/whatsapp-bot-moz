# Multi-Company WhatsApp Humanized AI Bot — Edição Oficial Moçambique (V4.0) 🤝🇲🇿

Sistema de atendimento **100% humanizado, acolhedor e blindado contra bugs**, projetado para responder aos seus clientes da **Braga.io**, **Vanguard Living Atelier** e **Inglês Semestre** enquanto você estiver ausente, fazendo cada cliente sentir-se acolhido, compreendido e seguro.

---

## 🛡️ O Que Foi Corrigido em Relação ao Seu Sistema Antigo (Blindagem V4.0)

| Problema que Acontecia no Bot Antigo | Como o Novo Motor V4.0 Resolve Definitivamente |
| :--- | :--- |
| **Cliente dizia apenas *"Olá"*, *"Tudo bem?"* ou *"Como é que é?"* e o bot despejava tudo das empresas de uma vez (assustando o cliente)** | **Saudação Humana e Leve (`is_pure_greeting`)**: Quando alguém saúda, o bot responde com carinho em apenas 2 parágrafos curtos (*"Olá! Tudo ótimo por aqui, graças a Deus! E consigo, como está tudo? 😊"*), perguntando com gentileza em que pode ajudar, sem despejar tabelas nem arquivos. |
| **Mandava links de Google Drive que não existem (`drive.google.com`)** | **Filtro `OutputSanitizer` Anti-Drive**: Bloqueia e remove qualquer tentativa da IA de inventar links de Google Drive ou links externos quebrados. |
| **Mandava um PDF esquisito logo no início que abria cheio de códigos estranhos** | **Conhecimento na Memória + PDF Binário Limpo Sob Demanda**: O bot já sabe todos os preços, fórmulas e regras na própria conversa (não precisa de PDF para atender). E, se o cliente pedir explicitamente o PDF, o servidor entrega o arquivo original íntegro (`/pdf/Catalogo_Oficial_Vanguard_Living_2026.pdf` ou `/pdf/Dossie_Executivo_Braga_io.pdf`) com cabeçalho binário oficial (`application/pdf`), sem códigos estranhos. |
| **Repetição infinita de mensagens e inundação do chat (parecendo vírus ou burla)** | **Dupla Trava (`fromMe` Loop Guard + `AntiFloodGuard`)**: Ignora mensagens enviadas pelo próprio número (`fromMe == True`) e bloqueia webhooks duplicados num intervalo de 15 segundos, garantindo que o bot **nunca** repita mensagens nem inunde o telemóvel do cliente. |

---

## 💛 As 5 Leis das Armas da Persuasão Aplicadas com Gentileza

1. **Afeição e Acolhimento (Sentir-se Amado e Recebido)**: O bot cumprimenta com calor humano, escuta a necessidade do cliente antes de falar de preços e valida o seu sonho ou preocupação.
2. **Reciprocidade Gentil**: Oferece análise gratuita da foto do sofá, visita com mostruário físico de tecidos na Matola/Maputo ou diagnóstico de sistema sem custo inicial.
3. **Prova Social Natural**: Cita com naturalidade as peças reais produzidas na oficina em Manhembana (Matola), as clínicas e bancos atendidos em Maputo e os alunos falando novos idiomas.
4. **Autoridade Serena**: Explica com segurança a estrutura em madeira tratada e espuma D35/D45, a engenharia 24/7 da Braga.io e o áudio 4-em-1 do Inglês Semestre.
5. **Compromisso Leve e Escassez Honesta**: Convida para o próximo passo com delicadeza, informando o prazo real de entrega de 15 dias e as vagas da quinzena.

---

## 🛋️ Resumo das Regras de Preço Ativas na Memória do Bot

1. **Vanguard Living Atelier (Manhembana, Boquisso — Matola)**:
   - **Se o cliente enviar foto**: Analisa a foto, calcula o custo de fabricação e aplica `[(Custo de Fabricação + 40%) × 2]`.
   - **Se o cliente não enviar foto**: Usa **sempre o Valor ALTO (Máximo — Linha Assinatura / Bouclé)** do catálogo:
     - Sofá Chaise "Aura" ou em L (3.0m–3.6m): **88.400 MZN**
     - Sofá Curvo Orgânico + Esferas (2.6m): **72.800 MZN**
     - Cama Casal/Queen + Cabeceira Estofada: **57.200 MZN**
     - Kit 3 Banquetas Altas (Ilha de Cozinha): **31.200 MZN**
     - Par de Poltronas Esculturais: **36.400 MZN**
     - Lounge Exterior Riviera (Madeira & Aço): **93.600 MZN**
     - Pacote Sala Completa Chave-na-Mão: **117.000 MZN**
2. **Inglês Semestre (Sistema Inglês sem Mestre — Prof. Braga)**:
   - **5 Línguas com Escopo de Áudio 4-em-1 Igualado** (Áudio 1.0x, Pronúncia Lenta 0.65x, Tradução Falada em Português ou **Chinês Mandarim**, e Áudio Bilingue Sequencial):
     - **Inglês (`en`)**, **Espanhol (`es`)**, **Francês (`fr`)**, **Russo (`ru`)** e **Português Especial para Chineses (`pt`)**.
   - **3 Escalões para todas as línguas**: Baixo (**500 MZN**), Médio (**1.500 MZN**) e Alto Executivo (**3.000 MZN**).
3. **Braga.io — Infraestrutura Digital para Líderes**:
   - Pergunta com gentileza o ramo/porte da empresa antes de cotar.
   - Tabela base (`3.500–10.000 MZN`, `35.000 MZN`, `70.000 MZN`, `15.000 MZN/mês`), **duplicando (2x) ou triplicando (3x)** para serviços complexos e empresas de arquitetura, e **extrapolando até `50.000.000 MZN`** para bancos.

---

## 🆓 Guia de Instalação 100% Gratuita (Passo a Passo)

Você pode rodar este bot **sem pagar absolutamente nada de mensalidade** usando a cota gratuita do Google AI Studio + hospedagem gratuita:

### Passo 1: Obter a Chave Gratuita do Gemini Flash (Opcional — o bot já funciona mesmo sem ela!)
1. Aceda gratuitamente a **aistudio.google.com** com a sua conta Google.
2. Toque em **Get API Key** ➔ **Create API Key** (é 100% gratuito).
3. Defina a variável de ambiente:
   ```bash
   export GEMINI_API_KEY="SUA_CHAVE_AQUI"
   ```

### Passo 2: Rodar o Servidor Gratuitamente
Você tem **2 opções 100% gratuitas**:

#### Opção A: Na Nuvem Gratuita 24/7 (Render.com ou Koyeb — Plano Free $0)
1. Suba os ficheiros (`whatsapp_multicompany_bot.py`, `companies_data.json`, pasta `media_assets/` e pasta `pdf_assets/`) para um repositório gratuito no **GitHub**.
2. Crie uma conta gratuita no **Render.com** (ou **Koyeb.com**) e selecione **New Web Service (Free Tier)**.
3. Comando de inicialização:
   ```bash
   uvicorn whatsapp_multicompany_bot:create_fastapi_app --factory --host 0.0.0.0 --port 8000
   ```
4. O Render gera um link seguro gratuito (`https://seu-bot.onrender.com/webhook`).

#### Opção B: Direto no Seu Computador ou Telemóvel Android (via Termux + Cloudflare Tunnel Gratuito)
1. Instale o Python e execute:
   ```bash
   pip install fastapi uvicorn requests pillow numpy
   python3 -m uvicorn whatsapp_multicompany_bot:create_fastapi_app --factory --host 0.0.0.0 --port 8000
   ```
2. Para expor na internet de graça, use o túnel gratuito da Cloudflare (`cloudflared tunnel --url http://localhost:8000`).

### Passo 3: Conectar ao Seu WhatsApp (`+258 87 778 3631`) Gratuitamente
- **Via Evolution API / Baileys (QR Code no WhatsApp Business)**: Aponte o Webhook da sua instância para `https://seu-link/webhook` marcando apenas o evento `MESSAGES_UPSERT` (o código V4.0 já tem a trava `fromMe` que impede qualquer repetição ou loop).
- **Via Meta WhatsApp Cloud API (Oficial Gratuita)**: Cole o link `https://seu-link/webhook` e o token `BRAGA_IO_SECURE_TOKEN_2026` no painel da Meta.
