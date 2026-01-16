import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO INICIAL ---
try:
    CHAVE_SECRETA = st.secrets["CHAVE_SECRETA"]
except:
    st.error("❌ Erro de Chave: Configure a 'CHAVE_SECRETA' nos Secrets do Streamlit.")
    st.stop()

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Analisador Loft (V28 - Dinâmico)", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        div.stButton > button:first-child {
            background-color: #ff6200;
            color: white;
            font-weight: bold;
            border: none;
            width: 100%;
            padding: 15px;
            font-size: 18px;
            text-transform: uppercase;
            border-radius: 8px;
        }
        div.stButton > button:first-child:hover {
            background-color: #e55800;
            color: white;
        }
        
        /* CARD VISUAL */
        .card { padding: 12px; margin-bottom: 8px; border-radius: 6px; border-left: 5px solid; display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; font-size: 14px; background-color: #1e1e1e; }
        .card-green { border-color: #28a745; color: #e6ffe6; }
        .card-yellow { border-color: #ffc107; color: #fffbe6; }
        .card-red { border-color: #dc3545; color: #ffe6e6; }
        .badge { padding: 2px 6px; border-radius: 4px; font-size: 10px; font-weight: bold; margin-left: 10px; text-transform: uppercase; color: black; }
        .bg-green { background-color: #28a745; color: white; }
        .bg-yellow { background-color: #ffc107; }
        .card-price { font-weight: bold; font-size: 15px; min-width: 80px; text-align: right; }
        .section-title { margin-top: 20px; font-weight: bold; text-transform: uppercase; font-size: 16px; }
        .green-text { color: #28a745; }
        .yellow-text { color: #ffc107; }
        .red-text { color: #dc3545; }
    </style>
""", unsafe_allow_html=True)

# --- 3. REGRAS DINÂMICAS ---

# REGRA 0: Só é enviada para a IA se houver arquivo de Vistoria de Entrada
REGRA_COMPARACAO = """
--- 0. REGRA DE OURO: DANO PRÉ-EXISTENTE (MODO COMPARATIVO ATIVO) ---
O USUÁRIO FORNECEU A VISTORIA DE ENTRADA. SUA OBRIGAÇÃO É COMPARAR.
Antes de aprovar qualquer item (inclusive Pintura Interna), verifique a VISTORIA DE ENTRADA fornecida.
Se o item já estava descrito como "Desgastado", "Ruim", "Manchado", "Riscado" ou "Danificado" na ENTRADA e não houve piora significativa:
❌ STATUS: Negado
❌ MOTIVO OBRIGATÓRIO (Copiar exatamente):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."
"""

# BASE DE CONHECIMENTO PADRÃO (Sempre ativa)
BASE_CONHECIMENTO = """
VOCÊ É O AUDITOR OFICIAL DA LOFT FIANÇA.
Analise cada item do orçamento aplicando estritamente as regras abaixo.
Se for NEGAR, use EXATAMENTE as frases abaixo.

--- 1. LIMPEZA (APROVAR SUJEIRA, NEGAR MATO) ---
A regra de "Desgaste Natural" NÃO se aplica a sujeira.
✅ APROVAR: "Limpeza interna", "Faxina", "Limpeza pesada", "Limpeza externa" (piso/entulho), "Caixa de gordura", "Bota-fora".

--- 2. PINTURA INTERNA (APROVAR) ---
Pintura de PAREDES, TETOS, PORTAS (Lado interno).
Regra Padrão: O inquilino deve devolver pintado/novo.
✅ STATUS: Aprovado
MOTIVO: "Pintura interna danificada/suja (Mau uso ou falta de conservação)."

--- 3. PINTURA EXTERNA E JARDINAGEM (NEGAR - AÇÃO DO TEMPO) ---
Itens expostos ao tempo (Sol, Chuva).
❌ ITENS A NEGAR: Pintura de Fachada, Muros, Portões Externos, Telhados, Jardinagem, Capina.
❌ MOTIVO OBRIGATÓRIO (Copiar exatamente):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco."

🚨 EXCEÇÃO (ANIMAIS): Se citar "Animal", "Cachorro", "Urina" → ✅ APROVADO (Motivo: Danos por animais).

--- 4. RESTITUIÇÃO AO ESTADO ORIGINAL (APROVAR REMOÇÕES) ---
Remover benfeitorias feitas pelo inquilino (Canil, Divisória, Varal, Telas).
✅ STATUS: Aprovado
MOTIVO: "Restituição do imóvel ao estado original (Remoção de benfeitoria não autorizada)."

--- 5. DESGASTE NATURAL / MOBÍLIA (NEGAR) ---
Itens móveis, desgaste de piso (riscos leves), lâmpadas, móveis planejados (uso normal).
❌ STATUS: Negado
❌ MOTIVO OBRIGATÓRIO (Copiar exatamente):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."

--- 6. REDES HIDRÁULICAS E ELÉTRICAS ---
A) NEGAR (Oculto): Fiação interna, resistência queimada, cano oculto, Alarme.
❌ MOTIVO OBRIGATÓRIO: "Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos."
B) APROVAR (Físico): Tomadas quebradas, Torneiras quebradas, Louças quebradas.

--- 7. ATO ILÍCITO / FURTO (NEGAR) ---
❌ MOTIVO OBRIGATÓRIO: "Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada."

--- FORMATO DE SAÍDA (JSON) ---
[
  {
    "Item": "Texto original",
    "Valor": 0.00,
    "Status": "Aprovado / Atenção / Negado",
    "Motivo": "Cole a frase exata aqui"
  }
]
"""

# EXEMPLOS DE APRENDIZADO
EXEMPLOS_TREINAMENTO = """
USE ESTES CASOS REAIS COMO GABARITO (ATENÇÃO AOS TEXTOS EXATOS):

--- CASOS DE JARDINAGEM E TEMPO (MOTIVO LONGO) ---
Item: "Limpeza Mato / Capina química" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco."

--- CASOS DE DESGASTE SIMPLES (MOTIVO CURTO) ---
Item: "Kit lâmpadas LED" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."

--- CASOS ELÉTRICOS OCULTOS (MOTIVO REDES) ---
Item: "Manutenção Central de Alarme" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos."

--- CASOS DE RESTITUIÇÃO E ANIMAIS (APROVADOS) ---
Item: "Remover 07 Canil Cimento" -> APROVADO (Motivo: Restituição ao estado original).
Item: "Pintura das paredes e portões - danificados por xixi de cachorro" -> APROVADO (Motivo: Danos causados por animais de estimação).
"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (V28 - Dinâmico)")
st.caption("Lógica Inteligente: Só verifica 'Dano Pré-existente' se houver Vistoria de Entrada anexada.")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada (Opcional)", type=['pdf', 'jpg', 'png'], key="entrada")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída (Opcional)", type=['pdf', 'jpg', 'png'], key="saida")

st.markdown("---")
st.markdown("### 💰 3. Orçamento")
tab_txt, tab_arq = st.tabs(["📝 Colar Texto", "📂 Anexar Arquivo"])
with tab_txt:
    orcamento_texto = st.text_area("Cole aqui:", height=150, placeholder="Ex: Item 1... R$ 100,00", label_visibility="collapsed")
with tab_arq:
    orcamento_arquivo = st.file_uploader("Upload Orçamento", type=['pdf', 'jpg', 'png'], key="orcamento")

# --- 5. PROCESSAMENTO ---
if st.button("⚡ ANALISAR AGORA"):
    
    if not (orcamento_texto or orcamento_arquivo):
        st.error("⚠️ Insira o orçamento.")
        st.stop()

    with st.status("⚖️ Processando regras...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "temperature": 0.0})
            
            prompt_parts = []

            # --- LÓGICA DINÂMICA (AQUI ESTÁ O SEGREDO) ---
            # Se o usuário mandou a Vistoria de Entrada, adicionamos a REGRA DE COMPARAÇÃO.
            # Se não mandou, essa regra nem entra no prompt, evitando confusão.
            if vistoria_entrada:
                prompt_parts.append(REGRA_COMPARACAO) # <--- SÓ ENTRA SE TIVER ARQUIVO
                st.toast("Modo Comparativo: ATIVADO ✅")
            
            # Adiciona as regras padrão e os exemplos
            prompt_parts.append(BASE_CONHECIMENTO)
            prompt_parts.append(EXEMPLOS_TREINAMENTO)

            # Adiciona os arquivos
            if vistoria_entrada:
                prompt_parts.append("CONTEXTO: DOCUMENTO DE VISTORIA DE ENTRADA")
                prompt_parts.append({"mime_type": vistoria_entrada.type, "data": vistoria_entrada.getvalue()})
            
            if vistoria_saida:
                prompt_parts.append("CONTEXTO: DOCUMENTO DE VISTORIA DE SAÍDA")
                prompt_parts.append({"mime_type": vistoria_saida.type, "data": vistoria_saida.getvalue()})

            prompt_parts.append("ORÇAMENTO A ANALISAR:")
            if orcamento_arquivo:
                prompt_parts.append({"mime_type": orcamento_arquivo.type, "data": orcamento_arquivo.getvalue()})
            else:
                prompt_parts.append(orcamento_texto)

            # Gera a resposta
            response = model.generate_content(prompt_parts)
            df = pd.read_json(io.StringIO(response.text))
            
            status.update(label="✅ Análise Concluída!", state="complete", expanded=False)

            # --- 6. VISUALIZAÇÃO ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            atencao = df[df['Status'].str.contains("Atenção|Amarela", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]

            if not aprovados.empty:
                st.markdown('<div class="section-title green-text">✅ APROVADOS (Cobrança Devida)</div>', unsafe_allow_html=True)
                for i, row in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><div>{row["Item"]}</div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not atencao.empty:
                st.markdown('<div class="section-title yellow-text">⚠️ ATENÇÃO (Validar)</div>', unsafe_allow_html=True)
                for i, row in atencao.iterrows():
                    st.markdown(f'<div class="card card-yellow"><div>{row["Item"]}</div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.markdown('<div class="section-title red-text">⛔ NEGADOS (Conforme Termo)</div>', unsafe_allow_html=True)
                for i, row in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><div>{row["Item"]}</div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            # --- 7. ÁREA DE CÓPIA PARA ONENOTE ---
            st.divider()
            st.subheader("📋 Relatório Final (Para OneNote)")
            st.info("💡 Passe o mouse no canto da caixa preta para copiar.")

            relatorio = "RELATÓRIO DE ANÁLISE TÉCNICA - LOFT FIANÇA\n"
            relatorio += "========================================\n\n"
            
            if not aprovados.empty:
                relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    relatorio += f"[+] {r['Item']} | R$ {r['Valor']:.2f}\n"
                relatorio += "\n"
            
            if not atencao.empty:
                relatorio += "⚠️ ATENÇÃO:\n"
                for i, r in atencao.iterrows():
                    relatorio += f"[?] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    relatorio += f"    Motivo: {r['Motivo']}\n"
                relatorio += "\n"

            if not negados.empty:
                relatorio += "⛔ NEGADOS:\n"
                for i, r in negados.iterrows():
                    relatorio += f"[-] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    relatorio += f"    Justificativa: {r['Motivo']}\n"
            
            total_aprovado = aprovados['Valor'].sum()
            total_negado = negados['Valor'].sum()
            
            relatorio += "\n========================================\n"
            relatorio += f"💰 TOTAL APROVADO:   R$ {total_aprovado:.2f}\n"
            relatorio += f"📉 TOTAL ECONOMIZADO: R$ {total_negado:.2f}\n"
            relatorio += "========================================"

            st.code(relatorio, language='text')

        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error("Erro ao processar.")
            st.write(e)
