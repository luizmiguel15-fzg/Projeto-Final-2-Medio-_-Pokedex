# =============================================================================
# PÁGINA: Inicio   (st.session_state.page == "inicio")
# -----------------------------------------------------------------------------
# Tela de boas-vindas, exibida logo depois de entrar com um usuário.
# É a página mais simples: apenas título, legenda e um banner.
#
# Esta página é DESENHADA pela função `renderizar`, chamada pelo Main.py.
# =============================================================================

import streamlit as st


# =============================================================================
# DESENHO DA PÁGINA
# =============================================================================

def renderizar() -> None:
    """Desenha a tela de boas-vindas (título, legenda e banner)."""

    st.title("Bem-vindo à Pokédex")
    st.caption("Guarde, consulte e lute com seus Pokémons favoritos.")

    # `width="stretch"` estica a imagem para ocupar toda a largura disponível.
    # O caminho é RELATIVO: o programa deve ser executado a partir da pasta
    # raiz do projeto (a que contém a pasta IMGs).
    st.image("IMGs/Banner_inicio.avif", width="stretch")
