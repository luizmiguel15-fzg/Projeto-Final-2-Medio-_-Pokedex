# =============================================================================
# MÓDULO: Usuario.py
# -----------------------------------------------------------------------------
# Classe `Usuario`: reúne todas as operações do banco de dados relacionadas
# aos usuários ("mestres Pokémon") — tabela `usuarios`.
#
# Operações (padrão CRUD), na ordem em que aparecem na classe:
#   1. CRIAR      -> cadastro_mestre_pokemon
#   2. LER        -> listar_usuarios (todos) e pegar_dados_usuario_atual (um só)
#   3. ATUALIZAR  -> atualizar_usuario
#   4. EXCLUIR    -> deletar_usuario
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
# =============================================================================

# Função que abre a conexão com o MySQL.
from Banco_De_Dados.conecao_BD import criar_conexao

# Função que prepara (valida e lê) a imagem de perfil do usuário.
from Systems.tratamento_IMGs import tratar_IMG_usuarios

# Tipo do arquivo enviado pelo `st.file_uploader` (usado só como type hint).
from streamlit.runtime.uploaded_file_manager import UploadedFile


class Usuario:
    """Gerencia os usuários (mestres Pokémon) na tabela `usuarios`.

    A classe não guarda estado: cada método abre sua própria conexão com o
    banco, executa a operação e a fecha. Por isso uma única instância pode ser
    reaproveitada em toda a aplicação (o Main.py guarda uma no session_state).
    """

    # =========================================================================
    # 1. CRIAR USUÁRIO
    # =========================================================================

    def cadastro_mestre_pokemon(
        self,
        nome: str
    ) -> tuple[bool, int | None, str | None]:
        """Cadastra um novo usuário e devolve o ID criado no banco.

        O usuário é criado já com a imagem de perfil PADRÃO (a foto pode ser
        trocada depois, em `atualizar_usuario`).

        Passo a passo:
            1. Valida o nome (não pode ser vazio nem só espaços).
            2. Abre a conexão com o banco.
            3. Carrega a imagem de perfil padrão.
            4. Executa o INSERT e confirma (commit).
            5. Devolve o ID gerado pelo AUTO_INCREMENT.

        Parâmetros:
            nome: nome do mestre Pokémon.

        Retorna (sucesso, novo_usuario_id, erro):
            - (True, id_do_usuario, None) em caso de sucesso;
            - (False, None, "mensagem") se o nome for inválido, se não
              conectar ao banco, se a imagem padrão falhar ou se o MySQL
              recusar o comando.
        """

        # Validação: `not nome` cobre None e "" ; `.strip()` cobre "   ".
        if not nome or not nome.strip():
            return False, None, "O nome do usuário não pode ficar vazio."

        # Remove espaços sobrando no início e no fim do nome.
        nome = nome.strip()

        # Abre uma nova conexão com o banco.
        conexao = criar_conexao()

        # `criar_conexao` devolve None quando não consegue conectar.
        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        # Começa como None para o `finally` saber se o cursor chegou a ser criado.
        garsom = None

        try:
            # Prepara a imagem de perfil padrão (sem argumento = imagem padrão).
            sucesso_img, dados_img, erro_img = tratar_IMG_usuarios()

            if not sucesso_img or dados_img is None:
                return False, None, erro_img or "Não foi possível carregar a imagem padrão."

            # Desempacota a dupla (bytes da imagem, tipo MIME).
            image_binaria_perfil, image_tipo_mime = dados_img

            # Cria o cursor ("garçom") que executará o comando SQL.
            garsom = conexao.cursor()

            # %s são marcadores de posição: o conector troca cada um pelo valor
            # correspondente de `valores`, já tratado de forma segura.
            sql = """
            INSERT INTO usuarios (
                nome, imagem_binaria_perfil, imagem_tipo_mime
            )
            VALUES (%s, %s, %s)
            """

            # A ordem dos valores segue a ordem das colunas no INSERT.
            valores = (
                nome,
                image_binaria_perfil,
                image_tipo_mime,
            )

            garsom.execute(sql, valores)

            # `lastrowid` = ID gerado pelo AUTO_INCREMENT neste INSERT.
            novo_usuario_id = garsom.lastrowid

            # Grava a alteração de forma definitiva no banco.
            conexao.commit()

            return True, novo_usuario_id, None

        except Exception as e:

            # Desfaz qualquer alteração pendente. Está dentro de outro try
            # porque o próprio rollback pode falhar (ex.: conexão já caída) e
            # isso não deve esconder o erro original.
            try:
                conexao.rollback()

            except Exception:
                pass

            return False, None, f"Erro ao cadastrar usuário: {e}"

        finally:
            # Sempre executa, com sucesso ou erro: libera cursor e conexão.
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 2. LER (LISTAR) USUÁRIOS
    # =========================================================================

    def listar_usuarios(
        self
    ) -> tuple[bool, list[tuple] | None, str | None]:
        """Busca todos os usuários cadastrados, ordenados pelo ID.

        Retorna (sucesso, usuarios, erro):
            - (True, lista_de_tuplas, None): cada tupla é uma linha da tabela
              na ordem das colunas:
                  (id, nome, imagem_binaria_perfil, imagem_tipo_mime)
              Se não houver usuários, a lista vem vazia (isso NÃO é erro).
            - (False, None, "mensagem"): falha de conexão ou de consulta.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # SELECT * traz todas as colunas; ORDER BY id mantém a ordem de
            # cadastro (o primeiro usuário criado aparece primeiro).
            sql = "SELECT * FROM usuarios ORDER BY id"

            garsom.execute(sql)

            # `fetchall` traz TODAS as linhas do resultado de uma só vez.
            usuarios = garsom.fetchall()

            # Não há commit/rollback aqui: SELECT apenas lê, não altera dados.
            return True, usuarios, None

        except Exception as e:
            return False, None, f"Erro ao listar usuários: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    def pegar_dados_usuario_atual(
        self,
        Usuario_ID: int
    ) -> tuple[bool, tuple | None, str | None]:
        """Busca no banco os dados ATUAIS de UM usuário, pelo ID.

        Diferença para `listar_usuarios`: aquela traz todos os usuários (e a
        lista fica guardada na sessão, podendo ficar desatualizada depois de
        trocar nome ou foto). Esta consulta o banco na hora, então sempre
        devolve o nome e a foto mais recentes. É usada por `ativar_usuario`
        (Systems/diversos.py).

        Parâmetros:
            Usuario_ID: ID (número inteiro) do usuário. Se vier um texto, como
                um nome, o MySQL não encontra nenhuma linha.

        Retorna (sucesso, usuario, erro):
            - (True, tupla, None): a linha da tabela, na ordem das colunas
                  (id, nome, imagem_binaria_perfil, imagem_tipo_mime)
              ou seja: [0] id, [1] nome, [2] foto em bytes, [3] tipo da foto;
            - (False, None, "mensagem"): falha de conexão, erro do MySQL ou
              nenhum usuário com esse ID.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # WHERE id = %s filtra por UM usuário. O ID vai pelo marcador %s
            # (e não colado no texto do SQL), o que protege contra SQL Injection.
            sql = "SELECT * FROM usuarios WHERE id = %s;"
            values = (Usuario_ID,)

            garsom.execute(sql, values)

            # `fetchone` traz só a PRIMEIRA linha do resultado, ou None se o
            # SELECT não encontrou nada. Como `id` é chave primária, há no
            # máximo uma linha.
            usuario = garsom.fetchone()

            # None = nenhum usuário com esse ID.
            if usuario is None:
                return False, None, f'Erro ao pegar dados do comando SELECT:'

            # Não há commit/rollback aqui: SELECT apenas lê, não altera dados.
            return True, usuario, None

        except Exception as e:
            # Qualquer erro do MySQL ou do conector. A mensagem inclui o ID para
            # facilitar achar no log qual consulta falhou.
            return False, None, f"Erro ao Pegar dados do usuário ID - {Usuario_ID}: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 3. ATUALIZAR USUÁRIO
    # =========================================================================

    def atualizar_usuario(
        self,
        id: int,
        novo_nome: str | None = None,
        nova_img: UploadedFile | None = None
    ) -> tuple[bool, str | None, str | None]:
        """Atualiza o nome e/ou a foto de perfil de um usuário.

        Os dois parâmetros de alteração são OPCIONAIS, mas pelo menos um deve
        ser informado. Só os campos recebidos entram no UPDATE (o SQL é
        montado dinamicamente), então enviar só o nome não mexe na foto, e
        vice-versa.

        Parâmetros:
            id: ID do usuário a ser alterado.
            novo_nome: novo nome (opcional). Não pode ser vazio.
            nova_img: novo arquivo de imagem enviado pelo usuário (opcional).

        Retorna (sucesso, mensagem, erro):
            - (True, "Usuário atualizado com sucesso!", None);
            - (False, None, "mensagem") se nada foi informado, se o nome for
              vazio, se a imagem for inválida, se o usuário não existir ou se
              o MySQL recusar o comando.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            # Se nem nome nem imagem foram enviados, não há o que atualizar.
            if novo_nome is None and nova_img is None:
                return False, None, "Nenhum dado fornecido para atualização."

            garsom = conexao.cursor()

            # Duas listas paralelas montadas conforme os campos recebidos:
            #   campos_atualizacao -> trechos do SET (ex.: "nome = %s")
            #   valores            -> valores que preencherão cada %s, na ordem
            campos_atualizacao = []
            valores = []

            # ---- Campo opcional: nome ---------------------------------------
            if novo_nome is not None:
                if not novo_nome.strip():
                    return False, None, "O nome do usuário não pode ficar vazio."

                campos_atualizacao.append("nome = %s")
                valores.append(novo_nome.strip())

            # ---- Campo opcional: imagem de perfil ---------------------------
            if nova_img is not None:
                # Valida o arquivo enviado e extrai (bytes, tipo MIME).
                sucesso_img, dados_img, erro_img = tratar_IMG_usuarios(nova_img)

                if not sucesso_img or dados_img is None:
                    return False, None, erro_img or "Não foi possível carregar a imagem."

                img_binaria, img_mime = dados_img

                # A imagem ocupa DUAS colunas: os bytes e o tipo MIME.
                campos_atualizacao.append("imagem_binaria_perfil = %s")
                campos_atualizacao.append("imagem_tipo_mime = %s")
                valores.extend([img_binaria, img_mime])

            # Junta os trechos com vírgula, ex.:
            #   SET nome = %s, imagem_binaria_perfil = %s, imagem_tipo_mime = %s
            # (somente nomes de colunas fixos do próprio código entram no texto
            # do SQL; os valores do usuário vão sempre pelos %s.)
            sql = f"""
            UPDATE usuarios
            SET {', '.join(campos_atualizacao)}
            WHERE id = %s
            """

            # O ID do WHERE é o último %s, por isso é o último valor da lista.
            valores.append(id)
            garsom.execute(sql, tuple(valores))

            # `rowcount` = quantas linhas foram alteradas. Zero significa que o
            # ID não existe OU que os novos valores eram idênticos aos antigos
            # (o MySQL não conta linhas "alteradas" para o mesmo valor).
            if garsom.rowcount == 0:
                conexao.rollback()
                return False, None, "Usuário não encontrado ou nenhum dado foi alterado."

            conexao.commit()
            return True, "Usuário atualizado com sucesso!", None

        except Exception as e:
            conexao.rollback()
            return False, None, f"Erro ao atualizar usuário: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()


    # =========================================================================
    # 4. EXCLUIR USUÁRIO
    # =========================================================================

    def deletar_usuario(
        self,
        id: int
    ) -> tuple[bool, str | None, str | None]:
        """Exclui um usuário do banco, JUNTO com todos os Pokémons dele.

        Como a tabela `pokemons` aponta para `usuarios` por chave estrangeira,
        o usuário não pode ser apagado enquanto tiver Pokémons. Por isso esta
        função executa DOIS comandos na MESMA transação:
            1. apaga os Pokémons do usuário;
            2. apaga o usuário.
        Se qualquer um falhar, nada é gravado (rollback) — nunca sobra um
        usuário "pela metade". Isso funciona mesmo em bancos criados com a
        versão antiga do pokedex.sql (sem ON DELETE CASCADE).

        Parâmetros:
            id: ID do usuário a ser excluído.

        Retorna (sucesso, mensagem, erro):
            - (True, "Usuário deletado com sucesso!", None);
            - (False, None, "Nenhum usuário encontrado.") se o ID não existe;
            - (False, None, "Erro ao deletar usuário: ...") para falhas do MySQL.
        """

        conexao = criar_conexao()

        if conexao is None:
            return False, None, "Não foi possível conectar ao banco."

        garsom = None

        try:
            garsom = conexao.cursor()

            # Passo 1: apaga primeiro os Pokémons do usuário (os "filhos"),
            # senão a chave estrangeira impediria apagar o usuário (o "pai").
            # Ainda NÃO há commit: se o passo 2 falhar, este DELETE é desfeito.
            sql_pokemons = "DELETE FROM pokemons WHERE usuario_id = %s"

            # O segundo argumento precisa ser uma tupla; a vírgula em `(id,)`
            # é o que faz o Python criar uma tupla de um único item.
            garsom.execute(sql_pokemons, (id,))

            # Passo 2: apaga o usuário em si.
            sql = "DELETE FROM usuarios WHERE id = %s"

            garsom.execute(sql, (id,))

            # `rowcount` agora se refere ao ÚLTIMO comando (o DELETE do usuário).
            # Nenhuma linha afetada = nenhum usuário com esse ID.
            if garsom.rowcount == 0:
                conexao.rollback()
                return False, None, "Nenhum usuário encontrado."

            conexao.commit()
            return True, "Usuário deletado com sucesso!", None

        except Exception as e:
            conexao.rollback()
            return False, None, f"Erro ao deletar usuário: {e}"

        finally:
            if garsom is not None:
                garsom.close()

            conexao.close()
