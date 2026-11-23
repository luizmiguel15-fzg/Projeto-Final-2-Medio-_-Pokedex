# =============================================================================
# MÓDULO: estilos.py
# -----------------------------------------------------------------------------
# Ponte entre o Python e o CSS da Pokédex.
#
# O visual fica dividido em DUAS partes que são enviadas juntas ao navegador:
#   1. style.css (na pasta raiz do projeto, ao lado do Main.py): regras FIXAS —
#      foto de perfil circular, formato dos "badges" de tipo e dos chips de
#      Vida/Ataque/Altura/Peso.
#   2. CSS GERADO por este módulo a partir das constantes de
#      Systems/constantes.py: uma cor e um ícone por tipo (CORES_TIPOS e
#      URL_ICONES_TIPOS) e as cores dos atributos (CORES_INFO). Assim as cores
#      têm uma única fonte e o style.css não precisa repeti-las.
#
# O módulo também cria o HTML (badges de tipo e chips de atributos) que as
# páginas exibem com `st.html(...)`.
#
# COMO LIGAR O VISUAL AO PROGRAMA (3 passos):
#   a) o Main.py importa `carregar_css` e a chama logo depois de
#      `st.set_page_config(...)` — isso envia o CSS ao navegador;
#   b) as páginas usam `tipos_html(...)` e `stats_html(...)` para montar o HTML
#      (Pages/Pokemons.py);
#   c) containers com `key=...` no Pages/Perfil.py recebem a classe
#      `st-key-<key>`, que o style.css usa para deixar a foto circular.
#
# Organização do arquivo:
#   1. LOCALIZAÇÃO DO style.css
#   2. CARREGAMENTO DO CSS        -> gerar_css_cores, carregar_css
#   3. HTML DOS COMPONENTES       -> url_icone_tipo, badge_tipo, tipos_html,
#                                    formatar_numero, stats_html
# =============================================================================

# `html` (biblioteca padrão) protege o texto vindo do banco antes de colocá-lo
# dentro de HTML (função `escape`).
import html

# `os` para montar o caminho do style.css; `re` para "enxugar" o CSS (veja
# `minificar_css`).
import os
import re

import streamlit as st

# Cores por tipo, cores dos atributos e endereço dos ícones.
from Systems.constantes import CORES_INFO, CORES_TIPOS, URL_ICONES_TIPOS

# Mostra o erro na tela e o registra no arquivo de logs.
from Systems.diversos import apresentar_escrever_erros


# =============================================================================
# 1. LOCALIZAÇÃO DO style.css
# =============================================================================

# Pasta deste arquivo (Systems/) e pasta raiz do projeto (a que tem o Main.py).
diretorioAtual = os.path.dirname(os.path.abspath(__file__))
diretorioMain = os.path.dirname(diretorioAtual)

# O caminho é montado a partir da posição DESTE arquivo (e não da pasta de onde
# o programa foi iniciado), então o CSS é encontrado em qualquer situação.
caminho_css = os.path.join(diretorioMain, "style.css")


# =============================================================================
# 2. CARREGAMENTO DO CSS
# =============================================================================

def gerar_css_cores() -> str:
    """Gera o trecho de CSS que depende das constantes de cores.

    Cria:
        - `:root { --cor-hp: ...; --cor-ataque: ...; --cor-peso: ...;
          --cor-altura: ...; --cor-tipo: ... }` — variáveis de CSS com as
          cores de CORES_INFO, usadas pelo style.css via `var(...)`;
        - uma regra por tipo, no formato `.tipo-fire { --cor: #EE8130; }`. A
          variável `--cor` é lida pelo style.css para pintar a borda, o texto
          e o fundo do badge daquele tipo.

    Retorna o CSS como texto.
    """

    linhas = [":root {"]

    # Uma variável `--cor-<nome>` para cada item de CORES_INFO
    # (hp, ataque, peso, altura, tipo).
    for nome, cor in CORES_INFO.items():
        linhas.append(f"  --cor-{nome}: {cor};")

    linhas.append("}")

    # Uma regra para cada tipo do dicionário CORES_TIPOS.
    for tipo, cor in CORES_TIPOS.items():
        linhas.append(f".tipo-{tipo} {{ --cor: {cor}; }}")

    return "\n".join(linhas)


