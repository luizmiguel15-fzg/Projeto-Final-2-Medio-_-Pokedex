# =============================================================================
# MÓDULO: menu_lateral.py
# -----------------------------------------------------------------------------
# Barra lateral (menu) da Pokédex, exibida enquanto há um usuário ativo.
# Reúne: botões de navegação entre as páginas, troca rápida de usuário e o
# botão de sair.
#
# É chamada pelo Main.py a cada execução do script.
# =============================================================================

import streamlit as st

# `mudar_pagina` troca a página e reexecuta o script; `trocar_usuario` é o
# callback da caixa "Trocar usuário".
from Systems.diversos import mudar_pagina, trocar_usuario


# =============================================================================
# DESENHO DO MENU
# =============================================================================

def desenhar_menu_lateral(usuarios, ids_usuarios) -> None:
    """Desenha a barra lateral com a navegação e as opções de usuário.

    Parâmetros:
        usuarios: lista de usuários do banco (tuplas
            `(id, nome, imagem_binaria_perfil, imagem_tipo_mime)`).
        ids_usuarios: lista só com os IDs, na mesma ordem de `usuarios`.

    Deve ser chamada apenas quando `st.session_state.usuario_id` não é None.
    """

    with st.sidebar:
        st.title("Menu")
        st.caption("Navegue entre as páginas da Pokédex.")

        st.write(f"Usuário: **{st.session_state.usuario_nome}**")

        # ---- Botões de navegação ---------------------------------------------
        # Cada um chama `mudar_pagina`, que troca a página e reexecuta o script.
        # Os nomes entre aspas são as chaves das páginas registradas no Main.py.
        if st.button("Início", use_container_width=True):
            mudar_pagina("inicio")

        if st.button("Pokémons", use_container_width=True):
            mudar_pagina("pokemons")

        if st.button("Batalha", use_container_width=True):
            mudar_pagina("batalha")

        if st.button("Perfil", use_container_width=True):
            mudar_pagina("perfil")

        st.divider()

        # ---- Troca rápida de usuário -----------------------------------------
        # Só faz sentido com 2 ou mais usuários. `on_change=trocar_usuario`
        # ativa o usuário assim que a opção muda.
        if len(usuarios) > 1:
            nomes_por_id = {usuario[0]: usuario[1] for usuario in usuarios}

            st.selectbox(
                "Trocar usuário:",
                options=ids_usuarios,
                format_func=lambda usuario_id: nomes_por_id[usuario_id],
                key="usuario_selecionado",
                on_change=trocar_usuario,
            )

        # ---- Sair ------------------------------------------------------------
        # Desativa o usuário atual e abre a tela de seleção de perfil.
        if st.button("Sair / trocar perfil", use_container_width=True):
            st.session_state.usuario_id = None
            st.session_state.usuario_nome = None
            st.session_state.pokemon = None
            st.session_state.img_perfil = None
            st.session_state.page = "selecionar_usuario"
            st.rerun()
