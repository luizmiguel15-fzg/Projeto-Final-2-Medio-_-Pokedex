-- =============================================================================
-- ARQUIVO: pokedex.sql
-- -----------------------------------------------------------------------------
-- Script de criação do banco de dados da Pokédex (MySQL / MariaDB).
--
-- Como usar:
--   Execute este arquivo UMA vez antes de rodar o programa Python, por exemplo:
--       mysql -u root -p < pokedex.sql
--   ou abrindo-o no MySQL Workbench / phpMyAdmin e executando tudo.
--
-- É seguro executar mais de uma vez: todos os comandos de criação usam
-- "IF NOT EXISTS", então nada é recriado nem apagado se já existir.
--
-- Estrutura geral (a ordem dos blocos importa):
--   1. CRIAÇÃO DO BANCO DE DADOS
--   2. CONFIGURAÇÕES DO SERVIDOR
--   3. TABELA `usuarios`   (precisa vir primeiro, pois `pokemons` depende dela)
--   4. TABELA `pokemons`   (referencia `usuarios` por chave estrangeira)
-- =============================================================================


-- =============================================================================
-- 1. CRIAÇÃO DO BANCO DE DADOS
-- =============================================================================

-- Cria o banco `pokedex` apenas se ele ainda não existir.
--   CHARACTER SET utf8mb4        -> suporta todos os caracteres Unicode
--                                   (acentos do português, emojis, etc.).
--   COLLATE utf8mb4_unicode_ci   -> regra de comparação/ordenação de texto;
--                                   "ci" = case-insensitive (não diferencia
--                                   maiúsculas de minúsculas nas buscas).
CREATE DATABASE IF NOT EXISTS pokedex
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Seleciona o banco `pokedex` como o banco ativo: todos os comandos seguintes
-- (como CREATE TABLE) serão executados dentro dele.
USE pokedex;


-- =============================================================================
-- 2. CONFIGURAÇÕES DO SERVIDOR
-- =============================================================================

-- Aumenta para 32 MB (33554432 bytes = 32 * 1024 * 1024) o tamanho máximo de
-- um único pacote/comando que o servidor aceita receber.
-- Isso é necessário porque as imagens dos Pokémons e dos usuários são salvas
-- DENTRO do banco (colunas LONGBLOB) e viajam no comando INSERT/UPDATE; com o
-- limite padrão, imagens maiores poderiam ser recusadas.
-- ATENÇÃO: "SET GLOBAL" exige permissão de administrador (o usuário `root`
-- tem) e vale apenas até o servidor MySQL ser reiniciado.
SET GLOBAL max_allowed_packet = 33554432;


-- =============================================================================
-- 3. TABELA `usuarios`
-- -----------------------------------------------------------------------------
-- Guarda os "mestres Pokémon" (perfis) cadastrados no sistema. Cada usuário
-- possui um nome e uma imagem de perfil armazenada diretamente no banco.
-- =============================================================================

CREATE TABLE IF NOT EXISTS usuarios (

    -- Identificador único do usuário. Número inteiro positivo (UNSIGNED) que
    -- o próprio MySQL incrementa a cada novo cadastro (AUTO_INCREMENT).
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,

    -- Nome do mestre Pokémon (até 200 caracteres). Obrigatório.
    nome VARCHAR(200) NOT NULL,

    -- Foto de perfil guardada como bytes brutos (LONGBLOB comporta até 4 GB).
    -- Pode ser NULL (sem imagem), embora o programa sempre grave uma imagem
    -- padrão ao cadastrar o usuário.
    imagem_binaria_perfil LONGBLOB NULL,

    -- Tipo da imagem (ex.: "image/png", "image/jpeg"). Serve para o programa
    -- saber como interpretar os bytes guardados em `imagem_binaria_perfil`.
    imagem_tipo_mime VARCHAR(100) NULL,

    -- Define `id` como chave primária: identifica cada linha de forma única
    -- e cria um índice para buscas rápidas por id.
    PRIMARY KEY (id)

-- InnoDB é o mecanismo de armazenamento que suporta transações
-- (commit/rollback) e chaves estrangeiras — ambos usados pelo programa.
) ENGINE=InnoDB;


-- =============================================================================
-- 4. TABELA `pokemons`
-- -----------------------------------------------------------------------------
-- Guarda os Pokémons cadastrados por cada usuário. Cada linha pertence a
-- exatamente um usuário (relação 1 usuário -> N pokémons).
-- =============================================================================

