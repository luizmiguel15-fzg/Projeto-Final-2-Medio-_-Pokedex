# =============================================================================
# MÓDULO: constantes.py
# -----------------------------------------------------------------------------
# Valores fixos compartilhados por várias partes do projeto.
# Ficam todos aqui para existir UMA única fonte de verdade: se algum valor
# mudar (por exemplo, o limite de Pokémons por usuário), basta alterar este
# arquivo.
#
# Quem usa o quê:
#   - LIMITE_POKEMONS -> Classes/Pokemon.py (impõe o limite no cadastro) e
#                        Pages/Pokemons.py (mostra o contador "x/5").
#   - TIPOS_POKEMON   -> Pages/Pokemons.py (caixas de seleção de tipo).
#   - CORES_TIPOS     -> Systems/estilos.py (gera as cores dos "badges" de tipo
#                        no CSS).
#   - URL_ICONES_TIPOS -> Systems/estilos.py (endereço do ícone de cada tipo,
#                        mostrado dentro do badge).
#   - CORES_INFO      -> Systems/estilos.py (cores de Vida, Ataque, Altura e
#                        Peso no card do Pokémon, e cor neutra de tipo).
#
# Organização do arquivo:
#   1. LIMITES
#   2. TIPOS DE POKÉMON  -> TIPOS_POKEMON, CORES_TIPOS, URL_ICONES_TIPOS
#   3. CORES DOS ATRIBUTOS -> CORES_INFO
# =============================================================================


# =============================================================================
# LIMITES
# =============================================================================

# Quantidade máxima de Pokémons que cada usuário pode cadastrar.
LIMITE_POKEMONS = 5


# =============================================================================
# TIPOS DE POKÉMON
# =============================================================================

# Os 18 tipos de Pokémon, com os nomes em inglês exatamente como a PokéAPI os
# devolve. Alimentam as caixas de seleção de "Tipo principal" e "Tipo
# secundário" nos diálogos de cadastro e edição.
TIPOS_POKEMON = [
    "normal",
    "fire",
    "water",
    "electric",
    "grass",
    "ice",
    "fighting",
    "poison",
    "ground",
    "flying",
    "psychic",
    "bug",
    "rock",
    "ghost",
    "dragon",
    "dark",
    "steel",
    "fairy",
]

# Cor (hexadecimal) associada a cada tipo, seguindo as cores oficiais dos
# jogos. (Antes chamado `type_colors` no Main.py.) O Systems/estilos.py
# transforma cada item em uma regra de CSS (ex.: `.tipo-fire { --cor: #EE8130 }`),
# então para mudar a cor de um tipo basta alterar o valor aqui.
CORES_TIPOS = {
    "normal": "#A8A77A",
    "fire": "#EE8130",
    "water": "#6390F0",
    "electric": "#F7D02C",
    "grass": "#7AC74C",
    "ice": "#96D9D6",
    "fighting": "#C22E28",
    "poison": "#A33EA1",
    "ground": "#E2BF65",
    "flying": "#A98FF3",
    "psychic": "#F95587",
    "bug": "#A6B91A",
    "rock": "#B6A136",
    "ghost": "#735797",
    "dragon": "#6F35FC",
    "dark": "#705746",
    "steel": "#B7B7CE",
    "fairy": "#D685AD",
}


# Endereço (pasta) dos ícones SVG de cada tipo, do repositório público
# "pokemon-type-svg-icons". O arquivo de cada tipo se chama `<tipo>.svg`
# (ex.: .../icons/fire.svg). O Systems/estilos.py monta a URL completa de cada
# tipo a partir desta base. O ícone é carregado pelo NAVEGADOR de quem usa o
# programa, então é preciso ter internet para ele aparecer; sem internet o
# badge continua funcionando, só que sem o ícone.
URL_ICONES_TIPOS = (
    "https://raw.githubusercontent.com/duiker101/"
    "pokemon-type-svg-icons/master/icons"
)


# =============================================================================
# CORES DOS ATRIBUTOS
# =============================================================================

# Cor de cada informação mostrada no card do Pokémon. Vira variáveis de CSS
# (`--cor-hp`, `--cor-ataque`, `--cor-peso`, `--cor-altura`, `--cor-tipo`)
# usadas pelo style.css.
#   - "hp"     : valor da VIDA.
#   - "ataque" : valor do ATAQUE. (Este não veio na paleta enviada; "#F08030"
#                é uma escolha, troque pela cor que preferir.)
#   - "peso"   : valor do PESO.
#   - "altura" : valor da ALTURA.
#   - "tipo"   : cor neutra usada no badge de um tipo desconhecido (que não
#                existe em CORES_TIPOS). Em tema CLARO, branco fica invisível;
#                se usar tema claro, troque por um cinza.
CORES_INFO = {
    "hp": "#78C850",
    "ataque": "#F08030",
    "peso": "#607D8B",
    "altura": "#2196F3",
    "tipo": "#FFFFFF",
}
