# =============================================================================
# MÓDULO: dados_pokemons.py
# -----------------------------------------------------------------------------
# Funções que buscam dados de Pokémons na PokéAPI (https://pokeapi.co),
# uma API pública e gratuita com informações de todos os Pokémons.
#
# Contém dois grupos:
#   1. LISTA DE POKÉMONS      -> carregar_pokemons
#   2. DADOS DO INIMIGO       -> dados_inimigo (adversário sorteado na batalha)
#
# Padrão de retorno do projeto:
#   (sucesso: bool, dados: ... | None, erro: str | None)
# =============================================================================

# Biblioteca para fazer requisições HTTP (acessar a PokéAPI).
import requests

# Módulo de números aleatórios, usado para sortear o inimigo (apelido `rn`).
import random as rn


# =============================================================================
# 1. LISTA DE POKÉMONS
# =============================================================================

def carregar_pokemons(
) -> tuple[bool, list[str] | None, str | None]:
    """Baixa da PokéAPI o nome de TODOS os Pokémons existentes.

    Usada no início do programa para preencher a lista de opções do cadastro
    (caixa de seleção "Nome do Pokémon") e para saber quantos Pokémons existem
    (necessário para sortear o inimigo da batalha).

    Como funciona (duas requisições):
        1. Chama a lista paginada da API só para descobrir o total de Pokémons
           (campo "count").
        2. Chama de novo pedindo `limit=<total>` — ou seja, tudo em uma única
           página — e extrai apenas o nome de cada um.

    Retorna (sucesso, lista, erro):
        - (True, ["bulbasaur", "ivysaur", ...], None): nomes em minúsculas.
        - (False, None, "mensagem"): falha de rede, resposta inválida, etc.
    """

    # Endereço base do recurso "pokemon" da PokéAPI.
    base_url = "https://pokeapi.co/api/v2/pokemon"

    try:
        # ---- Requisição 1: descobrir o total de Pokémons ---------------------
        r = requests.get(base_url, timeout=5)

        # Levanta exceção se a resposta for um erro HTTP (4xx / 5xx).
        r.raise_for_status()

        # "count" = quantidade total de Pokémons cadastrados na API.
        count = r.json()["count"]

        # ---- Requisição 2: baixar a lista completa em uma só página ----------
        # limit=count -> quantos itens vir; offset=0 -> começar do primeiro.
        r = requests.get(
            f"{base_url}?limit={count}&offset=0",
            timeout=10
        )

        r.raise_for_status()

        # List comprehension: percorre "results" (lista de {name, url}) e
        # guarda só o nome, convertido para minúsculas.
        lista_pokemons = [
            p["name"].lower()
            for p in r.json()["results"]
        ]

        return True, lista_pokemons, None

    except (requests.RequestException, ValueError, KeyError, TypeError) as e:
        # RequestException: sem internet, timeout ou erro HTTP.
        # ValueError: a resposta não era JSON válido.
        # KeyError / TypeError: o JSON não tinha a estrutura esperada.
        return False, None, f"Erro ao carregar Pokémons: {e}"


# =============================================================================
# 2. DADOS DO INIMIGO (BATALHA)
# =============================================================================

def dados_inimigo(
    max_tentativas: int = 5,
    lista_poke: list | None = None
) -> tuple[bool, dict[str, str | int | None] | None, str | None]:
    """Sorteia um Pokémon selvagem e devolve seus dados para usar na batalha.

    Parâmetros:
        max_tentativas: quantas vezes tentar sortear/consultar antes de desistir.
            Existe porque o número sorteado pode não corresponder a um Pokémon
            válido na API (a numeração da PokéAPI não é totalmente contínua), e
            porque a internet pode falhar pontualmente. Padrão: 5.
        lista_poke: lista de nomes retornada por `carregar_pokemons`. Aqui ela
            é usada SOMENTE pelo tamanho, para definir o intervalo do sorteio.

    Retorna (sucesso, dados, erro):
        - (True, dict, None) com as chaves:
              "nome"          -> nome do Pokémon
              "dano"          -> poder de ataque (stat "attack")
              "vida"          -> pontos de vida atuais (stat "hp")
              "vida_max"      -> pontos de vida máximos (igual a "vida" no início)
              "defesa"        -> defesa (stat "defense")
              "tipo"          -> tipo primário (ex.: "fire")
              "sprite_ataque" -> URL da imagem frontal do Pokémon
        - (False, None, "mensagem"): parâmetros inválidos ou todas as
          tentativas falharam.
    """

    # ---- Validação dos parâmetros --------------------------------------------
    # Sem lista não há como saber o intervalo do sorteio.
    if lista_poke is None or len(lista_poke) == 0:
        return False, None, "Lista de Pokémons não fornecida ou vazia."

    # Com zero (ou menos) tentativas o laço abaixo nem rodaria.
    if max_tentativas <= 0:
        return False, None, "O número de tentativas deve ser maior que zero."

    # ---- Laço de tentativas --------------------------------------------------
    # O "_" indica que o contador do laço não é usado; só importa repetir.
    for _ in range(max_tentativas):

        # Sorteia um número entre 1 e o total de Pokémons (inclusive) e o usa
        # como ID do Pokémon na PokéAPI.
        num_poke = rn.randint(1, len(lista_poke))

        try:
            # Consulta a PokéAPI pelo ID sorteado.
            r = requests.get(
                f"https://pokeapi.co/api/v2/pokemon/{num_poke}",
                timeout=5
            )

            r.raise_for_status()

            d = r.json()

            # "stats" é uma lista fixa na PokéAPI, na ordem:
            #   [0] hp, [1] attack, [2] defense, ...
            # "base_stat" é o valor numérico de cada atributo.
            vida = d["stats"][0]["base_stat"]

            dados = {
                "nome": d["name"],
                "dano": d["stats"][1]["base_stat"],
                "vida": vida,
                "vida_max": vida,  # no início da batalha a vida atual é a máxima
                "defesa": d["stats"][2]["base_stat"],
                "tipo": d["types"][0]["type"]["name"],  # primeiro tipo da lista
                "sprite_ataque": d["sprites"]["front_default"],
            }

            # Deu certo: devolve já na primeira tentativa bem-sucedida.
            return True, dados, None

        except (
            requests.RequestException,
            ValueError,
            KeyError,
            IndexError,
            TypeError
        ):
            # Qualquer falha (ID inexistente/404, rede, JSON inesperado) apenas
            # descarta esta tentativa e passa para a próxima.
            continue

    # Saiu do laço sem nenhum sucesso: todas as tentativas falharam.
    return False, None, "Nenhum Pokémon encontrado após as tentativas."