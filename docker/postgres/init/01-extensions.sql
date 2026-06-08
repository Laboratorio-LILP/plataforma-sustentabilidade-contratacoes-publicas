-- ============================================================
-- PESCP — extensões Postgres requeridas no boot do container.
-- Roda apenas na primeira inicialização do banco (Postgres
-- carrega /docker-entrypoint-initdb.d/*.sql se o data dir está
-- vazio).
-- ============================================================

-- Suporte a unaccent para busca em português (busca por
-- "Critério" também encontra "Criterio")
CREATE EXTENSION IF NOT EXISTS unaccent;

-- pg_trgm para similaridade aproximada (busca tolerante a erros
-- de digitação em iteração futura)
CREATE EXTENSION IF NOT EXISTS pg_trgm;
