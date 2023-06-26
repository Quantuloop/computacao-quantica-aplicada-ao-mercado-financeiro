# Computação clássica e quântica aplicadas ao mercado financeiro

Os códigos são relacionados ao nosso artigo que pode ser encontrado no link:

<https://doi.org/10.1590/1806-9126-RBEF-2022-0099>

O repositório encontra-se organizado da seguinte forma:

1. Um Jupyter notebook que explora a abordagem clássica (Markowitz) onde você poderá obter a Fronteira Eficiente para diversos ativos como: ações da B3, ações de empresas americanas (NYSE/NASDAQ), Criptomoedas etc.
   Bem como contém uma abordagem quântica de uma implementação simples do QAOA (Quantum Approximate Optimization Algorithm) e do VQE (Variational Quantum Eigensolver) com o Qiskit (IBM Q), podendo ser usado para o mesmo grupo de ativos e testado diretamente no Google Colab.
    - [Notebook 1 - Implementação da abordagem clássica e uma pequena demonstração do QAOA com Qiski](Quantum_Finance_DualQ.ipynb)
2. Um Jupyter notebook que explora a abordagem quântica com o QAOA usando o myQLM com os mesmos ingredientes anteriores, onde exploramos mais profundamente a qualidade da solução e a covergência do QAOA em função do número de camadas. Jupyter notebook elaborado majoritariamente pela equipe do Senai/Cimatec (Anton e Gleydson).
    - [Notebook 2 - implementação do QAOA com o myQLM](QAOA_myQLM.ipynb)
3. Um Jupyter notebook que explora a abordagem quântica com o QAOA usando o [Ket](https://quantumket.org).
    - [Notebook 3 - implementação do QAOA com o Ket](QAOA_ket.ipynb)

## Instalação Notebooks 2 e 3

Para instalar as dependências necessárias para executar os notebooks 2 e 3 use o [Poetry](https://python-poetry.org) com o seguinte comando:

```shell
poetry install
```

Python 3.10 é necessário.
