-- Exercício 15 — dados fictícios de produtos, vendas e campanhas (demonstração).

CREATE TABLE produtos (
    id SERIAL PRIMARY KEY,
    sku VARCHAR(64) UNIQUE NOT NULL,
    nome VARCHAR(200) NOT NULL,
    descricao TEXT,
    preco_unitario NUMERIC(12, 2) NOT NULL CHECK (preco_unitario >= 0),
    quantidade_estoque INT NOT NULL DEFAULT 0 CHECK (quantidade_estoque >= 0),
    categoria VARCHAR(100)
);

CREATE TABLE vendas (
    id SERIAL PRIMARY KEY,
    produto_id INT NOT NULL REFERENCES produtos (id),
    quantidade INT NOT NULL CHECK (quantidade > 0),
    valor_total NUMERIC(12, 2) NOT NULL CHECK (valor_total >= 0),
    canal VARCHAR(40) NOT NULL DEFAULT 'online',
    data_venda TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_vendas_produto ON vendas (produto_id);
CREATE INDEX idx_vendas_data ON vendas (data_venda);

CREATE TABLE campanhas_marketing (
    id SERIAL PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    texto TEXT NOT NULL,
    produtos_ids INT[] NOT NULL DEFAULT '{}',
    criado_em TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Produtos iniciais
INSERT INTO produtos (sku, nome, descricao, preco_unitario, quantidade_estoque, categoria)
VALUES
    ('SKU-AUR-X1', 'Auriculares Bluetooth X1', 'Som stereo, ANC basico.', 89.90, 140, 'Audio'),
    ('SKU-CAM-PRO', 'Camara IP Pro', '1080p, visao noturna.', 149.00, 45, 'Seguranca'),
    ('SKU-TAB-LITE', 'Tablet Lite 10"', 'Ecran 10 polegadas, 64 GB.', 229.90, 30, 'Informatica'),
    ('SKU-CAF-DEL', 'Maquina Cafe Delta', 'Capsulas compatíveis.', 119.00, 0, 'Cozinha'),
    ('SKU-FIT-BAND', 'Pulseira Fitness', 'Monitoriza sono e passos.', 59.90, 200, 'Wearables');

-- Vendas de exemplo (últimos dias)
INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 3, 3 * preco_unitario, 'online', NOW() - INTERVAL '10 days'
FROM produtos WHERE sku = 'SKU-AUR-X1';

INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 1, 1 * preco_unitario, 'loja', NOW() - INTERVAL '8 days'
FROM produtos WHERE sku = 'SKU-CAM-PRO';

INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 2, 2 * preco_unitario, 'online', NOW() - INTERVAL '5 days'
FROM produtos WHERE sku = 'SKU-TAB-LITE';

INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 5, 5 * preco_unitario, 'online', NOW() - INTERVAL '3 days'
FROM produtos WHERE sku = 'SKU-FIT-BAND';

INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 2, 2 * preco_unitario, 'marketplace', NOW() - INTERVAL '2 days'
FROM produtos WHERE sku = 'SKU-AUR-X1';

INSERT INTO vendas (produto_id, quantidade, valor_total, canal, data_venda)
SELECT id, 1, 1 * preco_unitario, 'online', NOW() - INTERVAL '1 day'
FROM produtos WHERE sku = 'SKU-CAM-PRO';
