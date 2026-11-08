"""Empacota fontes e resultados auditados; exclui o PDF antigo e dados brutos de piloto."""

import argparse
import hashlib
import json
import zipfile
from pathlib import Path


def arquivos_entrega(raiz):
    raiz = Path(raiz)
    arquivos = set()
    for padrao in ('*.py', 'requirements*.txt', 'pytest.ini', 'README.md',
                   'relatorio.tex', 'image.png', 'Case-UFMG*.pdf'):
        arquivos.update(p for p in raiz.glob(padrao) if p.is_file())
    for pasta in ('configs', 'docs/tp2', 'tests', 'scripts', '.vscode',
                  'results/tp1_corrigido', 'results/tp2'):
        arquivos.update(p for p in (raiz/pasta).rglob('*') if p.is_file()
                        and '__pycache__' not in p.parts and not p.name.endswith('.tmp'))
    referencia = raiz/'results/referencias_tp1.json'
    if referencia.is_file():
        arquivos.add(referencia)
    for nome in ('medicao_piloto.json', 'auditoria_independente.json'):
        path = raiz/'results/piloto_tp2_lote'/nome
        if path.is_file():
            arquivos.add(path)
    return sorted(arquivos, key=lambda p: p.relative_to(raiz).as_posix())


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as arquivo:
        for bloco in iter(lambda: arquivo.read(1024*1024), b''):
            h.update(bloco)
    return h.hexdigest()


def montar_pacote(raiz, output):
    raiz, output = Path(raiz).resolve(), Path(output).resolve()
    medicao = json.loads((raiz/'results/tp2/medicao_oficial.json').read_text(encoding='utf-8'))
    if medicao['fase'] != 'auditada_com_figuras' or medicao['concluidas'] != 160:
        raise ValueError('Pacote exige 160 buscas auditadas com figuras oficiais.')
    for nome in ('analise.json', 'resultados_tp2.tex'):
        if not (raiz/'results/tp2'/nome).is_file():
            raise ValueError(f'Produto de análise ausente: {nome}')
    arquivos = arquivos_entrega(raiz)
    manifesto = {
        'tipo': 'fontes_e_resultados_para_compilacao',
        'pdf_tp2_compilado_incluido': False,
        'ressalva': 'relatorio.pdf antigo foi excluído. Compilar e revisar o PDF TP2 no computador com LaTeX.',
        'arquivos_sha256': {p.relative_to(raiz).as_posix(): sha256(p) for p in arquivos},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as pacote:
        for i, path in enumerate(arquivos, 1):
            pacote.write(path, path.relative_to(raiz).as_posix())
            if i % 25 == 0:
                print(f'Empacotados {i}/{len(arquivos)} arquivos', flush=True)
        pacote.writestr('manifesto_entrega.json', json.dumps(manifesto, ensure_ascii=False, indent=2))
        pacote.writestr('LEIA-ME-ANTES-DO-ENVIO.txt',
                        'Este pacote contém fontes e resultados TP2 auditados, não o PDF final compilado.\n'
                        'Extraia mantendo a estrutura de pastas. No computador com LaTeX, execute:\n'
                        '  ./scripts/compilar_relatorio.ps1\n'
                        'Revise todas as páginas de build/latex/relatorio.pdf.\n'
                        'Depois execute ./scripts/compilar_relatorio.ps1 -PublicarPdf para atualizar o PDF da raiz.\n'
                        'Entregue o PDF TP2 revisado com o código e os resultados exigidos.\n'
                        'O PDF TP1 anterior não está incluído, para evitar envio por engano.\n'
                        'Consulte README.md e docs/tp2/PROTOCOLO_EXPERIMENTAL.md.\n')
    with zipfile.ZipFile(output) as pacote:
        corrompido = pacote.testzip()
        if corrompido is not None:
            raise ValueError(f'Falha CRC no pacote: {corrompido}')
        if set(pacote.namelist()) != set(manifesto['arquivos_sha256']) | {
                'manifesto_entrega.json', 'LEIA-ME-ANTES-DO-ENVIO.txt'}:
            raise ValueError('Conteúdo ZIP diverge do manifesto.')
    resultado = {'arquivo': str(output), 'tamanho_bytes': output.stat().st_size,
                 'sha256': sha256(output), 'arquivos': len(arquivos),
                 'pdf_final_pendente': True}
    output.with_suffix('.manifesto.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='dist/tp2_fontes_resultados.zip')
    args = parser.parse_args()
    print(json.dumps(montar_pacote(Path(__file__).parent, args.output), ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
