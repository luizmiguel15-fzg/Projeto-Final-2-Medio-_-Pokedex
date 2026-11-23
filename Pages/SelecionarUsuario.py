# =============================================================================
# PÁGINA: SelecionarUsuario   (st.session_state.page == "selecionar_usuario")
# -----------------------------------------------------------------------------
# Tela para escolher qual perfil (usuário) usar.
#
# Quando aparece: depois de clicar em "Sair / trocar perfil" na barra lateral
# (que desativa o usuário atual e vem para cá).
#
# Esta página é DESENHADA pela função `renderizar`, chamada pelo Main.py.
# =============================================================================

import streamlit as st

# Coloca o usuário escolhido como ativo na sessão.
from Systems.diversos import ativar_usuario


# =============================================================================
# DESENHO DA PÁGINA
# =============================================================================

def renderizar(usuarios, ids_usuarios) -> None:
    """Desenha a caixa de seleção de usuário e os botões "Entrar" / "Criar".

    Parâmetros:
        usuarios: lista de usuários do banco (tuplas
            `(id, nome, imagem_binaria_perfil, imagem_tipo_mime)`).
        ids_usuarios: lista só com os IDs, na mesma ordem de `usuarios`.
    """

    st.title("Selecionar usuário")
    st.caption("Escolha o perfil que deseja utilizar.")

    if usuarios:
        # Dicionário {id: nome}, para mostrar o NOME na caixa de seleção
        # enquanto o valor escolhido continua sendo o ID.
        nomes_por_id = {usuario[0]: usuario[1] for usuario in usuarios}

        usuario_escolhido = st.selectbox(
            "Usuário:",
            options=ids_usuarios,
            format_func=lambda usuario_id: nomes_por_id[usuario_id],
            key="usuario_selecionado",
        )

        if st.button("Entrar"):
            ativar_usuario(usuario_escolhido)
            st.rerun()

    if st.button("Criar novo usuário"):
        st.session_state.page = "Cadastro"
        st.rerun()
