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
st.set_page_config(page_title="Analisador Loft (V29 - Treinamento Manual)", page_icon="🏢", layout="wide")

st.markdown("""
    <style>
        div.stButton > button:first-child {
            background-color: #ff6200; color: white; font-weight: bold; border: none; width: 100%; padding: 15px; font-size: 18px; text-transform: uppercase; border-radius: 8px;
        }
        div.stButton > button:first-child:hover { background-color: #e55800; color: white; }
        .card { padding: 12px; margin-bottom: 8px; border-radius: 6px; border-left: 5px solid; display: flex; justify-content: space-between; align-items: center; font-family: sans-serif; font-size: 14px; background-color: #1e1e1e; }
        .card-green { border-color: #28a745; color: #e6ffe6; }
        .card-yellow { border-color: #ffc107; color: #fffbe6; }
        .card-red { border-color: #dc3545; color: #ffe6e6; }
        .card-price { font-weight: bold; font-size: 15px; min-width: 80px; text-align: right; }
        .section-title { margin-top: 20px; font-weight: bold; text-transform: uppercase; font-size: 16px; }
        .green-text { color: #28a745; }
        .yellow-text { color: #ffc107; }
        .red-text { color: #dc3545; }
    </style>
""", unsafe_allow_html=True)

# --- 3. REGRAS E CÉREBRO DA IA ---

# REGRA 0: Só ativa se tiver Vistoria de Entrada
REGRA_COMPARACAO = """
--- 0. REGRA DE OURO: DANO PRÉ-EXISTENTE (MODO COMPARATIVO ATIVO) ---
O USUÁRIO FORNECEU A VISTORIA DE ENTRADA. SUA OBRIGAÇÃO É COMPARAR.
Antes de aprovar qualquer item, verifique a VISTORIA DE ENTRADA fornecida.
Se o item já estava descrito como "Desgastado", "Ruim", "Manchado", "Riscado" ou "Danificado" na ENTRADA e não houve piora significativa:
❌ STATUS: Negado
❌ MOTIVO OBRIGATÓRIO: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel."
"""

# BASE DE CONHECIMENTO PADRÃO
BASE_CONHECIMENTO = """
VOCÊ É O AUDITOR OFICIAL DA LOFT FIANÇA.
Sua análise deve ser cirúrgica. NÃO invente motivos. NÃO misture os textos.

--- 1. LIMPEZA (APROVAR) ---
✅ APROVAR: "Limpeza interna", "Faxina", "Limpeza pesada", "Limpeza externa" (piso/entulho), "Caixa de gordura", "Bota-fora".
MOTIVO: "Falta de manutenção adequada (limpeza)."

--- 2. PINTURA INTERNA (APROVAR) ---
✅ APROVAR: Paredes, Tetos, Portas (Lado interno).
MOTIVO: "Pintura interna danificada/suja (Mau uso ou falta de conservação)."

--- 3. RESTITUIÇÃO (APROVAR) ---
✅ APROVAR: "Remover Canil", "Remover Divisória", "Remover Varal", "Remover Telas".
MOTIVO: "Restituição do imóvel ao estado original (Remoção de benfeitoria não autorizada)."

--- ⚠️ REGRAS DE NEGATIVA (USE O TEXTO EXATO ABAIXO) ⚠️ ---

🔴 TIPO A: EXTERNO / JARDIM / TEMPO (Use para: Fachada, Muros, Telhados, Calhas, Mato, Jardim)
❌ MOTIVO OBRIGATÓRIO (Copiar ID A):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco."

🔴 TIPO B: ELÉTRICA / HIDRÁULICA OCULTA (Use para: Fiação interna, Alarme, Interfone, Cano dentro da parede)
❌ MOTIVO OBRIGATÓRIO (Copiar ID B):
"Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos."

🔴 TIPO C: ATO ILÍCITO / FURTO (Use para: Itens roubados, furtados)
❌ MOTIVO OBRIGATÓRIO (Copiar ID C):
"Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada."

🔴 TIPO D: DESGASTE COMUM / MOBÍLIA (Use para: Lâmpadas, Móveis, Riscos no piso, Desgaste natural interno)
❌ MOTIVO OBRIGATÓRIO (Copiar ID D):
"Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."

--- FORMATO DE SAÍDA (JSON) ---
[ { "Item": "Texto original", "Valor": 0.00, "Status": "Aprovado / Negado", "Motivo": "Cole o texto do TIPO A, B, C ou D aqui" } ]"""

