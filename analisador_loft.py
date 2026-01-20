import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
try:
    CHAVE_SECRETA = st.secrets["CHAVE_SECRETA"]
except:
    st.error("❌ Erro: Configure a 'CHAVE_SECRETA' nos Secrets do Streamlit.")
    st.stop()

st.set_page_config(page_title="Auditor Loft - Versão Final", page_icon="🏢", layout="wide")

# ==============================================================================
# 🔴 ÁREA DE TREINAMENTO (Seu Histórico do OneNote)
# ==============================================================================
# Cole abaixo os exemplos de casos que você já resolveu.
# A IA vai usar isso para copiar o seu estilo de decisão.
# ==============================================================================
EXEMPLOS_TREINAMENTO = """
--- EXEMPLO 1 ---
Item: Pintura de Fachada Externa
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, danos causados pela ação paulatina de temperatura e umidade.

--- EXEMPLO 2 ---
Item: Troca de Lâmpadas LED
Decisão: NEGADO
Motivo: Pagamento negado. Lâmpada é item de consumo e desgaste natural.

--- EXEMPLO 3 ---
Item: Pintura Interna (Sala com riscos de caneta)
Decisão: APROVADO
Motivo: Pintura interna danificada por mau uso (riscos), diferindo da vistoria de entrada.

--- EXEMPLO 4 ---
Item: Limpeza Pesada e Remoção de Lixo
Decisão: APROVADO
Motivo: Imóvel entregue limpo e devolvido sujo com pertences.

--- EXEMPLO 5 ---
Item: Cortina da Sala Rasgada
Decisão: NEGADO
Motivo: Pagamento negado... item não fixo/mobília.

(Você pode colar mais exemplos aqui embaixo seguindo esse padrão...)
"""
# ==============================================================================


# ==============================================================================
# 🔵 BASE DE CONHECIMENTO (Regras Oficiais Loft Fiança)
# ==============================================================================
BASE_CONHECIMENTO = """
VOCÊ É UM AUDITOR TÉCNICO DA LOFT FIANÇA.
Sua missão é analisar orçamentos de reparo comparando Vistoria de Entrada vs. Saída.

REGRA DE OURO:
1. Se o dano já existia na entrada (mesmo estado) -> NEGAR.
2. Se o dano é desgaste natural (tempo) -> NEGAR.
3. Se o dano é mau uso comprovado (mudança de estado) -> APROVAR.

REGRAS ESPECÍFICAS (COPIADAS DO TERMO):

1. DESGASTES NATURAIS (NEGAR)
   - Tinta desbotada, marcas leves de móveis, lâmpadas queimadas, encardido de rejunte.
   - Frase Obrigatória: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel."

2. AÇÃO DO TEMPO / ÁREA EXTERNA (NEGAR)
   - Pintura externa, muros, fachadas, portões expostos, jardinagem (mato crescido).
   - Frase Obrigatória: "Pagamento negado... danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração."

3. ITENS NÃO FIXOS / MOBÍLIA (NEGAR)
   - Sofás, cortinas soltas, eletros, móveis não planejados.
   - Frase Obrigatória: "Pagamento negado... item não fixo/mobília."

4. HIDRÁULICA E ELÉTRICA
   - Oculto/Interno (Fiação, cano na parede) -> NEGAR (Estrutural).
   - Visível/Uso (Tomada quebrada, sifão quebrado, louça sanitária quebrada) -> APROVAR (Mau uso).
   - Frase Obrigatória se negar: "Pagamento negado... Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes."

5. CAÇAMBAS E ENTULHOS
   - Só aprovar se houver obras/reparos aprovados que gerem entulho.
   - Se for apenas lixo do inquilino -> Aprovar como "Retirada de itens".

6. ATO ILÍCITO (Item Furtado)
   - Confirmar se o item realmente sumiu comparando vistorias.
   - Frase: "Danos causados por atos ilícitos..."

FORMATO DE SAÍDA JSON:
[
  {"Item": "Nome", "Valor": 0.00, "Status": "Aprovado/Negado", "Motivo": "Texto da regra"}
]
"""

