# =============================================================================
# PÁGINA: Pokemons   (st.session_state.page == "pokemons")
# -----------------------------------------------------------------------------
# "Minha Pokédex": lista os Pokémons do usuário ativo em cartões e permite
# CADASTRAR novos Pokémons, EDITAR e EXCLUIR os existentes.
#
# Organização do arquivo:
#   1. DIÁLOGOS (janelas modais)
#        1.1 modal_cadastrar_pokemon
#        1.2 modal_editar_pokemon
#        1.3 modal_excluir_pokemon
#   2. PESQUISA
#        limpar_pesquisa  (botão "Limpar pesquisa")
#   3. DESENHO DA PÁGINA
#        renderizar  (chamada pelo Main.py)
#
# PESQUISA: dentro do expander "Pesquisar Meus Pokémons" o usuário filtra os
# cartões por parte do nome e/ou número da Pokédex. A consulta é feita por
# `Pokemon.buscar_pokemons` (Classes/Pokemon.py) e os cartões são desenhados por
# `imprimir_card_pokemon` (Systems/diversos.py, seção 6) — a MESMA função que
# desenha a lista completa, só que recebendo a lista filtrada.
#
# Os diálogos recebem tudo de que precisam POR PARÂMETRO (o objeto `Pokemon`,
# a lista de nomes, o registro editado) — não dependem de variáveis globais.
#
# VISUAL DO CARTÃO DO POKÉMON (desenhado por `imprimir_card_pokemon`, em
# Systems/diversos.py):
#   - dados à esquerda e imagem à direita (duas colunas 3:2); a descrição fica
#     embaixo, em largura total;
#   - os badges de tipo (com ícone) e os chips de Vida/Ataque/Altura/Peso são
#     HTML criado por Systems/estilos.py e pintado pelo style.css (na pasta
#     raiz). Para isso funcionar, o Main.py precisa chamar `carregar_css()`.
# =============================================================================

import streamlit as st

# Constantes compartilhadas: limite de Pokémons por usuário e lista de tipos.
from Systems.constantes import LIMITE_POKEMONS, TIPOS_POKEMON

# Mostra o erro na tela e o registra no arquivo de logs.
from Systems.diversos import apresentar_escrever_erros, imprimir_card_pokemon


# =============================================================================
# 1. DIÁLOGOS (JANELAS MODAIS)
# -----------------------------------------------------------------------------
# `@st.dialog` transforma a função em uma janela flutuante (modal) por cima da
# página. Ela só aparece quando a função é CHAMADA (pela `renderizar`, mais
# abaixo, enquanto o "interruptor" correspondente de st.session_state estiver
# ligado).
# =============================================================================


# -----------------------------------------------------------------------------
# 1.1 DIÁLOGO: CADASTRAR NOVO POKÉMON
# -----------------------------------------------------------------------------

