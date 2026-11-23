Projeto final da materia de DS - Desenvolvimento de Sistemas. Letrada pelo Dr. Professor Humberto Augusto Piovesana Zanetti

Desenvolvido por: 
- Luiz Miguel Franciscon Zolgio Gonzaga 
- Leticia Oliveira de Andrade 
- Isabela Carlos Pereira

# Pokédex — Banco de Dados

Aplicação web desenvolvida em **Python e Streamlit**, com banco de dados **MySQL/MariaDB**, que permite criar perfis de usuários (mestres Pokémon), cadastrar e gerenciar Pokémon, visualizar informações e participar de batalhas.

Os dados dos usuários e Pokémon são armazenados no banco de dados. Informações e imagens de Pokémon também são obtidas pela internet, por meio da PokéAPI.

## Funcionalidades

- Cadastro e seleção de perfis de usuários.
- Personalização do perfil, incluindo imagem.
- Cadastro e gerenciamento de Pokémon por usuário.
- Consulta de informações dos Pokémon.
- Batalhas com Pokémon e inimigos selecionados/sorteados pelo sistema.
- Interface web criada com Streamlit.
- Armazenamento de imagens no banco de dados.

## Tecnologias utilizadas

- Python
- Streamlit
- MySQL ou MariaDB
- MySQL Connector/Python
- Requests
- PokéAPI
- HTML/CSS (estilização da interface)

## 1. Requisitos

Instale/configure os itens abaixo antes de executar o projeto:

- **Python 3** — recomenda-se uma versão recente compatível com Streamlit e as bibliotecas usadas no projeto.
- **XAMPP** (ou outra instalação de MySQL/MariaDB). O projeto precisa do serviço de banco de dados; o Apache não é necessário para o Streamlit em si.
- **Navegador** (Chrome, Edge, Firefox etc.).
- **Internet** — usada para buscar informações dos Pokémon na PokéAPI e carregar recursos externos.

### Instalação do Python

1. Acesse https://www.python.org/downloads/.
2. Baixe e execute o instalador do Python para Windows.
3. Durante a instalação, marque **Add Python to PATH** (se essa opção estiver disponível).
4. Conclua a instalação.
5. Abra o Prompt de Comando e confirme:

```bash
python --version
```

Se o comando `python` não funcionar, tente:

```bash
py --version
```

### Instalação do XAMPP

1. Acesse https://www.apachefriends.org/.
2. Baixe o XAMPP para seu sistema operacional e instale-o.
3. Abra o **XAMPP Control Panel**.
4. Na linha **MySQL**, clique em **Start**.
5. (Opcional, mas recomendado para administrar o banco visualmente) Na linha **Apache**, clique em **Start** também.

> O Apache é iniciado para disponibilizar o phpMyAdmin pelo XAMPP. A aplicação Streamlit não depende do Apache: ela é executada pelo comando Streamlit no Python.

## 2. Preparar o banco de dados

O projeto inclui o script SQL em `Banco_De_Dados/pokedex.sql`. Ele cria o banco `pokedex` e as tabelas `usuarios` e `pokemons`.

### Opção A — Usando phpMyAdmin (interface gráfica do XAMPP)

1. Com o MySQL e, para esta opção, o Apache iniciados no XAMPP, abra o navegador.
2. Acesse http://localhost/phpmyadmin/.
3. Entre na aba **Importar**.
4. Em **Selecionar arquivo**, escolha `Banco_De_Dados/pokedex.sql` dentro da pasta do projeto.
5. Mantenha as opções padrão e execute a importação.
6. Confirme que o banco `pokedex` e as tabelas `usuarios` e `pokemons` foram criados.

### Opção B — Usando o terminal MySQL

Se o cliente `mysql` estiver disponível no terminal, abra o Prompt de Comando na pasta do projeto e execute (ajuste o caminho do executável se o MySQL estiver instalado em outro local):

```bash
mysql -u root < Banco_De_Dados/pokedex.sql
```

