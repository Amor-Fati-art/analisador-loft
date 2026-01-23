import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
import pandas as pd
import io

# --- 1. CONFIGURAÇÃO DE SEGURANÇA ---
try:
    CHAVE_SECRETA = st.secrets["CHAVE_SECRETA"]
except (FileNotFoundError, KeyError):
    st.error("❌ ERRO: Arquivo secrets.toml não encontrado.")
    st.stop()

st.set_page_config(page_title="Auditor Loft - Oficial & Treinado", page_icon="🏢", layout="wide")
st.markdown("""
<style>
.card { padding: 15px; border-radius: 10px; margin-bottom: 10px; background-color: #1e1e1e; border: 1px solid #333; }
.card-green { border-left: 5px solid #28a745; }
.card-red { border-left: 5px solid #dc3545; }
.card-yellow { border-left: 5px solid #ffc107; }
.price { float: right; font-weight: bold; }
</style>
""", unsafe_allow_html=True)
# --- BARRA LATERAL (LINK PARA SHAREPOINT) ---
with st.sidebar:
    st.header("🆘 Central de Ajuda")
    
    st.warning(
        """
        ⚠️ **Aviso de Falibilidade**
        
        A IA é uma ferramenta de apoio e pode cometer erros. Se o motivo da negativa parecer errado, consulte a **Base Oficial**.
        """
    )
    
    # Link do SharePoint da Loft
    url_sharepoint = "https://loftms365.sharepoint.com/sites/baseconhecimentoinadimplncia/SitePages/Planos%20e%20coberturas/Regras-de-cobertura-para-multas-rescisórias,-aviso-prévio-e-reparos.aspx?web=1"
    
    st.link_button("🔗 Abrir Base de Conhecimento", url_sharepoint)
    
    st.divider()
    
    # Resumo rápido para consulta imediata
    with st.expander("📖 Regras Rápidas (Resumo)"):
        st.markdown("""
        - **Chaves/Cadeados:** APROVAR (Segurança).
        - **Limpeza Geral:** APROVAR.
        - **Limpeza Sofá/Cortina:** NEGAR (Item Móvel).
        - **Torneira Pingando:** NEGAR (Manutenção).
        - **Torneira Quebrada:** APROVAR (Dano).
        - **Vidro Quebrado:** APROVAR.
        """)
# --- 2. CONFIGURAÇÃO ANTI-BLOQUEIO ---
SAFETY_SETTINGS = {
    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
}

