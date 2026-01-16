import streamlit as st
import google.generativeai as genai
import pandas as pd
import io

# --- 1. SUA CHAVE API ---
CHAVE_SECRETA = "AIzaSyAlavpN_GYrq8Xro-PRWgVmdzY0mkbvLrQ"

# --- 2. CONFIGURAÇÃO VISUAL ---
st.set_page_config(page_title="Analisador Loft (Master Knowledge)", page_icon="🏢", layout="wide")

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

# --- 3. A GRANDE BASE DE CONHECIMENTO (AQUI FICA A INTELIGÊNCIA) ---
# DICA: Você pode colar o texto do manual da Loft inteiro aqui dentro das aspas.
BASE_CONHECIMENTO = ""Motivos de Negativa na Análise de Reparos – Não Cobertos pelo Termo Loft Fiança
 

Listamos os principais motivos que podem levar à negativa do pagamento de reparos na desocupação, conforme os critérios do Termo de Cobertura da Loft Fiança:

⚠️ Importante: Para que o reparo seja aprovado pela Loft Fiança, é necessário apresentar o laudo descritivo da vistoria de entrada e saída, juntamente com as fotos comparativas de entrada e saída do imóvel, além do orçamento detalhado. 

No laudo da vistoria Final o dano causado pelo inquilino precisa estar descrito.

 

Desgastes Naturais
É o deterioramento normal que ocorre com o tempo e o uso regular de um imóvel, mesmo quando o inquilino cuida adequadamente do espaço. Ele não é causado por mau uso ou negligência, mas sim pelo envelhecimento natural dos materiais e itens da propriedade.

Exemplos de desgaste natural:

Tinta da parede desbotada com o tempo, sem cobertura (área externa como paredes, muros, calçadas);
Marcas leves no piso por uso de móveis;
Torneiras ou chuveiros com desgaste por uso contínuo (vazamentos);
Lâmpadas queimadas;
Encardido de rejunte por tempo de uso.
 

ℹ️ Motivo utilizado para negativa: Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação.

 

 

O que não é desgaste natural ou seja, são as deteriorações causadas por:

Mau uso ou uso inadequado: Quando o inquilino ou seus visitantes agem de forma negligente, imprudente ou intencional, causando prejuízo ao imóvel.
Falta de manutenção adequada: Pequenas manutenções que são de responsabilidade do inquilino (limpeza, consertos simples) e que, se não forem feitas, podem levar a problemas maiores.
Danos causados por animais de estimação: Arranhões, mordidas, sujeira persistente, etc.
Alterações não autorizadas: Modificações na estrutura ou características do imóvel sem o consentimento prévio do locador.
 

Exemplos práticos do que NÃO é desgaste natural:

Paredes:
Manutenção das paredes internas ou cobertas do imóvel.
Troca da cor do imóvel, entregar diferente a vistoria de entrada (interna e externa)
Furos excessivos ou de tamanho grande (que exigem mais que uma simples massa corrida e pintura interna e externa).
Manchas de umidade causadas por falta de ventilação, derramamento de líquidos ou infiltrações por mau uso não reportadas e não reparadas a tempo pelo inquilino.
Pintura danificada por riscos, rabiscos, sujeiras e tintas de cores diferentes aplicadas sem autorização.
Marcas de batida ou arranhões profundos.
 
Pisos e Revestimentos:
Pisos lascados, quebrados ou com trincas profundas causadas por queda de objetos pesados ou mau uso.
Manchas permanentes por produtos químicos, tinta ou outros líquidos.
Azulejos quebrados ou descolados.
Rachaduras significativas, desde que comprovada que foi mau uso.
Papel de parede danificado.
 
Portas e Janelas:
Vidros quebrados ou trincados.
Portas arrancadas das dobradiças, com furos grandes, ou danificadas por batidas.
Trincos, fechaduras ou maçanetas quebradas por força excessiva.
 
Instalações Elétricas e Hidráulicas:
Tomadas ou interruptores quebrados, arrancados.
Problemas elétricos causados por sobrecarga (uso excessivo de benjamins, por exemplo).
Vazamentos e infiltrações decorrentes de torneiras não consertadas ou ralos entupidos por falta de limpeza.
Quebra de louças sanitárias (vaso sanitário, pia) ou espelhos por impacto.
Torneiras quebradas, ou modificados (troca de marca e modelo).
Chuveiros quebrados ou modificados (troca de marca e modelo).
Lâmpadas embutidas quebradas, ou modificadas (troca de marca e modelo).
 
