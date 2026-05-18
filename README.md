# ZIGURAT_TFM
♿ Verificação Automatizada de Conformidade BIM — ABNT NBR 9050:2020

Trabalho de Conclusão de Master (TFM) — Master Internacional em IA para Arquitetura e Construção
Zigurat Institute of Technology

Sistema LLM-cêntrico e multi-agente para verificação automatizada de conformidade de acessibilidade arquitetônica a partir de modelos BIM no formato IFC, com interface web interativa construída em Streamlit.

👥 Grupo 1 — Autores
NomeFunção no GrupoKevin DiasPesquisa e desenvolvimentoViviane SuzukePesquisa e desenvolvimentoSergio RosenboimPesquisa e desenvolvimentoWilliam MouraPesquisa e desenvolvimentoRenata RochaBIM & IFC / Coordenação técnica
Orientação acadêmica: Zigurat Institute of Technology

🎯 Objetivo
Automatizar a auditoria de acessibilidade de edificações verificando 12 itens selecionados da ABNT NBR 9050:2020 diretamente a partir do modelo IFC, sem necessidade de inspeção manual completa.
O sistema adota uma abordagem LLM-cêntrica — o modelo de linguagem atua como motor de raciocínio ao longo de todo o pipeline: interpreta a norma, analisa os dados extraídos do IFC, cruza evidências e redige o laudo técnico. Essa escolha contrasta com abordagens de geometria computacional pura, que exigem metadados BIM completos e precisos, algo raramente encontrado em exportações reais de projetos brasileiros.
Entregáveis gerados pelo sistema

Checklist .xlsx — 12 itens com status, valores encontrados, valores exigidos e recomendações
Relatório .docx — Laudo técnico completo com resumo executivo, metodologia, análise contextual e limitações
Relatório .html — Versão visual interativa para apresentação e compartilhamento


🏗️ Arquitetura: Pipeline LLM-Cêntrico
O coração do sistema é um pipeline sequencial de 4 agentes CrewAI, onde cada agente é especializado em uma etapa do processo de auditoria. Pense nisso como uma linha de montagem inteligente: o modelo BIM entra "bruto" numa ponta e sai como um laudo técnico estruturado na outra.
┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Agente 1    │───▶│  Agente 2    │───▶│  Agente 3    │───▶│  Agente 4    │
│  Extrator    │    │  Auditor     │    │  Consultor   │    │  Redator     │
│  BIM / IFC   │    │  NBR 9050    │    │  de Contexto │    │  Técnico     │
└──────────────┘    └──────────────┘    └──────────────┘    └──────────────┘
       ▲                                        ▲
   Modelo .ifc                          Planilha de normas
                                        (.xlsx externo)
AgentePapelFerramenta principalAgente 1 — ExtratorEspecialista em Extração de Dados BIM/IFCextrair_elementos_acessibilidade_ifc via IfcOpenShellAgente 2 — AuditorAuditor de Acessibilidade NBR 9050:2020Raciocínio LLM sobre o inventário do Agente 1Agente 3 — ConsultorConsultor de Contexto de Projeto AECconsultar_documentos_projeto (BEP + Memorial)Agente 4 — RedatorRedator de Relatórios Técnicos AECgerar_checklist_xlsx + gerar_relatorio_docx

Por que multi-agente? Cada agente tem um system prompt especializado e acesso apenas às ferramentas que precisa. Isso reduz alucinações, melhora rastreabilidade e permite escalar — adicionar um novo agente de priorização, por exemplo, não exige reescrever o sistema inteiro.


✅ Itens NBR 9050:2020 Verificados
O sistema verifica 12 itens distribuídos em 4 categorias de classificação, que refletem a complexidade crescente da verificação:
CategoriaDefiniçãoItemElemento BIMGeométricaDimensão diretamente mensurável no IFC6.6Rampas — inclinação máximaGeométrica6.11.1Corredores — largura mínimaGeométrica6.11.2Portas — vão livre mínimo (0,80m × 2,10m)CondicionalDepende de condições do contexto6.11.3Janelas — peitoril mínimo (1,20m)Condicional5.4.3Corrimão — altura e presença bilateralCondicional6.3.4Pisos — desníveis com chanfroRelacionalRelação espacial entre elementos7.5Circulação — espaço de giro Ø 1,50mRelacional7.7.2.1Bacia sanitária — altura 0,43–0,45mRelacional7.7.1Vaso sanitário — espaço lateral livre 0,80mQualitativaAtributo textual / semântico4.6.6Portas — maçaneta tipo alavancaQualitativa7.6–7.8Box de acessibilidade — barras de apoioQualitativa7.8Lavatório — suspenso ou sem coluna
Status possíveis: ✅ Conforme · ❌ Não Conforme · ⚠️ Indeterminado · N/A

