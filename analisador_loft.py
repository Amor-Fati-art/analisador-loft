import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
try:
    # Tenta buscar a chave nos "Cofres" do site (Streamlit Cloud)
    CHAVE_SECRETA = st.secrets["CHAVE_SECRETA"]
except (FileNotFoundError, KeyError):
    # SE FALHAR (NO SEU PC), USA ESTA NOVA CHAVE DIRETA:
    CHAVE_SECRETA = "AIzaSyC9XBUq93SZ8Odkr4LtfoKsJadZ9bmT2DY"

st.set_page_config(page_title="Auditor Loft - Versão Final", page_icon="🏢", layout="wide")

# --- AVISO CRÍTICO PARA O ANALISTA (POP-UP) ---
st.title("🏢 Auditor Loft - Base Integrada")
st.warning("""
⚠️ **ATENÇÃO OBRIGATÓRIA: CONFERÊNCIA DE MOTIVOS**
A IA é uma ferramenta de apoio. **VOCÊ É O RESPONSÁVEL FINAL.**
* **Verifique o Motivo:** Se for Lâmpada/Ducha/Torneira, o motivo deve ser "Rede Elétrica/Hidráulica" e não apenas "Desgaste".
* **Itens Faltantes:** Se sumiu, é "Ato Ilícito".
* **Conferência Visual:** Sempre compare com as fotos antes de finalizar.
""")

st.caption("Sistema treinado para seguir rigorosamente as Regras da Empresa (Loft Fiança)")

# ==============================================================================
# 🔴 ÁREA DE TREINAMENTO (Seus Exemplos Originais Mantidos)
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
Valores Aprovados:
TROCA DO PAPEL DE PAREDE: 780 REAIS
REFAZER TEXTURA DA PAREDE: 550 REAIS
TROCA DA PORTA DE VIDRO: 1750 REAIS
LIMPEZA DAS PAREDES EXERNAS COM COBERTURA: 550 REAIS
TROCA DO BALANÇO DE MADEIRA : 750 REAIS
FAXINA: 350 REAIS

Valores Negados:
LIMPEZA DA VC DE GORDURA: 480 REAIS
TROCA DO MOTOR E AQUECEDOR: 9.200 REAIS 
TROCA DA LÂMPADA DA CHURRASQUEIRA: 35 REAIS
Motivo: Pagamento negado, conforme consta no nosso termo:  
"Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco." 

REPARO DO FOGÃO : 450 REAIS 
Motivo: Tendo em vista que a nossa análise é comparativa entre vistorias de entrada e saída, considerando que no laudo técnico e fotográfico da Entrada não foi possível identificar dano causado pelo locatário.
Informamos por fim que, a ausência de cobertura pela Loft Fiança não isenta a responsabilidade do locatário com relação aos valores considerados devidos em razão do contrato de locação, podendo a imobiliária cobrar diretamente do inquilino os valores negados.

TROCAR A TORNEIRA DO JARDIM: 35 REAIS 
Motivo: Pagamento negado, conforme consta no nosso termo:  
"Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos." 

TROCA DO ESPELHO DO BANHEIRO DA PISCINA: 150 REAIS 
Motivo: Pagamento negado, conforme consta no nosso termo:  
"Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada." 

Valores Negados:
Motor piscina R$ 6.866,00 
Motivo: 
O pagamento foi negado, conforme previsto em nosso termo, que exclui a cobertura para: "Danos nas redes hidráulicas e elétricas que não consistam em danos aparentes e de acabamentos externos."  
-----------------------------------------------------
• Pintura interna: R$ 2.752,50
• Limpeza geral do imovel: R$ 240,00
• Ajuste tomada: R$ 180,00
Valor total aprovado: R$ 3.489,75

