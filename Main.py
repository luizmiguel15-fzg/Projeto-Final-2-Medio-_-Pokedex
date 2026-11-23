# =============================================================================
# ARQUIVO: Main.py  —  Ponto de entrada da Pokédex (interface em Streamlit)
# -----------------------------------------------------------------------------
# Como executar (na pasta raiz do projeto):
#       streamlit run Main.py
# (Requer um Streamlit recente: o projeto usa `st.navigation(position="hidden")`
#  e `st.container(horizontal=True)`.)
#
# PAPEL DESTE ARQUIVO
#   O Main.py é o "maestro": ele NÃO desenha nenhuma tela. Ele apenas
#     1. configura a aplicação e carrega os dados globais;
#     2. prepara a sessão e decide quem pode acessar o quê;
#     3. escolhe QUAL página mostrar e chama o arquivo dela (pasta Pages/).
#
# COMO O STREAMLIT FUNCIONA (importante para entender este arquivo):
#   O Streamlit executa este arquivo INTEIRO, de cima para baixo, a cada clique
#   de botão ou mudança de campo. Por isso:
#     - o que precisa "sobreviver" entre um clique e outro fica guardado em
#       `st.session_state` (um dicionário persistente da sessão);
#     - a página exibida é escolhida por `st.session_state.page`;
#     - `st.rerun()` força uma nova execução imediata do script.
#
# MAPA DAS PÁGINAS  (valor de st.session_state.page -> arquivo)
#       "Cadastro"           -> Pages/Cadastro.py
#       "selecionar_usuario" -> Pages/SelecionarUsuario.py
#       "inicio"             -> Pages/Inicio.py
#       "pokemons"           -> Pages/Pokemons.py
#       "batalha"            -> Pages/Batalha.py
#       "perfil"             -> Pages/Perfil.py
#   Cada arquivo de página expõe uma função `renderizar(...)` que desenha a
#   tela. A barra lateral fica em Systems/menu_lateral.py.
#   Para criar uma página nova: crie Pages/NovaPagina.py com `renderizar`,
#   importe-a abaixo e registre-a na função `montar_paginas`.
#
# VISUAL (CSS)
#   O visual personalizado (foto de perfil circular, badges de tipo com ícone e
#   chips coloridos de Vida/Ataque/Altura/Peso no card do Pokémon) vem de:
#       style.css            -> regras fixas (pasta raiz, ao lado deste arquivo)
#       Systems/estilos.py   -> carrega o CSS e cria o HTML dos badges/chips
#       Systems/constantes.py-> as cores (CORES_TIPOS, CORES_INFO) e os ícones
#   Para ele funcionar, ESTE arquivo precisa chamar `carregar_css()` logo depois
#   de `st.set_page_config(...)` (seção 2). Sem essa chamada, as páginas
#   continuam funcionando, mas sem o visual personalizado.
#
# ORGANIZAÇÃO DO ARQUIVO (a ordem de execução importa):
#   1. IMPORTAÇÕES (inclui `carregar_css`, de Systems/estilos.py)
#   2. CONFIGURAÇÃO DA PÁGINA E DO VISUAL (set_page_config + carregar_css)
#   3. CARREGAMENTO DA LISTA DE POKÉMONS (PokéAPI)
#   4. INICIALIZAÇÃO DO ESTADO DA SESSÃO
#   5. CARREGAMENTO DOS USUÁRIOS E CONTROLE DE ACESSO
#   6. ROTEAMENTO: MAPA DE PÁGINAS E EXECUÇÃO
# =============================================================================


# =============================================================================
# 1. IMPORTAÇÕES
# =============================================================================

import streamlit as st

# Classe que conversa com a tabela `usuarios` do banco.
from Classes.Usuario import Usuario

# Cada página é um módulo da pasta Pages/ (um arquivo .py por página).
from Pages import Batalha, Cadastro, Inicio, Perfil, Pokemons, SelecionarUsuario

# Busca na PokéAPI a lista com o nome de todos os Pokémons.
from Systems.dados_pokemons import carregar_pokemons