@st.dialog("Cadastrar novo Pokémon")
def modal_cadastrar_pokemon(POKE, lista_poke):
    """Janela com o formulário para cadastrar um novo Pokémon.

    Parâmetros:
        POKE: objeto `Pokemon` do usuário ativo (grava no banco).
        lista_poke: lista com o nome de todos os Pokémons (vinda da PokéAPI),
            usada nas opções da caixa "Nome do Pokémon".

    Campos obrigatórios: número da Pokédex, nome e tipo principal.
    Campos opcionais: tipo secundário, altura, peso, vida, ataque, habilidade
    e descrição. Valores 0 (ou texto vazio) são enviados como None, o que
    grava NULL no banco.

    Botões:
        - Cancelar: fecha a janela.
        - Cadastrar: valida, chama `POKE.guardar_dados(...)` e, se der certo,
          fecha a janela e atualiza a página. O limite de Pokémons por usuário
          é verificado dentro de `guardar_dados`.
    """

    st.write("Preencha os dados do Pokémon que deseja adicionar.")

    # `key` dá um identificador único a cada campo, para o Streamlit lembrar
    # o valor digitado entre as reexecuções do script.
    numero_pokedex = st.number_input(
        "Número da Pokédex", min_value=1, step=1, value=1, key="cad_numero"
    )

    # Caixa de seleção com todos os nomes vindos da PokéAPI.
    # `format_func` só muda o texto exibido (primeira letra maiúscula); o valor
    # escolhido continua sendo o nome original em minúsculas.
    nome = st.selectbox(
        "Nome do Pokémon",
        options=lista_poke,
        format_func=lambda nome: nome.capitalize(),
        key="cad_nome",
    )

    # O "" inicial obriga o usuário a escolher um tipo (validado mais abaixo).
    tipo1 = st.selectbox("Tipo principal", [""] + TIPOS_POKEMON, key="cad_tipo1")

    # "Nenhum" representa a ausência de tipo secundário.
    tipo2 = st.selectbox(
        "Tipo secundário", ["Nenhum"] + TIPOS_POKEMON, key="cad_tipo2"
    )

    altura = st.number_input(
        "Altura (m)", min_value=0.0, value=0.0, step=0.1, key="cad_altura"
    )

    peso = st.number_input(
        "Peso (kg)", min_value=0.0, value=0.0, step=0.1, key="cad_peso"
    )

    vida = st.number_input("Vida", min_value=0, value=0, key="cad_vida")

    ataque = st.number_input("Ataque", min_value=0, value=0, key="cad_ataque")

    habilidade = st.text_input("Habilidade", key="cad_habilidade")

    descricao = st.text_area("Descrição", key="cad_descricao")

    # Dois botões lado a lado, em duas colunas.
    col1, col2 = st.columns(2)

    with col1:

        if st.button("Cancelar", key="cancelar_cadastro", use_container_width=True):

            # Desliga o "interruptor" que mantém o diálogo aberto e recarrega.
            st.session_state.abrir_cadastro = False
            st.rerun()

    with col2:

        if st.button("Cadastrar", key="enviar_cadastro", use_container_width=True):

            # ---- Validações antes de enviar ao banco -------------------------
            if not nome.strip():
                st.warning("Informe o nome do Pokémon.")

            elif numero_pokedex <= 0:
                st.warning("Informe um número válido da Pokédex.")

            elif not tipo1:
                st.warning("Selecione o tipo principal.")

            else:

                # Converte os valores da tela para o formato esperado pelo banco:
                #   - "Nenhum" -> None; 0 ou vazio -> None (vira NULL).
                sucesso, mensagem, erro = POKE.guardar_dados(
                    numero_pokedex=int(numero_pokedex),
                    nome=nome.strip().lower(),
                    tipo_primario=tipo1,
                    tipo_secuntario=None if tipo2 == "Nenhum" else tipo2,
                    altura=altura if altura > 0 else None,
                    peso=peso if peso > 0 else None,
                    vida=vida if vida > 0 else None,
                    ataque=ataque if ataque > 0 else None,
                    habilidade=habilidade if habilidade else None,
                    descricao=descricao if descricao else None,
                )

                if sucesso:

                    st.success(mensagem)
                    st.session_state.abrir_cadastro = False
                    st.rerun()

                else:
                    apresentar_escrever_erros(erro)


# -----------------------------------------------------------------------------
# 1.2 DIÁLOGO: EDITAR POKÉMON
# -----------------------------------------------------------------------------

