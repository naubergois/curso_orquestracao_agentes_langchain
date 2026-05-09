-- Exercício 19 — memória de chat por utilizador (resumos persistentes, PostgreSQL).

CREATE TABLE utilizadores (
    id SERIAL PRIMARY KEY,
    external_id VARCHAR(128) UNIQUE NOT NULL,
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE resumo_acumulado (
    utilizador_id INT PRIMARY KEY REFERENCES utilizadores (id) ON DELETE CASCADE,
    texto TEXT NOT NULL DEFAULT '',
    actualizado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sessoes_chat (
    id SERIAL PRIMARY KEY,
    utilizador_id INT NOT NULL REFERENCES utilizadores (id) ON DELETE CASCADE,
    session_uuid UUID NOT NULL,
    resumo_sessao TEXT,
    criada_em TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    encerrada_em TIMESTAMPTZ,
    UNIQUE (session_uuid)
);

CREATE INDEX idx_sessoes_utilizador ON sessoes_chat (utilizador_id, criada_em DESC);

-- Utilizador de demonstração
INSERT INTO utilizadores (external_id)
VALUES ('demo-alice')
ON CONFLICT (external_id) DO NOTHING;

INSERT INTO resumo_acumulado (utilizador_id, texto)
SELECT u.id, ''
FROM utilizadores u
WHERE u.external_id = 'demo-alice'
ON CONFLICT (utilizador_id) DO NOTHING;
