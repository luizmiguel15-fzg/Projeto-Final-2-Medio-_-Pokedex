# =============================================================================
# MÓDULO: diversos.py
# -----------------------------------------------------------------------------
# Funções de apoio usadas pelo Main.py, pelas páginas (pasta Pages/) e pela
# barra lateral (Systems/menu_lateral.py). Cada um importa apenas o que usa,
# por exemplo: `from Systems.diversos import mudar_pagina, trocar_usuario`.
#
# Organização do arquivo:
#   1. IMPORTAÇÕES E CONFIGURAÇÃO DO ARQUIVO DE LOGS
#   2. NAVEGAÇÃO ENTRE PÁGINAS                  -> mudar_pagina
#   3. DATA, HORA E REGISTRO DE ERROS (LOGS)    -> obter_data_horario,
#                                                  apresentar_escrever_erros
#   4. GERENCIAMENTO DE USUÁRIOS NA SESSÃO      -> atualizar_lista_usuarios,
#                                                  ativar_usuario, trocar_usuario
#   5. LÓGICA DA BATALHA POKÉMON                -> preparar_pokemon_batalha,
#                                                  iniciar_batalha, calcular_dano,
#                                                  atacar_inimigo, turno_inimigo,
#                                                  defender_pokemon,
#                                                  encerrar_batalha
#
# Conceito importante: `st.session_state` é o "caderninho" do Streamlit. Como o
# Streamlit reexecuta o script inteiro a cada clique, é nele que guardamos o
# que precisa sobreviver entre uma execução e outra (usuário ativo, página
# atual, batalha em andamento, etc.).
# =============================================================================


# =============================================================================
# 1. IMPORTAÇÕES E CONFIGURAÇÃO DO ARQUIVO DE LOGS
# =============================================================================

# `datetime` (apelidado `dt`) para obter data e hora atuais.
from datetime import datetime as dt

# `os` para montar caminhos de arquivo e verificar se um arquivo existe.
import os

# Números aleatórios (apelido `rn`), usados no cálculo de dano da batalha.
import random as rn

# Classes que conversam com o banco de dados.
from Classes.Usuario import Usuario
from Classes.Pokemon import Pokemon

# Busca os dados de um Pokémon inimigo sorteado na PokéAPI.
from Systems.dados_pokemons import dados_inimigo

# Biblioteca da interface web.
import streamlit as st

# Nome do arquivo onde os erros do programa são registrados.
NOME_ARQ = "Logs_error.txt"

# Pasta onde ESTE arquivo (diversos.py) está. `abspath` converte para caminho
# absoluto e `dirname` remove o nome do arquivo, deixando só a pasta.
diretorioAtual = os.path.dirname(os.path.abspath(__file__))

# Pasta RAIZ do projeto (a que contém o Main.py): é a pasta "pai" de Systems/.
# `dirname` aplicado de novo remove o último nome do caminho, subindo um nível.
diretorioMain = os.path.dirname(diretorioAtual)

# Caminho completo do arquivo de logs: fica na pasta raiz do projeto, ao lado
# do Main.py (e NÃO dentro de Systems/). Um log antigo que tenha ficado em
# Systems/Logs_error.txt deixa de ser usado.
logs_path = os.path.join(diretorioMain, NOME_ARQ)


# =============================================================================
# 2. NAVEGAÇÃO ENTRE PÁGINAS
# =============================================================================

def mudar_pagina(pagina: str) -> None:
    """Troca a página exibida e reexecuta o script para aplicar a mudança.

    Parâmetros:
        pagina: nome da página de destino. Os valores usados no Main.py são
            "inicio", "pokemons", "batalha", "perfil", "selecionar_usuario"
            e "Cadastro".

    Como funciona: grava o nome da página em `st.session_state.page` (que o
    Main.py lê para decidir o que desenhar) e chama `st.rerun()`, que
    reexecuta o script imediatamente, já mostrando a nova página.
    """
    st.session_state.page = pagina
    st.rerun()


# =============================================================================
# 3. DATA, HORA E REGISTRO DE ERROS (LOGS)
# =============================================================================

