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
st.set_page_config(page_title="Analisador Loft (V20)", page_icon="🏢", layout="wide")

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

# --- 3. BASE DE CONHECIMENTO (REGRAS DE PINTURA ATUALIZADAS) ---
BASE_CONHECIMENTO = """
VOCÊ É O AUDITOR OFICIAL DA LOFT FIANÇA.
Sua análise deve ser estritamente baseada nas regras abaixo.

--- 1. REGRA DE OURO: PINTURA INTERNA (SEMPRE APROVAR) ---
Qualquer pintura de PAREDES, TETOS, PORTAS ou JANELAS que fiquem DENTRO do imóvel (Interno ou com cobertura) deve ser APROVADA.
Não importa se a justificativa é "sujeira", "furos", "riscos" ou "tempo". Pintura interna é responsabilidade do inquilino entregar nova.
✅ STATUS: Aprovado

--- 2. REGRA: PINTURA EXTERNA (SEM COBERTURA -> NEGAR) ---
Apenas pinturas de itens expostos ao tempo (sem telhado/cobertura) devem ser negadas por ação do tempo.
Itens: Fachada do prédio, Muros externos, Calçadas, Portões de garagem expostos à chuva/sol.
❌ STATUS: Negado
❌ MOTIVO: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel... danos causados pela ação paulatina de temperatura, umidade..."

--- 3. ITENS NÃO FIXOS / MOBÍLIA (NEGAR) ---
Itens móveis: Sofás, camas, mesas, cadeiras, cortinas, persianas, tapetes, eletrodomésticos.
❌ STATUS: Negado
❌ MOTIVO: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel."

--- 4. REDES HIDRÁULICAS E ELÉTRICAS (ANÁLISE MISTA) ---
A) NEGAR (Vício Oculto/Interno): Fiação dentro da parede, resistência queimada, vazamento oculto, cano estourado.
❌ MOTIVO: "Pagamento negado... danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes..."

B) APROVAR (Mau Uso Aparente): Tomadas/Interruptores quebrados, arrancados ou pintados. Torneiras/Louças quebradas fisicamente.
✅ STATUS: Aprovado

--- 5. ATO ILÍCITO / ITENS RETIRADOS (NEGAR) ---
Se o item foi FURTADO ou RETIRADO.
❌ MOTIVO: "Danos causados por atos ilícitos, dolosos ou por culpa grave..."

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
st.title("🏢 Analisador Loft (V20 - Pintura Correta)")
st.caption("Regra de Pintura Interna Atualizada: Sempre Aprovar.")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada", type=['pdf', 'jpg', 'png'], key="entrada")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída", type=['pdf', 'jpg', 'png'], key="saida")

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

    with st.status("⚖️ Verificando regras de pintura...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "temperature": 0.0})
            
            prompt_parts = [BASE_CONHECIMENTO]

            if vistoria_entrada:
                prompt_parts.append("CONTEXTO: ENTRADA")
                prompt_parts.append({"mime_type": vistoria_entrada.type, "data": vistoria_entrada.getvalue()})
            
            if vistoria_saida:
                prompt_parts.append("CONTEXTO: SAÍDA")
                prompt_parts.append({"mime_type": vistoria_saida.type, "data": vistoria_saida.getvalue()})

            prompt_parts.append("ORÇAMENTO A ANALISAR:")
            if orcamento_arquivo:
                prompt_parts.append({"mime_type": orcamento_arquivo.type, "data": orcamento_arquivo.getvalue()})
            else:
                prompt_parts.append(orcamento_texto)

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
                    # Removemos a justificativa dos aprovados para ficar mais limpo, se quiser pode voltar
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
