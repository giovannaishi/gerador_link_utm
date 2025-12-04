import streamlit as st
import pandas as pd
import urllib.parse
import re
from datetime import datetime
from io import BytesIO

# ==================================================
# CONFIGURAÇÃO INICIAL
# ==================================================
st.set_page_config(page_title="Gerador de Links Growth", layout="wide")

# Lista Oficial de Bases (Ordenada)
BASES_OFICIAIS = [
    "_base_bootcamp_ia",
    "_base_c04_minicurso_master",
    "_base_c05_mother_reset",
    "_base_campanhas_antigas",
    "_base_campanhas_varejo",
    "_base_conquer_carreiras",
    "_base_desengajadas",
    "_base_estrategias_digitais",
    "_base_gc_conquer_talks",
    "_base_gp_minicurso",
    "_base_inteligencia_emocional",
    "_base_intensivo_bia",
    "_base_lab_lid",
    "_base_lib_de_ia",
    "_base_liberacao_apresentacoes_que_conquistam",
    "_base_liberacao_carisma",
    "_base_liberacao_em_vendas",
    "_base_liberacao_foco",
    "_base_liberacao_lideranca",
    "_base_liberacao_oratoria",
    "_base_liberacao_pos_de_iagel",
    "_base_liberacao_sinal_plus",
    "_base_lideranca",
    "_base_mba_neurociencia",
    "_base_ongoing_unificada",
    "_base_oratoria",
    "_base_produtividade_inteligente"
]
BASES_OFICIAIS.sort()

st.title("🚀 Gerador de Links Parametrizados")
st.markdown("---")

# ==================================================
# 1. INPUT DO LINK
# ==================================================
# st.header("1. Link Master") # Removi o header para ficar mais limpo como no print
st.subheader("Cole o link parametrizado inicial aqui:")

url_input = st.text_input(
    "URL:",
    label_visibility="collapsed",
    placeholder="https://conquer.plus/?utm_campaign=...&utm_content=botao_1-30092025"
)

if not url_input:
    st.info("👆 Aguardando inserção do link...")
    st.stop()

# ==================================================
# 🚨 VALIDAÇÃO, SEGURANÇA E PREPARAÇÃO
# ==================================================
if " " in url_input:
    st.error("⛔ **ERRO:** O link contém espaços em branco. Remova-os.")
    st.stop()

if not url_input.startswith(("http://", "https://")):
    st.error("⛔ **ERRO:** O link deve começar com 'http://' ou 'https://'.")
    st.stop()

try:
    parsed = urllib.parse.urlparse(url_input)
    params = urllib.parse.parse_qs(parsed.query)
    
    campanha_original = params.get('utm_campaign', [''])[0]
    content_original = params.get('utm_content', [''])[0]
    
    if not campanha_original:
        st.error("⛔ **ERRO:** Faltou 'utm_campaign'.")
        st.stop()

    if not content_original:
        st.error("⛔ **ERRO:** Faltou 'utm_content'.")
        st.stop()

    # 1. Validação de Caracteres
    if re.search(r'[^a-zA-Z0-9\-_=]', content_original):
        st.error("⛔ **ERRO DE FORMATO:** O parâmetro 'utm_content' contém caracteres inválidos.")
        st.stop() 

    # 2. Limpeza da Base (utm_campaign)
    campanha_limpa = campanha_original
    base_removida = None
    padrao_base = r'(_base.*)$'
    match_base = re.search(padrao_base, campanha_original, re.IGNORECASE)
    
    if match_base:
        base_removida = match_base.group()
        campanha_limpa = re.sub(padrao_base, '', campanha_original, count=1, flags=re.IGNORECASE)

    # 3. Preparação do Sufixo (para Botões/Imagens novos)
    content_sufixo = content_original
    match_sufixo = re.search(r'([-]?\d+)$', content_original)
    if match_sufixo:
        content_sufixo = match_sufixo.group()

    # Feedback discreto
    if base_removida:
        st.caption(f"✅ Base antiga removida. Usando campanha base: **{campanha_limpa}**")
    else:
        st.caption("✅ Configurações liberadas.")

except Exception as e:
    st.error(f"⛔ Erro ao ler link: {e}")
    st.stop()

st.markdown("---")

# ==================================================
# 2. CONFIGURAÇÃO (LAYOUT IDÊNTICO À IMAGEM)
# ==================================================
col_bases, col_formatos = st.columns(2)
bases_selecionadas = []

# --- COLUNA 1: BASES ---
with col_bases:
    st.header("🅰️ Bases")
    usar_todas = st.checkbox("Selecionar todas as bases oficiais", value=True)
    
    if usar_todas:
        bases_selecionadas = st.multiselect("Bases:", BASES_OFICIAIS, default=BASES_OFICIAIS)
    else:
        bases_selecionadas = st.multiselect("Bases:", BASES_OFICIAIS)
    
    extra = st.text_input("Base extra:", placeholder="Ex: _base_nova")
    if extra: bases_selecionadas.append(extra)

