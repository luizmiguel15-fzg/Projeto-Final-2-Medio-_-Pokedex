# =============================================================================
# PÁGINA: Cadastro   (st.session_state.page == "Cadastro")
# -----------------------------------------------------------------------------
# Tela de criação de um novo "mestre Pokémon" (usuário).
#
# Quando aparece:
#   - na primeira execução do sistema, quando o banco ainda não tem nenhum
#     usuário (o Main.py força esta página);
#   - quando o usuário clica em "Criar novo usuário" na página de seleção.
#
# Esta página é DESENHADA pela função `renderizar`, chamada pelo Main.py.
# =============================================================================

import streamlit as st

# Funções de apoio: recarregar a lista de usuários, ativar um usuário na
# sessão e mostrar/registrar erros.
from Systems.diversos import (
    apresentar_escrever_erros,
    ativar_usuario,
    atualizar_lista_usuarios,
)


# =============================================================================
# DESENHO DA PÁGINA
# =============================================================================

def renderizar(USU) -> None:
    """Desenha o formulário de cadastro de usuário.

    Parâmetros:
        USU: objeto `Usuario` (Classes/Usuario.py), usado para gravar o novo
            usuário no banco.

    Fluxo ao clicar em "Cadastrar":
        1. Valida que o nome não está vazio.
        2. Grava o usuário no banco (nome com cada palavra capitalizada).
        3. Se deu certo: recarrega a lista de usuários, ativa o novo usuário
           (o que leva para a página "inicio") e reexecuta o script.
        4. Se falhou: mostra o erro e o registra no arquivo de logs.
    """

    st.title("Pokédex")
    st.caption("Guarde, consulte e lute com seus Pokémons favoritos.")
    st.divider()

    st.subheader("Cadastro de mestre Pokémon")

    nome = st.text_input(
        "Digite seu nome de mestre Pokémon *",
        key="nome_usuario",
        placeholder="Ash Ketchum",
    )

    if st.button("Cadastrar", key="btn_cadastrar_usuario"):
        if not nome.strip():
            st.error("Digite um nome antes de realizar o cadastro.")
        else:
            # `.title()` deixa a primeira letra de cada palavra maiúscula
            # ("ash ketchum" -> "Ash Ketchum").
            sucesso, novo_usuario_id, erro = USU.cadastro_mestre_pokemon(nome.title())

            if sucesso and novo_usuario_id is not None:
                # Recarrega a lista, ativa o novo usuário e o marca como
                # selecionado nas caixas de seleção.
                atualizar_lista_usuarios()
                ativar_usuario(novo_usuario_id)
                st.session_state.usuario_selecionado = novo_usuario_id
                st.success("Usuário cadastrado com sucesso!")
                st.rerun()
            else:
                apresentar_escrever_erros(
                    erro or "Não foi possível cadastrar o usuário."
                )