def minificar_css(css: str) -> str:
    """Transforma o CSS em UMA linha só, sem comentários nem linhas em branco.

    Por quê: o CSS é enviado com `st.markdown(..., unsafe_allow_html=True)`, e o
    Markdown tem duas armadilhas — uma linha em branco ENCERRA o bloco de HTML e
    linhas com 4 ou mais espaços de recuo viram "bloco de código" (o CSS
    apareceria como texto na tela, sem ser aplicado). Em uma linha só, nada disso
    acontece. Os comentários também saem (não são necessários no navegador).
    """

    # Remove os comentários /* ... */ (inclusive os de várias linhas).
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)

    # Qualquer sequência de espaços/quebras de linha vira um espaço só.
    return re.sub(r"\s+", " ", css).strip()


def carregar_css() -> None:
    """Envia ao navegador o CSS da Pokédex (cores geradas + style.css).

    Deve ser chamada UMA vez por execução do script, no Main.py, logo depois
    de `st.set_page_config`. Como o Streamlit reexecuta o script a cada clique,
    o CSS é reenviado a cada execução (é leve e é o jeito normal de fazer).

    Se o style.css não puder ser lido, o erro é exibido e registrado no log e
    o programa continua funcionando, só que sem o visual personalizado.
    """

    css_fixo = ""

    try:
        # Lê o style.css inteiro como texto.
        with open(caminho_css, "r", encoding="utf-8") as arquivo:
            css_fixo = arquivo.read()

    except OSError as e:
        apresentar_escrever_erros(f"Não foi possível carregar o style.css: {e}")

    # As cores vêm ANTES do style.css, para as variáveis já existirem quando
    # as regras fixas as usarem.
    # Usa `st.markdown` com `unsafe_allow_html=True` (e NÃO `st.html`): é o jeito
    # que garante que a tag <style> seja realmente aplicada à página.
    css = minificar_css(f"{gerar_css_cores()}\n{css_fixo}")
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


# =============================================================================
# 3. HTML DOS COMPONENTES
# =============================================================================

def url_icone_tipo(tipo) -> str | None:
    """Monta a URL do ícone SVG de um tipo de Pokémon.

    Parâmetros:
        tipo: nome do tipo em inglês (ex.: "fire").

    Retorna a URL no formato `<URL_ICONES_TIPOS>/<tipo>.svg`, ou None se o
    tipo não for um dos conhecidos (assim nunca se monta uma URL com texto
    arbitrário vindo do banco).
    """

    if tipo not in CORES_TIPOS:
        return None

    return f"{URL_ICONES_TIPOS}/{tipo}.svg"


def badge_tipo(tipo) -> str:
    """Cria o HTML de um "badge" (etiqueta arredondada) de um tipo de Pokémon.

    O badge tem o ÍCONE do tipo (imagem carregada da internet) e o nome do tipo.

    Parâmetros:
        tipo: nome do tipo em inglês (ex.: "electric"), como guardado no banco.

    A cor vem da classe `tipo-<nome>` (gerada em `gerar_css_cores`). Um tipo
    que não exista em CORES_TIPOS recebe a classe neutra `tipo-desconhecido` e
    fica sem ícone. O texto passa por `html.escape`, então nada do banco vira
    HTML solto.

    Retorna o HTML do badge.
    """

    classe = f"tipo-{tipo}" if tipo in CORES_TIPOS else "tipo-desconhecido"

    # O `style` na própria imagem fixa o tamanho do ícone mesmo se o CSS falhar
    # (sem ele o SVG ocuparia a tela inteira). `alt=""` deixa o texto alternativo
    # vazio: se a imagem não carregar (sem internet), nada estranho aparece no
    # lugar e o nome do tipo continua lá.
    url = url_icone_tipo(tipo)
    icone = f'<img class="tipo-icone" src="{html.escape(url)}" alt="" style="width:1.2em;height:1.2em">' if url else ""

    return (
        f'<span class="tipo-badge {classe}">'
        f"{icone}{html.escape(str(tipo))}"
        "</span>"
    )


