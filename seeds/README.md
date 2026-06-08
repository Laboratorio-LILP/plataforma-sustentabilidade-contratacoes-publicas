# Diretório `seeds/`

Aqui ficam as planilhas XLSX que alimentam a PESCP via o management command
`import_pescp_seed`.

## Arquivos versionados

- **`pescp_seed_template.xlsx`** — template canônico com as 7 abas e seus cabeçalhos.
  É gerado por `tools/gerar_seed_template.py`. Contém algumas linhas de exemplo
  para orientar o time de conteúdo. **Não inclua dados reais aqui.**

## Arquivos NÃO versionados

- `pescp_seed_v1.xlsx`, `pescp_seed_v1.1.xlsx`, etc. — planilhas reais alimentadas
  pelo time do LILP e parceiros (USP/UNESP/UNICAMP/PNUD). Estão no `.gitignore`.

## Como produzir uma nova planilha

1. Copie o template:
   ```bash
   cp seeds/pescp_seed_template.xlsx seeds/pescp_seed_v1.xlsx
   ```
2. Edite no Excel/LibreOffice preenchendo as 7 abas. Respeite os cabeçalhos
   exatos — o importador é case-insensitive nas chaves mas estrito quanto
   à presença das colunas.
3. Valide com `--dry-run`:
   ```bash
   make seed FILE=seeds/pescp_seed_v1.xlsx
   # ou diretamente:
   docker compose exec web python manage.py import_pescp_seed \
       --file=seeds/pescp_seed_v1.xlsx --dry-run
   ```
4. Importe de verdade:
   ```bash
   make seed FILE=seeds/pescp_seed_v1.xlsx
   ```

Veja `docs/IMPORTACAO_SEED.md` para o detalhamento completo das colunas e regras.
