# SDR Agent - Elite Dev IA

Agente SDR automatizado usando IA Gemini + Gradio que atende leads, conduz conversas naturais e agenda reuniões.

## 🚀 Setup Rápido

1. **Criar ambiente virtual:**
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

2. **Instalar dependências:**
```bash
pip install -r requirements.txt
```

3. **Configurar variáveis (.env):**
```
# IA Provider (apenas Gemini)
LLM_PROVIDER=gemini
GEMINI_API_KEY=sua_chave_gemini

# Integrações
PIPEFY_API_TOKEN=seu_token_pipefy  
CAL_API_TOKEN=seu_token_cal
PIPEFY_PIPE_ID=seu_pipe_id
```

4. **Executar:**
```bash
python app.py
```

## 🎯 Funcionalidades

- ✅ Conversa natural via IA Gemini 2.5 Flash
- ✅ Function calling customizado com fallback automático
- ✅ Coleta dados: nome, email, empresa, necessidade
- ✅ Confirmação de interesse
- ✅ Agendamento automático de reuniões
- ✅ Registro no Pipefy com prevenção de duplicatas
- ✅ Interface responsiva com Gradio

## 🔧 Fluxo do Agente

1. **Apresentação** - Se apresenta como SDR da empresa
2. **Descoberta** - Coleta informações do lead progressivamente
3. **Qualificação** - Pergunta sobre interesse em reunião
4. **Agendamento** - Oferece horários e agenda automaticamente
5. **Registro** - Salva no Pipefy com todos os dados

## 🔗 Integrações

### Gemini 2.5 Flash + Fallback
- Múltiplos modelos: 2.5-flash → 2.0-flash → flash-latest
- Function calling via formato customizado [FUNÇÃO:nome:json]
- Conversa natural em português
- Fallback automático para máxima disponibilidade
- Tratamento robusto de erros e rate limits

### Pipefy API
- Endpoint GraphQL: `https://api.pipefy.com/graphql`
- Campos: nome, email, empresa, necessidade, interesse_confirmado, meeting_link
- Prevenção de duplicatas usando email como chave única
- Atualização automática de cards existentes

### Cal.com API
- Agendamento automático via API v1
- Criação de eventos com timezone Brasil
- Retorna link direto da reunião
- Configuração de duração por event type

## 📋 Fluxo Detalhado

1. **Saudação**: "Olá! Sou assistente da Elite Dev IA..."
2. **Descoberta**: Coleta nome, email, empresa, necessidade
3. **Qualificação**: "Gostaria de agendar uma conversa com nosso time?"
4. **Registro**: Salva lead no Pipefy com interesse confirmado
5. **Agendamento**: Oferece 3 horários → Usuário escolhe → Agenda automaticamente
6. **Confirmação**: Retorna link da reunião e atualiza Pipefy

## 🚨 Configuração Obrigatória

**Antes de executar, configure no .env:**
```bash
# IA (obrigatório)
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIza...  # Obter em https://aistudio.google.com/

# Pipefy (obrigatório)
PIPEFY_API_TOKEN=eyJ...  # Token de API do Pipefy
PIPEFY_PIPE_ID=123456   # ID do pipe de pré-vendas

# Cal.com (obrigatório)
CAL_API_TOKEN=cal_live_...  # Token da API Cal.com
```

## 📊 Dados Coletados

- ✅ Nome completo
- ✅ Email (chave única para duplicatas)
- ✅ Empresa
- ✅ Necessidade/dor específica
- ✅ Status de interesse (boolean)
- ✅ Link da reunião (se agendada)
- ✅ Data/hora da reunião (ISO format)

## 🎯 Critérios de Sucesso

- [x] Conversa natural e progressiva
- [x] Function calling customizado com fallback
- [x] Confirmação explícita de interesse
- [x] Agendamento automático funcional
- [x] Persistência no Pipefy sem duplicatas
- [x] Interface limpa sem logs desnecessários
- [x] Tratamento robusto de erros

## 🧪 Testes

**Executar todos os testes:**
```bash
python tests.py
```

**Testar individualmente:**
```bash
# Testar Gemini
python -c "from agent.llm_factory import get_llm_provider; print('✅ Gemini OK' if get_llm_provider() else '❌ Erro')"

# Testar Pipefy
python -c "from tests import testar_pipefy; testar_pipefy()"

# Testar Cal.com
python -c "from tests import testar_cal; testar_cal()"
```

## 🔧 Troubleshooting

**Erro Gemini**: Verifique se GEMINI_API_KEY está correta
**Erro 429 (Rate Limit)**: Sistema tenta automaticamente outros modelos
**Erro Pipefy**: Confirme PIPEFY_API_TOKEN e PIPEFY_PIPE_ID
**Erro Cal.com**: Verifique CAL_API_TOKEN (formato: cal_live_...)
**Erro 401**: Tokens inválidos ou expirados

## 📱 Deploy

**Gradio automático:**
```bash
python app.py  # Gera link público automaticamente
```

**Gradio Cloud:**
```bash
gradio deploy
```

**Hugging Face Spaces:**
- Upload arquivos + requirements.txt
- Configure secrets no HF Spaces

## 🧪 Teste Local

**Interface:** http://localhost:7861
**Porta:** 7861 (configurável no app.py)

## 📁 Estrutura do Projeto

```
sdr-agent/
├── agent/
│   ├── llm_factory.py      # Provider Gemini com fallback
│   └── sdr_agent.py        # Lógica principal
├── integracoes/
│   ├── cal_integration.py  # Cal.com API
│   └── pipefy_real.py      # Pipefy GraphQL
├── app.py                  # Interface Gradio
├── tests.py               # Testes centralizados
├── requirements.txt       # Dependências
└── .env                   # Configurações
```