INSERT INTO pacientes (
    nome, idade, sexo, imc,
    pressao_sistolica, pressao_diastolica,
    glicemia_jejum, colesterol_ldl, hdl, triglicerideos,
    tabagismo, atividade_fisica, historico_familiar_cv, notas_clinicas
) VALUES
(
    'Ana Martins', 42, 'F', 22.5,
    118, 76, 88, 98, 58, 110,
    'nunca', 'regular', FALSE,
    'Sem queixas; controlo periódico.'
),
(
    'Bruno Costa', 58, 'M', 31.2,
    152, 96, 142, 168, 38, 220,
    'ativo', 'sedentário', TRUE,
    'Obesidade grau I; já teve episódio de dor torácica atípica (investigado).'
),
(
    'Carla Sousa', 67, 'F', 26.8,
    138, 84, 118, 145, 42, 180,
    'ex-fumador', 'moderada', TRUE,
    'Ex-fumadora há 8 anos; DLP em tratamento.'
),
(
    'Diogo Alves', 29, 'M', 24.0,
    122, 78, 92, 108, 52, 95,
    'nunca', 'sedentário', FALSE,
    'Trabalho de escritório; pouca caminhada.'
),
(
    'Eva Ribeiro', 71, 'F', 20.1,
    128, 72, 105, 125, 72, 140,
    'nunca', 'regular', FALSE,
    'HDL elevado; boa adesão à dieta mediterrânica.'
),
(
    'Filipe Teixeira', 45, 'M', 27.4,
    148, 92, 132, 155, 40, 260,
    'ativo', 'sedentário', TRUE,
    'Tabagismo ~15 cigarros/dia; triglicerídeos persistentemente altos.'
);
