# LaTeX neste computador

Instalação solicitada pelo usuário após a preparação da campanha TP2.
O MiKTeX foi instalado no escopo do usuário pelo pacote `MiKTeX.MiKTeX`
do winget, com hash do instalador verificado pelo gerenciador. A instalação
básica 25.12 foi atualizada; o compilador passou a informar MiKTeX 26.5.

Executáveis em `%LOCALAPPDATA%/Programs/MiKTeX/miktex/bin/x64/`.
O instalador adicionou esse diretório ao PATH do usuário. Reabrir o VS Code
e os terminais permite reconhecer `pdflatex` pelo nome.

## Compilar

Na raiz do projeto:

```powershell
./scripts/compilar_relatorio.ps1
```

O script também encontra a instalação MiKTeX do usuário quando o terminal
ainda está com o PATH antigo. Compila pelo menos duas passagens, até
estabilizar referências, e produz `build/latex/relatorio.pdf`.
O PDF antigo na raiz é preservado. Após aprovar o resultado, usar
`./scripts/compilar_relatorio.ps1 -PublicarPdf` para atualizá-lo.

No VS Code, abrir `relatorio.tex` e executar a tarefa
**Relatório: compilar com LaTeX instalado** ou usar **Ctrl+Alt+B** com a
receita **Projeto: pdflatex (duas passagens)** do LaTeX Workshop.
O visualizador usa uma aba do editor e a saída fica em `build/latex/`.
A configuração usa `pdflatex` diretamente, sem exigir Perl ou latexmk.

## Pacotes e manutenção

Foi habilitada a instalação automática de pacotes ausentes pelo MiKTeX;
uma primeira compilação pode precisar de internet. As atualizações da
instalação básica e os pacotes exigidos pelo relatório foram instalados.
Para manutenção posterior, usar MiKTeX Console ou `miktex packages update`.

Referências oficiais: [instalação MiKTeX](https://miktex.org/howto/install-miktex),
[gerenciador de pacotes](https://docs.miktex.org/manual/miktex-packages.html)
e [receitas LaTeX Workshop](https://github.com/James-Yu/LaTeX-Workshop/wiki/Compile).

## Validação

A primeira compilação local gerou o relatório cumulativo com 30 páginas e
referências estabilizadas. Um pequeno transbordamento de texto identificado
no log foi corrigido nas fontes, sem alterar os resultados científicos.
A nova compilação terminou com referências estabilizadas, sem erros LaTeX,
referências indefinidas, caracteres ausentes ou transbordamentos no log.
As 30 páginas foram renderizadas e inspecionadas, com conferência ampliada
das tabelas e da discussão. O resultado está em `build/latex/relatorio.pdf`.

O executável ainda emitiu um aviso de que não foram verificadas atualizações,
apesar de `miktex packages check-update` informar que não há atualizações e
`initexmf --report` registrar a verificação e a atualização desta sessão.
Esse aviso residual não impediu a compilação; o estado pode ser consultado
pelo MiKTeX Console.

O pacote `dist/tp2_fontes_resultados.zip` preparado antes desta instalação
continua sendo o registro das fontes/resultados daquela etapa. Ele não
contém estas novas configurações locais nem o PDF agora gerado em `build/`.