def obter_data_horario() -> tuple[bool, str | None, str, str]:
    """Obtém a data e a hora atuais já formatadas como texto.

    Retorna (sucesso, mensagem_de_erro, data, hora):
        - Sucesso: (True, None, "21/11/2026", "21:45:10")
          (data no formato dd/mm/aaaa e hora no formato hh:mm:ss).
        - Falha: (False, "Erro ao obter data e hora atual: ...",
          "DATA INDISPONIVEL", "HORA INDISPONIVEL") — textos reserva, para que
          o chamador sempre tenha algo para mostrar.
    """

    # Valores reserva, usados caso a leitura do relógio falhe.
    data = "DATA INDISPONIVEL"
    hora = "HORA INDISPONIVEL"

    try:
        # Momento atual do relógio do computador.
        now = dt.now()

        # strftime formata a data/hora: %d dia, %m mês, %Y ano com 4 dígitos,
        # %H hora (00-23), %M minutos, %S segundos.
        data = now.strftime("%d/%m/%Y")
        hora = now.strftime("%H:%M:%S")

        return True, None, data, hora

    except Exception as e:
        return False, f"Erro ao obter data e hora atual: {e}", data, hora


def apresentar_escrever_erros(msg_error: str) -> None:
    """Mostra um erro na tela E o registra no arquivo de logs.

    Cada registro é gravado numa linha no formato:
        [dd/mm/aaaa] - [hh:mm:ss]: mensagem do erro

    Quando o dia muda em relação ao último registro do arquivo, é escrita
    antes uma linha separadora com a nova data (===== 22/11/2026 =====),
    para organizar o log por dia.

    Parâmetros:
        msg_error: texto do erro a ser mostrado e registrado.
    """

    # ---- Passo 1: criar o arquivo de logs, se ainda não existir --------------
    # Modo "w" cria o arquivo; aqui ele recebe um cabeçalho com o título.
    if not os.path.exists(logs_path):
        with open(logs_path, "w", encoding="utf-8") as log:
            log.write(
                "================================================\n"
                "          LOGS DE ERROS DO PROGRAMA\n"
                "================================================\n\n"
            )

    # ---- Passo 2: obter data e hora e montar o prefixo da linha --------------
    sucesso, msg_erro_hora, data, hora = obter_data_horario()
    data_hora = f"[{data}] - [{hora}]: "

    # ---- Passo 3: inserir separador de dia, se o dia mudou -------------------
    # Só é possível comparar datas se o relógio funcionou (`sucesso` True).
    if sucesso:
        # Lê o arquivo inteiro como lista de linhas.
        with open(logs_path, "r", encoding="utf-8") as log:
            linhas = log.readlines()

        ultima_linha = ""

        # Percorre as linhas de trás para frente até achar a última que não
        # esteja em branco.
        for linha in reversed(linhas):
            if linha.strip():
                ultima_linha = linha
                break

        # Linhas de registro começam com "[" (as de cabeçalho/separador não).
        if ultima_linha.startswith("["):
            # Os caracteres 1 a 10 da linha são a data: "[21/11/2026]" ->
            # "21/11/2026". (A posição 0 é o "[" e a 11 é o "]".)
            data_anterior = ultima_linha[1:11]

            # Se a data do último registro difere da de hoje, abre uma nova
            # seção no arquivo com a data atual.
            if data_anterior != data:
                with open(logs_path, "a", encoding="utf-8") as log:
                    log.write("\n" + "=" * 15 + f" {data} " + "=" * 15 + "\n\n")

    # ---- Passo 4: gravar o erro e exibi-lo na tela ---------------------------
    # Modo "a" (append) acrescenta no final sem apagar o conteúdo anterior.
    with open(logs_path, "a", encoding="utf-8") as log:
        # Se o relógio falhou, esse problema também é exibido e registrado
        # (em maiúsculas) antes da mensagem principal.
        if not sucesso and msg_erro_hora is not None:
            st.warning(data_hora + msg_erro_hora.upper())
            log.write(data_hora + msg_erro_hora.upper() + "\n")

        # `st.warning` mostra a caixa amarela de aviso na interface.
        st.warning(data_hora + msg_error)
        log.write(data_hora + msg_error + "\n")


# =============================================================================
# 4. GERENCIAMENTO DE USUÁRIOS NA SESSÃO
# =============================================================================