# ==============================================================================
# 3. LEI: REGRAS OFICIAIS (BASE DE CONHECIMENTO COMPLETA)
# ==============================================================================
REGRAS_OFICIAIS = """
Reparos na desocupação do imóvel

Ao desocupar o imóvel, o inquilino deve garantir que ele seja devolvido nas mesmas condições em que foi recebido, conforme descrito na vistoria de entrada. Podem ser cobrados como reparos:
Pintura (se exigida no contrato);
Conserto de danos causados durante a locação (ex: furos, quebras, manchas);
Troca de itens danificados (ex: tomadas, lâmpadas, torneiras);
Limpeza do imóvel

A vistoria de saída será usada para comparar o estado atual com o inicial. Se forem identificados danos, a imobiliária deve apresentar os orçamento e cobrar o valor dos reparos.
⚠️ A imobiliária deve abrir uma linha individual para reparos na desocupação do imóvel. Caso informe a multa junto aos valores locatícios (aluguel, condomínio, IPTU), a equipe de inadimplência deve desmembrar o valor em uma nova linha, já que o pagamento da multa é feito com base no valor original, sem juros ou multas adicionais.
 
Documentos necessários para analise dos Reparos:
Laudo da vistoria de Entrada – Assinada pelo Locatário e Vistoriador/ imobiliária/ locador> Obrigatório a assinatura de ambos.​​
Laudo da vistoria de Saída – Assinada pelo Locatário e Vistoriador/imobiliária/ locador> Obrigatório a assinatura do vistoriador, porém a do inquilino, pode ser substituída por um e-mail conforme padrão estabelecido.​
Metragem do imóvel (apenas da área construída); 
 
Não precisa solicitar metragem caso o valor de custo de saída da plataforma já seja acima de R$4.000,00 ou se valor de reparos e/ ou multa contratual estiver dentro do valor de custo de saída.​
 
Fotos (vistoria de entrada e saída): Sempre solicitar as fotos coloridas quando houver reparos para o comparativo. ​​​
º A imobiliária pode enviar vídeo desde que demonstrem exclusivamente os itens com defeitos com os devidos “cortes” ou informando os minutos dos pontos em inconformidade.
Importante: o vídeo substitui as fotos, mas é imprescindível o envio dos laudos das vistorias assinadas.
 
Caso o documento não apresente as fotos, antes de solicitar à imobiliária, verificar se elas já foram enviadas por e-mail, consultando a caixa de entrada fotos@loft.com.br.
A prioridade é o envio dos arquivos pela plataforma. O envio por e-mail deve ser orientado à imobiliária apenas em casos excepcionais, onde a plataforma apresente erro, devido ao formato e tamanho do arquivo.
 
Anexar 02 orçamentos (descritivos/detalhados, incluindo dados do prestador (CPF/CNPJ) e do imóvel (endereço) -  Os orçamentos precisam descrever os serviços e valores individualmente, separando mão de obra e material da parte interna da parte externa. Será considerado o orçamento de menor valor para análise;​
 
✅ Na página da Imobiliária estão disponíveis modelos e sugestões de documentos que devem ser utilizados no momento da abertura da inadimplência por rescisão.
 
⚠️ Todos os itens pagos pela Loft Fiança serão posteriormente cobrados do locatário. Por isso, é imprescindível que cada item apontado na cobrança final esteja devidamente comprovado por meio de documentos. Os valores repassados para manutenção na desocupação estão limitados conforme as regras do item "Custo de Saída" do TCG (Termo de Cobertura Geral).
 
Analisando Reparos no Imóvel

Quando a imobiliária solicita cobertura para valores relacionados a de reparos, o processo de análise segue os critérios abaixo:
Documentos utilizados para análise conforme: Reparos na desocupação do imóvel
 
Dois orçamentos comparativos
Devem conter o detalhamento individual dos serviços, incluindo dados do prestador (CPF/CNPJ) e do imóvel (endereço)
Ambos devem referir-se aos mesmos serviços e escopo, para permitir comparação justa.
Laudo descritivo da vistoria de entrada e saída com fotos para o comparativo.
As imagens devem comprovar o estado original do imóvel (entrada) e o dano ou desgaste ao final da locação (saída).
Servem como base para validar se os reparos são de responsabilidade do inquilino, conforme o Termo.
 
❌ As fotos não substituem o laudo descritivo elas devem ser utilizadas apenas como complemento da análise, nunca como único critério na analise.
 
Orçamento considerado:
Sempre será considerado o orçamento de menor valor entre os dois apresentados, desde que:
Atenda o escopo completo do reparo necessário;
Esteja dentro de um valor de mercado razoável;
Tenha qualidade e detalhamento suficiente para análise.
 
⚠️ Importante:
O envio incompleto da documentação pode levar à recusa da solicitação ou à necessidade de reabertura do processo.
Reparos que não constem no Termo de Cobertura da Loft não serão reembolsados, mesmo com orçamento e vistoria.
 
Critérios de análise:
A equipe responsável irá verificar se os danos são cobertos pelo Termo da Loft (ex: pintura, danos em portas, pias, etc.).
A avaliação será feita com base na comparação entre as vistorias (antes e depois), garantindo que:
O dano não é considerado desgaste natural;
O item não foi substituído ou alterado pelo proprietário;
Há evidência clara de que o reparo é necessário.

Etapas para Análise de Reparos – Itens com ou sem cobertura pela Loft
 
Verificar se há itens fora da cobertura
O primeiro passo da análise é identificar, entre os itens enviados pela imobiliária para reembolso, quais não possuem cobertura conforme o Termo da Loft (Motivos de Negativa na Análise de Reparos – Não Cobertos pelo Termo Loft Fiança). Esses itens devem ser separados ou sinalizados, pois não serão considerados para pagamento.
Validar os itens cobertos individualmente, para cada item com cobertura, é necessário:
Verificar o estado do item na vistoria de entrada, com base no laudo e fotos;
Comparar com o estado do item na vistoria de saída, também considerando o laudo e os registros fotográficos enviados;
Avaliar se há mudança significativa de estado entre a entrada e a saída do imóvel.
Analisar itens com dano pré-existente (vistoria de entrada já indicava problema), nesses casos, a análise deve ser feita com mais atenção. Antes de recusar o pagamento, é importante avaliar:
Se houve agravamento do dano por mau uso do inquilino, ou seja, o estado final está visivelmente pior do que na entrada;
Ou se trata-se de desgaste natural pelo tempo de uso, sem evidência de má conservação.
 
Somente após essa avaliação é possível concluir pela aprovação parcial, total ou negativa do item solicitado.
⚠️ Todos os reparos informados no orçamento devem estar devidamente descritos no laudo da vistoria final.
Itens que não constarem no laudo descritivo devem ser negados, mesmo que haja fotos comprovando o dano.
 
ℹ️ Cenários onde o valor da multa contratual enviada pela imobiliária seja superior ao cálculo é necessário realizar a negativa do valor excedente na plataforma conforme notas e gerador de e-mail.
 
Após a conclusão da análise, caso o valor do orçamento seja superior a R$ 2.000,00, é necessário encaminhá-lo à Refera para que seja realizada a precificação dos orçamentos, conforme procedimento.
 
✅💡 Dica: Antes de encaminhar o orçamento para análise da Refera, é fundamental verificar se o contrato ainda possui fiança disponível para cobertura dos reparos. Em alguns casos, a multa contratual já compromete até 90% do limite do custo de saída, o que pode tornar a análise da Refera desnecessária, já que não haverá saldo suficiente para pagamento dos reparos.
 
Motivos de Negativa na Análise de Reparos – Não Cobertos pelo Termo Loft Fiança
 
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
Cortinas e persianas simples: Aqueles que são penduradas em varões ou trilhos que podem ser facilmente desparafusados sem danificar a parede.
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
 
⚠️ Valores acima de 400,00, a imobiliária precisa comprovar quantidade de caçambas utilizadas.
"""