Se o usuário `root` tiver senha, use o comando abaixo e digite a senha quando solicitado:

```bash
mysql -u root -p < Banco_De_Dados/pokedex.sql
```

> O script SQL define `max_allowed_packet` para 32 MB e cria as tabelas com `IF NOT EXISTS`. A configuração global do pacote pode exigir privilégios administrativos e é temporária, podendo voltar ao padrão após reiniciar o servidor.

## 3. Configuração da conexão

A conexão com o MySQL é definida em:

`Banco_De_Dados/conecao_BD.py`

Atualmente, o projeto utiliza estas configurações:

| Configuração | Valor atual    |
| -------------- | -------------- |
| Host           | `localhost`  |
| Banco          | `pokedex`    |
| Usuário       | `root`       |
| Senha          | vazia (`''`) |

Se seu MySQL estiver usando outra porta, usuário ou senha, altere os valores dentro da função `criar_conexao()` desse arquivo.

> **Atenção:** usuário `root` sem senha é uma configuração de desenvolvimento/local. Não utilize essa configuração em um servidor exposto ou ambiente de produção.

## 4. Instalar as bibliotecas Python

Abra o terminal na pasta principal do projeto — a pasta `Pokedex_BD`, onde está o arquivo `Main.py` — e execute:

```bash
python -m pip install streamlit mysql-connector-python requests
```

Os pacotes instalados são:

- `streamlit` — interface web e execução do aplicativo.
- `mysql-connector-python` — conexão Python com MySQL/MariaDB.
- `requests` — requisições HTTP usadas para consultar dados e imagens.

Se o comando `python` não for reconhecido, tente usar `py`:

```bash
py -m pip install streamlit mysql-connector-python requests
```

## 5. Iniciar o projeto (ordem correta)

Sempre que for utilizar a aplicação:

1. Abra o **XAMPP Control Panel**.
2. Na linha **MySQL**, clique em **Start** e aguarde o serviço ficar ativo.
3. Se precisar abrir o phpMyAdmin para consultar/administrar o banco, inicie também o **Apache**.
4. Confira se o banco `pokedex` já existe. Na primeira utilização, importe `Banco_De_Dados/pokedex.sql` seguindo a seção anterior. Não é necessário importar novamente se o banco e as tabelas já estiverem criados.
5. Abra o Prompt de Comando, PowerShell ou terminal do VS Code.
6. Entre na pasta do projeto. Exemplo (ajuste para o local onde você extraiu os arquivos):

```bash
cd caminho\para\Pokedex_BD
```

7. Execute o Streamlit:

```bash
python -m streamlit run Main.py
```

Ou, caso utilize o launcher `py`:

```bash
py -m streamlit run Main.py
```

8. O Streamlit exibirá um endereço local no terminal, normalmente `http://localhost:8501`. Abra esse endereço no navegador para utilizar a Pokédex.

> Mantenha o terminal do Streamlit aberto enquanto estiver usando o programa. Para encerrar, volte ao terminal e pressione `Ctrl + C`. O MySQL pode ser desligado pelo XAMPP quando terminar.

## 6. Estrutura de pastas

```text
Pokedex_BD/
├── Main.py                       # Entrada e roteamento principal do Streamlit
├── style.css                     # Estilos CSS da interface
├── Banco_De_Dados/
│   ├── conecao_BD.py            # Configuração/conexão com o MySQL
│   └── pokedex.sql              # Criação do banco e das tabelas
├── Classes/
│   ├── Pokemon.py                # Classe e operações relacionadas a Pokémon
│   └── Usuario.py                # Classe e operações relacionadas a usuários
├── Pages/                         # Telas da aplicação
│   ├── Inicio.py
│   ├── Cadastro.py
│   ├── SelecionarUsuario.py
│   ├── Pokemons.py
│   ├── Batalha.py
│   └── Perfil.py
├── Systems/                       # Funções de apoio, dados, imagens e estilos
│   ├── constantes.py
│   ├── dados_pokemons.py
│   ├── diversos.py
│   ├── estilos.py
│   ├── menu_lateral.py
│   └── tratamento_IMGs.py
└── IMGs/                          # Imagens utilizadas na aplicação
```