def atualizar_lista_usuarios() -> None:
    """Recarrega do banco a lista de usuários e guarda na sessão.

    Efeitos em `st.session_state`:
        - Sucesso: `usuarios` recebe a lista e `usuarios_carregados` vira True.
        - Falha: o erro é exibido/registrado e `usuarios_carregados` vira False
          (o Main.py tentará carregar de novo na próxima execução).

    Deve ser chamada sempre que a tabela `usuarios` mudar (cadastro, exclusão,
    troca de nome e troca de foto de perfil), para a interface refletir o
    estado atual do banco. Se ela não for chamada depois de trocar o nome, as
    caixas de seleção de usuário continuam mostrando o nome antigo.
    """

    # Instância local só para usar o método de listagem.
    USU = Usuario()

    sucesso, usuarios, erro = USU.listar_usuarios()

    if not sucesso or usuarios is None:
        apresentar_escrever_erros(erro or "Não foi possível carregar os usuários.")
        st.session_state.usuarios_carregados = False
        return

    st.session_state.usuarios = usuarios
    st.session_state.usuarios_carregados = True
    return


def ativar_usuario(usuario_id: int) -> None:
    """Define qual usuário está "logado" na sessão e vai para a página inicial.

    Busca os dados ATUAIS do usuário DIRETO NO BANCO (por
    `Usuario.pegar_dados_usuario_atual`), copia nome e foto para a sessão e
    cria o objeto `Pokemon` vinculado a ele. Consultar o banco, em vez de usar
    a lista guardada em `st.session_state.usuarios`, evita ativar um usuário
    com nome ou foto desatualizados.

    Parâmetros:
        usuario_id: ID do usuário a ser ativado. Precisa ser um número inteiro;
            qualquer outro tipo (como um nome) é recusado e registrado no log.

    A linha devolvida pelo banco é uma tupla:
        (id, nome, imagem_binaria_perfil, imagem_tipo_mime)
    por isso os índices 1 e 2 abaixo são o nome e a foto.
    """

    # ---- Trava de diagnóstico --------------------------------------------------
    # Foi criada para descobrir quem chamava esta função com um NOME no lugar do
    # ID (o culpado era a caixa "Trocar usuario", hoje protegida em
    # `trocar_usuario`). Se um valor que não é inteiro chegar aqui, ele é
    # recusado e o log mostra o valor e as últimas chamadas (`format_stack`),
    # o que revela quem o enviou. Pode ser removida, mas protege o login.
    if not isinstance(usuario_id, int):
        import traceback
        apresentar_escrever_erros(
            f"ativar_usuario recebeu {usuario_id!r} ({type(usuario_id).__name__}); "
            "esperado int.\n" + "".join(traceback.format_stack(limit=4))
        )
        return

    # Instância local só para usar o método de consulta (a classe não guarda estado).
    USU = Usuario()

    # `usuario` é a linha do banco (veja o formato no docstring).
    susseco, usuario, erro = USU.pegar_dados_usuario_atual(usuario_id)


    # Falha na consulta (sem conexão, ID inexistente...): mostra e registra o
    # erro e mantém o usuário anterior ativo.
    if not susseco or usuario is None:
        apresentar_escrever_erros(erro)
        return

    # Copia os dados do usuário para a sessão.
    st.session_state.usuario_id = usuario_id
    st.session_state.usuario_nome = usuario[1]
    st.session_state.img_perfil = usuario[2]

    # Objeto que gerencia os Pokémons DESTE usuário.
    st.session_state.pokemon = Pokemon(usuario_id)

    # Depois de ativar um usuário, o programa volta para a página inicial.
    st.session_state.page = "inicio"


def trocar_usuario() -> None:
    """Ativa o usuário escolhido na caixa "Trocar usuário" da barra lateral.

    Só ativa se o valor da caixa for um ID de usuário que existe. Quando o nome
    de um usuário muda, o Streamlit recria a caixa e ela pode disparar esta
    função com o TEXTO da opção (o nome antigo) em vez do ID. Esse valor é
    ignorado, e o Main.py recoloca a caixa no usuário ativo na execução seguinte.
    """

    # Valor atual da caixa. Deveria ser o ID, mas pode vir como nome (texto).
    valor = st.session_state.get("usuario_selecionado")

    # IDs que realmente existem (coluna 0 de cada linha da lista de usuários).
    ids = [usuario[0] for usuario in st.session_state.usuarios]

    # Só um ID válido ativa o usuário. Qualquer outro valor (nome, None...) é
    # ignorado de propósito: não é uma escolha do usuário, e ativar com um
    # valor assim causava o erro "usuário de ID <nome>".
    if valor in ids:
        ativar_usuario(valor)