# Funções de apoio: logs de erro e gerenciamento de usuários na sessão.
from Systems.diversos import (
    apresentar_escrever_erros,
    ativar_usuario,
    atualizar_lista_usuarios,
)

# Envia ao navegador o CSS da Pokédex (style.css + cores geradas).
from Systems.estilos import carregar_css

# Barra lateral (menu) exibida quando há um usuário ativo.
from Systems.menu_lateral import desenhar_menu_lateral


# =============================================================================
# 2. CONFIGURAÇÃO DA PÁGINA E DO VISUAL
# -----------------------------------------------------------------------------
# `st.set_page_config` precisa ser o PRIMEIRO comando do Streamlit executado no
# script; só depois dele vem `carregar_css()`.
# =============================================================================

st.set_page_config(
    page_title="Pokédex",   # título que aparece na aba do navegador
    layout="wide",          # usa a largura total da tela
    page_icon="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/items/poke-ball.png",
)

# Aplica o visual personalizado (foto circular, badges de tipo com ícone, chips
# de Vida/Ataque/Altura/Peso): envia ao navegador o style.css + as cores geradas
# de Systems/constantes.py. Fica logo depois do set_page_config, é executada a
# cada reexecução do script e vale para TODAS as páginas.
carregar_css()


# =============================================================================
# 3. CARREGAMENTO DA LISTA DE POKÉMONS (PokéAPI)
# =============================================================================

@st.cache_data
def get_pokemons():
    """Busca a lista de nomes de todos os Pokémons, usando cache.

    O decorador `@st.cache_data` guarda o resultado depois da primeira
    chamada. Assim, nos cliques seguintes (quando o script é reexecutado) a
    PokéAPI NÃO é consultada de novo, o que deixa o programa bem mais rápido.

    Retorna o mesmo que `carregar_pokemons`: (sucesso, lista_de_nomes, erro).
    """
    return carregar_pokemons()


# Executa a busca (ou lê do cache). `lista_poke` é repassada às páginas que
# precisam dela: cadastro de Pokémon (caixa de seleção de nomes) e batalha
# (sorteio do inimigo).
sucesso, lista_poke, erro = get_pokemons()

# Se a PokéAPI falhou, mostra o aviso na tela e grava no arquivo de logs.
if not sucesso and erro is not None:
    apresentar_escrever_erros(erro)


# =============================================================================
# 4. INICIALIZAÇÃO DO ESTADO DA SESSÃO
# -----------------------------------------------------------------------------
# `setdefault(chave, valor)` cria a chave SOMENTE se ela ainda não existir.
# Assim, na primeira execução ela recebe o valor inicial e, nas reexecuções
# seguintes, o valor já guardado é preservado.
# =============================================================================

# Página atual (decide qual arquivo de Pages/ será desenhado).
st.session_state.setdefault("page", "inicio")

# Usuário ativo: objeto de acesso ao banco, nome e id.
st.session_state.setdefault("usuario", Usuario())
st.session_state.setdefault("usuario_nome", None)
st.session_state.setdefault("usuario_id", None)
st.session_state.setdefault("img_perfil", None)  # bytes da foto de perfil

# Lista de usuários carregada do banco (lista de tuplas).
st.session_state.setdefault("usuarios", [])

# `pokemon`: objeto Pokemon do usuário ativo.
# `pokemon_batalha`: dicionário da batalha em andamento (None = sem batalha).
st.session_state.setdefault("pokemon", None)
st.session_state.setdefault("pokemon_batalha", None)

# Dados auxiliares da batalha (zerados por `encerrar_batalha`).
st.session_state.setdefault("inimigo", None)
st.session_state.setdefault("battle_log", [])

# Indica se a lista de usuários já foi carregada do banco com sucesso.
st.session_state.setdefault("usuarios_carregados", False)


# Atalho: objeto Usuario repassado às páginas que acessam a tabela `usuarios`.
USU = st.session_state.usuario


# =============================================================================
# 5. CARREGAMENTO DOS USUÁRIOS E CONTROLE DE ACESSO
# =============================================================================

# Carrega os usuários do banco apenas se ainda não foram carregados.
if not st.session_state.usuarios_carregados:
    atualizar_lista_usuarios()