# --- AREA DE TREINAMENTO (COLE SEUS EXEMPLOS AQUI) ---
# Você pode colar centenas de linhas aqui dentro das aspas triplas.
# Não se preocupe com o tamanho.
EXEMPLOS_TREINAMENTO = """
AQUI ESTÃO EXEMPLOS DE ANÁLISES REAIS (GABARITO):

CASO 1:
Item: "Limpeza Mato / Capina química" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel... danos causados pela ação paulatina de temperatura..."

CASO 2:
Item: "Kit lâmpadas LED" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel..."

CASO 3:
Item: "Manutenção Central de Alarme" -> NEGADO
Motivo: "Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes..."

CASO 4:
Item: "Remover 07 Canil Cimento" -> APROVADO (Restituição ao estado original).

CASO 5:
Item: "Pintura das paredes e portões - danificados por xixi de cachorro" -> APROVADO (Danos causados por animais de estimação).

*** COLE AQUI ABAIXO OS OUTROS EXEMPLOS DO SEU COLEGA ***
Detalhamento Geral do(s) valor(es) aprovado(s)
Reparos:• Pintura interna: R$ 1.308,00
• Limpeza piso do imóvel depois dos reparos: R$ 215,00
• Pintura portas e aberturas: R$ 384,50
• Retoque pintura portas: R$ 230,00
• Limpeza de piso pós reparos: R$ 215,00

Valor(es) negado(s)
Reparos:• Diferença refera: R$ 689,65Motivo da negativa:Valores negados, visto que a aprovação dos reparos foi realizada de acordo com os valores praticados na região em que atua, conforme orçamento Refera.
• Troca de luminária: R$ 40,00Motivo da negativa:Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xi) danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.
• Repor cortina bege: R$ 1.750,00
• Colocar uma cama completa: R$ 2.100,00
• Reparar prateleira do nicho empenado: R$ 450,00
• Repor 1 faca e 1 espeto de cabo branco parcialmente negado conforme valor da linha: R$ 130,00Motivo da negativa:Valores Contratados: Independentemente da anuência do(s) Locatário(s) e/ou Corresponsável(eis), as despesas que venham a ser indicadas pela Imobiliária para fins de composição do Valor Locatício, a Fiança Loft será prestada para fins de pagamento dos Valores Contratados, que incluem:
(iv)  Danos causados ao imóvel, assim como a eventuais móveis embutidos e equipamentos fixos.Valor total negado: R$ 5.159,65

Pintura externa não expecificado se possui cobertura (Teto) Verificar Fotos da vistoria de entrada e saída para análise detalhada do estado


"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (V29 - Big Data)")
st.caption("Sistema treinado com regras rígidas e exemplos manuais.")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada (Ativa Regra 0)", type=['pdf', 'jpg', 'png'], key="entrada")
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

    with st.status("⚖️ Processando...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json", "temperature": 0.0})
            
            prompt_parts = []

            # Lógica Dinâmica: Só ativa Comparação se tiver Vistoria de Entrada
            if vistoria_entrada:
                prompt_parts.append(REGRA_COMPARACAO)
                st.toast("Modo Comparativo: ATIVADO ✅")
            
            prompt_parts.append(BASE_CONHECIMENTO)
            prompt_parts.append(EXEMPLOS_TREINAMENTO) # Aqui ele lê o bloco gigante de texto

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

            # --- 7. RELATÓRIO ---
            st.divider()
            st.subheader("📋 Relatório Final")
            relatorio = "RELATÓRIO DE ANÁLISE TÉCNICA - LOFT FIANÇA\n========================================\n\n"
            
            if not aprovados.empty:
                relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    relatorio += f"[+] {r['Item']} | R$ {r['Valor']:.2f}\n"
                relatorio += "\n"
            
            if not negados.empty:
                relatorio += "⛔ NEGADOS:\n"
                for i, r in negados.iterrows():
                    relatorio += f"[-] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    relatorio += f"    Justificativa: {r['Motivo']}\n"
            
            total_aprovado = aprovados['Valor'].sum()
            total_negado = negados['Valor'].sum()
            
            relatorio += f"\n💰 TOTAL APROVADO:   R$ {total_aprovado:.2f}\n📉 TOTAL ECONOMIZADO: R$ {total_negado:.2f}"
            st.code(relatorio, language='text')

        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error("Erro ao processar.")
            st.write(e)
