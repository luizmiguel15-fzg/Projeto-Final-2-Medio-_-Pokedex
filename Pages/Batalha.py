# =============================================================================
# PÁGINA: Batalha   (st.session_state.page == "batalha")
# -----------------------------------------------------------------------------
# Luta do Pokémon do usuário contra um Pokémon selvagem sorteado na PokéAPI.
#
# A página tem DUAS telas, conforme `st.session_state.pokemon_batalha`:
#   - None        -> tela de escolha do Pokémon e botão "Iniciar batalha";
#   - dicionário  -> tela da luta (cartões, ações e histórico).
#
# Aqui fica só a INTERFACE. As regras (cálculo de dano, turnos, vitória e
# derrota) estão em Systems/diversos.py, na seção "LÓGICA DA BATALHA".
#
# Esta página é DESENHADA pela função `renderizar`, chamada pelo Main.py.
# =============================================================================

import streamlit as st

# Regras da batalha e funções de apoio.
from Systems.diversos import (
    apresentar_escrever_erros,
    atacar_inimigo,
    defender_pokemon,
    encerrar_batalha,
    iniciar_batalha,
    mudar_pagina,
)


# =============================================================================
# DESENHO DA PÁGINA
# =============================================================================

def renderizar(lista_poke) -> None:
    """Desenha a página de batalha.

    Parâmetros:
        lista_poke: lista com o nome de todos os Pokémons (PokéAPI), usada
            para sortear o inimigo ao iniciar a batalha.
    """

    st.title("⚔️ Batalha Pokémon")

    POKE = st.session_state.pokemon

    if POKE is None:

        st.warning("Selecione um usuário primeiro.")

    else:

        sucesso, pokemons_usuario, erro = POKE.listar_pokemons()

        if not sucesso:

            apresentar_escrever_erros(erro)
            pokemons_usuario = []

        # Sem Pokémons cadastrados não há como batalhar.
        if not pokemons_usuario:

            st.info("Você precisa cadastrar pelo menos um Pokémon para batalhar.")

            if st.button("Ir para minha Pokédex"):
                mudar_pagina("pokemons")

        else:

            batalha = st.session_state.pokemon_batalha

            # ---- Tela 1: escolher o Pokémon e iniciar -----------------------
            if batalha is None:

                st.subheader("Escolha seu Pokémon")

                # As opções são os próprios registros (tuplas) do banco;
                # `format_func` mostra "Nome - #número" (p[3] = nome,
                # p[2] = número da Pokédex).
                pokemon_escolhido = st.selectbox(
                    "Pokémon:",
                    options=pokemons_usuario,
                    format_func=lambda p: f"{p[3].capitalize()} - #{p[2]}",
                    key="escolher_pokemon_batalha",
                )

                if st.button("⚔️ Iniciar batalha", use_container_width=True):

                    # Monta a batalha: sorteia o inimigo na PokéAPI.
                    sucesso, nova_batalha, erro = iniciar_batalha(
                        pokemon_escolhido, lista_poke
                    )

                    if sucesso:

                        st.session_state.pokemon_batalha = nova_batalha
                        st.rerun()

                    else:
                        apresentar_escrever_erros(erro)

            # ---- Tela 2: batalha em andamento ou finalizada -----------------
            else:

                jogador = batalha["jogador"]
                inimigo = batalha["inimigo"]

                # Dois cartões lado a lado: jogador à esquerda, inimigo à direita.
                col1, col2 = st.columns(2)

                with col1:

                    with st.container(border=True):

                        st.subheader(jogador["nome"].capitalize())

                        if jogador["imagem"] is not None:
                            st.image(jogador["imagem"], width=200)

                        st.caption(f"Tipo: {jogador['tipo']}")

                        # `st.progress` espera um valor de 0.0 a 1.0: aqui é a
                        # fração de vida restante (vida atual / vida máxima).
                        st.progress(max(0, jogador["vida"]) / jogador["vida_max"])

                        st.write(f"❤️ {jogador['vida']} / {jogador['vida_max']} HP")

                        st.write(f"⚔️ Ataque: {jogador['ataque']}")

                with col2:

                    with st.container(border=True):

                        st.subheader(inimigo["nome"].capitalize())

                        # A imagem do inimigo é uma URL da PokéAPI.
                        if inimigo.get("sprite_ataque"):
                            st.image(inimigo["sprite_ataque"], width=200)

                        st.caption(f"Tipo: {inimigo['tipo']}")

                        st.progress(max(0, inimigo["vida"]) / inimigo["vida_max"])

                        st.write(f"❤️ {inimigo['vida']} / {inimigo['vida_max']} HP")

                        # No inimigo, o poder de ataque fica na chave "dano".
                        st.write(f"⚔️ Ataque: {inimigo['dano']}")

                st.divider()

                # Os botões mudam conforme o estado da batalha.
                if batalha["status"] == "em andamento":

                    col1, col2 = st.columns(2)

                    with col1:

                        if st.button("⚔️ Atacar", use_container_width=True):

                            batalha = atacar_inimigo(batalha)

                            st.session_state.pokemon_batalha = batalha
                            st.rerun()

                    with col2:

                        if st.button("🛡️ Defender", use_container_width=True):

                            batalha = defender_pokemon(batalha)

                            st.session_state.pokemon_batalha = batalha
                            st.rerun()

                    # Fugir: descarta a batalha e volta à tela de escolha.
                    if st.button("🏃 Fugir da batalha", use_container_width=True):

                        encerrar_batalha()
                        st.rerun()

                elif batalha["status"] == "vitoria":

                    st.success("🏆 Você venceu a batalha!")

                    if st.button("🔄 Nova batalha", use_container_width=True):

                        encerrar_batalha()
                        st.rerun()

                elif batalha["status"] == "derrota":

                    st.error("💔 Você perdeu a batalha!")

                    if st.button("🔄 Tentar novamente", use_container_width=True):

                        encerrar_batalha()
                        st.rerun()

                st.divider()

                # Histórico da batalha: `reversed` mostra as mensagens mais
                # recentes primeiro.
                with st.expander("📜 Histórico da batalha", expanded=True):

                    for mensagem in reversed(batalha["log"]):

                        st.write(f"• {mensagem}")