# =============================================================================
# 5. LÓGICA DA BATALHA POKÉMON
# -----------------------------------------------------------------------------
# A batalha é um dicionário guardado em `st.session_state.pokemon_batalha`:
#   {
#     "jogador":    dict do Pokémon do jogador (veja preparar_pokemon_batalha),
#     "inimigo":    dict do inimigo (veja dados_inimigo),
#     "log":        lista de mensagens do histórico da batalha,
#     "status":     "em andamento" | "vitoria" | "derrota",
#     "defendendo": True se o jogador escolheu Defender neste turno
#   }
# Fluxo de um turno:
#   Atacar   -> atacar_inimigo -> (se o inimigo sobreviver) turno_inimigo
#   Defender -> defender_pokemon -> turno_inimigo (com o dano reduzido)
# =============================================================================

def preparar_pokemon_batalha(registro):
    """Converte um registro do banco em um dicionário usável na batalha.

    Parâmetros:
        registro: tupla de uma linha da tabela `pokemons` (veja a ordem das
            colunas em Pokemon.listar_pokemons). Índices usados aqui:
            0 id, 3 nome, 4 tipo_principal, 8 vida, 9 ataque, 12 imagem.

    Retorna um dicionário com as chaves: id, nome, tipo, vida, vida_max,
    ataque, defesa e imagem.

    Observações:
        - `vida` e `ataque` são opcionais no banco (podem ser NULL/None). O
          operador `or` aplica valores padrão: 100 de vida e 10 de ataque.
          (Atenção: o valor 0 também é falso, então vida 0 também vira 100.)
        - A defesa do jogador é fixa em 0, pois essa informação não é
          guardada no banco.
    """

    return {
        "id": registro[0],
        "nome": registro[3],
        "tipo": registro[4],
        "vida": registro[8] or 100,
        "vida_max": registro[8] or 100,
        "ataque": registro[9] or 10,
        "defesa": 0,
        "imagem": registro[12],
    }


def iniciar_batalha(registro, lista_poke):
    """Monta uma nova batalha: Pokémon do jogador contra um inimigo sorteado.

    Parâmetros:
        registro: tupla do Pokémon escolhido pelo jogador (linha da tabela).
        lista_poke: lista com os nomes de todos os Pokémons (usada para sortear
            o inimigo).

    Retorna (sucesso, batalha, erro):
        - (True, dicionario_da_batalha, None): batalha pronta, com status
          "em andamento" e as duas primeiras mensagens no histórico;
        - (False, None, "mensagem"): não foi possível obter o inimigo.
    """

    # Converte o registro do banco no formato usado na batalha.
    jogador = preparar_pokemon_batalha(registro)

    # Sorteia e busca na PokéAPI os dados do inimigo.
    sucesso, inimigo, erro = dados_inimigo(lista_poke=lista_poke)

    if not sucesso:
        return False, None, erro

    batalha = {
        "jogador": jogador,
        "inimigo": inimigo,
        # `.capitalize()` deixa a primeira letra maiúscula ("pikachu" -> "Pikachu").
        "log": [
            f"{jogador['nome'].capitalize()} entrou na batalha!",
            f"Um {inimigo['nome'].capitalize()} selvagem apareceu!",
        ],
        "status": "em andamento",
        "defendendo": False,
    }

    return True, batalha, None


