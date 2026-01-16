import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. SUA CHAVE API ---
CHAVE_SECRETA = "AIzaSyAlavpN_GYrq8Xro-PRWgVmdzY0mkbvLrQ"

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Analisador Loft (V15)", page_icon="🏢", layout="wide")

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

# --- 3. REGRAS DE NEGÓCIO (AJUSTE FINO EXTERNO) ---
BASE_CONHECIMENTO = """
VOCÊ É UM AUDITOR DA LOFT. GERE UM JSON BASEADO NESTAS REGRAS ESTRITAS:

🔴 REGRA DE INTEGRIDADE (TEXTO):
NUNCA abrevie a descrição. Copie o texto do item EXATAMENTE como está no orçamento.

⚡ REGRA ELÉTRICA/HIDRÁULICA (ITENS FIXOS):
Tomadas, Espelhos, Interruptores, Torneiras:
- Faltando/Quebrado/Manchado/Solto = APROVADO (Verde).
- Parou de funcionar/Desgaste interno = NEGAR (Vermelho).

🚧 REGRA DE ÁREA EXTERNA (PORTÕES/GRADES):
Se o item for "Portão", "Grade", "Muro", "Fachada", "Calçada" ou "Telhado":
- CLASSIFICAR SEMPRE COMO "Atenção" (Amarelo).
- Motivo: "Item Externo - Verificar se é desgaste (Sol/Chuva) ou Mau Uso".

🟠 REGRAS GERAIS:
1. DESGASTE NATURAL (NEGAR): Tinta desbotada, rejunte encardido, lâmpada queimada.
2. NÃO FIXOS (NEGAR): Móveis, Cortinas, Eletros, Decoração.
3. DANOS FÍSICOS (APROVAR): Quebrados, Rasgados, Furos, Manchas, Sujeira (Exceto se for item externo, vide regra acima).
4. PINTURA: Interna (Aprovar se suja/riscada). Externa (Atenção/Amarelo).

OUTPUT JSON:
[{"Item": "Texto Original", "Valor": 0.00, "Status": "Status Exato", "Motivo": "Explicação"}]

STATUS PERMITIDOS:
- "Aprovado"
- "Atenção"
- "Negado"
"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (V15 - Regra Portão)")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada (Opcional)", type=['pdf', 'jpg', 'png'], key="entrada")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída (Opcional)", type=['pdf', 'jpg', 'png'], key="saida")

st.markdown("---")
st.markdown("### 💰 3. Orçamento")
orcamento_texto = st.text_area("Cole o texto do orçamento aqui:", height=150, placeholder="Cole a lista completa...", label_visibility="collapsed")
orcamento_arquivo = st.file_uploader("Ou anexe a imagem/PDF:", type=['pdf', 'jpg', 'png'], key="orcamento")

# --- 5. PROCESSAMENTO ---
if st.button("⚡ ANALISAR AGORA"):
    
    if not (orcamento_texto or orcamento_arquivo):
        st.error("⚠️ Insira o orçamento.")
        st.stop()

    with st.status("⚙️ Aplicando regras de engenharia...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            # Modelo Rápido
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
            
            status.update(label="✅ Concluído!", state="complete", expanded=False)

            # --- 6. VISUALIZAÇÃO ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            atencao = df[df['Status'].str.contains("Atenção|Amarela", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]

            if not aprovados.empty:
                st.markdown('<div class="section-title green-text">✅ APROVADOS (Cobrança Devida)</div>', unsafe_allow_html=True)
                for i, row in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><div>{row["Item"]} <span class="badge bg-green">FOTO</span></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not atencao.empty:
                st.markdown('<div class="section-title yellow-text">⚠️ ATENÇÃO (Análise Humana Necessária)</div>', unsafe_allow_html=True)
                for i, row in atencao.iterrows():
                    # Destaque especial para portão na UI
                    obs = row["Motivo"]
                    if "Portão" in row["Item"] or "Externo" in str(row["Motivo"]):
                        obs = "⚠️ ITEM EXTERNO: Verificar se é ferrugem (Negar) ou batida (Aprovar)."
                    
                    st.markdown(f'<div class="card card-yellow"><div>{row["Item"]} <span class="badge bg-yellow">VERIFICAR</span><br><small>{obs}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.markdown('<div class="section-title red-text">⛔ NEGADOS (Indevidos)</div>', unsafe_allow_html=True)
                for i, row in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><div>{row["Item"]}<br><small>Motivo: {row["Motivo"]}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            # --- 7. COPY AREA ---
            st.divider()
            st.subheader("📋 Copiar para OneNote")
            
            relatorio = "RELATÓRIO DE ANÁLISE\n====================\n\n"
            
            if not aprovados.empty:
                relatorio += "✅ APROVADOS:\n"
                for i, row in aprovados.iterrows(): relatorio += f"• {row['Item']} | R$ {row['Valor']:.2f}\n"
            
            if not atencao.empty:
                relatorio += "\n⚠️ ATENÇÃO:\n"
                for i, row in atencao.iterrows(): relatorio += f"• {row['Item']} | R$ {row['Valor']:.2f} ({row['Motivo']})\n"

            if not negados.empty:
                relatorio += "\n⛔ NEGADOS:\n"
                for i, row in negados.iterrows(): relatorio += f"• {row['Item']} | R$ {row['Valor']:.2f} ({row['Motivo']})\n"

            relatorio += f"\nTOTAL APROVADO: R$ {aprovados['Valor'].sum():.2f}"
            st.code(relatorio, language='text')

        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error("Erro ao processar.")
            st.write(e)