🖥️ Interface Web — Streamlit App
O sistema conta com uma interface web completa que elimina a necessidade do Google Colab para uso em produção. A interface segue o padrão visual do TFM (identidade Zigurat).
Funcionalidades da interface

Upload de arquivos — modelo .ifc e planilha de normas .xlsx
Configuração de LLM — suporte a Anthropic (Claude) e Google (Gemini), com campo para inserção de API Key
Seleção de modelo — escolha entre versões disponíveis de cada provedor
Painel de progresso — indicador visual dos 4 agentes em execução em tempo real
Aba Resultados — tabela interativa com filtros por status e por categoria
Rastreabilidade por GlobalId — cada elemento analisado exibe seu GlobalId IFC, permitindo localização direta no Revit, BIMcollab Zoom, Solibri e usBIM
Download de entregáveis — checklist .xlsx, relatório .docx e relatório .html com um clique


O que é o GlobalId? É o identificador único e permanente de cada elemento no modelo IFC — como o CPF de uma porta ou rampa. Com ele, você cola o código no campo de busca do Revit ou do seu software de coordenação BIM e vai diretamente ao elemento não conforme, sem busca manual.


📦 Stack Tecnológica
Python 3.10+
├── crewai / crewai-tools     # Orquestração multi-agente
├── ifcopenshell              # Leitura e extração de dados IFC
├── streamlit                 # Interface web
├── openpyxl                  # Geração do checklist .xlsx
├── python-docx               # Geração do laudo .docx
└── anthropic / google-genai  # LLMs (Claude e Gemini)
Instalação
bashpip install crewai crewai-tools
pip install ifcopenshell
pip install streamlit
pip install openpyxl python-docx
pip install anthropic google-generativeai
Variáveis de ambiente
bashANTHROPIC_API_KEY=sk-ant-...   # Para uso com Claude
GOOGLE_API_KEY=...             # Para uso com Gemini

As chaves também podem ser inseridas diretamente na sidebar do app Streamlit, sem necessidade de variável de ambiente.


📁 Estrutura do Repositório
TFM-NBR9050/
├── app.py                                  # App Streamlit (interface principal)
├── pipeline/
│   ├── agents.py                           # Definição dos 4 agentes CrewAI
│   ├── tasks.py                            # Tasks e dependências entre agentes
│   ├── tools.py                            # Ferramentas: extração IFC, geração de relatórios
│   └── crew.py                             # Montagem e execução do Crew
├── normas/
│   └── Normas_Acessibilidade_NBR9050.xlsx  # Planilha externa com os 12 itens verificáveis
├── docs/
│   ├── bep_projeto.docx                    # BIM Execution Plan (exemplo de input)
│   └── memorial_descritivo.docx            # Memorial de Acabamentos (exemplo de input)
├── notebooks/
│   └── M5T2_nbr9050_crewai_ifc2x3.ipynb   # Notebook Colab (versão acadêmica)
└── output/                                 # Pasta de saída (gerada automaticamente)
    ├── checklist_nbr9050_YYYYMMDD.xlsx
    ├── relatorio_acessibilidade_YYYYMMDD.docx
    └── relatorio_acessibilidade_YYYYMMDD.html

▶️ Como Executar
Opção 1 — App Streamlit (recomendado)
bash# Clone o repositório
git clone https://github.com/seu-usuario/TFM-NBR9050.git
cd TFM-NBR9050

# Instale as dependências
pip install -r requirements.txt