def tipos_html(tipo_principal, tipo_secundario=None) -> str:
    """Cria o HTML da linha de badges de tipo de um Pokémon.

    Parâmetros:
        tipo_principal: tipo principal (sempre existe).
        tipo_secundario: tipo secundário, ou None/vazio se não tiver.

    Retorna o HTML com um badge (ou dois) dentro de `<div class="tipos-linha">`.
    """

    badges = badge_tipo(tipo_principal)

    # O badge do tipo secundário só aparece se ele existir.
    if tipo_secundario:
        badges += badge_tipo(tipo_secundario)

    return f'<div class="tipos-linha">{badges}</div>'


def formatar_numero(valor, unidade: str = "") -> str:
    """Formata um número do banco para exibição, com unidade opcional.

    O MySQL devolve altura e peso como `Decimal` (ex.: Decimal('0.70')) e vida
    e ataque como inteiros. Esta função padroniza: tira zeros inúteis
    ("0.70" -> "0.7", "6.00" -> "6") e acrescenta a unidade.

    Parâmetros:
        valor: número (int, float, Decimal) ou None.
        unidade: texto colocado depois do número (ex.: "m", "kg").

    Retorna o texto já escapado para HTML, ou "—" se `valor` for None.
    """

    if valor is None:
        return "—"

    try:
        numero = float(valor)

    except (TypeError, ValueError):
        # Valor que não é número: mostra como texto, escapado.
        return html.escape(str(valor))

    # `.2f` fixa 2 casas decimais (sem notação científica); os `rstrip`
    # removem zeros e o ponto que sobrarem no fim ("6.00" -> "6").
    texto = f"{numero:.2f}".rstrip("0").rstrip(".")

    return f"{texto} {unidade}".strip()


def stats_html(vida, ataque, altura=None, peso=None) -> str:
    """Cria o HTML dos chips coloridos de Vida, Ataque, Altura e Peso.

    Os chips ficam em DUAS linhas: Vida + Ataque e, abaixo, Altura + Peso.

    Parâmetros:
        vida: pontos de vida (número) ou None.
        ataque: poder de ataque (número) ou None.
        altura: altura em metros (número/Decimal) ou None.
        peso: peso em quilogramas (número/Decimal) ou None.

    Valores None aparecem como "—" (são opcionais no banco). As cores vêm das
    classes `stat-hp`, `stat-ataque`, `stat-altura` e `stat-peso` do style.css.

    Retorna o HTML dentro de `<div class="stats-bloco">`.
    """

    def chip(rotulo, texto, classe):
        # Função interna: monta UM chip "rótulo + valor". O `texto` já vem
        # formatado e escapado por `formatar_numero`.
        return (
            f'<span class="stat-chip {classe}">'
            f'<span class="stat-rotulo">{rotulo}</span>'
            f'<span class="stat-valor">{texto}</span>'
            "</span>"
        )

    linha_combate = (
        '<div class="stats-linha">'
        + chip("Vida", formatar_numero(vida), "stat-hp")
        + chip("Ataque", formatar_numero(ataque), "stat-ataque")
        + "</div>"
    )

    linha_fisica = (
        '<div class="stats-linha">'
        + chip("Altura", formatar_numero(altura, "m"), "stat-altura")
        + chip("Peso", formatar_numero(peso, "kg"), "stat-peso")
        + "</div>"
    )

    return f'<div class="stats-bloco">{linha_combate}{linha_fisica}</div>'
