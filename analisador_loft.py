import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. SUA CHAVE API ---
# Correção: Use o NOME da variável, não a chave em si
CHAVE_SECRETA = st.secrets["AIzaSyCw81FxyeCB-UJmV_k2J6VrxJWb5qrd__Y"]

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Analisador Loft (Termo Oficial)", page_icon="🏢", layout="wide")

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

# --- 3. BASE DE CONHECIMENTO (COM FRASES JURÍDICAS OBRIGATÓRIAS) ---
BASE_CONHECIMENTO = """
VOCÊ É O AUDITOR OFICIAL DA LOFT FIANÇA.
Sua análise deve ser estritamente baseada nas regras abaixo.

--- 1. DESGASTES NATURAIS & AÇÃO DO TEMPO (NEGAR) ---
O que é: Deterioramento normal pelo tempo, sol, chuva ou uso regular.
Itens:
- Pintura desbotada, descascada por umidade natural ou tempo.
- Marcas leves no piso.
- Torneiras/Chuveiros pingando (vedante) ou com desgaste de uso.
- Lâmpadas queimadas.
- Encardido de rejunte, bolor ou mofo por falta de ventilação estrutural.
- Ferrugem/Oxidação em metais (portões, maçanetas).
- Itens externos (portões, grades, calçadas) com pintura gasta.

❌ MOTIVO DA NEGATIVA (Copie EXATAMENTE):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco."

--- 2. ITENS NÃO FIXOS / MOBÍLIA (NEGAR) ---
O que é: Itens que podem ser removidos sem dano à estrutura.
Itens: Sofás, camas, mesas, cadeiras, cortinas, persianas, tapetes, eletrodomésticos (geladeira, fogão), controle remoto, decoração.

❌ MOTIVO DA NEGATIVA (Copie EXATAMENTE):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."

--- 3. REDES HIDRÁULICAS E ELÉTRICAS (ANÁLISE MISTA) ---
A) NEGAR (Desgaste/Vício Oculto):
- Fiação antiga, curto interno na parede, resistência de chuveiro queimada, vazamento interno (cano estourado na parede), flexível ressecado.
❌ MOTIVO DA NEGATIVA (Copie EXATAMENTE):
"Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos."

B) APROVAR (Mau Uso/Dano Aparente):
- Tomadas/Interruptores quebrados, arrancados ou pintados.
- Torneiras quebradas fisicamente (alavanca solta).
- Louças (pia/vaso) quebradas por impacto.
✅ MOTIVO: "Dano físico aparente causado por mau uso."

--- 4. ATO ILÍCITO / ITENS RETIRADOS (NEGAR) ---
O que é: Itens que foram FURTADOS ou RETIRADOS do imóvel pelo inquilino.
Atenção: Se o item está lá mas está QUEBRADO, é Mau Uso (Aprovar). Se o item SUMIU, é Ato Ilícito (Negar).

❌ MOTIVO DA NEGATIVA (Copie EXATAMENTE):
"Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada."

--- 5. DANOS POR TERCEIROS (NEGAR) ---
O que é: Danos causados por imobiliária, corretores ou prestadores de serviço do proprietário.
❌ MOTIVO DA NEGATIVA: "Dano causado por terceiros não vinculados ao contrato de locação."

--- 6. O QUE APROVAR (MAU USO COMPROVADO) ---
Classificar como "Aprovado" (Verde):
- Paredes: Furos excessivos, riscos de caneta, sujeira pesada, mudança de cor não autorizada.
- Pisos: Lascados, quebrados, queimados ou com manchas químicas.
- Portas/Janelas: Vidros quebrados, fechaduras quebradas por força, madeira arranhada profundamente (cães).
- Fixos: Armários embutidos quebrados (portas arrancadas, gavetas quebradas).
- Caçambas: Apenas se vinculadas a reparos aprovados e valor < R$ 400.

--- FORMATO DE SAÍDA (JSON) ---
[
  {
    "Item": "Texto original do orçamento",
    "Valor": 0.00,
    "Status": "Aprovado / Atenção / Negado",
    "Motivo": "Use OBRIGATORIAMENTE as frases de negativa acima se for Negado. Se Aprovado, descreva o mau uso."
  }
]
"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (Jurídico V18)")
st.caption("Baseada no Termo de Cobertura Loft Fiança")

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
if st.button("⚡ ANALISAR CONFORME TERMO"):
    
    if not (orcamento_texto or orcamento_arquivo):
        st.error("⚠️ Insira o orçamento.")
        st.stop()

    with st.status("⚖️ Aplicando regras jurídicas Loft...", expanded=True) as status:
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
            
            status.update(label="✅ Análise Jurídica Concluída!", state="complete", expanded=False)

            # --- 6. VISUALIZAÇÃO ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            atencao = df[df['Status'].str.contains("Atenção|Amarela", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]

            if not aprovados.empty:
                st.markdown('<div class="section-title green-text">✅ APROVADOS (Mau Uso / Danos)</div>', unsafe_allow_html=True)
                for i, row in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><div>{row["Item"]} <span class="badge bg-green">FOTO</span></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not atencao.empty:
                st.markdown('<div class="section-title yellow-text">⚠️ ATENÇÃO (Verificar Documentação)</div>', unsafe_allow_html=True)
                for i, row in atencao.iterrows():
                    st.markdown(f'<div class="card card-yellow"><div>{row["Item"]} <span class="badge bg-yellow">VERIFICAR</span><br><small>{row["Motivo"]}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.markdown('<div class="section-title red-text">⛔ NEGADOS (Termo Loft)</div>', unsafe_allow_html=True)
                for i, row in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><div>{row["Item"]}<br><small>Motivo: {row["Motivo"]}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            # --- 7. COPY AREA (TEXTO SIMPLES PARA ONENOTE) ---
            st.divider()
            st.subheader("📋 Relatório Oficial Loft")
            
            relatorio = "RELATÓRIO DE ANÁLISE - LOFT FIANÇA\n====================================\n\n"
            if not aprovados.empty:
                relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f}\n"
                relatorio += "\n"
            
            if not atencao.empty:
                relatorio += "⚠️ ATENÇÃO (VALIDAR):\n"
                for i, r in atencao.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f} ({r['Motivo']})\n"
                relatorio += "\n"

            if not negados.empty:
                relatorio += "⛔ NEGADOS (CONF. TERMO):\n"
                for i, r in negados.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f}\n"
                    relatorio += f"  MOTIVO: {r['Motivo']}\n"
            
            total_geral = aprovados['Valor'].sum()
            total_negado = negados['Valor'].sum()
            
            relatorio += "\n===================================="
            relatorio += f"\nTOTAL APROVADO: R$ {total_geral:.2f}"
            relatorio += f"\nTOTAL NEGADO:   R$ {total_negado:.2f}"

            st.code(relatorio, language='text')

        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error("Erro ao processar.")
            st.write(e)