# Inicie o app
streamlit run app.py
Acesse http://localhost:8501 no navegador. Faça upload do .ifc e da planilha de normas, insira sua API Key e clique em Iniciar Verificação.
Opção 2 — Google Colab
Abra notebooks/M5T2_nbr9050_crewai_ifc2x3.ipynb no Colab, faça upload dos arquivos de projeto e execute as células em ordem. A execução completa leva aproximadamente 9–15 minutos, incluindo pausas de rate limit entre agentes.

⚙️ Configurações Principais
ParâmetroValor padrãoDescriçãomodelo LLMclaude-sonnet-4-5Modelo de linguagem (configurável na UI)rate_limit_pause15sPausa entre tarefas para respeitar limites de APISchema IFC suportadoIFC2X3 e IFC4Detecção automática com fallbackplanilha_normasNormas_Acessibilidade_NBR9050.xlsxFonte das regras de verificação

⚠️ Limitações Conhecidas e Decisões de Design
1. Schema IFC2X3 e IfcSanitaryTerminal
A entidade IfcSanitaryTerminal foi introduzida apenas no IFC4. Em projetos exportados via Revit com schema IFC2X3 — que ainda predomina no mercado brasileiro — o sistema usa IfcFlowTerminal como fallback. Alturas de instalação de bacias sanitárias ficam Indeterminadas pois o dado existe apenas na geometria 3D, não nos atributos nativos.
2. Metadados dimensionais ausentes
Atributos como OverallWidth, OverallRise e OverallRun frequentemente estão nulos em exportações Revit, mesmo quando a dimensão existe no modelo 3D. Itens como vão livre de portas podem ser subestimados ou classificados como Indeterminados.
3. Verificações qualitativas
Itens como "maçaneta tipo alavanca" ou "lavatório suspenso" dependem de atributos textuais nos PropertySets, que raramente são preenchidos em projetos reais. Requerem inspeção manual complementar.
4. IfcSpace ausente
Itens que dependem de espaços modelados (corredores, giro de cadeira de rodas) ficam automaticamente como Indeterminados se o modelo não exportar IfcSpace.
Por que LLM e não geometria computacional pura?
CritérioLLM PuroGeometria PuraHíbrido (Proposto)Interpretação de texto normativoAlta capacidadeInviávelAlta capacidadePrecisão geométrica (<1mm)Baixa confiabilidadeAlta precisãoAlta precisãoClassificação qualitativaAdequadoInviávelAdequadoResiliência a IFC incompletoModeradaBaixaAlta (fallback)Rastreabilidade de evidênciasLimitadaAltaAlta

🔬 Contexto Acadêmico

Programa: Master Internacional em IA para Arquitetura e Construção — Zigurat Institute of Technology
Módulo de referência: M5T2 — Sistemas Agentic AI aplicados ao AEC
Norma verificada: ABNT NBR 9050:2020 — Acessibilidade a edificações, mobiliário, espaços e equipamentos urbanos
Modelo IFC de teste: Atlas Londrina Test Tower (1589_21-ARQ-LO-IFC-R01.ifc) — torre de testes de elevadores (~150m, 11.270 m²), Londrina/PR
Documentos de projeto utilizados: BEP-R00 e MED-R00 (uso exclusivamente acadêmico)


🛠️ Extensões Futuras

Análise geométrica 3D via ifcopenshell.geom — extrair dimensões diretamente da malha sólida, resolvendo os itens Indeterminados por falta de atributos
Agente pré-processador de qualidade de modelo — avalia completude de Psets antes da auditoria, ajustando expectativas de resultado
Agente de priorização — ordena não conformidades por criticidade e custo estimado de correção
Exportação para BCF — integração com BIM Collaboration Format para envio direto de issues ao Solibri, BIMcollab Zoom ou BIMcollab Cloud
Extensão para outras normas — a planilha de normas é o único arquivo a editar para suportar Decreto-Lei 163/2021, normas municipais ou requisitos LEED
Deploy em nuvem — Streamlit Community Cloud ou HuggingFace Spaces para acesso sem instalação local


📄 Licença
Este projeto foi desenvolvido para fins exclusivamente acadêmicos no contexto do TFM do Master Internacional em IA para Arquitetura e Construção — Zigurat Institute of Technology. Os documentos de projeto utilizados como input (BEP e Memorial Descritivo) são de uso interno acadêmico.
