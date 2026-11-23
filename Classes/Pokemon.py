# =============================================================================
# MÓDULO: Pokemon.py
# -----------------------------------------------------------------------------
# Classe `Pokemon`: reúne todas as operações do banco de dados relacionadas
# aos Pokémons de UM usuário — tabela `pokemons`.
#
# Cada objeto é criado para um usuário específico (`usuario_id`), e todos os
# métodos trabalham apenas com os Pokémons DESSE usuário.
#
# Operações (padrão CRUD), na ordem em que aparecem na classe:
#   0. CONSTRUTOR -> __init__
#   1. CRIAR      -> guardar_dados
#   2. LER        -> listar_pokemons, buscar_pokemons (pesquisa)
#   3. ATUALIZAR  -> atualizar_pokemon
#   4. EXCLUIR    -> deletar_pokemon
#
# Convenções que se repetem em TODOS os métodos:
#   - Retorno em tupla: (sucesso: bool, resultado, erro: str | None).
#   - A variável `garsom` é o CURSOR do banco ("o garçom" que leva o pedido SQL
#     até o banco e traz a resposta de volta).
#   - Estrutura try / except / finally:
#       try      -> executa o SQL;
#       except   -> desfaz (rollback) e devolve a mensagem de erro;
#       finally  -> SEMPRE fecha o cursor e a conexão, mesmo se der erro.
#   - Todo SQL usa parâmetros (%s) em vez de juntar texto, o que protege contra
#     SQL Injection.
#
# Regras de negócio impostas AQUI (e não apenas na tela):
#   - Cada usuário pode ter no máximo LIMITE_POKEMONS Pokémons (veja
#     Systems/constantes.py). O cadastro é recusado ao atingir o limite.
#   - Um usuário só enxerga/altera/apaga os próprios Pokémons.
# =============================================================================

# Função que abre a conexão com o MySQL.
from Banco_De_Dados.conecao_BD import criar_conexao

# Função que baixa a imagem do Pokémon na PokéAPI (ou usa a imagem padrão).
from Systems.tratamento_IMGs import tratar_IMG_pokemons

# Quantidade máxima de Pokémons por usuário.
from Systems.constantes import LIMITE_POKEMONS