# Variáveis de apoio repassadas às páginas e à barra lateral.
usuarios = st.session_state.usuarios
ids_usuarios = [usuario[0] for usuario in usuarios]  # coluna 0 = id

# Regras de acesso:
#   - Sem nenhum usuário no banco: limpa a sessão e força a página "Cadastro".
#   - Com usuários, mas nenhum ativo (e fora das páginas de escolha/cadastro):
#     ativa automaticamente o primeiro usuário da lista.
if not usuarios:
    st.session_state.usuario_id = None
    st.session_state.usuario_nome = None
    st.session_state.pokemon = None
    st.session_state.page = "Cadastro"

elif st.session_state.usuario_id is None and st.session_state.page not in [
    "selecionar_usuario",
    "Cadastro",
]:
    ativar_usuario(ids_usuarios[0])

# Mantém válida a opção selecionada nas caixas de seleção de usuário: se o
# valor guardado não existe mais (ex.: usuário excluído), usa o usuário ativo
# ou, na falta dele, o primeiro da lista.
if ids_usuarios:
    usuario_selecionado = st.session_state.get("usuario_selecionado")

    if usuario_selecionado not in ids_usuarios:
        st.session_state.usuario_selecionado = (
            st.session_state.usuario_id or ids_usuarios[0]
        )


# =============================================================================
# 6. ROTEAMENTO: MAPA DE PÁGINAS E EXECUÇÃO
# =============================================================================

def montar_paginas():
    """Monta o mapa {nome da página -> função que a desenha}.

    As chaves são os valores que `st.session_state.page` pode assumir. Cada
    valor é uma função SEM argumentos (uma `lambda`) que chama o
    `renderizar` da página já repassando o que ela precisa:
        - USU          -> páginas que gravam usuários no banco;
        - lista_poke   -> páginas que usam a lista de nomes da PokéAPI;
        - usuarios / ids_usuarios -> página de seleção de usuário.

    Retorna o dicionário de páginas.
    """

    return {
        "Cadastro": lambda: Cadastro.renderizar(USU),
        "selecionar_usuario": lambda: SelecionarUsuario.renderizar(
            usuarios, ids_usuarios
        ),
        "inicio": lambda: Inicio.renderizar(),
        "pokemons": lambda: Pokemons.renderizar(lista_poke),
        "batalha": lambda: Batalha.renderizar(lista_poke),
        "perfil": lambda: Perfil.renderizar(USU),
    }


def roteador():
    """Desenha a barra lateral (se houver usuário ativo) e a página atual.

    Esta é a ÚNICA "página" do ponto de vista do Streamlit (veja o comentário
    abaixo, em `st.navigation`). A troca entre as telas da Pokédex é feita
    aqui dentro, lendo `st.session_state.page`.
    """

    # A barra lateral só existe com um usuário ativo.
    if st.session_state.usuario_id is not None:
        desenhar_menu_lateral(usuarios, ids_usuarios)

    paginas = montar_paginas()
    pagina_atual = st.session_state.page

    # Nome de página que não existe no mapa: registra o erro em vez de
    # deixar a tela em branco.
    if pagina_atual not in paginas:
        apresentar_escrever_erros(f"Página desconhecida: '{pagina_atual}'.")
        return

    # Chama a função da página escolhida.
    paginas[pagina_atual]()


# `st.navigation` com UMA única página e menu OCULTO ("hidden"):
#   - o menu e a troca de telas continuam sendo os da própria Pokédex
#     (barra lateral + st.session_state.page);
#   - a chamada serve para DESLIGAR a descoberta automática de páginas do
#     Streamlit. Sem ela, o Streamlit trataria cada arquivo da pasta Pages/
#     como uma página independente e criaria um menu duplicado (isso acontece
#     em sistemas onde "Pages" e "pages" são a mesma pasta, como o Windows).
navegacao = st.navigation(
    [st.Page(roteador, title="Pokédex", default=True)],
    position="hidden",
)

# Executa a "página" única, que é o `roteador` definido acima.
navegacao.run()
