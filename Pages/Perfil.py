# =============================================================================
# PÁGINA: Perfil   (st.session_state.page == "perfil")
# -----------------------------------------------------------------------------
# Tela do usuário ativo: mostra a foto e o nome, e permite trocar a foto,
# trocar o nome e EXCLUIR a conta.
#
# Organização do arquivo:
#   1. DIÁLOGO  -> confirmar_exclusao (confirmação de exclusão da conta)
#   2. DESENHO DA PÁGINA -> renderizar (chamada pelo Main.py)
#
# FOTO CIRCULAR: a foto do topo e a pré-visualização da nova foto ficam dentro
# de containers com `key="perfil_topo"` e `key="perfil_preview"`. O Streamlit
# transforma cada key em uma classe CSS (`st-key-perfil_topo`,
# `st-key-perfil_preview`), e o style.css (pasta raiz do projeto) usa essas
# classes para cortar a imagem em círculo. Se mudar uma key aqui, mude também a
# classe correspondente no style.css. O style.css só é aplicado porque o
# Main.py chama `carregar_css()`.
# =============================================================================

import streamlit as st

# Funções de apoio: mostrar/registrar erros, ativar um usuário na sessão e
# recarregar a lista de usuários do banco.
from Systems.diversos import (
    apresentar_escrever_erros,
    ativar_usuario,
    atualizar_lista_usuarios,
)


# =============================================================================
# 1. DIÁLOGO: EXCLUIR CONTA
# =============================================================================

@st.dialog("Excluir conta")
def confirmar_exclusao(USU):
    """Janela de confirmação para excluir a conta do usuário ativo.

    Parâmetros:
        USU: objeto `Usuario` (Classes/Usuario.py), usado para apagar no banco.

    A exclusão remove o usuário E todos os Pokémons dele (veja
    `Usuario.deletar_usuario`).

    Após a exclusão bem-sucedida:
        - se ainda existirem outros usuários, ativa automaticamente o primeiro
          da lista;
        - se NÃO sobrar nenhum, limpa os dados da sessão e leva para a página
          de "Cadastro".
    """

    st.warning(
        "Tem certeza de que deseja excluir sua conta? "
        "Todos os seus Pokémons cadastrados também serão excluídos. "
        "Essa ação não pode ser desfeita."
    )

    col1, col2 = st.columns(2)

    with col1:
        # Cancelar: apenas reexecuta o script, o que fecha a janela.
        if st.button("Cancelar", use_container_width=True):
            st.rerun()

    with col2:
        if st.button("Excluir conta", type="primary", use_container_width=True):

            sucesso, msg, erro = USU.deletar_usuario(st.session_state.usuario_id)

            if sucesso:
                # Recarrega a lista de usuários do banco (já sem o excluído).
                atualizar_lista_usuarios()
                st.success(msg)

                # Ainda há usuários: ativa o primeiro da lista e recarrega.
                if len(st.session_state.usuarios) >= 1:
                    ativar_usuario(st.session_state.usuarios[0][0])
                    st.rerun()

                # Não sobrou ninguém: limpa a sessão e vai ao cadastro.
                st.session_state.usuario_id = None
                st.session_state.usuario_nome = None
                st.session_state.img_perfil = None
                st.session_state.pokemon = None

                st.session_state.page = "Cadastro"

                st.rerun()

            else:
                apresentar_escrever_erros(erro)


# =============================================================================
# 2. DESENHO DA PÁGINA
# =============================================================================

def renderizar(USU) -> None:
    """Desenha a página de perfil.

    Parâmetros:
        USU: objeto `Usuario` (Classes/Usuario.py), usado para atualizar a
            foto/nome e para excluir a conta.
    """

    # Foto de perfil e saudação na mesma linha, centralizadas verticalmente.
    # `key="perfil_topo"` faz o Streamlit criar a classe `st-key-perfil_topo`,
    # que o style.css usa para deixar a foto CIRCULAR.
    with st.container(
        horizontal=True, vertical_alignment="center", gap="medium", key="perfil_topo"
    ):

        st.image(st.session_state.img_perfil, width=120)
        st.title(f"Olá {st.session_state.usuario_nome}")

    st.divider()

    # ---- Trocar a imagem de perfil -------------------------------------------
    with st.expander("Mudar imagem de perfil"):

        arquivo = st.file_uploader(
            "Selecione uma imagem",
            type=["png", "jpg", "jpeg", "avif"],
            key="nova_imagem_perfil",
            max_upload_size=32,
            accept_multiple_files=False,
        )

        # Só mostra a pré-visualização e o botão depois que um arquivo é escolhido.
        if arquivo is not None:
            # Pré-visualização maior (350 px) que a foto do topo da página (120 px).
            # Dentro do container com `key="perfil_preview"` ela também fica
            # CIRCULAR (regra no style.css), mostrando como a foto será cortada.
            with st.container(key="perfil_preview"):
                st.image(arquivo, width=350)

            if st.button("Salvar nova imagem", key="salvar_imagem"):

                sucesso, msg_sucesso, erro = USU.atualizar_usuario(
                    st.session_state.usuario_id, nova_img=arquivo
                )

                if sucesso:
                    # Atualiza a cópia da foto guardada na sessão (é ela que o
                    # topo desta página desenha), sem precisar ir ao banco.
                    st.session_state.img_perfil = arquivo.getvalue()
                    st.success(msg_sucesso)

                    # Recarrega a lista de usuários do banco: ela guarda a foto
                    # de cada usuário e ficaria com a foto antiga ao trocar de
                    # usuário pelo menu lateral.
                    atualizar_lista_usuarios()
                    st.rerun()

                else:
                    apresentar_escrever_erros(erro)

    # ---- Trocar o nome do perfil ---------------------------------------------
    with st.expander("Mudar nome do perfil"):

        novo_nome = st.text_input(
            "Digite seu novo nome",
            value=st.session_state.usuario_nome,
            key="novo_nome_perfil",
        )

        if st.button("Salvar novo nome", key="salvar_nome"):

            if not novo_nome:
                st.error("O nome não pode ficar vazio.")

            else:
                # `.strip()` remove espaços extras e `.title()` capitaliza cada palavra.
                sucesso, msg_sucesso, erro = USU.atualizar_usuario(
                    st.session_state.usuario_id, novo_nome=novo_nome.strip().title()
                )

                if sucesso:
                    # Atualiza o nome guardado na sessão (usado no menu lateral
                    # e na saudação "Olá ...").
                    st.session_state.usuario_nome = novo_nome.strip().title()
                    st.success(msg_sucesso)

                    # Recarrega a lista de usuários do banco: sem isso as caixas
                    # de seleção de usuário continuariam mostrando o nome antigo.
                    atualizar_lista_usuarios()
                    st.rerun()

                else:
                    apresentar_escrever_erros(erro)

    # ---- Excluir a conta -----------------------------------------------------
    # Abre o diálogo de confirmação (seção 1 deste arquivo).
    if st.button("Excluir Conta", type="primary", use_container_width=True):
        confirmar_exclusao(USU)