# ==============================================================================
# 4. JURISPRUDÊNCIA: EXEMPLOS DE TREINAMENTO
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

--- EXEMPLO 6 (SEGURANÇA) ---
Item: Chave do portão
Decisão: APROVADO
Motivo: Item de segurança essencial/restituição obrigatória.

--- EXEMPLO 7 (SEGURANÇA) ---
Item: Cadeado pado
Decisão: APROVADO
Motivo: Item de segurança essencial/restituição obrigatória.

--- EXEMPLO 8 (ITEM MÓVEL) ---
Item: Assento de Vaso Sanitário
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: item não fixo/mobília.

--- EXEMPLO 9 (ITEM MÓVEL) ---
Item: Ralo do Banheiro
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: item não fixo/mobília.


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
(iv)  Danos causados ao imóvel, assim como a eventuais móveis embutidos e equipamentos fixos.
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
(xii)  danos estruturais nos telhados e/ou porção diversa do imóvel decorrentes de caso fortuito e/ou força maior ou, ainda, de dolo do(s) Locatário(s).
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

Detalhamento Geral do(s) valor(es) aprovado(s)
Reparos:
• Pintura interna: R$ 1.635,00
(com bônus Refera aplicado, total: R$ 1.798,50)
Valor total aprovado: R$ 1.798,50
Valor(es) aprovado(s)
Reparos:
• Pintura interna do imóvel –: R$ 1.400,00
• Limpeza geral do imóvel –: R$ 250,00
• Restauração da parte inferior da porta – cozinha –: R$ 100,00
• Restauração do piso cerâmico – quarto –: R$ 100,00
• Descarte de objetos –: R$ 80,00
• Remoção de móvel – banheiro –: R$ 60,00
• Remoção de manchas de ferrugem no piso cerâmico – área de serviço –: R$ 60,00
• Remoção de encanamento – cozinha –: R$ 60,00
• Reposição de 1 chave da porta de entrada –: R$ 50,00
• Remoção de acessório fixado na parede – banheiro –: R$ 35,00
• Remoção de manchas no piso cerâmico – banheiro –: R$ 35,00
Valor total aprovado: R$ 2.230,00
Valor(es) negado(s)
Reparos:
• Troca de chuveiro – banheiro –: R$ 200,00
Motivo da negativa:
Exclusões dos Valores Contratados: A obrigação da Loft quanto ao pagamento de Valores Contratados inadimplidos pelo(s) Locatário(s) não incluem responsabilidade em relação ao pagamento de despesas e danos decorrentes de:
(xi) danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.
• Remoção de mancha da cuba – banheiro –: R$ 150,00
Motivo da negativa:
Negado, tendo em vista que o valor informado é incluso dentro da limpeza geral.
Valor total negado: R$ 350,00