# --- INTERFACE VISUAL ---
st.markdown("""
    <style>
        .card { padding: 10px; margin-bottom: 5px; border-radius: 5px; border-left: 5px solid; background-color: #262730; }
        .card-green { border-color: #28a745; }
        .card-red { border-color: #dc3545; }
        .card-yellow { border-color: #ffc107; }
        .price { float: right; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

st.title("🏢 Auditor Loft - Base Integrada")
st.caption("Sistema carregado com: Base de Conhecimento Oficial + Seus Exemplos de Treinamento")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada (Opcional)", type=['pdf', 'txt'], key="ent")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída (Recomendado)", type=['pdf', 'txt'], key="sai")

st.markdown("### 📝 Orçamento para Análise")
tab1, tab2 = st.tabs(["Digitar/Colar", "Upload Arquivo"])
with tab1:
    orcamento_txt = st.text_area("Cole os itens aqui:", height=150)
with tab2:
    orcamento_arq = st.file_uploader("Arquivo de Orçamento", type=['pdf', 'jpg'])

# --- LÓGICA DE PROCESSAMENTO ---
if st.button("🔍 ANALISAR AGORA"):
    
    if not (orcamento_txt or orcamento_arq):
        st.warning("Por favor, insira um orçamento.")
        st.stop()

    with st.status("🤖 Consultando regras e exemplos...", expanded=True) as status:
        genai.configure(api_key=CHAVE_SECRETA)
        model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
        
        # Montagem do Prompt
        prompt = [BASE_CONHECIMENTO]
        
        prompt.append("HISTÓRICO DE APRENDIZADO (USE ISSO COMO EXEMPLO DE DECISÃO):")
        prompt.append(EXEMPLOS_TREINAMENTO)
        
        if vistoria_entrada:
            prompt.append("CONTEXTO: VISTORIA DE ENTRADA")
            prompt.append({"mime_type": vistoria_entrada.type, "data": vistoria_entrada.getvalue()})
        
        if vistoria_saida:
            prompt.append("CONTEXTO: VISTORIA DE SAÍDA")
            prompt.append({"mime_type": vistoria_saida.type, "data": vistoria_saida.getvalue()})
            
        prompt.append("ORÇAMENTO A ANALISAR:")
        if orcamento_arq:
            prompt.append({"mime_type": orcamento_arq.type, "data": orcamento_arq.getvalue()})
        else:
            prompt.append(orcamento_txt)
            
        try:
            response = model.generate_content(prompt)
            df = pd.read_json(io.StringIO(response.text))
            status.update(label="✅ Análise Concluída", state="complete", expanded=False)
            
            # --- RESULTADOS ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]
            atencao = df[df['Status'].str.contains("Atenção", case=False)]
            
            # Exibição Visual
            if not aprovados.empty:
                st.subheader("✅ Aprovados")
                for i, r in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.subheader("⛔ Negados")
                for i, r in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)
            
            if not atencao.empty:
                st.subheader("⚠️ Atenção")
                for i, r in atencao.iterrows():
                    st.markdown(f'<div class="card card-yellow"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)

            # --- RELATÓRIO COPY/PASTE ---
            st.divider()
            st.subheader("📋 Relatório Final")
            
            txt_relatorio = "RELATÓRIO TÉCNICO - ANÁLISE DE REPAROS\n"
            txt_relatorio += "======================================\n"
            
            if not aprovados.empty:
                txt_relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    txt_relatorio += f"[+] {r['Item']} | R$ {r['Valor']:.2f}\n"
            
            if not negados.empty:
                txt_relatorio += "\n⛔ NEGADOS:\n"
                for i, r in negados.iterrows():
                    txt_relatorio += f"[-] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    txt_relatorio += f"    Motivo: {r['Motivo']}\n"
            
            val_total = df['Valor'].sum()
            val_aprov = aprovados['Valor'].sum()
            
            txt_relatorio += "\n======================================\n"
            txt_relatorio += f"TOTAL SOLICITADO: R$ {val_total:.2f}\n"
            txt_relatorio += f"TOTAL APROVADO:   R$ {val_aprov:.2f}"
            
            st.code(txt_relatorio)

        except Exception as e:
            st.error(f"Erro ao processar: {e}")