Outros:
Móveis danificados (se o imóvel for mobiliado com armários fixos e embutidos) por mau uso (armários arranhadas profundamente, quebrados).
Entupimentos de ralos e vasos sanitários por descarte incorreto de lixo.
Danos causados por infestação de pragas (se a causa for falta de higiene do inquilino).
 

Danos em itens Fixos e Embutidos 
Para entender o que não é um item fixo e embutido, primeiro precisamos definir o que são esses termos no contexto de um imóvel, especialmente em contratos de locação.
 

Itens fixos e embutidos são aqueles que estão permanentemente conectados à estrutura do imóvel, não podendo ser removidos sem causar danos significativos à propriedade ou ao próprio item. Eles geralmente fazem parte da construção ou foram instalados de forma a se integrar ao ambiente.

 

Exemplos comuns de itens fixos e embutidos:

Armários planejados ou embutidos: Cozinha, quartos, banheiros, lavanderia, etc.
Pias e bancadas: De cozinha, banheiro, lavanderia (se forem fixas e não móveis (sem pés).
Louças sanitárias: Vasos sanitários, bidês, cubas de pia (se fixas).
Metais sanitários: Torneiras, chuveiros, válvulas de descarga (se instalados de forma permanente).
Portas e janelas: E seus respectivos batentes, maçanetas, dobradiças e vidros.
Pisos e revestimentos: Cerâmicas, porcelanatos, laminados, tacos, azulejos de parede.
Espelhos grandes e fixos: Aqueles que são colados ou parafusados diretamente na parede.
Iluminação embutida: Spots, luminárias de teto que são parte da instalação elétrica e não apenas penduradas.
Painéis de TV planejados ou fixos: Que são aparafusados ou integrados à parede ou móvel.
Aquecedores a gás: Quando instalados permanentemente para servir o imóvel.
Interfones e caixas de correio: Que fazem parte da infraestrutura do edifício ou casa.

Quando o inquilino é responsável:

O inquilino deve reparar ou indenizar a imobiliária em caso de danos causados por mau uso, quebra, remoção indevida ou descaracterização desses itens (troca por outro diferente do laudo inicial).


Quando não é cobrado:

Desgaste natural (ex.: amarelamento por tempo, pequenos arranhões) não é coberto e não pode ser cobrado do inquilino

 

O Que NÃO é Item Fixo e Embutido:

O que não é um item fixo ou embutido são aqueles bens que podem ser removidos do imóvel sem causar danos à estrutura ou ao próprio item, e que geralmente são considerados bens móveis ou objetos de decoração e uso pessoal do inquilino (ou do locador, se o imóvel for mobiliado e esses itens forem removíveis).

 

Exemplos práticos do que NÃO é item fixo e embutido:

Móveis soltos: Sofás, camas, mesas, cadeiras, estantes (que não são planejadas), cômodas, armários avulsos (guarda-roupas, sapateiras).
Eletrodomésticos: Geladeiras, fogões, micro-ondas, máquinas de lavar roupa, lava louças, televisores.
Cortinas e persianas simples: Aquelas que são penduradas em varões ou trilhos que podem ser facilmente desparafusados sem danificar a parede.
Objetos de decoração: Quadros, espelhos pequenos, vasos, luminárias de chão ou de mesa.
Tapetes e carpetes soltos: Que não são colados ao piso.
Utensílios de cozinha: Louças, talheres, panelas.
Aparelhos de ar-condicionado portáteis: Que não exigem instalação permanente (Springer, Split).
Chuveiros elétricos ou a gás: Se forem de encaixe simples e não demandarem modificação estrutural para remoção. (No entanto, a troca de um chuveiro elétrico pode exigir que o inquilino reponha o chuveiro pelo mesmo modelo, caso ele tenha sido entregue no imóvel).
 

 

ℹ️ Motivo utilizado para negativa: Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação.

 

⚠️ Importante: Para que o reparo seja aprovado pela Loft Fiança, é necessário apresentar fotos comparativas da vistoria de entrada e saída, além do orçamento detalhado.

 

Danos por terceiros 
São considerados danos por terceiros aqueles causados por pessoas não relacionadas ao contrato de locação, como:

Prestadores de serviço contratados pelo locatário (imobiliária ou proprietário) (ex.: pintores, chaveiros, eletricistas);
Corretores ou representantes da imobiliária durante visitas;
Técnicos ou fornecedores que acessaram o imóvel sem acompanhamento do inquilino;
Itens da área externa que fiquem expostos;

Esses danos não são de responsabilidade do inquilino e, portanto, não devem ser cobrados como parte do custo de saída.

 

Caso a imobiliária informe um dano no imóvel, é necessário verificar:

Quem teve acesso ao imóvel no período;
Se há evidência de que o dano foi causado antes ou depois da entrega das chaves;
Documentação (fotos, relatos, laudo) que comprove que se trata de uso indevido do inquilino.

A Loft Fiança não cobre reparos relacionados a danos causados por terceiros.

 

⚠️ Importante: Para que o reparo seja aprovado pela Loft Fiança, é necessário apresentar fotos comparativas da vistoria de entrada e saída, além do orçamento detalhado.

 

 

Danos nas Redes Hidráulicas e Elétricas 
Os danos nas redes hidráulicas e elétricas do imóvel devem ser analisados com base na vistoria de entrada, nas condições de uso e no tempo de ocupação.

 

O que pode ser causado pelo inquilino: danos causados por mau uso ou interferência indevida, como:

tomadas ou interruptores quebrados, com fios aparentes;
alteração da voltagem;
torneiras danificados por uso incorreto ou troca de modelo em relação a vistoria de entrada;
vazamentos visíveis causados por mau uso ou impacto;
 

Itens não cobertos pelo Termo: problemas estruturais ou vícios ocultos, como:

Fiação antiga com mau contato;
Vazamentos internos por desgaste natural (torneiras e chuveiros);
Encanamento corroído pelo tempo;
Instabilidade elétrica decorrente da rede original.
Cercas elétricas que ficam expostas a ação do tempo e a terceiros.

Danos de origem estrutural ou desgaste natural não são responsabilidade do inquilino e não são cobertos pela Loft Fiança.

 

ℹ️ Motivo utilizado para negativa: Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.

 

Ato Ilícito
Um ato ilícito acontece quando uma pessoa faz algo proibido por lei, causando prejuízo a outra parte, é considerado ato ilícito qualquer atitude que viole o contrato de locação ou a legislação vigente, podendo gerar indenização ou penalidades legais.

 

Exemplos comuns:

Causar danos ao imóvel intencionalmente;
Retirar itens do imóvel sem autorização;
 

A Loft Fiança não cobre reparos relacionados a ato danos por ato ilícito causados pelo locatício ou por terceiros.

 

ℹ️ Motivo utilizado para negativa: Danos causados por atos ilícitos, dolosos ou por culpa grave, equiparável ao dolo, praticados pelo(s) Locatário(s), ou por pessoa a ele(s) vinculada.

 

⚠️ Antes de realizar a negativa, é necessário confirmar que o item não está presente no imóvel e que foi, de fato, retirado. Caso o item ainda esteja no local, não se trata de ato ilícito, sendo necessário apenas avaliar se há necessidade de reparo.

 

Danos em telhados
Os danos em telhados devem ser avaliados com base na origem do problema, no estado do imóvel na vistoria de entrada e no tempo de ocupação do inquilino.

 

O inquilino pode ser responsabilizado quando os danos forem causados por:

Instalações indevidas (ex.: antenas, equipamentos, ganchos);
Tráfego sobre o telhado sem necessidade ou autorização;
Rompimento de telhas por mau uso ou impacto direto.
 

Quando não é responsabilidade do inquilino:

Infiltrações causadas por estrutura antiga ou falhas de construção;
Quebra de telhas por chuvas fortes, ventanias ou outros eventos climáticos;
Desgaste natural ou manutenção não realizada pelo proprietário ao longo dos anos.
 

A Loft Fiança não cobre reparos relacionados a desgaste natural, má conservação prévia ou danos estruturais. Para análise, é necessário apresentar fotos comparativas e, se possível, laudo técnico ou vistoria que comprove a origem do dano.

ℹ️ Motivo utilizado para negativa: Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco.

 

 

Danos por ação do tempo

 

São considerados danos por ação do tempo aqueles que ocorrem naturalmente ao longo dos anos, mesmo com uso adequado e cuidados regulares. Esses danos não decorrem de mau uso ou negligência por parte do inquilino.

 

Exemplos:

Desbotamento de pintura devido à exposição solar;
Oxidação de metais (ex.: maçanetas, dobradiças);
Rachaduras em paredes causadas por movimentação natural da estrutura, vibração;
Danos causados pela ação paulatina de temperatura, umidade;
Desgaste em rejuntes, rodapés ou pisos por tempo de uso;
Ressecamento de borrachas de vedação em janelas ou box.
Jardinagem;
 

Danos por ação do tempo não são cobrados do inquilino e não estão cobertos pelo Termo de Cobertura da Loft Fiança.

Para qualquer reparo solicitado, é essencial que haja documentação (laudos, fotos e vistorias) que comprovem a origem do dano.

 

ℹ️ Motivo utilizado para negativa: Pagamento negado, conforme consta no nosso termo: Quaisquer deteriorações decorrentes do uso normal do imóvel, objeto do Contrato de Locação, danos causados pela ação paulatina de temperatura, umidade, infiltração e vibração, bem como poluição e contaminação decorrente de qualquer causa, inclusive a áreas internas que estejam expostas a este risco.

 

Caçambas e entulhos
A cobrança por caçamba ou remoção de entulho só pode ser aceita quando estiver vinculada à execução de reparos no imóvel após a saída do inquilino. O pagamento poderá ser aprovado em caráter de exceção, desde que haja comprovação documental ou que a necessidade do serviço esteja claramente indicada na vistoria de saída.

 

Aprovamos em exceção quando:

Houver comprovação de reparos ou manutenção necessários, com nota fiscal ou orçamento detalhado;
A caçamba for usada exclusivamente para descarte de materiais decorrentes da reforma ou reparos;
For apresentada nota fiscal ou recibo em nome da imobiliária ou do prestador de serviço vinculado.
Para o descarte de móveis, lixo comum ou entulho deixado pelo inquilino;
 

⚠️ Valores acima de 400,00, a imobiliária precisa comprovar quantidade de caçambas utilizadas."
VOCÊ É O AUDITOR SÊNIOR DE ENGENHARIA DA LOFT.
Sua autoridade é máxima. Siga estas diretrizes para aprovar ou negar custos.

--- 1. DIRETRIZES DE INTERPRETAÇÃO (DIFERENTES IMOBILIÁRIAS) ---
As imobiliárias enviam orçamentos em formatos variados. Use esta lógica:
- "Pintura suja", "Demão de tinta", "Repintura parede" -> Tudo refere-se a PINTURA (Aplicar regra de Pintura).
- "Sifão vazando", "Troca de sifão", "Kit hidráulico pia" -> Tudo refere-se a HIDRÁULICA.
- Se o texto for confuso, priorize a regra do "Dano Físico" vs "Desgaste Natural".

--- 2. REGRAS TÉCNICAS DETALHADAS ---

🟢 CATEGORIA: PINTURA INTERNA (Paredes e Tetos)
- APROVAR (Verde): Se houver menção a: Sujo, Riscado, Manchado, Furos (quadros/suportes), Mudança de cor não autorizada, Massa corrida danificada.
- ATENÇÃO (Amarelo): Se mencionar "Pintura Teto" (verificar se não é infiltração do vizinho de cima).
- NEGAR (Vermelho): Se a justificativa for apenas "Pintura antiga" ou "Desbotada pelo tempo" (Vida útil) sem danos físicos.

🔴 CATEGORIA: PINTURA EXTERNA & FACHADA
- ATENÇÃO (Amarelo): Portões, Grades, Muros, Calçadas, Telhados, Áreas de lazer externa.
  - Motivo Obrigatório: "Item Externo - Verificar se é ferrugem (natural) ou batida (mau uso)".
- NEGAR (Vermelho): Pintura de fachada de prédio inteira (responsabilidade do condomínio).

⚡ CATEGORIA: ELÉTRICA (ITENS FIXOS)
- APROVAR (Verde): Espelhos de tomada, Tomadas inteiras, Interruptores, Bocais de luz.
  - Regra: Se está quebrado, faltando, pintado ou solto, o inquilino deve pagar a reposição.
- NEGAR (Vermelho): Resistência de chuveiro queimada, Lâmpadas queimadas (salvo se entregue novas na entrada com prova), Fiação interna (curto circuito dentro da parede).

💧 CATEGORIA: HIDRÁULICA
- APROVAR (Verde): Louças quebradas (Pia, Vaso), Assento sanitário quebrado/faltando, Torneira quebrada fisicamente (alavanca solta/quebrada).
- NEGAR (Vermelho): Reparos de vazamento interno (pinga-pinga), Troca de vedante/courinho, Flexível ressecado pelo tempo, Registro emperrado por falta de uso.

🪑 CATEGORIA: ITENS NÃO FIXOS (MOBÍLIA)
- NEGAR (Vermelho) TODOS: Sofá, Mesa, Cadeira, Cortina, Persiana, Eletrodomésticos, Tapetes, Itens de decoração.
- Motivo: "Item não fixo / Acessório não estrutural".

🚫 CATEGORIA: LIMPEZA & ENTULHO
- APROVAR (Verde): Limpeza geral pós-obra ou limpeza pesada se o imóvel foi entregue sujo.
- ATENÇÃO (Amarelo): Caçambas com valor acima de R$ 400,00.

--- 3. FORMATO DE SAÍDA OBRIGATÓRIO (JSON) ---
Analise item a item e retorne APENAS este formato JSON:
[
  {
    "Item": "Copie o texto original EXATAMENTE como escrito no orçamento",
    "Valor": 0.00,
    "Status": "Escolha entre: Aprovado / Atenção / Negado",
    "Motivo": "Explicação curta baseada nas regras acima"
  }
]
"""

# --- 4. INTERFACE ---
st.title("🏢 Analisador Loft (Master Knowledge)")
st.caption("Base de Conhecimento Integrada v17")

col1, col2 = st.columns(2)
with col1:
    vistoria_entrada = st.file_uploader("📂 1. Vistoria Entrada", type=['pdf', 'jpg', 'png'], key="entrada")
with col2:
    vistoria_saida = st.file_uploader("📂 2. Vistoria Saída", type=['pdf', 'jpg', 'png'], key="saida")

st.markdown("---")
st.markdown("### 💰 3. Orçamento")
st.caption("A IA vai cruzar o orçamento com a Base de Conhecimento acima.")

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

    with st.status("🧠 Consultando Base de Conhecimento...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            # Modelo Inteligente
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
                st.markdown('<div class="section-title green-text">✅ APROVADOS</div>', unsafe_allow_html=True)
                for i, row in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><div>{row["Item"]} <span class="badge bg-green">FOTO</span></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not atencao.empty:
                st.markdown('<div class="section-title yellow-text">⚠️ ATENÇÃO / EXTERNO</div>', unsafe_allow_html=True)
                for i, row in atencao.iterrows():
                    obs = row["Motivo"]
                    # Reforço visual para portão/externo
                    if "Externo" in str(row["Motivo"]) or "Portão" in row["Item"]:
                        obs = "⚠️ ITEM EXTERNO: Verificar responsabilidade."
                    st.markdown(f'<div class="card card-yellow"><div>{row["Item"]} <span class="badge bg-yellow">VERIFICAR</span><br><small>{obs}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.markdown('<div class="section-title red-text">⛔ NEGADOS</div>', unsafe_allow_html=True)
                for i, row in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><div>{row["Item"]}<br><small>Motivo: {row["Motivo"]}</small></div><div class="card-price">R$ {row["Valor"]:.2f}</div></div>', unsafe_allow_html=True)

            # --- 7. COPY AREA (TEXTO SIMPLES PARA ONENOTE) ---
            st.divider()
            st.subheader("📋 Relatório Final (Copiar)")
            
            relatorio = "RELATÓRIO TÉCNICO\n=================\n\n"
            if not aprovados.empty:
                relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f}\n"
                relatorio += "\n"
            
            if not atencao.empty:
                relatorio += "⚠️ ATENÇÃO:\n"
                for i, r in atencao.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f} ({r['Motivo']})\n"
                relatorio += "\n"

            if not negados.empty:
                relatorio += "⛔ NEGADOS:\n"
                for i, r in negados.iterrows():
                    relatorio += f"• {r['Item']} | R$ {r['Valor']:.2f} ({r['Motivo']})\n"
            
            total_geral = aprovados['Valor'].sum()
            total_negado = negados['Valor'].sum()
            
            relatorio += "\n================="
            relatorio += f"\nTOTAL APROVADO: R$ {total_geral:.2f}"
            relatorio += f"\nTOTAL ECONOMIZADO: R$ {total_negado:.2f}"

            st.code(relatorio, language='text')

        except Exception as e:
            status.update(label="❌ Erro", state="error")
            st.error("Erro ao processar. Verifique se a chave API está correta ou se o arquivo é válido.")
            st.write(e)