@st.dialog("Atualizar Pokémon")
def modal_editar_pokemon(POKE, registro):
    """Janela com o formulário para editar um Pokémon já cadastrado.

    Parâmetros:
        POKE: objeto `Pokemon` do usuário ativo (grava no banco).
        registro: tupla com a linha completa da tabela `pokemons` (as 16
            colunas, na ordem do banco). Os campos do formulário já abrem
            preenchidos com os valores atuais.

    Observações:
        - O número da Pokédex e a imagem NÃO podem ser editados aqui.
        - Escolher "Nenhum" no tipo secundário REMOVE o tipo secundário salvo
          (é enviado `limpar_tipo_secundario=True`).
        - Todas as chaves (`key`) incluem o `pokemon_id`, para que os campos
          de Pokémons diferentes não se misturem.
    """

    # Desempacota a tupla do banco em variáveis com nomes legíveis, na mesma
    # ordem das colunas da tabela.
    (
        pokemon_id,
        usuario_id,
        numero,
        nome,
        tipo1,
        tipo2,
        altura,
        peso,
        hp,
        ataque,
        habilidade,
        descricao,
        imagem,
        mime,
        criado_em,
        atualizado_em,
    ) = registro

    st.write(f"Editando **{nome.capitalize()}**")

    # `.strip()` já remove espaços extras do nome digitado.
    novo_nome = st.text_input("Nome", value=nome, key=f"edit_nome_{pokemon_id}").strip()

    # `index` define qual opção abre selecionada: a posição do tipo atual na
    # lista (ou 0, a primeira opção, se o tipo atual não estiver na lista).
    novo_tipo1 = st.selectbox(
        "Tipo principal",
        TIPOS_POKEMON,
        index=TIPOS_POKEMON.index(tipo1) if tipo1 in TIPOS_POKEMON else 0,
        key=f"edit_tipo1_{pokemon_id}",
    )

    # Aqui a lista tem "Nenhum" na posição 0, por isso o índice do tipo atual
    # é deslocado em +1. Sem tipo secundário -> índice 0 ("Nenhum").
    novo_tipo2 = st.selectbox(
        "Tipo secundário",
        ["Nenhum"] + TIPOS_POKEMON,
        index=(TIPOS_POKEMON.index(tipo2) + 1) if tipo2 in TIPOS_POKEMON else 0,
        key=f"edit_tipo2_{pokemon_id}",
    )

    # `float(altura or 0)`: o banco devolve Decimal ou None; isso converte
    # para número decimal comum e troca None por 0.
    nova_altura = st.number_input(
        "Altura (m)",
        min_value=0.0,
        value=float(altura or 0),
        step=0.1,
        key=f"edit_altura_{pokemon_id}",
    )

    novo_peso = st.number_input(
        "Peso (kg)",
        min_value=0.0,
        value=float(peso or 0),
        step=0.1,
        key=f"edit_peso_{pokemon_id}",
    )

    novo_hp = st.number_input(
        "Vida", min_value=0, value=int(hp or 0), key=f"edit_hp_{pokemon_id}"
    )

    novo_ataque = st.number_input(
        "Ataque", min_value=0, value=int(ataque or 0), key=f"edit_ataque_{pokemon_id}"
    )

    nova_habilidade = st.text_input(
        "Habilidade", value=habilidade or "", key=f"edit_habilidade_{pokemon_id}"
    )

    nova_descricao = st.text_area(
        "Descrição", value=descricao or "", key=f"edit_descricao_{pokemon_id}"
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Cancelar", key=f"cancelar_edicao_{pokemon_id}", use_container_width=True
        ):
            # Desliga o "interruptor" que mantém o diálogo aberto e recarrega.
            st.session_state.abrir_edicao = False
            st.rerun()

    with col2:
        if st.button(
            "Salvar alterações",
            key=f"salvar_edicao_{pokemon_id}",
            use_container_width=True,
        ):

            # Única validação: o nome não pode ficar vazio.
            if not novo_nome:
                st.warning("O nome do Pokémon não pode ficar vazio.")

            else:

                sem_tipo_secundario = novo_tipo2 == "Nenhum"

                sucesso, mensagem, erro = POKE.atualizar_pokemon(
                    pokemon_id=pokemon_id,
                    nome=novo_nome,
                    tipo_primario=novo_tipo1,
                    tipo_secuntario=None if sem_tipo_secundario else novo_tipo2,
                    altura=nova_altura,
                    peso=novo_peso,
                    vida=novo_hp,
                    ataque=novo_ataque,
                    habilidade=nova_habilidade,
                    descricao=nova_descricao,
                    # "Nenhum" escolhido -> apaga o tipo secundário (NULL).
                    limpar_tipo_secundario=sem_tipo_secundario,
                )

                if sucesso:
                    st.success(mensagem)
                    st.session_state.abrir_edicao = False
                    st.rerun()

                else:
                    apresentar_escrever_erros(erro)


# -----------------------------------------------------------------------------
# 1.3 DIÁLOGO: EXCLUIR POKÉMON
# -----------------------------------------------------------------------------

