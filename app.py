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

# Lista Oficial de Bases
BASES_OFICIAIS = [
    "_base_campanhas_antigas", "_base_produtividade_inteligente", "_base_estrategias_digitais",
    "_base_liberacao_oratoria", "_base_intensivo_bia", "_base_gc_conquer_talks",
    "_base_liberacao_sinal_plus", "_base_conquer_carreiras", "_base_gp_minicurso",
    "_base_campanhas_varejo", "_base_lib_de_ia", "_base_liberacao_apresentacoes_que_conquistam",
    "_base_liberacao_lideranca", "_base_inteligencia_emocional", "_base_liberacao_foco",
    "_base_mba_neurociencia", "_base_liberacao_em_vendas", "_base_desengajadas"
]

st.title("🚀 Gerador de Links Parametrizados")
st.markdown("---")

# ==================================================
# 1. INPUT DO LINK
# ==================================================
st.header("1. Link Master")
st.caption("Cole o link parametrizado aqui")

url_input = st.text_input(
    "URL:",
    placeholder="https://conquer.plus/?utm_campaign=...&utm_content=botao_1-3009"
)

if not url_input:
    st.info("👆 Aguardando inserção do link...")
    st.stop()

# ==================================================
# 🚨 VALIDAÇÃO, SEGURANÇA E LIMPEZA
# ==================================================
# 1. Validação Básica de URL
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

    # --- NOVO: VALIDAÇÃO RÍGIDA DE CARACTERES ---
    # Regex: Procura por qualquer caracter que NÃO seja letra, número, hifen, underline ou igual.
    # Se encontrar, bloqueia.
    if re.search(r'[^a-zA-Z0-9\-_=]', content_original):
        st.error("⛔ **ERRO DE FORMATO:** O parâmetro 'utm_content' contém caracteres inválidos.")
        st.warning("💡 **Permitido apenas:** Letras (a-z), Números (0-9), Hífen (-), Underline (_) e Igual (=).")
        st.caption(f"Conteúdo encontrado: {content_original}")
        st.stop() # Trava o script aqui

    # --- 2. LIMPEZA DE BASE (utm_campaign) ---
    campanha_atual = campanha_original
    base_removida = None
    
    for base in sorted(BASES_OFICIAIS, key=len, reverse=True):
        if campanha_original.endswith(base):
            campanha_atual = campanha_original.replace(base, "")
            base_removida = base
            break 

    # --- 3. LIMPEZA DE FORMATO (utm_content) ---
    padrao_sujo = r'^(botao|img|hiperlink)[-_]?\d+'
    match_sujo = re.search(padrao_sujo, content_original, re.IGNORECASE)
    
    content_atual = content_original
    item_removido = None
    
    if match_sujo:
        item_removido = match_sujo.group()
        content_atual = re.sub(padrao_sujo, '', content_original, count=1)

    # --- FEEDBACK DE LIMPEZA ---
    if base_removida or item_removido:
        msg = "🧹 **Limpeza Automática Realizada:**"
        if base_removida:
            msg += f"\n- Base removida: **'{base_removida}'**"
        if item_removido:
            msg += f"\n- Formato removido: **'{item_removido}'**"
        
        st.warning(msg)
        st.caption(f"Usaremos a campanha base: **{campanha_atual}** e o sufixo: **{content_atual}**")
    else:
        st.success("✅Configurações liberadas!")

except Exception as e:
    st.error(f"⛔ Erro ao ler link: {e}")
    st.stop()

st.markdown("---")

# ==================================================
# 2. CONFIGURAÇÃO
# ==================================================
st.header("2. O que vamos gerar?")

col_bases, col_formatos = st.columns(2)

# Variáveis globais de controle
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
    
    st.markdown("**Tipos de Link:**")
    gerar_base_link = st.checkbox("Link Base (Limpo)", value=True, help="Gera 1 link original (já limpo) para cada base selecionada.")
    gerar_botoes = st.checkbox("Botões", value=True, help="Gera botao_1, botao_2...")
    gerar_imagens = st.checkbox("Imagens", value=False)
    gerar_hiperlinks = st.checkbox("Hiperlinks", value=False)
    
    st.markdown("---")
    
    # LÓGICA DA QUANTIDADE
    qtd_variacoes = st.number_input("Quantidade Total de Links (para Botões/Imagens/hiperlinks):", min_value=1, max_value=200, value=40)
    
    st.info(f"ℹ️ **Lógica de Distribuição:**\n"
            f"Se você pedir **{qtd_variacoes} botões** e tiver **{len(bases_selecionadas) if bases_selecionadas else 0} bases**:\n"
            f"O sistema distribui as bases sequencialmente nos links (Base 1 -> Botão 1, Base 2 -> Botão 2... Base 1 -> Botão 19).")

st.markdown("---")

# ==================================================
# 3. PROCESSAMENTO (COM DADOS LIMPOS)
# ==================================================
st.header("3. Resultado")

if st.button("🔄 Processar Tudo", type="primary"):
    
    if not bases_selecionadas:
        st.error("⚠️ Você precisa selecionar pelo menos uma base.")
        st.stop()

    resultados = []
    total_bases = len(bases_selecionadas)
    
    # -----------------------------------------------------------
    # 1. LINK BASE (Gera estritamente 1 para cada base selecionada)
    # -----------------------------------------------------------
    if gerar_base_link:
        for base in bases_selecionadas:
            novos_params = params.copy()
            # Usa a campanha LIMPA + Base nova
            novos_params['utm_campaign'] = [f"{campanha_atual}{base}"]
            # Usa o content LIMPO
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

    # -----------------------------------------------------------
    # 2. FORMATOS NUMERADOS (Botões, Imagens, Hiperlinks)
    # -----------------------------------------------------------
    tipos_ativos = []
    if gerar_botoes: tipos_ativos.append("botao")
    if gerar_imagens: tipos_ativos.append("img")
    if gerar_hiperlinks: tipos_ativos.append("hiperlink")

    if tipos_ativos:
        for tipo in tipos_ativos:
            # Loop da Quantidade Solicitada (ex: 1 até 40)
            for i in range(1, qtd_variacoes + 1):
                
                # LÓGICA CÍCLICA
                indice_base = (i - 1) % total_bases
                base_da_vez = bases_selecionadas[indice_base]
                
                novos_params = params.copy()
                
                # Monta Campanha (Limpa + Base da vez)
                novos_params['utm_campaign'] = [f"{campanha_atual}{base_da_vez}"]
                
                # Monta Content Numerado (Prefixo + Content Limpo)
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
                    "Base": base_da_vez,
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