def calcular_dano(ataque, defesa=0):
    """Calcula o dano de um golpe, com um pouco de aleatoriedade.

    Fórmula:
        1. dano_base = max(5, ataque - defesa // 2)
           -> a defesa do alvo absorve METADE do seu valor; o dano base nunca
              é menor que 5.
        2. resultado = número inteiro sorteado entre (dano_base - 5) e
           (dano_base + 5), com mínimo de 1.

    Parâmetros:
        ataque: poder de ataque de quem ataca.
        defesa: defesa de quem recebe o golpe (padrão 0).

    Retorna o dano (inteiro, sempre >= 1).
    """

    # `//` é a divisão inteira (descarta a parte decimal).
    dano = max(5, ataque - (defesa // 2))

    # `randint(a, b)` sorteia um inteiro entre a e b, ambos incluídos.
    return rn.randint(max(1, dano - 5), dano + 5)


def atacar_inimigo(batalha):
    """Executa o ataque do jogador; se o inimigo sobreviver, ele contra-ataca.

    Passo a passo:
        1. Calcula o dano do jogador (levando em conta a defesa do inimigo).
        2. Subtrai do inimigo, sem deixar a vida ficar negativa.
        3. Registra a mensagem no histórico.
        4. Se a vida do inimigo chegou a 0: status "vitoria" e a batalha acaba.
        5. Caso contrário, o inimigo responde chamando `turno_inimigo`.

    Parâmetros:
        batalha: dicionário da batalha (é modificado diretamente).

    Retorna o dicionário da batalha atualizado.
    """

    jogador = batalha["jogador"]
    inimigo = batalha["inimigo"]

    dano = calcular_dano(jogador["ataque"], inimigo["defesa"])

    # `max(0, ...)` impede vida negativa.
    inimigo["vida"] = max(0, inimigo["vida"] - dano)

    batalha["log"].append(f"{jogador['nome'].capitalize()} causou {dano} de dano!")

    # Inimigo derrotado: encerra sem dar a ele o direito de contra-atacar.
    if inimigo["vida"] <= 0:

        batalha["status"] = "vitoria"

        batalha["log"].append(f"{inimigo['nome'].capitalize()} foi derrotado!")

        return batalha

    # Inimigo ainda de pé: é a vez dele.
    return turno_inimigo(batalha)


def turno_inimigo(batalha):
    """Executa o contra-ataque do inimigo sobre o Pokémon do jogador.

    Passo a passo:
        1. Calcula o dano do inimigo (levando em conta a defesa do jogador).
        2. Se o jogador escolheu Defender no turno, o dano é reduzido à
           metade (mínimo 1) e a marca de defesa é desligada.
        3. Subtrai do jogador, sem deixar a vida ficar negativa.
        4. Se a vida do jogador chegou a 0: status "derrota".

    Parâmetros:
        batalha: dicionário da batalha (é modificado diretamente).

    Retorna o dicionário da batalha atualizado.
    """

    jogador = batalha["jogador"]
    inimigo = batalha["inimigo"]

    # No inimigo, o poder de ataque fica na chave "dano" (vem da PokéAPI).
    dano = calcular_dano(inimigo["dano"], jogador["defesa"])

    # Efeito da ação "Defender": corta o dano pela metade, só neste turno.
    if batalha["defendendo"]:
        dano = max(1, dano // 2)
        batalha["defendendo"] = False

        batalha["log"].append("Sua defesa reduziu o dano recebido!")

    jogador["vida"] = max(0, jogador["vida"] - dano)

    batalha["log"].append(f"{inimigo['nome'].capitalize()} causou {dano} de dano!")

    # Jogador sem vida: fim de batalha com derrota.
    if jogador["vida"] <= 0:

        batalha["status"] = "derrota"

        batalha["log"].append(f"{jogador['nome'].capitalize()} não consegue continuar!")

    return batalha


def defender_pokemon(batalha):
    """Executa a ação "Defender" do jogador.

    Liga a marca `defendendo` (que reduz à metade o dano do próximo golpe
    inimigo) e passa a vez ao inimigo imediatamente.

    Parâmetros:
        batalha: dicionário da batalha (é modificado diretamente).

    Retorna o dicionário da batalha atualizado (já após o turno do inimigo).
    """

    batalha["defendendo"] = True

    batalha["log"].append(
        f"{batalha['jogador']['nome'].capitalize()} está se defendendo!"
    )

    return turno_inimigo(batalha)


def encerrar_batalha():
    """Limpa da sessão todos os dados da batalha atual.

    É chamada ao fugir, ao clicar em "Nova batalha" (após vitória) ou em
    "Tentar novamente" (após derrota). Com `pokemon_batalha = None`, o
    Pages/Batalha.py volta a mostrar a tela de escolha do Pokémon.
    """

    st.session_state.pokemon_batalha = None
    st.session_state.inimigo = None
    st.session_state.battle_log = []