@st.dialog("Excluir Pokémon")
def modal_excluir_pokemon(POKE, registro):
    """Janela de confirmação para excluir um Pokémon do usuário.

    Necessária porque o cadastro tem um limite (LIMITE_POKEMONS): sem poder
    excluir, o usuário que chegasse ao limite ficaria sem opção.

    Parâmetros:
        POKE: objeto `Pokemon` do usuário ativo (apaga no banco).
        registro: tupla com a linha da tabela `pokemons` do Pokémon alvo.
            Só são usados o índice 0 (id) e o 3 (nome).
    """

    pokemon_id = registro[0]
    nome = registro[3]

    st.warning(
        f"Tem certeza de que deseja excluir **{nome.capitalize()}**? "
        "Essa ação não pode ser desfeita."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Cancelar", key=f"cancelar_exclusao_{pokemon_id}", use_container_width=True
        ):
            # Desliga o "interruptor" que mantém o diálogo aberto e recarrega.
            st.session_state.abrir_exclusao_pokemon = False
            st.rerun()

    with col2:
        if st.button(
            "Excluir",
            key=f"confirmar_exclusao_{pokemon_id}",
            type="primary",
            use_container_width=True,
        ):

            sucesso, mensagem, erro = POKE.deletar_pokemon(pokemon_id)

            if sucesso:
                st.session_state.abrir_exclusao_pokemon = False
                st.rerun()

            else:
                apresentar_escrever_erros(erro)


# =============================================================================
# 2. PESQUISA
# =============================================================================

def limpar_pesquisa() -> None:
    #Esvazia os dois campos da pesquisa (usada como `on_click` do botão).

    st.session_state.pesquisa_nome = ""
    st.session_state.pesquisa_numero = None


# =============================================================================
# 3. DESENHO DA PÁGINA
# =============================================================================

