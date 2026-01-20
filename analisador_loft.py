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
st.set_page_config(page_title="Analisador Loft (V23)", page_icon="🏢", layout="wide")

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

# --- 3. BASE DE CONHECIMENTO (V23 - CRUZAMENTO ENTRADA x SAÍDA) ---
BASE_CONHECIMENTO = """
VOCÊ É O AUDITOR OFICIAL DA LOFT FIANÇA.
Sua missão principal é comparar Vistoria de Entrada vs. Saída.

--- 🔴 REGRA ZERO (A MAIS IMPORTANTE): CRUZAMENTO DE DADOS ---
Antes de aprovar qualquer item, verifique a "Vistoria de Entrada" (se fornecida).
SE O DANO JÁ EXISTIA NA ENTRADA (Mesmo estado, risco, mancha ou quebra) -> O STATUS DEVE SER NEGADO.
Não importa se é pintura interna ou limpeza. Se já estava assim, o inquilino não paga.
❌ MOTIVO: "Dano pré-existente (Já constava na Vistoria de Entrada)."

--- 1. LIMPEZA (Se não for pré-existente -> APROVAR) ---
Se o imóvel foi entregue limpo e devolvido sujo:
✅ ITENS: "Limpeza interna/externa", "Faxina", "Retirada de lixo/entulho", "Caixa de gordura".
✅ MOTIVO: "Falta de manutenção adequada (Imóvel entregue sujo)."

--- 2. PINTURA INTERNA (Se não for pré-existente -> APROVAR) ---
Pintura de PAREDES, TETOS, PORTAS (Lado interno).
Se na entrada estava bom e na saída tem riscos/sujeira/furos:
✅ STATUS: Aprovado
✅ MOTIVO: "Pintura interna danificada/suja (Mau uso ou falta de conservação)."

--- 3. PINTURA EXTERNA (SEM COBERTURA -> NEGAR) ---
Itens expostos a chuva/sol (Muros, Fachadas, Portões externos).
❌ STATUS: Negado
❌ MOTIVO: "Pagamento negado... danos causados pela ação paulatina de temperatura e umidade."

--- 4. ITENS NÃO FIXOS / MOBÍLIA (NEGAR) ---
Sofás, cortinas, eletros, móveis soltos.
❌ STATUS: Negado
❌ MOTIVO: "Pagamento negado... item não fixo/mobília."

--- 5. REDES HIDRÁULICAS E ELÉTRICAS ---
A) NEGAR (Vício Oculto): Fiação interna, cano estourado dentro da parede.
B) APROVAR (Dano Físico): Tomadas quebradas, Torneiras soltas, Louças quebradas.

--- 6. ATO ILÍCITO (Itens Furtados/Retirados) ---
❌ STATUS: Negado
❌ MOTIVO: "Danos causados por atos ilícitos (Item retirado/furtado)..."

--- FORMATO DE SAÍDA (JSON) ---
[
  {
    "Item": "Texto original",
    "Valor": 0.00,
    "Status": "Aprovado / Atenção / Negado",
    "Motivo": "Justificativa curta"
  }
]
"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (V23 - Comparador Inteligente)")
st.caption("Regra Suprema Ativa: Se o dano já existia na entrada, o sistema NEGA automaticamente.")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada (Obrigatório p/ Comparar)", type=['pdf', 'jpg', 'png'], key="entrada")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída", type=['pdf', 'jpg', 'png'], key="saida")

st.markdown("---")
st.markdown("### 💰 3. Orçamento")
tab_txt, tab_arq = st.tabs(["📝 Colar Texto", "📂 Anexar Arquivo"])
with tab_txt:
    orcamento_texto = st.text_area("Cole aqui:", height=150, placeholder="Ex: Pintura Sala... R$ 500,00", label_visibility="collapsed")
with tab_arq:
    orcamento_arquivo = st.file_uploader("Upload Orçamento", type=['pdf', 'jpg', 'png'], key="orcamento")

# --- 5. PROCESSAMENTO ---
if st.button("⚡ ANALISAR CRUZAMENTO DE DADOS"):
    
    if not (orcamento_texto or orcamento_arquivo):
        st.error("⚠️ Insira o orçamento.")
        st.stop()

    with st.status("🧠 Cruzando Vistoria de Entrada vs. Saída...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "temperature": 0.0})
            
            prompt_parts = [BASE_CONHECIMENTO]

            if vistoria_entrada:
                prompt_parts.append("CONTEXTO: DOCUMENTO DE VISTORIA DE ENTRADA (PROVA DO ESTADO INICIAL)")
                prompt_parts.append({"mime_type": vistoria_entrada.type, "data": vistoria_entrada.getvalue()})
            else:
                prompt_parts.append("AVISO: SEM VISTORIA DE ENTRADA. APLIQUE REGRAS PADRÃO.")
            
            if vistoria_saida:
                prompt_parts.append("CONTEXTO: DOCUMENTO DE VISTORIA DE SAÍDA (ESTADO FINAL)")
                prompt_parts.append({"mime_type": vistoria_saida.type, "data": vistoria_saida.getvalue()})

            prompt_parts.append("ORÇAMENTO A ANALISAR (Compare com a Entrada se houver):")
            if orcamento_arquivo:
                prompt_parts.append({"mime_type": orcamento_arquivo.type, "data": orcamento_arquivo.getvalue()})
            else:
                prompt_parts.append(orcamento_texto)

            response = model.generate_content(prompt_parts)
            df = pd.read_json(io.StringIO(response.text))
            
            status.update(label="✅ Comparação Concluída!", state="complete", expanded=False)

            # --- 6. VISUALIZAÇÃO ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            atencao = df[df['Status'].str.contains("Atenção|Amarela", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]

            if not aprovados.empty:
                st.markdown('<div class="section-title green-text">✅ APROVADOS (Dano Novo / Sujeira Nova)</div>', unsafe_allow_html=True)
                for i, row in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><div>{row["Item"]}</div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not atencao.empty:
                st.markdown('<div class="section-title yellow-text">⚠️ ATENÇÃO (Verificar)</div>', unsafe_allow_html=True)
                for i, row in atencao.iterrows():
                    st.markdown(f'<div class="card card-yellow"><div>{row["Item"]}</div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.markdown('<div class="section-title red-text">⛔ NEGADOS (Pré-existente ou Indevido)</div>', unsafe_allow_html=True)
                for i, row in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><div>{row["Item"]}<br><small>Motivo: {row["Motivo"]}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            # --- 7. COPY AREA ---
            st.divider()
            st.subheader("📋 Relatório Final")
            st.info("💡 Passe o mouse na caixa preta para copiar.")

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
            st.error("Erro ao processar. Verifique os arquivos.")
            st.write(e)