# --- COLUNA 2: FORMATOS ---
with col_formatos:
    st.header("🅱️ Formatos e Quantidade")
    
    st.markdown("**Selecione as variações:**")
    
    # Checkboxes com tooltips (?)
    gerar_base_link = st.checkbox("Link Base", value=True, help="Mantém o conteúdo original e apenas troca a base.")
    gerar_botoes = st.checkbox("Botões", value=True, help="Gera novos botões sequenciais (botao_1...)")
    gerar_imagens = st.checkbox("Imagens", value=False, help="Gera novas imagens sequenciais (img_1...)")
    gerar_hiperlinks = st.checkbox("Hiperlinks", value=False, help="Gera novos hiperlinks sequenciais (hiperlink_1...)")
    
    st.markdown("---")
    
    st.markdown("**Quantidade de Variações POR BASE:**")
    qtd_variacoes = st.number_input("Qtd", min_value=1, max_value=200, value=40, label_visibility="collapsed")
    
    # Cálculo para o Box Azul
    total_estimado = 0
    if bases_selecionadas:
        links_por_base = 0
        if gerar_base_link: links_por_base += 1
        if gerar_botoes: links_por_base += qtd_variacoes
        if gerar_imagens: links_por_base += qtd_variacoes
        if gerar_hiperlinks: links_por_base += qtd_variacoes
        total_estimado = len(bases_selecionadas) * links_por_base

    st.info(f"ℹ️ **Modo Multiplicação:** Se você selecionou **{len(bases_selecionadas)} bases** e **{qtd_variacoes} variações**, o sistema gerará **{total_estimado} links** no total.")

st.markdown("---")

# ==================================================
# 3. PROCESSAMENTO
# ==================================================
# Botão grande
if st.button("🔄 Processar Tudo", type="primary", use_container_width=True):
    
    if not bases_selecionadas:
        st.error("⚠️ Selecione pelo menos uma base.")
        st.stop()

    resultados = []
    
    # Itera sobre cada Base Selecionada
    for base in bases_selecionadas:
        
        # A) LINK BASE (Preserva Original)
        if gerar_base_link:
            novos_params = params.copy()
            novos_params['utm_campaign'] = [f"{campanha_limpa}{base}"]
            novos_params['utm_content'] = [content_original] # Intacto
            
            nova_query = urllib.parse.urlencode(novos_params, doseq=True)
            link_final = urllib.parse.urlunparse(parsed._replace(query=nova_query))
            
            resultados.append({
                "Grupo": "Links Base",
                "Tipo": "Link Base",
                "Identificador": "Original",
                "Base": base,
                "Link Final": link_final
            })

        # B) VARIAÇÕES (Gera Novos usando Sufixo)
        tipos_ativos = []
        if gerar_botoes: tipos_ativos.append("botao")
        if gerar_imagens: tipos_ativos.append("img")
        if gerar_hiperlinks: tipos_ativos.append("hiperlink")

        if tipos_ativos:
            for tipo in tipos_ativos:
                for i in range(1, qtd_variacoes + 1):
                    
                    novos_params = params.copy()
                    novos_params['utm_campaign'] = [f"{campanha_limpa}{base}"]
                    
                    nome_formatado = f"{tipo}_{i}"
                    
                    if content_sufixo.startswith('-') or content_sufixo == '':
                        novo_content = f"{nome_formatado}{content_sufixo}"
                    else:
                        novo_content = f"{nome_formatado}-{content_sufixo}"
                    
                    novos_params['utm_content'] = [novo_content]
                    
                    nova_query = urllib.parse.urlencode(novos_params, doseq=True)
                    link_final = urllib.parse.urlunparse(parsed._replace(query=nova_query))
                    
                    resultados.append({
                        "Grupo": f"{tipo.capitalize()}s",
                        "Tipo": tipo.capitalize(),
                        "Identificador": nome_formatado,
                        "Base": base,
                        "Link Final": link_final
                    })

    # EXIBIÇÃO
    if resultados:
        df = pd.DataFrame(resultados)
        st.success(f"✅ Sucesso! {len(df)} links gerados.")
        
        cols = ["Tipo", "Identificador", "Base", "Link Final"]
        st.dataframe(df[cols], use_container_width=True)
        
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        nome = f"Links_Growth_{datetime.now().strftime('%H%M')}.csv"
        
        st.download_button("📥 Baixar Planilha (.csv)", data=csv, file_name=nome, mime="text/csv")
    else:
        st.warning("⚠️ Nenhuma opção selecionada.")