## 7. Solução de problemas

### Erro ao conectar ao MySQL

- Confira se o MySQL está iniciado no XAMPP.
- Verifique host, banco, usuário, senha e porta em `Banco_De_Dados/conecao_BD.py`.
- Confirme que o banco `pokedex` existe e que o script SQL foi executado.
- Se o MySQL estiver configurado para uma porta diferente da padrão, ajuste a conexão no código.

### `streamlit` não é reconhecido

Instale ou reinstale as bibliotecas:

```bash
python -m pip install streamlit mysql-connector-python requests
```

E execute pelo módulo:

```bash
python -m streamlit run Main.py
```

### Erro ao carregar Pokémon ou imagens

- Confira sua conexão com a internet.
- A aplicação consulta a PokéAPI; se o serviço estiver indisponível, alguns dados podem não carregar.
- Consulte o arquivo `Logs_error.txt` na pasta do projeto para mensagens de erro registradas.

### Porta do Streamlit ocupada

Se a porta padrão `8501` estiver sendo usada, o Streamlit pode indicar outra porta disponível no terminal. Acesse o endereço exibido.

## 8. Créditos — Inteligências Artificiais

Durante o desenvolvimento deste projeto, ferramentas de Inteligência Artificial foram utilizadas como apoio. Preencha abaixo as ferramentas e suas contribuições:

- **IA utilizada:** Claude IA

  1. **Prompt utilizado:**
    Comente cada arquivo .py e o .sql do projeto em pt-BR, com docstrings detalhadas (o que a função faz, parâmetros, retorno e efeitos colaterais). Agrupe as funções por assunto dentro do próprio arquivo, com um       cabeçalho em cada grupo e um índice de organização no topo do arquivo. Não mova código entre arquivos.

      **Resposta da IA:**
          Comentei todos os arquivos. Cada um ganhou um cabeçalho que explica o papel dele e a ordem das seções. As funções ficaram agrupadas por assunto, cada grupo com seu título (por exemplo "1. IMPORTAÇÕES", "2.          DIÁLOGOS", "3. DESENHO DA PÁGINA"). Todas têm docstring com o que fazem, os parâmetros e o retorno. No .sql, expliquei cada tabela, coluna e chave.



  2. **Prompt utilizado:**
        Estou com um problema. Toda vez que meu usuário troca de NOME ele não consegue logo depois trocar de IMAGEM. Descobri que o usuario_id estava recebendo o NOME do usuário e não o número (int) do id. Tentei           corrigir com a função pegar_dados_usuario_atual. Possível culpado: o trocar_usuario? (log: trocar_usuario recebeu 'Iiiiii' (str), que não é um ID válido. IDs existentes: [1, 3])
     
     **Resposta da IA:**
          O log confirmou que o culpado era o trocar_usuario. Ele é o callback on_change do selectbox da barra lateral. O selectbox usa o nome como texto de exibição. Quando o nome muda, o Streamlit trata a caixa             como um widget novo e dispara o on_change com o texto antigo ('Iiiiii'). Esse texto ia parar no usuario_id.

     >Em trocar_usuario, validar que o valor recebido está na lista de ids existentes. Se não for um id válido, o valor é ignorado.
     >
     >Em ativar_usuario, conferir com isinstance(int), para o erro aparecer no log em vez de quebrar depois.
     >
     >Em Perfil.py, chamar atualizar_lista_usuarios() depois de salvar nome ou imagem. Assim a lista da sessão não fica velha.

---

© 2026 Luiz Miguel Franciscon Zolgio Gonzaga; Leticia Oliveira de Andrade & Isabela Carlos Pereira

Desenvolvio como projeto final do 2° Medio
