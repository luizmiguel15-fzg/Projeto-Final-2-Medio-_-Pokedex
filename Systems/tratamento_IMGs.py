# =============================================================================
# MÓDULO: tratamento_IMGs.py
# -----------------------------------------------------------------------------
# Prepara as imagens que serão gravadas no banco de dados.
# O banco guarda a imagem como bytes (LONGBLOB) + o tipo MIME (ex.: "image/png"),
# por isso as funções daqui sempre devolvem a dupla (bytes, mime).
#
# Contém duas funções, uma para cada tipo de imagem:
#   - tratar_IMG_pokemons  -> imagem de um Pokémon (baixada da PokéAPI)
#   - tratar_IMG_usuarios  -> foto de perfil de um usuário
#
# Padrão de retorno usado nas duas funções (e no projeto inteiro):
#   (sucesso: bool, dados: (bytes, mime) | None, erro: str | None)
# =============================================================================

# `requests` faz as chamadas HTTP para a PokéAPI (apelidado de `req`).
import requests as req

# `mimetypes` descobre o tipo MIME de um arquivo a partir da extensão dele.
import mimetypes

# Tipo do arquivo enviado pelo usuário no `st.file_uploader` do Streamlit.
# Aqui é usado apenas como anotação de tipo (type hint).
from streamlit.runtime.uploaded_file_manager import UploadedFile


# =============================================================================
# IMAGENS DE POKÉMONS
# =============================================================================

def tratar_IMG_pokemons(nome: str) -> tuple[bool, tuple[bytes, str] | None, str | None]:
    """Obtém a imagem oficial de um Pokémon na PokéAPI, pronta para o banco.

    Fluxo:
        1. Carrega do disco a imagem padrão de erro ("ERROR404_img-pokemon.png").
           Ela é o plano B: se qualquer coisa der errado na internet, o Pokémon
           ainda é cadastrado, só que com essa imagem.
        2. Consulta a PokéAPI pelo nome do Pokémon e descobre a URL da imagem
           "official-artwork".
        3. Baixa a imagem dessa URL e devolve os bytes + o tipo MIME.

    Parâmetros:
        nome: nome do Pokémon em minúsculas (ex.: "pikachu"), como a PokéAPI espera.

    Retorna (sucesso, dados, erro):
        - (True, (bytes, mime), None): imagem baixada com sucesso OU imagem
          padrão usada como substituta (falha de rede, Pokémon sem arte, etc.).
          Falhas de internet NÃO são tratadas como erro de propósito.
        - (False, None, "mensagem"): único caso de erro real — a imagem padrão
          não foi encontrada no disco.
    """

    # Caminho RELATIVO: só funciona se o programa for executado a partir da
    # pasta raiz do projeto (a que contém a pasta IMGs).
    caminho_padrao = "IMGs/ERROR404_img-pokemon.png"

    # ---- Passo 1: carregar a imagem padrão (plano B) -------------------------
    try:
        # "rb" = leitura em modo binário, necessário para imagens.
        with open(caminho_padrao, "rb") as f:
            img_padrao_binaria = f.read()

        # A imagem padrão é um PNG, então o MIME é fixo.
        img_padrao_mime = "image/png"

    except OSError as e:
        # Arquivo ausente, sem permissão, etc. Sem plano B não há como seguir.
        return False, None, f"Imagem padrão não encontrada: {e}"

    # ---- Passo 2 e 3: buscar a imagem verdadeira na PokéAPI ------------------
    try:
        # Pede à PokéAPI os dados do Pokémon. `timeout=5` evita que o programa
        # fique travado se a internet estiver lenta ou fora do ar.
        r = req.get(f"https://pokeapi.co/api/v2/pokemon/{nome}", timeout=5)

        # Lança uma exceção se a resposta for um erro HTTP (ex.: 404 = o nome
        # não existe na PokéAPI).
        r.raise_for_status()

        # Converte o corpo da resposta (JSON) em dicionário Python.
        d = r.json()

        # Navega pelo JSON até a URL da arte oficial do Pokémon.
        url_img = d["sprites"]["other"]["official-artwork"]["front_default"]

        # Alguns Pokémons não têm arte oficial: a URL vem como None.
        # Nesse caso usa-se a imagem padrão (e isso conta como sucesso).
        if url_img is None:
            return True, (img_padrao_binaria, img_padrao_mime), None

        # Baixa a imagem em si (timeout maior, pois o arquivo é mais pesado).
        resposta_img = req.get(url_img, timeout=10)
        resposta_img.raise_for_status()

        # `.content` são os bytes brutos da imagem, exatamente o que o banco guarda.
        imagem_binaria = resposta_img.content

        # O tipo MIME vem no cabeçalho HTTP "Content-Type" (ex.: "image/png").
        mime_type = resposta_img.headers.get("Content-Type")

        # Segurança: se o cabeçalho faltar ou não indicar uma imagem, assume PNG.
        if not mime_type or not mime_type.startswith("image/"):
            mime_type = "image/png"

        return True, (imagem_binaria, mime_type), None

    except (req.RequestException, ValueError, KeyError, TypeError):
        # Qualquer problema no caminho acima cai aqui e usa a imagem padrão:
        #   - RequestException: sem internet, timeout, erro HTTP (inclui 404);
        #   - ValueError: a resposta não era um JSON válido;
        #   - KeyError / TypeError: o JSON veio sem a estrutura esperada.
        return True, (img_padrao_binaria, img_padrao_mime), None