class Pokemon:
    """Gerencia os Pokémons de um usuário na tabela `pokemons`."""

    # =========================================================================
    # 0. CONSTRUTOR
    # =========================================================================

    def __init__(self, usuario_id: int):
        """Cria o gerenciador de Pokémons de um usuário.

        Parâmetros:
            usuario_id: ID (da tabela `usuarios`) do dono dos Pokémons. É
                usado em todas as consultas para que um usuário nunca veja
                nem altere os Pokémons de outro.
        """
        self.usuario_id = usuario_id


    # =========================================================================
    # 1. CRIAR (CADASTRAR) POKÉMON
    # =========================================================================

    def guardar_dados(
        self,
        numero_pokedex: int,
        nome: str,
        tipo_primario: str,
        tipo_secuntario: str | None = None,
        altura: float | None = None,
        peso: float | None = None,
        vida: int | None = None,
        ataque: int | None = None,
        habilidade: str | None = None,
        descricao: str | None = None,
    ) -> tuple[bool, str | None, str | None]:
        """Cadastra um novo Pokémon para o usuário.

        A imagem NÃO é informada pelo chamador: ela é buscada automaticamente
        na PokéAPI pelo `nome` (com imagem padrão como reserva) e gravada junto
        com os demais dados.

        Parâmetros obrigatórios:
            numero_pokedex: número do Pokémon na Pokédex (único por usuário).
            nome: nome do Pokémon em minúsculas (ex.: "pikachu"); também é a
                chave usada para buscar a imagem na PokéAPI.
            tipo_primario: tipo principal (ex.: "electric").

        Parâmetros opcionais (None vira NULL no banco):
            tipo_secuntario, altura (m), peso (kg), vida, ataque,
            habilidade, descricao.

        LIMITE: se o usuário já tem LIMITE_POKEMONS Pokémons (5), o cadastro é
        recusado ANTES de baixar a imagem, para não gastar internet à toa.

        Retorna (sucesso, mensagem, erro):
            - (True, "Pokémon cadastrado com sucesso!", None);
            - (False, None, "mensagem") se não conectar, se o limite foi
              atingido, se a imagem falhar ou se o MySQL recusar o INSERT
              (por exemplo, quando o usuário já tem esse `numero_pokedex`
              cadastrado — restrição UNIQUE).
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # ---- Regra do limite de Pokémons por usuário ---------------------
            # COUNT(*) devolve UMA linha com UMA coluna (a quantidade).
            # `fetchone()` traz essa linha e o desempacotamento `(quantidade,)`
            # extrai o número de dentro da tupla.
            garsom.execute(
                "SELECT COUNT(*) FROM pokemons WHERE usuario_id = %s",
                (self.usuario_id,),
            )
            (quantidade_atual,) = garsom.fetchone()

            if quantidade_atual >= LIMITE_POKEMONS:
                return (
                    False,
                    None,
                    f"Limite de {LIMITE_POKEMONS} Pokémons atingido. "
                    "Exclua um Pokémon antes de cadastrar outro.",
                )

            # Busca a imagem antes do INSERT: se ela falhar de vez, nem
            # chegamos a gravar nada no banco.
            sucesso_img, dados_img, erro_img = tratar_IMG_pokemons(nome)

            if not sucesso_img or dados_img is None:
                return False, None, erro_img

            # Desempacota a dupla (bytes da imagem, tipo MIME).
            img_binaria, img_mime = dados_img

            # 13 colunas e 13 marcadores %s, na MESMA ordem dos `valores`.
            # As colunas `id`, `criado_em` e `atualizado_em` ficam de fora
            # porque o próprio MySQL as preenche.
            sql = """
            INSERT INTO pokemons (
                usuario_id,
                numero_pokedex,
                nome,
                tipo_principal,
                tipo_secundario,
                altura_m,
                peso_kg,
                vida,
                ataque,
                habilidade,
                descricao,
                imagem_binaria,
                imagem_tipo_mime
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            valores = (
                self.usuario_id,
                numero_pokedex,
                nome,
                tipo_primario,
                tipo_secuntario,
                altura,
                peso,
                vida,
                ataque,
                habilidade,
                descricao,
                img_binaria,
                img_mime,
            )

            garsom.execute(sql, valores)

            # Confirma a gravação de forma definitiva.
            conexao.commit()

            return True, "Pokémon cadastrado com sucesso!", None

        except Exception as e:
            # Desfaz qualquer alteração pendente e devolve o motivo do erro.
            conexao.rollback()
            return False, None, f"Erro ao guardar dados: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 2. LER (LISTAR E PESQUISAR) POKÉMONS
    # =========================================================================

    def listar_pokemons(self) -> tuple[bool, list[tuple] | None, str | None]:
        """Lista todos os Pokémons cadastrados pelo usuário.

        Retorna (sucesso, pokemons, erro):
            - (True, lista_de_tuplas, None): cada tupla é uma linha da tabela,
              com as colunas nesta ordem (índices usados em
              Pages/Pokemons.py, Pages/Batalha.py e Systems/diversos.py):
                  0 id, 1 usuario_id, 2 numero_pokedex, 3 nome,
                  4 tipo_principal, 5 tipo_secundario, 6 altura_m, 7 peso_kg,
                  8 vida, 9 ataque, 10 habilidade, 11 descricao,
                  12 imagem_binaria, 13 imagem_tipo_mime,
                  14 criado_em, 15 atualizado_em
              Lista vazia significa "nenhum Pokémon ainda" (não é erro).
            - (False, None, "mensagem"): falha de conexão ou de consulta.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # O WHERE garante que só os Pokémons DESTE usuário sejam trazidos.
            sql = "SELECT * FROM pokemons WHERE usuario_id = %s"

            # A vírgula em `(self.usuario_id,)` cria uma tupla de um item.
            garsom.execute(sql, (self.usuario_id,))

            # Traz todas as linhas do resultado de uma vez.
            pokemons = garsom.fetchall()

            # SELECT só lê dados, então não há commit/rollback.
            return True, pokemons, None

        except Exception as e:
            return False, None, f"Erro ao listar pokémons: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    def buscar_pokemons(
        self, nome: str | None = None, numero_pokedex: int | None = None
    ) -> tuple[bool, list[tuple] | None, str | None]:
        """Pesquisa entre os Pokémons do usuário por nome e/ou número da Pokédex.

        O SQL é montado dinamicamente (como em `atualizar_pokemon`): o filtro
        do dono (`usuario_id`) está SEMPRE presente e cada critério informado
        acrescenta um `AND ...`. Quando os dois critérios são informados, o
        Pokémon precisa atender aos DOIS. Sem nenhum critério, devolve todos.

        Parâmetros:
            nome: parte do nome a procurar (ex.: "bulb" encontra "bulbasaur").
                A busca é por trecho (LIKE '%trecho%') e não diferencia
                maiúsculas de minúsculas (colação padrão do MySQL). None ou
                texto vazio = não filtrar por nome.
            numero_pokedex: número exato do Pokémon na Pokédex. None = não
                filtrar por número.

        Retorna (sucesso, pokemons, erro):
            - (True, lista_de_tuplas, None): mesmas colunas de
              `listar_pokemons`. Lista vazia = nada encontrado (não é erro);
            - (False, None, "mensagem"): falha de conexão ou de consulta.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # O WHERE garante que só os Pokémons DESTE usuário sejam trazidos.
            sql = "SELECT * FROM pokemons WHERE usuario_id = %s"
            valores = [self.usuario_id]

            # `.strip()` ignora espaços; texto vazio ("") conta como "sem filtro".
            if nome is not None and nome.strip():

                sql += " AND nome LIKE %s"
                valores.append(f"%{nome.strip()}%")

            if numero_pokedex is not None:
                
                sql += " AND numero_pokedex = %s"
                valores.append(int(numero_pokedex))

            garsom.execute(sql, tuple(valores))

            # Traz todas as linhas do resultado de uma vez.
            pokemons = garsom.fetchall()

            # SELECT só lê dados, então não há commit/rollback.
            return True, pokemons, None

        except Exception as e:
            return False, None, f"Erro ao pesquisar pokémons: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 3. ATUALIZAR POKÉMON
    # =========================================================================

    def atualizar_pokemon(
        self,
        pokemon_id: int,
        nome: str | None = None,
        tipo_primario: str | None = None,
        tipo_secuntario: str | None = None,
        altura: float | None = None,
        peso: float | None = None,
        vida: int | None = None,
        ataque: int | None = None,
        habilidade: str | None = None,
        descricao: str | None = None,
        limpar_tipo_secundario: bool = False,
    ) -> tuple[bool, str | None, str | None]:
        """Atualiza apenas os campos informados de um Pokémon do usuário.

        O SQL é montado dinamicamente: somente os parâmetros diferentes de
        None entram no SET. Assim é possível alterar um único campo sem tocar
        nos demais. A imagem e o número da Pokédex não podem ser alterados aqui.

        Como `None` significa "não alterar", existe o parâmetro separado
        `limpar_tipo_secundario` para REMOVER o tipo secundário (gravar NULL).

        Parâmetros:
            pokemon_id: ID (coluna `id`) do registro a ser alterado.
            nome ... descricao: novos valores; o que for None é ignorado.
            limpar_tipo_secundario: se True, o tipo secundário é apagado
                (vira NULL). Não pode ser usado junto com `tipo_secuntario`
                (não faz sentido definir e apagar ao mesmo tempo).

        Retorna (sucesso, mensagem, erro):
            - (True, "Pokémon com ID X atualizado com sucesso!", None);
            - (False, None, "mensagem") se nada foi informado, se os
              parâmetros se contradizem, se o Pokémon não existe / não
              pertence ao usuário, se os valores eram idênticos aos atuais
              ou se o MySQL recusar o comando.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            # `all(...)` é True só se TODOS os valores da lista forem None, ou
            # seja, se o chamador não pediu nenhuma alteração. Pedir para
            # limpar o tipo secundário também conta como uma alteração.
            if not limpar_tipo_secundario and all(
                valor is None
                for valor in [
                    nome,
                    tipo_primario,
                    tipo_secuntario,
                    altura,
                    peso,
                    vida,
                    ataque,
                    habilidade,
                    descricao,
                ]
            ):
                return False, None, "Nenhum dado fornecido para atualização."

            # Pedidos contraditórios: definir um tipo secundário E apagá-lo.
            if limpar_tipo_secundario and tipo_secuntario is not None:
                return (
                    False,
                    None,
                    "Não é possível definir e limpar o tipo secundário ao mesmo tempo.",
                )

            garsom = conexao.cursor()

            # Duas listas paralelas montadas conforme os campos recebidos:
            #   campos_atualizacao -> trechos do SET (ex.: "vida = %s")
            #   valores            -> valores que preencherão cada %s, na ordem
            campos_atualizacao = []
            valores = []

            # Para cada parâmetro recebido, acrescenta "coluna = %s" no SET e
            # o valor correspondente na lista de valores. Repare que o nome do
            # parâmetro no Python difere do nome da coluna no banco em alguns
            # casos (ex.: `tipo_primario` -> coluna `tipo_principal`).

            if nome is not None:
                campos_atualizacao.append("nome = %s")
                valores.append(nome)

            if tipo_primario is not None:
                campos_atualizacao.append("tipo_principal = %s")
                valores.append(tipo_primario)

            if tipo_secuntario is not None:
                campos_atualizacao.append("tipo_secundario = %s")
                valores.append(tipo_secuntario)

            # Remoção do tipo secundário: grava NULL diretamente no SQL. Como
            # não há valor a enviar, NÃO se acrescenta nada em `valores` (não
            # existe %s para este trecho).
            if limpar_tipo_secundario:
                campos_atualizacao.append("tipo_secundario = NULL")

            if altura is not None:
                campos_atualizacao.append("altura_m = %s")
                valores.append(altura)

            if peso is not None:
                campos_atualizacao.append("peso_kg = %s")
                valores.append(peso)

            if vida is not None:
                campos_atualizacao.append("vida = %s")
                valores.append(vida)

            if ataque is not None:
                campos_atualizacao.append("ataque = %s")
                valores.append(ataque)

            if habilidade is not None:
                campos_atualizacao.append("habilidade = %s")
                valores.append(habilidade)

            if descricao is not None:
                campos_atualizacao.append("descricao = %s")
                valores.append(descricao)

            # Junta os trechos com vírgula. Só nomes de colunas fixos do código
            # entram no texto do SQL; os valores vão sempre pelos %s.
            # O WHERE usa DOIS filtros: o id do Pokémon E o dono, impedindo que
            # um usuário altere o Pokémon de outro.
            sql = f"""
            UPDATE pokemons
            SET {', '.join(campos_atualizacao)}
            WHERE id = %s AND usuario_id = %s
            """

            # Os dois %s do WHERE entram por último, na ordem em que aparecem.
            valores.extend([pokemon_id, self.usuario_id])

            garsom.execute(sql, tuple(valores))

            # `rowcount` = linhas realmente alteradas. Zero significa que o
            # Pokémon não existe / não é deste usuário OU que os valores novos
            # eram idênticos aos antigos.
            if garsom.rowcount == 0:
                conexao.rollback()
                return (
                    False,
                    None,
                    f"Nenhum Pokémon encontrado com ID {pokemon_id} ou nenhum dado foi alterado.",
                )

            conexao.commit()

            return True, f"Pokémon com ID {pokemon_id} atualizado com sucesso!", None

        except Exception as e:
            conexao.rollback()
            return False, None, f"Erro ao atualizar pokémon: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 4. EXCLUIR POKÉMON
    # =========================================================================

    def deletar_pokemon(self, pokemon_id: int) -> tuple[bool, str | None, str | None]:
        """Exclui um Pokémon do usuário pelo ID do registro.

        Parâmetros:
            pokemon_id: ID (coluna `id`) do Pokémon a ser excluído.

        O DELETE filtra também por `usuario_id`, então um usuário só consegue
        excluir os próprios Pokémons.

        Retorna (sucesso, mensagem, erro):
            - (True, "Pokémon com ID X deletado com sucesso!", None);
            - (False, None, "Nenhum Pokémon encontrado com ID X.") se não
              existir ou pertencer a outro usuário;
            - (False, None, "Erro ao deletar pokémon: ...") para falhas do MySQL.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            sql = """
            DELETE FROM pokemons
            WHERE id = %s AND usuario_id = %s
            """

            garsom.execute(sql, (pokemon_id, self.usuario_id))

            # Zero linhas afetadas = nada foi encontrado para apagar.
            if garsom.rowcount == 0:
                conexao.rollback()
                return False, None, f"Nenhum Pokémon encontrado com ID {pokemon_id}."

            conexao.commit()

            return True, f"Pokémon com ID {pokemon_id} deletado com sucesso!", None

        except Exception as e:
            conexao.rollback()
            return False, None, f"Erro ao deletar pokémon: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()