--- EXEMPLO 10 (ELETRICA FUNCIONAL) ---
Item: Luminária arandela não funcionando
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.

--- EXEMPLO 11 (HIDRAULICA CONEXAO) ---
Item: Chuveiro com cano quebrado na entrada da conexão
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: Danos nas redes hidráulicas e elétricas, que não consistam em danos aparentes e acabamentos externos.
--------------------------------------------
--- EXEMPLO 12 (LIMPEZA MOBILIA) ---
Item: Higienização do Sofá
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: item não fixo/mobília.

--- EXEMPLO 13 (LIMPEZA MOBILIA) ---
Item: Lavagem de Cortinas
Decisão: NEGADO
Motivo: Pagamento negado, conforme consta no nosso termo: item não fixo/mobília.

--- EXEMPLO 14 (LIMPEZA ESTRUTURAL) ---
Item: Remoção mancha da cuba - banheiro
Decisão: APROVADO
Motivo: Limpeza de item fixo (cuba).

"""

# --- 5. FUNÇÃO AUXILIAR ---
def _montar_prompt(regras, exemplos, v_ent, v_sai, o_txt, o_arq):
    prompt = ["VOCÊ É UM ANALISTA DE REPAROS DA LOFT FIANÇA."]
    prompt.append("SUA MISSÃO É SEGUIR ESTRITAMENTE AS 'REGRAS OFICIAIS DA EMPRESA' ABAIXO:")
    prompt.append("--- INÍCIO DAS REGRAS OFICIAIS (BASE DE CONHECIMENTO) ---")
    prompt.append(regras)
    prompt.append("--- FIM DAS REGRAS OFICIAIS ---")
    
    prompt.append("""
    \nAGORA, COM BASE NO TEXTO ACIMA, APLIQUE AS SEGUINTES REGRAS OPERACIONAIS DE DECISÃO EM ORDEM DE PRIORIDADE:
    
    0. **REGRA SUPREMA: ITENS REMOVÍVEIS**: Se o item for **ASSENTO DE VASO, TAMPA DE VASO, RALO ou GRELHA**, você deve **NEGAR** (Red).
       - Motivo OBRIGATÓRIO: "Pagamento negado, conforme consta no nosso termo: item não fixo/mobília."
       - Obs: Isso vale MESMO que o item esteja quebrado ou faltando. A regra de item removível prevalece sobre furto.
    
    1. **Pintura Interna e Danos Físicos Internos**: O texto diz que 'Podem ser cobrados como reparos: Pintura e Conserto de danos'. Logo, se for Pintura Interna, Buracos na Parede, Piso/Azulejo Quebrado ou Danificado (Interno): APROVAR (Green).
    
    2. **Pintura Externa (Muros/Fachadas)**: O texto menciona 'Tinta desbotada... área externa' como desgaste natural (negado). 
       PORÉM, se o orçamento disser explicitamente 'COM COBERTURA' ou 'ÁREA COBERTA', você deve APROVAR. 
       Se o orçamento NÃO disser se é coberto, marque como VERIFICAR (Yellow/Amarelo) para checagem visual.
    
    3. **Itens Faltantes / Furtados**: O texto classifica como 'Ato Ilícito' e diz que a 'Loft Fiança não cobre'. Portanto: NEGAR (Red).
       🔴 **EXCEÇÃO CRÍTICA (SEGURANÇA):** Se o item faltante for **CHAVE, CADEADO ou CONTROLE DE PORTÃO**, você deve **APROVAR** (Green). Motivo: Item de segurança essencial, deve ser restituído.
    
    4. **Torneiras, Chuveiros, Luminárias e Hidráulica/Elétrica**: 
       - Se o orçamento disser "Não funcionando", "Queimada", "Vazamento", "Pingando" ou "Curto" -> NEGAR (Vermelho - Defeito Funcional/Rede).
       - Se o orçamento disser "Cano quebrado na parede", "Quebra na rosca/conexão" ou "Entrada da conexão" -> NEGAR (Vermelho - Problema na Rede Hidráulica).
       - Se o orçamento disser "Faltando" -> NEGAR (Vermelho - Ato Ilícito).
       - Apenas se for "Louça Quebrada" (ex: pia partida ao meio) ou "Vidro Quebrado" -> APROVAR (Verde).
       - ⚠️ Demais casos genéricos ("Danificada", "Com defeito") -> VERIFICAR (Amarelo).
    
    5. **Desgaste Natural / Ação do Tempo**: Use o motivo de negativa exato do texto oficial para NEGAR (Red).
    
    6. **Limpeza**: O texto diz 'Podem ser cobrados... Limpeza do imóvel'. APROVAR (Green).
                  **Limpeza (Regra de Fixo vs Móvel)**: 
       - **APROVAR (Green):** Limpeza Geral, Faxina, Chão, Paredes, Vidros, Pias, Cubas, Banheiros (Itens fixos na estrutura).
       - **NEGAR (Red):** Limpeza/Higienização de ITENS MÓVEIS (Sofá, Cortina, Tapete solto, Colchão, Cama, Eletrodomésticos). 
       - Motivo da Negativa para Móveis: "Pagamento negado, conforme consta no nosso termo: item não fixo/mobília."

    FORMATO DE SAÍDA JSON OBRIGATÓRIO:
    [{"Item": "Nome do item", "Valor": 0.00, "Status": "Aprovado/Negado/Verificar", "Motivo": "Copie o motivo exato do texto oficial acima, sem inventar."}]
    """)
    
    prompt.append("\nHISTÓRICO DE CASOS PASSADOS (EXEMPLOS PRÁTICOS):")
    prompt.append(exemplos)
    
    if v_ent:
        prompt.append("CONTEXTO: VISTORIA DE ENTRADA")
        prompt.append({"mime_type": v_ent.type, "data": v_ent.getvalue()})
    if v_sai:
        prompt.append("CONTEXTO: VISTORIA DE SAÍDA")
        prompt.append({"mime_type": v_sai.type, "data": v_sai.getvalue()})
    
    prompt.append("ORÇAMENTO A ANALISAR:")
    if o_arq:
        prompt.append({"mime_type": o_arq.type, "data": o_arq.getvalue()})
    else:
        prompt.append(o_txt)
    return prompt

# --- 6. INTERFACE ---
st.title("🏢 Auditor Loft - Base Oficial Integrada")
st.warning("""
⚠️ **ATENÇÃO OBRIGATÓRIA: CONFERÊNCIA DE MOTIVOS**
A IA é uma ferramenta de apoi, verifique se os valores foram analise correto antes de aprovar. **VOCÊ É O RESPONSÁVEL FINAL.**
""")

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

    with st.status("🤖 Consultando Base Oficial (Gemini 2.5)...", expanded=True) as status:
        try:
            genai.configure(api_key=CHAVE_SECRETA)
            
            # --- MODELO ATUALIZADO (2.5 FLASH) ---
            model = genai.GenerativeModel('gemini-2.5-flash', generation_config={"response_mime_type": "application/json"})
            
            # Passamos REGRAS_OFICIAIS e EXEMPLOS_TREINAMENTO para o prompt
            response = model.generate_content(
                _montar_prompt(REGRAS_OFICIAIS, EXEMPLOS_TREINAMENTO, vistoria_entrada, vistoria_saida, orcamento_txt, orcamento_arq),
                safety_settings=SAFETY_SETTINGS
            )
            
            if not response.parts:
                st.error("Erro no retorno da IA. Tente novamente.")
                st.stop()

            df = pd.read_json(io.StringIO(response.text))
            
            status.update(label="✅ Análise Concluída", state="complete", expanded=False)
            
            # --- RESULTADOS ---
            st.divider()
            
            aprovados = df[df['Status'].str.contains("Aprovado", case=False)]
            verificar = df[df['Status'].str.contains("Verificar|Atenção", case=False)]
            negados = df[df['Status'].str.contains("Negado", case=False)]
            
            if not aprovados.empty:
                st.subheader("✅ Aprovados")
                for i, r in aprovados.iterrows():
                    st.markdown(f'<div class="card card-green"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)

            if not verificar.empty:
                st.subheader("⚠️ Atenção: Verificar Visualmente")
                for i, r in verificar.iterrows():
                    st.markdown(f'<div class="card card-yellow"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small style="color: #FFC107">{r["Motivo"]}</small></div>', unsafe_allow_html=True)

            if not negados.empty:
                st.subheader("⛔ Negados")
                for i, r in negados.iterrows():
                    st.markdown(f'<div class="card card-red"><b>{r["Item"]}</b><span class="price">R$ {r["Valor"]:.2f}</span><br><small>{r["Motivo"]}</small></div>', unsafe_allow_html=True)
            
            # --- RELATÓRIO ---
            st.divider()
            st.subheader("📋 Relatório Final (Baseado no Termo)")
            
            txt_relatorio = "RELATÓRIO TÉCNICO - ANÁLISE DE REPAROS\n"
            txt_relatorio += "======================================\n"
            
            if not aprovados.empty:
                txt_relatorio += "✅ APROVADOS:\n"
                for i, r in aprovados.iterrows():
                    txt_relatorio += f"[+] {r['Item']} | R$ {r['Valor']:.2f}\n"

            if not verificar.empty:
                txt_relatorio += "\n⚠️ VERIFICAR (INCERTEZA NO ITEM):\n"
                for i, r in verificar.iterrows():
                    txt_relatorio += f"[?] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    txt_relatorio += f"    Obs: {r['Motivo']}\n"
            
            if not negados.empty:
                txt_relatorio += "\n⛔ NEGADOS:\n"
                for i, r in negados.iterrows():
                    txt_relatorio += f"[-] {r['Item']} | R$ {r['Valor']:.2f}\n"
                    txt_relatorio += f"    Motivo: {r['Motivo']}\n"
            
            val_total = df['Valor'].sum()
            val_aprov = aprovados['Valor'].sum() if not aprovados.empty else 0
            
            txt_relatorio += "\n======================================\n"
            txt_relatorio += f"TOTAL SOLICITADO: R$ {val_total:.2f}\n"
            txt_relatorio += f"TOTAL APROVADO:   R$ {val_aprov:.2f}"
            
            st.code(txt_relatorio)

        except Exception as e:
            st.error(f"Erro no processamento: {e}")
