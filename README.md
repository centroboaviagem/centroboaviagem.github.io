# Site do Centro Cultural Boa Viagem

Site estático de [ccbv.org.br](https://ccbv.org.br), publicado pelo GitHub Pages a partir da pasta `docs/`.

## Como editar

| O que mudar | Onde |
|---|---|
| Textos de uma página | `src/paginas/<página>/index.html` |
| Menu, telefone, e-mail, endereço | `src/config.json` |
| Posts do Instagram exibidos | `src/config.json` → `instagram.posts` (links `https://www.instagram.com/p/...`) |
| Galerias de fotos | `src/config.json` → `galerias`: `{"titulo": "...", "descricao": "...", "pasta_drive": "<id da pasta>"}`. A pasta do Google Drive precisa estar compartilhada como "Qualquer pessoa com o link". |
| Formulário de contato | `src/config.json` → `formulario_contato` (link do Google Forms terminado em `viewform?embedded=true`) |
| Cores e aparência | `src/static/css/estilo.css` |
| Imagens | `src/static/img/` |

Os vídeos do YouTube aparecem sozinhos: o site embute a lista de envios do canal.

Depois de editar, gere o site e confira localmente:

```bash
python build.py --servir
```

Abra http://localhost:8000. Se estiver tudo certo, faça commit de `src/` **e** de `docs/` e envie (`git push`).
O GitHub Pages atualiza o site em um ou dois minutos.

## Estrutura

- `build.py`: gera `docs/` a partir de `src/` (só biblioteca padrão do Python).
- `src/layout.html`: cabeçalho, menu e rodapé comuns.
- `src/paginas/`: conteúdo das páginas. A primeira linha de cada arquivo é um comentário com o título e a descrição.
- `src/config.json` → `redirecionamentos`: endereços do site WordPress antigo que levam às páginas novas.
- `scripts/baixar_imagens.py`: usado uma vez para trazer as imagens do site antigo.