Valor(es) negado(s)
Reparos:
• Armário: Acabamento superior foi arrancado, instalar novamente: R$ 150,00
• Armário: Gaveta sem puxador, fazer reposição: R$ 100,00
• Armário: Acabamento soltando na lateral direita, fazer fixação: R$ 200,00
Motivo da negativa:
Valores Contratados: Independentemente da anuência do(s) Locatário(s) e/ou Corresponsável(eis), as despesas que venham a ser indicadas pela Imobiliária para fins de composição do Valor Locatício, a Fiança Loft será prestada para fins de pagamento dos Valores Contratados, que incluem:
(iv)  Danos causados ao imóvel, assim como a eventuais móveis embutidos e equipamentos fixos.
Valor total negado: R$ 1.225,25
------------------------------------------------
Valor(es) aprovado(s)
Reparos:
• Pintura porta de ferro sala: R$ 80,00
• Reposição de vidros área de serviço: R$ 300,00
• Troca de tomadas: R$ 120,00
• Troca de fechadura completa quarto: R$ 180,00
• Reposição de vidros quebrados porta: R$ 150,00
Valor total aprovado: R$ 830,00

Valor(es) negado(s)
Reparos:
• Repor telhas: R$ 800,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xii)  danos estruturais nos telhados e/ou porção diversa do imóvel decorrentes de caso fortuito e/ou força maior ou, ainda, de dolo do(s) Locatário(s).
• Troca de chuveiro: R$ 210,00
• Troca de ducha higiênica: R$ 120,00
• Troca de lâmpadas: R$ 80,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xi) danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.
• Reposição de prateleiras e porta shampoo: R$ 140,00
• Repor mangueira: R$ 120,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xiii) danos causados por atos ilícitos, dolosos ou por culpa grave, equiparáveis ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada.
• Pintura paredes externa: R$ 1.000,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(iv) quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco.
Valor total negado: R$ 2.470,00
------------------------------------------------
Detalhamento Geral do(s) valor(es) aprovado(s)
Reparos:
• Pintura interna: R$ 1.230,00
• Descarte de entulho deixado no imóvel: R$ 380,00
(com bônus Refera aplicado, total: R$ 1.771,00)
Valor total aprovado: R$ 1.771,00

Valor(es) negado(s)
Reparos:
• EM LÁTEX: R$ 240,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(iv) quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco.
• Lâmpada: R$ 15,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xiii) danos causados por atos ilícitos, dolosos ou por culpa grave, equiparáveis ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada.
• Sifão: R$ 15,00
• Sifão: R$ 15,00
• Descarga: R$ 140,00
• Vaso Sanitário: R$ 60,00
• Lâmpada: R$ 15,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xi) danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.
Valor total negado: R$ 589,00
----------------------------------------------
Valores Aprovados:
Pintura interna: R$ 800,00 
Materiais de pintura: R$ 300,00 
Limpeza: R$ 200,00 
Produtos de limpeza: R$ 40,00 
Valores Negados:
Cozinha - reposição de 01 panela laranja indução 340,00
Pagamento negado, conforme consta no nosso termo:  
"Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparáveis ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada." 

Cozinha - banco realizar higienização 70,00
Quarto - colchão e box higienização 23,00
Quarto - cortina e blackout lavagem ( incluso retirada e instalação ) 220,00
Sacada - troca varal portátil 180,00
Sala e corredor - higienização sofá 220,00
Sala e corredor - painel rack, remover gaveta para retirada papeis 10,00
Sala e corredor - tapete higienização 190,00
Pagamento negado, conforme consta no nosso termo:  
"Danos causados ao imóvel, assim como a eventuais móveis embutidos e equipamentos fixos." 

Quarto - revisão ar condicionado 220,00
Pagamento negado, conforme consta no nosso termo:  
"Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação." 
"""

# ==============================================================================
# 🔵 BASE DE CONHECIMENTO (Atualizada com a Tabela DE/PARA)
# ==============================================================================
BASE_CONHECIMENTO = """
VOCÊ É UM ANALISTA DE REPAROS DA LOFT FIANÇA.
Sua missão é seguir estritamente o TERMO DA EMPRESA.
Ignore leis externas. A Regra da Empresa é soberana.

🚨 **TABELA DE MOTIVOS OBRIGATÓRIOS (DE/PARA)** 🚨
Você deve classificar o motivo da negativa de acordo com o TIPO do item abaixo.
A Monitoria exige o motivo técnico correto, não use "Desgaste Natural" para tudo.