# =============================================================================
# IMAGENS DE USUÁRIOS
# =============================================================================

def tratar_IMG_usuarios(
    img_nova: UploadedFile | None = None
) -> tuple[bool, tuple[bytes, str] | None, str | None]:
    """Prepara a foto de perfil de um usuário para ser gravada no banco.

    A função tem DOIS modos de funcionamento, conforme o parâmetro:
        - Sem `img_nova` (None): carrega a imagem de perfil padrão do disco.
          Usado ao cadastrar um usuário novo.
        - Com `img_nova`: valida e lê a imagem que o usuário enviou pelo
          `st.file_uploader`. Usado ao trocar a foto de perfil.

    Parâmetros:
        img_nova: arquivo enviado pelo usuário no Streamlit, ou None.

    Retorna (sucesso, dados, erro):
        - (True, (bytes, mime), None): imagem pronta para o banco.
        - (False, None, "mensagem"): arquivo padrão ausente, imagem vazia,
          arquivo que não é imagem ou erro inesperado de leitura.
    """

    # ---- Modo 1: nenhuma imagem enviada -> usar a imagem padrão --------------
    if img_nova is None:

        # Caminho RELATIVO à pasta de onde o programa é executado.
        caminho_img = "IMGs/img_perfil_padrao.png"

        try:
            with open(caminho_img, "rb") as img:
                imagem_binaria = img.read()

            # Descobre o MIME pela extensão do arquivo (".png" -> "image/png").
            # `guess_type` devolve (tipo, codificação); só o tipo interessa,
            # por isso a codificação é ignorada com "_".
            mime_type, _ = mimetypes.guess_type(caminho_img)

            # Se não for possível descobrir, usa o tipo genérico para "bytes".
            mime_type = mime_type or "application/octet-stream"

            return True, (imagem_binaria, mime_type), None

        except OSError as e:
            return False, None, f"Erro ao carregar imagem padrão: {e}"

    # ---- Modo 2: imagem enviada pelo usuário -> validar e ler ----------------
    try:
        # `.getvalue()` devolve todos os bytes do arquivo enviado.
        imagem_binaria = img_nova.getvalue()

        # O Streamlit informa o tipo MIME do arquivo em `.type`.
        mime_type = img_nova.type

        # Validação 1: o arquivo não pode estar vazio (0 bytes).
        if not imagem_binaria:
            return False, None, "A imagem selecionada está vazia."

        # Validação 2: o tipo precisa existir e começar com "image/"
        # (rejeita PDFs, textos, etc. que tenham sido enviados por engano).
        if not mime_type or not mime_type.startswith("image/"):
            return False, None, "O arquivo selecionado não é uma imagem válida."

        return True, (imagem_binaria, mime_type), None

    except Exception as e:
        # Rede de segurança para qualquer falha inesperada ao ler o arquivo.
        return False, None, f"Erro ao carregar imagem: {e}"
