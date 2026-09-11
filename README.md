# Calibração espectral com MZI e HCN

Código em Python desenvolvido durante o projeto de iniciação
científica de Laura Fernanda de Sousa, na Unicamp.

O projeto reúne o processamento de sinais experimentais,
a calibração da escala de frequência óptica e a geração
de figuras utilizadas no relatório.

## Objetivo

Utilizar as linhas de absorção do cianeto de hidrogênio (HCN)
como referências de frequência e as franjas do interferômetro
de Mach-Zehnder (MZI) para acompanhar a variação relativa
da frequência durante a varredura do laser.

A escala calibrada é aplicada ao sinal de transmissão
da cavidade óptica registrado na mesma aquisição.

O código também gera figuras teóricas sobre decaimento,
energia intracavidade, transmitância e regimes de acoplamento.

## Origem dos dados

As aquisições realizadas por Laura são utilizadas para
ilustrar o sinal do MZI antes da calibração.

Os dados utilizados na análise da cavidade foram cedidos
por Gustavo Nunes. A calibração dessa aquisição utiliza
seus próprios canais de HCN e MZI.

Os sinais de medições diferentes não são combinados
para calibrar a transmissão da cavidade.

## Organização dos arquivos

Para reproduzir a análise com a configuração atual:

```text
pasta_do_projeto/
├── graficos_calibracao_final.py
├── dados_mzi.csv
├── DADOS GUSTA .parquet
├── README.md
└── figuras_codigo_atualizado/   # Criada automaticamente
```

O nome `DADOS GUSTA .parquet` contém um espaço antes de `.parquet`.

O CSV deve conter a coluna `MZI`.
O Parquet deve conter as colunas `trans`, `mzi` e `hcn`.

A disponibilidade dos dados deve ser verificada separadamente:
o código não baixa os arquivos automaticamente.

## Instalação

É necessário ter Python instalado.

No terminal, instale as bibliotecas:

```bash
python -m pip install numpy pandas matplotlib scipy pyarrow
```

O processamento foi testado com Python 3.13.

## Como executar

1. Salve o código e os dados na organização indicada acima.
2. Abra um terminal na pasta do projeto.
3. Execute:

```bash
python graficos_calibracao_final.py
```

Não coloque o código dentro da pasta de figuras.
Salve o arquivo com apenas uma extensão `.py`.

As principais opções ficam no início do código:

```python
MOSTRAR_JANELAS = True
FAZER_EXPERIMENTO = True
FAZER_MODELOS = True
FAZER_RLC = True
```

- `MOSTRAR_JANELAS`: abre as figuras para visualização.
- `FAZER_EXPERIMENTO`: processa os dados experimentais.
- `FAZER_MODELOS`: gera as figuras teóricas.
- `FAZER_RLC`: gera o gráfico do circuito, quando os arquivos
  correspondentes estão disponíveis e o processamento
  experimental está ativado.

Para gerar somente as figuras teóricas, use:

```python
FAZER_EXPERIMENTO = False
FAZER_MODELOS = True
```

Para salvar as figuras sem abrir janelas:

```python
MOSTRAR_JANELAS = False
```

### Dados opcionais do circuito RLC

Na configuração atual, o código procura a pasta
`dados indutor pequeno` um nível acima da pasta do código.

Os arquivos devem seguir o formato utilizado na aquisição
original: nomes como `100khz.csv` e `1mhz.csv`, coluna
`POUT` e uma segunda linha contendo as unidades.

Se esses arquivos não estiverem disponíveis, o gráfico
do RLC não será gerado. Também é possível desativá-lo
com `FAZER_RLC = False`.

## Resultados

As figuras são salvas em PDF na pasta
`figuras_codigo_atualizado`, ao lado do código.

Os PDFs têm largura de 6,53 polegadas, fontes principais
de 12 pt e legendas abaixo dos gráficos, quando presentes.

São geradas figuras de:

- MZI antes da calibração, com máximos e mínimos;
- energia e transmitância sobrepostas;
- sinal de transmissão da cavidade;
- MZI e HCN lado a lado;
- detalhe dos sinais de HCN e MZI da mesma aquisição;
- verificação interna da calibração;
- decaimento com e sem perdas;
- comparação entre os perfis lorentziano e gaussiano;
- energia e transmitância nos regimes de acoplamento;
- saídas de um MZI ideal para diferentes fases;
- resposta experimental do circuito RLC, quando disponível;
- curva de calibração.

Também são salvos:

- `referencias_hcn.csv`: associação utilizada entre linhas
  do HCN, índices das amostras e frequências;
- `resultados.txt`: resumo do recorte, FSR mediano
  e erro RMS da verificação interna.

Uma nova execução substitui os resultados de mesmo nome.
Os recortes exportados pelo botão de zoom recebem
nomes com horário.

## Ampliação dos gráficos

Com as janelas abertas, utilize as ferramentas de navegação
do Matplotlib.

No gráfico da cavidade, arraste horizontalmente sobre
o intervalo de interesse, sem ativar a lupa.
O eixo vertical será ajustado ao sinal selecionado.

- **Visão geral:** restaura o enquadramento inicial da cavidade.
- **Salvar zoom em PDF:** exporta os limites visíveis.

Os controles interativos dependem do ambiente gráfico
disponível no computador.

## Método de calibração

1. Selecionar um trecho da aquisição.
2. Detectar as linhas de absorção do HCN.
3. Associar essas linhas aos comprimentos de onda de referência.
4. Identificar máximos e mínimos do MZI da mesma aquisição.
5. Construir uma coordenada de ciclos, considerando meio ciclo
   entre extremos consecutivos alternados.
6. Converter os comprimentos de onda no vácuo em frequências.
7. Interpolar linearmente, por trechos, a frequência
   em função da contagem de ciclos.
8. Aplicar a escala ao sinal da cavidade.

O processamento é restrito ao intervalo entre a primeira
e a última referência de HCN utilizadas.

A filtragem gaussiana auxilia a detecção dos extremos.
Ela não representa um ajuste gaussiano das linhas espectrais.

## Uso com outras medições

A configuração atual foi preparada para os arquivos
utilizados neste relatório. Ela não identifica automaticamente
qualquer aquisição.

Para utilizar outros dados, revise:

- caminhos e formatos dos arquivos;
- nomes dos canais;
- início e fim do trecho de varredura;
- parâmetros de filtragem e detecção;
- identidade e ordem das linhas do HCN;
- unidades dos sinais;
- intervalos escolhidos para visualização.

A lista atual de referências corresponde às linhas
R26 até R0, seguidas de P1 até P27.

Encontrar 54 mínimos não comprova, por si só,
que essa associação esteja correta.

Não se deve assumir que metade do arquivo corresponde
necessariamente a uma varredura completa de ida.

## Limitações da análise

O erro RMS apresentado é uma verificação interna
da interpolação, obtida pela exclusão de referências
intermediárias. Ele não representa a incerteza total
da calibração.

O sinal da cavidade é apresentado como sinal adquirido.
Ele não deve ser interpretado automaticamente como
transmitância absoluta.

As figuras teóricas são ilustrativas. O código não realiza
ajustes das ressonâncias para determinar larguras de linha,
taxas de perda ou fatores de qualidade.

As normalizações de energia são indicadas nos gráficos:
a comparação de formas utiliza o máximo de cada curva,
enquanto a comparação de energia entre regimes utiliza
uma referência comum.

## Referência do HCN

Gilbert, S. L.; Swann, W. C.; Wang, C.-M.
*Hydrogen Cyanide H13C14N Absorption Reference for
1530 nm to 1565 nm Wavelength Calibration: SRM 2519a*.
NIST Special Publication 260-137, edição de 2005.
Tabela 3.

[Publicação do NIST](https://www.nist.gov/system/files/documents/srm/SP260-137.pdf)

## Autoria e agradecimentos

Projeto de iniciação científica de Laura Fernanda de Sousa,
desenvolvido na Unicamp.

Agradecimentos a Gustavo Nunes pela cessão dos dados
utilizados na análise espectral da cavidade.
