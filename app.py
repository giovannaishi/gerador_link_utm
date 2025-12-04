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
st.header("1. Link Master")
st.caption("Cole o link parametrizado.")

url_input = st.text_input(
    "URL:",
    placeholder="https://conquer.plus/?utm_campaign=...&utm_content=botao_1-30092025"
)

if not url_input:
    st.info("👆 Aguardando inserção do link...")
    st.stop()

# ==================================================
# 🚨 VALIDAÇÃO, SEGURANÇA E LIMPEZA
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

    # --- 1. VALIDAÇÃO DE SEGURANÇA ---
    if re.search(r'[^a-zA-Z0-9\-_=]', content_original):
        st.error("⛔ **ERRO DE FORMATO:** O parâmetro 'utm_content' contém caracteres inválidos.")
        st.warning("💡 **Permitido apenas:** Letras (a-z), Números (0-9), Hífen (-), Underline (_) e Igual (=).")
        st.stop() 

    # --- 2. LIMPEZA DE BASE (utm_campaign) ---
    # Remove qualquer coisa do final que comece com "_base"
    campanha_atual = campanha_original
    base_removida = None
    
    padrao_base = r'(_base.*)$'
    match_base = re.search(padrao_base, campanha_original, re.IGNORECASE)
    
    if match_base:
        base_removida = match_base.group()
        campanha_atual = re.sub(padrao_base, '', campanha_original, count=1, flags=re.IGNORECASE)

    # --- 3. LIMPEZA DE CONTENT (utm_content) ---
    # REGRA: Manter apenas o sufixo numérico (com ou sem hifen) do final.
    content_atual = content_original
    prefixo_removido = None
    
    match_sufixo = re.search(r'([-]?\d+)$', content_original)
    
    if match_sufixo:
        sufixo_encontrado = match_sufixo.group()
        if content_original != sufixo_encontrado:
            prefixo_removido = content_original.replace(sufixo_encontrado, "")
            content_atual = sufixo_encontrado

    # --- FEEDBACK DE LIMPEZA ---
    if base_removida or prefixo_removido:
        msg = "🧹 **Limpeza Automática Realizada:**"
        if base_removida:
            msg += f"\n- Base antiga removida: **'{base_removida}'**"
        if prefixo_removido:
            msg += f"\n- Prefixo removido do content: **'{prefixo_removido}'**"
        st.warning(msg)
    else:
        st.success("✅ Configurações liberadas!")
    
    st.caption(f"🔧 **Usaremos a** Campanha: `{campanha_atual}` | Sufixo: `{content_atual}`")

except Exception as e:
    st.error(f"⛔ Erro ao ler link: {e}")
    st.stop()

st.markdown("---")

# ==================================================
# 2. CONFIGURAÇÃO
# ==================================================
st.header("2. O que vamos gerar?")

col_bases, col_formatos = st.columns(2)
bases_selecionadas = []

# --- COLUNA 1: BASES ---
with col_bases:
    st.subheader("🅰️ Bases")
    usar_todas = st.checkbox("Selecionar todas as bases oficiais", value=True)
    
    if usar_todas:
        bases_selecionadas = st.multiselect("Bases:", BASES_OFICIAIS, default=BASES_OFICIAIS)
    else:
        bases_selecionadas = st.multiselect("Bases:", BASES_OFICIAIS)
    
    extra = st.text_input("Base extra:", placeholder="Ex: _base_nova")
    if extra: bases_selecionadas.append(extra)

# --- COLUNA 2: FORMATOS ---
with col_formatos:
    st.subheader("🅱️ Formatos e Quantidade")
    
    st.markdown("**Selecione as variações:**")
    gerar_base_link = st.checkbox("Link Base", value=True, help="Gera link com apenas o sufixo (sem botao/imagem/hiperlink).")
    gerar_botoes = st.checkbox("Botões", value=True, help="Adiciona prefixo botao_X")
    gerar_imagens = st.checkbox("Imagens", value=False, help="Adiciona prefixo img_X")
    gerar_hiperlinks = st.checkbox("Hiperlinks", value=False, help="Adiciona prefixo hiperlink_X")
    
    st.markdown("---")
    
    qtd_variacoes = st.number_input("Quantidade de Variações POR BASE:", min_value=1, max_value=100, value=40)
    
    # Texto explicativo atualizado
    total_estimado = len(bases_selecionadas) * qtd_variacoes if bases_selecionadas else 0
    st.info(f"ℹ️ **Modo Multiplicação:** Se você selecionou **{len(bases_selecionadas)} bases** e **{qtd_variacoes} variações**, o sistema gerará **{total_estimado} links** de botões/imagens (mais os links base).")

st.markdown("---")

# ==================================================
# 3. PROCESSAMENTO
# ==================================================
st.header("3. Resultado")

if st.button("🔄 Processar Tudo", type="primary"):
    
    if not bases_selecionadas:
        st.error("⚠️ Você precisa selecionar pelo menos uma base.")
        st.stop()

    resultados = []
    
    # ITERA SOBRE AS BASES (NÍVEL SUPERIOR)
    for base in bases_selecionadas:
        
        # 1. LINK BASE (1 por base)
        if gerar_base_link:
            novos_params = params.copy()
            novos_params['utm_campaign'] = [f"{campanha_atual}{base}"]
            novos_params['utm_content'] = [content_atual] 
            
            nova_query = urllib.parse.urlencode(novos_params, doseq=True)
            link_final = urllib.parse.urlunparse(parsed._replace(query=nova_query))
            
            resultados.append({
                "Grupo": "Links Base",
                "Tipo": "Link Base",
                "Identificador": "Original",
                "Base": base,
                "Link Final": link_final
            })

        # 2. VARIAÇÕES (Multiplica Qtd x Base)
        tipos_ativos = []
        if gerar_botoes: tipos_ativos.append("botao")
        if gerar_imagens: tipos_ativos.append("img")
        if gerar_hiperlinks: tipos_ativos.append("hiperlink")

        if tipos_ativos:
            for tipo in tipos_ativos:
                # Gera de 1 até a Quantidade solicitada PARA ESTA BASE
                for i in range(1, qtd_variacoes + 1):
                    
                    novos_params = params.copy()
                    
                    # Campanha + Base Atual
                    novos_params['utm_campaign'] = [f"{campanha_atual}{base}"]
                    
                    # Content + Prefixo + Sufixo
                    nome_formatado = f"{tipo}_{i}"
                    
                    if content_atual.startswith('-') or content_atual == '':
                        novo_content = f"{nome_formatado}{content_atual}"
                    else:
                        novo_content = f"{nome_formatado}-{content_atual}"
                    
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
        st.success(f"✅ Processo concluído! {len(df)} links gerados.")
        
        cols = ["Tipo", "Identificador", "Base", "Link Final"]
        st.dataframe(df[cols], use_container_width=True)
        
        csv = df.to_csv(index=False, sep=';', encoding='utf-8-sig').encode('utf-8-sig')
        nome = f"Links_Growth_{datetime.now().strftime('%H%M')}.csv"
        
        st.download_button("📥 Baixar Planilha (.csv)", data=csv, file_name=nome, mime="text/csv")
    else:
        st.warning("⚠️ Nenhuma opção selecionada.")
