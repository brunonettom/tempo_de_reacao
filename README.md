# Tarefa de Tempo de Reação em Série (SRTT)

Este é um programa que implementa a Tarefa de Tempo de Reação em Série (SRTT), um paradigma experimental amplamente utilizado para estudar a aprendizagem implícita de sequências motoras.

## Descrição

A SRTT é um experimento psicológico em que os participantes respondem a estímulos visuais que aparecem em posições fixas na tela. O experimento alterna entre blocos com sequências estruturadas (repetitivas) e blocos com sequências aleatórias. Os tempos de reação mais rápidos nos blocos estruturados indicam aprendizagem implícita.

## Características

- Interface gráfica implementada em Pygame
- Alternância entre blocos estruturados e aleatórios
- Medição precisa de tempos de reação
- Armazenamento e exportação de dados em formato CSV
- Feedback visual para respostas corretas
- O estímulo permanece na mesma posição até que a resposta correta seja dada
- Nenhuma posição é repetida imediatamente após ter aparecido
- Rastreamento do número de tentativas para cada estímulo

## Requisitos

- Python 3.6 ou superior
- Pygame
- Os seguintes pacotes Python:
  - random
  - time
  - csv
  - os
  - datetime

## Instalação

1. Clone este repositório ou baixe os arquivos
2. Instale as dependências com:

```
pip install pygame
```

## Como Executar

Execute o script Python no terminal:

```
python srtt_experiment.py
```

## Instruções do Experimento

1. Ao iniciar, digite o ID do participante e pressione Enter
2. Leia as instruções e pressione Espaço para iniciar
3. Quando um círculo ficar vermelho, pressione a tecla correspondente o mais rápido possível:
   - Posição 1 (esquerda): tecla 'Z'
   - Posição 2: tecla 'X'
   - Posição 3: tecla 'N'
   - Posição 4 (direita): tecla 'M'
4. O experimento consiste em 8 blocos de 60 estímulos cada
5. Haverá pausas entre os blocos para descanso

## Dados

Os resultados são salvos em um arquivo CSV no diretório 'results' com as seguintes informações:
- ID do participante
- Número do bloco
- Tipo de bloco (estruturado ou aleatório)
- Número do trial
- Posição do estímulo
- Tempo de reação (ms)
- Acerto (verdadeiro/falso)
- Timestamp

## Parâmetros Configuráveis

Os parâmetros do experimento podem ser ajustados no início do arquivo `srtt_experiment.py`:

- `POSITIONS`: Número de posições de estímulo (padrão: 4)
- `BLOCKS`: Número total de blocos (padrão: 8)
- `TRIALS_PER_BLOCK`: Número de trials por bloco (padrão: 60)
- `SEQUENCE_LENGTH`: Comprimento da sequência estruturada (padrão: 10)

## Fundamentação Teórica

A SRTT foi desenvolvida para estudar a aquisição de memória procedural na ausência de consciência explícita. Os participantes respondem a estímulos visuais, sem saber que alguns blocos seguem uma sequência fixa. A redução dos tempos de reação nos blocos estruturados é interpretada como evidência de aprendizagem implícita.

A sequência utilizada contém dependências de segunda ordem para evitar que padrões triviais sejam detectados conscientemente. A SRTT é amplamente utilizada em estudos neuropsicológicos para investigar a integridade dos sistemas de memória procedural, especialmente em condições que afetam os núcleos da base.
