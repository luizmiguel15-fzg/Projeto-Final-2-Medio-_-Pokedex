# =============================================================================
# MÓDULO: conecao_BD.py
# -----------------------------------------------------------------------------
# Responsável por abrir a conexão com o banco de dados MySQL da Pokédex.
# Todas as classes (Usuario, Pokemon) importam a função `criar_conexao` daqui,
# então qualquer mudança de host, usuário ou senha deve ser feita APENAS neste
# arquivo.
# =============================================================================

# Biblioteca oficial do MySQL para Python (pacote `mysql-connector-python`).
# É importada com o apelido `myc` para encurtar as chamadas.
import mysql.connector as myc

# `Error` é a classe base de todos os erros lançados pelo conector
# (servidor fora do ar, senha errada, banco inexistente, etc.).
from mysql.connector import Error


# =============================================================================
# CONEXÃO COM O BANCO DE DADOS
# =============================================================================

def criar_conexao():
    """Abre e devolve uma nova conexão com o banco de dados `pokedex`.

    Cada chamada cria uma conexão NOVA e independente. Quem chamou a função
    é responsável por fechá-la (`conexao.close()`) quando terminar — as classes
    do projeto fazem isso dentro de um bloco `finally`.

    Parâmetros de conexão (fixos no código):
        - host:     'localhost' (o MySQL roda na mesma máquina do programa)
        - database: 'pokedex'   (criado pelo arquivo pokedex.sql)
        - user:     'root'
        - password: ''          (senha vazia — adequado apenas para estudo/dev)

    Retorna:
        - Um objeto de conexão do MySQL, se deu tudo certo;
        - `None`, se ocorreu qualquer erro de conexão. Nesse caso a mensagem
          do erro é apenas impressa no terminal, e quem chamou deve checar
          `if conexao is None` antes de usar.
    """

    try:
        # Tenta estabelecer a conexão com os dados abaixo.
        conexao = myc.connect(
            host='localhost',
            database='pokedex',
            user='root',
            password=''
        )

        # Sucesso: devolve a conexão pronta para criar cursores e executar SQL.
        return conexao

    except Error as e:
        # Falha (servidor desligado, banco inexistente, credenciais erradas...):
        # mostra o motivo no terminal e devolve None para sinalizar o problema
        # sem derrubar o programa.
        print(f'Erro ao conectar MySQL: {e}')
        return None
