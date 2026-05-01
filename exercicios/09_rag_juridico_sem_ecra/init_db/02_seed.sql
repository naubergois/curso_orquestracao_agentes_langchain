-- Dados de demonstração (sem valor jurídico real).
INSERT INTO processos (
    numero, tribunal, tipo_acao, estado, data_distribuicao,
    partes, objeto, sumario_factual, valor_causa, temas
) VALUES
(
    '1234/25.3T8PRT',
    'Tribunal Judicial da Comarca de Lisboa — 8.ª Vara Cível',
    'Ação declarativa de condenação',
    'Pendente — despacho saneador',
    '2025-01-15',
    'Autor: Sociedade Gamma, Lda. | Réu: David Silva',
    'Declaração de existência de negócio jurídico válido e condenação ao cumprimento de contrato-promessa.',
    'Discussão sobre validade da manifestação de vontades e existência de causa e objeto determinados ou determináveis.',
    42000.00,
    'negócio jurídico; contrato; declaração negocial; vontade; causa; objeto'
),
(
    '892/24.2T8FDC',
    'Tribunal Judicial do Porto — Juízo de Execução',
    'Execução por quantia certa',
    'Pendente — tentativa de penhora',
    '2024-11-02',
    'Exequente: Banco Delta, S.A. | Executado: Maria Ferreira',
    'Execução fundada em título executivo extrajudicial sobre dívida contratual.',
    'Questões subsidiárias sobre boa-fé nas negociações pré-contratuais (art. 227.º CC) e integração de cláusulas.',
    18500.50,
    'boa-fé contratual; negociações; interpretação; contrato; execução'
),
(
    '56/23.1T8CRT',
    'Tribunal da Relação de Coimbra — seção cível',
    'Apelação — responsabilidade civil extracontratual',
    'Julgado — aguarda trânsito',
    '2023-06-20',
    'Apelante: João Reis | Apelado: Município exemplo e outro',
    'Indemnização por danos patrimoniais e não patrimoniais na sequência de acidente com imputação subjetiva.',
    'Discussão central sobre nexo de causalidade, culpa e âmbito indemnizatório.',
    75000.00,
    'responsabilidade civil; culpa; causalidade; indemnização; danos'
),
(
    '4321/25.1T8PVT',
    'Tribunal Judicial de Braga — 1.ª Vara Cível',
    'Exceção dilatória de prescrição e caducidade (incidental)',
    'Pendente — audiência prévia',
    '2025-03-01',
    'Requerente: Paulo Antunes | Requerido: Seguradora Omega, S.A.',
    'Incidente sobre prescrição da pretensão resarcitória face a prazo interruptivo e caducidade de direito material.',
    'Distinção pedagógica entre prescrição (liberação da obrigação) e caducidade (extinção do próprio direito).',
    12000.00,
    'prescrição; caducidade; prazo; interrupção; direito material'
),
(
    '777/24.4T8PRT',
    'Tribunal Judicial da Comarca de Lisboa — 4.ª Vara Comercial',
    'Ação declarativa com cumprimento subsidiário',
    'Em saneamento',
    '2024-08-12',
    'Autor: Investimentos Lua, S.A. | Réu: Hórus — Engenharia, Lda.',
    'Resolução contratual por incumprimento definitivo e restituição de prestações com juros.',
    'Análise de mora do devedor e resolução com fundamento em clausula resolutiva tácita negociada.',
    98000.00,
    'resolução; incumprimento; mora; contrato; restituição'
)
ON CONFLICT (numero) DO NOTHING;

-- Liga cada processo a um PDF didático já indexado no Chroma (`metadata.source`).
INSERT INTO processo_anexos_pdf (processo_id, nome_ficheiro, descricao)
SELECT p.id, v.nome, v.descricao
FROM processos p
JOIN (
    VALUES
        ('1234/25.3T8PRT', 'negocio_juridico.pdf', 'Síntese teórica: negócio jurídico e declaração negocial'),
        ('892/24.2T8FDC', 'boa_fe.pdf', 'Boa-fé nas negociações e função interpretativa'),
        ('56/23.1T8CRT', 'responsabilidade_civil.pdf', 'Fundamentos da responsabilidade civil contratual e extracontratual'),
        ('4321/25.1T8PVT', 'prescricao_caducidade.pdf', 'Prescrição vs caducidade (visão geral)'),
        ('777/24.4T8PRT', 'contrato.pdf', 'Formação e execução do contrato; incumprimento')
) AS v (numero, nome, descricao) ON p.numero = v.numero
ON CONFLICT (processo_id, nome_ficheiro) DO NOTHING;