CREATE TABLE IF NOT EXISTS pokemons (

    -- ---- Identificação -------------------------------------------------------

    -- Identificador único do registro (gerado automaticamente).
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,

    -- Dono do Pokémon: guarda o `id` do usuário na tabela `usuarios`.
    -- A ligação é garantida pela FOREIGN KEY mais abaixo.
    usuario_id INT UNSIGNED NOT NULL,

    -- Número do Pokémon na Pokédex oficial (ex.: Pikachu = 25).
    numero_pokedex INT UNSIGNED NOT NULL,

    -- ---- Dados básicos -------------------------------------------------------

    -- Nome do Pokémon (ex.: "pikachu"). Obrigatório.
    nome VARCHAR(200) NOT NULL,

    -- Tipo principal (ex.: "electric"). Obrigatório.
    tipo_principal VARCHAR(30) NOT NULL,

    -- Tipo secundário (ex.: "flying"). Opcional, pois nem todo Pokémon tem dois.
    tipo_secundario VARCHAR(30) NULL,

    -- ---- Medidas físicas -----------------------------------------------------

    -- Altura em metros. DECIMAL(6,2) = até 6 dígitos no total, 2 após a vírgula
    -- (ex.: 1234.56). DECIMAL é exato, ao contrário de FLOAT.
    altura_m DECIMAL(6,2) NULL,

    -- Peso em quilogramas. DECIMAL(7,2) = até 7 dígitos, 2 casas decimais.
    peso_kg DECIMAL(7,2) NULL,

    -- ---- Atributos de batalha ------------------------------------------------

    -- Pontos de vida (HP) usados na batalha. Opcional.
    vida INT UNSIGNED NULL,

    -- Poder de ataque usado na batalha. Opcional.
    ataque INT UNSIGNED NULL,

    -- ---- Informações extras --------------------------------------------------

    -- Habilidade principal (ex.: "static"). Opcional.
    habilidade VARCHAR(100) NULL,

    -- Descrição livre em texto longo. Opcional.
    descricao TEXT NULL,

    -- ---- Imagem --------------------------------------------------------------

    -- Imagem do Pokémon em bytes (baixada da PokéAPI ou imagem padrão de erro).
    imagem_binaria LONGBLOB NULL,

    -- Tipo MIME da imagem (ex.: "image/png").
    imagem_tipo_mime VARCHAR(100) NULL,

    -- ---- Controle de datas (preenchidas automaticamente pelo MySQL) ----------

    -- Data/hora em que o registro foi criado. O valor padrão é o momento atual
    -- do INSERT; não é preciso informar nada pelo programa.
    criado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    -- Data/hora da última modificação. Começa igual a `criado_em` e é
    -- atualizada automaticamente (ON UPDATE) sempre que a linha for alterada.
    atualizado_em TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    -- ---- Chaves e restrições -------------------------------------------------

    -- Chave primária: `id` identifica cada Pokémon cadastrado de forma única.
    PRIMARY KEY (id),

    -- Chave estrangeira: `usuario_id` só aceita valores que existam em
    -- `usuarios.id`. Assim é impossível cadastrar um Pokémon para um usuário
    -- inexistente.
    -- ON DELETE CASCADE: ao apagar um usuário, o MySQL apaga automaticamente
    -- todos os Pokémons dele (sem isso, a exclusão do usuário seria RECUSADA
    -- enquanto ele tivesse Pokémons cadastrados).
    CONSTRAINT fk_pokemon_usuario
        FOREIGN KEY (usuario_id)
        REFERENCES usuarios(id)
        ON DELETE CASCADE,

    -- Restrição de unicidade: o mesmo usuário não pode cadastrar duas vezes o
    -- mesmo `numero_pokedex`. Usuários DIFERENTES podem ter o mesmo Pokémon.
    UNIQUE KEY uq_usuario_pokemon
        (usuario_id, numero_pokedex),

    -- ---- Índices (aceleram buscas e filtros) ---------------------------------

    -- Busca/ordenação por número da Pokédex.
    KEY idx_pokemon_numero (numero_pokedex),

    -- Busca por nome do Pokémon.
    KEY idx_pokemon_nome (nome),

    -- Busca de todos os Pokémons de um usuário (usada na listagem do programa:
    -- SELECT * FROM pokemons WHERE usuario_id = ...).
    KEY idx_pokemon_usuario (usuario_id)

) ENGINE=InnoDB;