TYPE A: LÂMPADAS, CHUVEIROS, DUCHAS, TORNEIRAS, REGISTROS
-> Se estiver queimado, vazando, pingando ou com defeito funcional.
-> **DECISÃO:** NEGAR.
-> **MOTIVO OBRIGATÓRIO (ELÉTRICA/HIDRÁULICA):** "Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos."

TYPE B: ITEM FALTANTE (SUMIU DO IMÓVEL)
-> Se na entrada tinha e na saída não tem (foi retirado/furtado).
-> **DECISÃO:** NEGAR.
-> **MOTIVO OBRIGATÓRIO (ATO ILÍCITO):** "Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada."

TYPE C: ÁREA EXTERNA (MUROS, FACHADAS, PORTÕES, JARDIM)
-> Danos por sol, chuva, ferrugem externa.
-> **DECISÃO:** NEGAR.
-> **MOTIVO OBRIGATÓRIO (AÇÃO DO TEMPO):** "Pagamento negado, conforme consta no nosso termo: danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco."

TYPE D: ITENS MÓVEIS (ASSENTO VASO, CORTINA, MÓVEL SOLTO)
-> **DECISÃO:** NEGAR.
-> **MOTIVO OBRIGATÓRIO (MOBÍLIA):** "Pagamento negado, conforme consta no nosso termo: item não fixo/mobília."

TYPE E: DESGASTE REAL (PINTURA INTERNA VELHA, RISCOS LEVES PISO)
-> Apenas para itens INTERNOS de acabamento.
-> **DECISÃO:** NEGAR.
-> **MOTIVO OBRIGATÓRIO (USO NORMAL):** "Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação."

FORMATO DE SAÍDA JSON:
[{"Item": "Nome", "Valor": 0.00, "Status": "Aprovado/Negado", "Motivo": "Texto da regra exata"}]
"""

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

    with st.status("🤖 Aplicando regras da empresa (Conferência Humana Necessária)...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            # --- LÓGICA HÍBRIDA (GEMINI 3 com BACKUP) ---
            try:
                # Tenta o modelo mais inteligente primeiro
                model = genai.GenerativeModel('gemini-3-flash-preview', generation_config={"response_mime_type": "application/json"})
                st.toast("🚀 Usando Gemini 3 Flash (Preview)")
            except:
                # Se falhar, usa o modelo estável
                model = genai.GenerativeModel('gemini-1.5-flash', generation_config={"response_mime_type": "application/json"})
                st.toast("⚠️ Usando Backup (Gemini 1.5 Flash)")

            # Montagem do Prompt
            prompt = [BASE_CONHECIMENTO]
            prompt.append("HISTÓRICO DE CASOS DA EMPRESA (SIGA ESTES PADRÕES DE DECISÃO):")
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
            
            response = model.generate_content(prompt)
            df = pd.read_json(io.StringIO(response.text))
            
            status.update(label="✅ Análise Concluída", state="complete", expanded=False)
            
            # --- RESULTADOS ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]
            
            if not aprovados.empty:
                st.subheader("✅ Aprovados")
                for i, r in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.subheader("⛔ Negados")
                for i, r in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)
            
            # --- RELATÓRIO COPY/PASTE ---
            st.divider()
            st.subheader("📋 Relatório Final (Para Copiar)")
            
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
                    # Aqui garante que o motivo apareça completo no relatório
                    txt_relatorio += f"    Motivo: {r['Motivo']}\n"
            
            val_total = df['Valor'].sum()
            val_aprov = aprovados['Valor'].sum() if not aprovados.empty else 0
            
            txt_relatorio += "\n======================================\n"
            txt_relatorio += f"TOTAL SOLICITADO: R$ {val_total:.2f}\n"
            txt_relatorio += f"TOTAL APROVADO:   R$ {val_aprov:.2f}"
            
            st.code(txt_relatorio)

        except Exception as e:
            st.error(f"Erro no processamento: {e}")