def renderizar(lista_poke) -> None:
    """Desenha a página "Minha Pokédex" do usuário ativo.

    Parâmetros:
        lista_poke: lista com o nome de todos os Pokémons (PokéAPI). Só é
            repassada ao diálogo de cadastro. Pode ser None/vazia se a
            PokéAPI estiver fora do ar — nesse caso o cadastro fica desativado.

    O que a página mostra:
        - contador "Pokémon cadastrados: x/LIMITE_POKEMONS";
        - o expander de PESQUISA (nome e/ou número da Pokédex);
        - os cartões: todos os Pokémons do usuário ou, havendo pesquisa, só os
          que atendem aos critérios. Em cada cartão: dados à esquerda, imagem
          à direita, descrição embaixo e botões de editar/excluir;
        - o botão "Cadastrar novo Pokémon" (desativado ao atingir o limite).

    Como os diálogos abrem: os botões ligam "interruptores" em
    st.session_state (`abrir_edicao`, `abrir_exclusao_pokemon`,
    `abrir_cadastro`) e reexecutam o script; enquanto o interruptor estiver
    ligado, o diálogo é desenhado. Essa parte fica FORA do bloco da pesquisa,
    para os botões continuarem funcionando nos resultados filtrados e para o
    cadastro estar disponível mesmo sem nenhum Pokémon.
    """

    # Objeto Pokemon do usuário ativo (criado por `ativar_usuario`).
    POKE = st.session_state.pokemon

    if POKE is None:
        st.warning("Selecione um usuário primeiro.")
        return

    # Busca no banco todos os Pokémons deste usuário.
    sucesso, pokemons_usuario, erro = POKE.listar_pokemons()

    # Em caso de falha, mostra o erro e segue com a lista vazia.
    if not sucesso:
        apresentar_escrever_erros(erro)
        pokemons_usuario = []

    quantidade_pokemons = len(pokemons_usuario)
    limite_atingido = quantidade_pokemons >= LIMITE_POKEMONS

    st.title("Minha Pokédex")

    # O limite também é imposto no banco, por `Pokemon.guardar_dados`.
    st.write(f"**Pokémon cadastrados: {quantidade_pokemons}/{LIMITE_POKEMONS}**")

    # ---- Pesquisa e cartões --------------------------------------------------
    if quantidade_pokemons == 0:
        st.info("Você ainda não cadastrou nenhum Pokémon.")

    else:
        # O expander fica ABERTO enquanto houver algo digitado na pesquisa.
        # (`.get` porque as chaves só existem depois do primeiro desenho.)
        pesquisa_ativa = bool(st.session_state.get("pesquisa_nome")) or (
            st.session_state.get("pesquisa_numero") is not None
        )

        with st.expander("Pesquisar Meus Pokémons", expanded=pesquisa_ativa):

            # Sem `autocomplete=`: esse parâmetro espera um TEXTO (dica do
            # navegador, ex.: "off") e não aceita uma lista de nomes.
            texto_nome = st.text_input(
                "Parte do nome do Pokémon",
                key="pesquisa_nome",
            )

            numero_pesquisa = st.number_input(
                "Número da Pokédex",
                min_value=1,
                step=1,
                value=None,
                key="pesquisa_numero",
            )

            # `on_click` roda `limpar_pesquisa` e depois reexecuta o script.
            st.button("Limpar pesquisa", key="limpar_pesquisa", on_click=limpar_pesquisa)

        # Campo de texto apagado devolve "" (e não None): `.strip()` tira os
        # espaços e `or None` transforma o texto vazio em "sem filtro".
        nome_pesquisa = (texto_nome or "").strip() or None

        pesquisando = nome_pesquisa is not None or numero_pesquisa is not None

        if pesquisando:
            sucesso, pokemons_exibidos, erro = POKE.buscar_pokemons(
                nome_pesquisa, numero_pesquisa
            )

            if not sucesso:
                apresentar_escrever_erros(erro)
                pokemons_exibidos = []

            st.caption(f"{len(pokemons_exibidos)} resultado(s) encontrado(s).")

            if not pokemons_exibidos:
                st.info("Nenhum Pokémon encontrado com esses critérios.")

        else:
            # Sem pesquisa: mostra todos.
            pokemons_exibidos = pokemons_usuario

        # Desenha os cartões da lista escolhida acima (completa ou filtrada).
        imprimir_card_pokemon(pokemons_exibidos)

    # ---- Diálogos de excluir e de editar ------------------------------------
    # Se o "interruptor" de exclusão estiver ligado, abre o diálogo de
    # confirmação com o registro guardado.
    if st.session_state.get("abrir_exclusao_pokemon", False):

        registro_exclusao = st.session_state.get("pokemon_excluir")

        if registro_exclusao is not None:
            modal_excluir_pokemon(POKE, registro_exclusao)

    # Se o "interruptor" de edição estiver ligado, abre o diálogo de edição com
    # o registro guardado. O diálogo é desenhado em toda reexecução enquanto
    # `abrir_edicao` for True.
    if st.session_state.get("abrir_edicao", False):

        registro_edicao = st.session_state.get("pokemon_editar")

        if registro_edicao is not None:
            modal_editar_pokemon(POKE, registro_edicao)

    st.divider()

    # ---- Cadastro de novo Pokémon --------------------------------------------
    # O botão fica desativado quando o limite foi atingido ou quando a lista de
    # nomes da PokéAPI não pôde ser carregada (sem ela não há o que escolher).
    if limite_atingido:
        st.caption(
            f"Você atingiu o limite de {LIMITE_POKEMONS} Pokémons. "
            "Para cadastrar outro, será preciso excluir um."
        )

    if not lista_poke:
        st.caption("Lista de Pokémons indisponível (PokéAPI fora do ar?).")

    if st.button(
        "➕ Cadastrar novo Pokémon",
        use_container_width=True,
        disabled=limite_atingido or not lista_poke,
    ):

        st.session_state.abrir_cadastro = True
        st.rerun()

    if st.session_state.get("abrir_cadastro", False):

        if lista_poke and not limite_atingido:
            modal_cadastrar_pokemon(POKE, lista_poke)

        else:
            # Situação em que o cadastro não é mais permitido: desliga o
            # "interruptor" para o diálogo não ficar preso aberto.
            st.session_state.abrir_cadastro = False
