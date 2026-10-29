"""Gera o site estático do CCBV em docs/ (publicado pelo GitHub Pages).

Uso, a partir da pasta site/:
    python build.py            # gera docs/
    python build.py --servir   # gera e abre um servidor local em http://localhost:8000

Só usa a biblioteca padrão do Python.

Estrutura:
    src/config.json        dados gerais, menu, redes, galerias, formulários e redirecionamentos
    src/layout.html        moldura comum a todas as páginas
    src/paginas/**.html    conteúdo de cada página; a 1ª linha é um comentário com JSON
                           ({"titulo": ..., "descricao": ...}). "index.html" vira a pasta.
    src/static/            copiado como está (css, imagens)
"""
import datetime
import html
import json
import re
import shutil
import sys
import urllib.parse
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SRC = RAIZ / "src"
SAIDA = RAIZ / "docs"


def carregar_config():
    return json.loads((SRC / "config.json").read_text(encoding="utf-8"))


def ler_pagina(arquivo):
    texto = arquivo.read_text(encoding="utf-8")
    m = re.match(r"\s*<!--\s*(\{.*?\})\s*-->\s*", texto, re.S)
    if not m:
        sys.exit(f"{arquivo}: falta o comentário inicial com JSON de título/descrição")
    return json.loads(m.group(1)), texto[m.end():]


def caminho_web(arquivo):
    """src/paginas/atividades/index.html -> 'atividades/'; index.html -> ''."""
    rel = arquivo.relative_to(SRC / "paginas").as_posix()
    if rel == "index.html":
        return ""
    if rel.endswith("/index.html"):
        return rel[: -len("index.html")]
    return rel  # ex.: 404.html


def prefixo_raiz(caminho):
    """Caminho relativo até a raiz do site, para funcionar também em usuario.github.io/repositorio/."""
    profundidade = caminho.count("/")
    return "../" * profundidade if profundidade else "./"


def bloco_youtube(cfg):
    lista = cfg["youtube"]["playlist_envios"]
    return (
        '<div class="video"><iframe loading="lazy" title="Vídeos do canal do CCBV no YouTube" '
        f'src="https://www.youtube-nocookie.com/embed/videoseries?list={lista}" '
        'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>'
    )


def bloco_instagram(cfg):
    usuario = cfg["instagram"]["usuario"]
    posts = [p for p in cfg["instagram"]["posts"] if p.strip()]
    botao = (
        f'<p class="botoes" style="justify-content:center"><a class="botao" href="https://www.instagram.com/{usuario}/" rel="noopener">'
        f"Seguir @{usuario} no Instagram</a></p>"
    )
    if not posts:
        return botao
    itens = "\n".join(
        f'<blockquote class="instagram-media" data-instgrm-permalink="{html.escape(p)}" data-instgrm-version="14">'
        f'<a href="{html.escape(p)}">Ver esta publicação no Instagram</a></blockquote>'
        for p in posts
    )
    return (
        f'<div class="instagram-posts">\n{itens}\n</div>\n{botao}\n'
        '<script async src="https://www.instagram.com/embed.js"></script>'
    )


def bloco_galerias(cfg):
    galerias = [g for g in cfg["galerias"] if g.get("pasta_drive")]
    if not galerias:
        return (
            '<p class="aviso">As galerias de fotos ainda estão sendo organizadas. '
            f'Enquanto isso, veja as fotos mais recentes no <a href="https://www.instagram.com/{cfg["instagram"]["usuario"]}/">Instagram</a>.</p>'
        )
    partes = []
    for g in galerias:
        pasta = urllib.parse.quote(g["pasta_drive"])
        partes.append(
            f'<article class="galeria-drive"><h3>{html.escape(g["titulo"])}</h3>'
            + (f'<p>{html.escape(g["descricao"])}</p>' if g.get("descricao") else "")
            + f'<iframe class="embed-drive" loading="lazy" title="{html.escape(g["titulo"])}" '
            f'src="https://drive.google.com/embeddedfolderview?id={pasta}#grid"></iframe>'
            f'<p><a href="https://drive.google.com/drive/folders/{pasta}" rel="noopener">Abrir a pasta no Google Drive</a></p></article>'
        )
    return "\n".join(partes)


def bloco_formulario(url, titulo):
    if not url:
        return ""
    return f'<iframe class="formulario" loading="lazy" title="{html.escape(titulo)}" src="{html.escape(url)}">Carregando…</iframe>'


def bloco_mapa(cfg):
    q = urllib.parse.quote(cfg["mapa_busca"])
    return (
        f'<iframe class="mapa" loading="lazy" title="Mapa: {html.escape(cfg["endereco"])}" '
        f'src="https://www.google.com/maps?q={q}&output=embed" referrerpolicy="no-referrer-when-downgrade"></iframe>'
    )


def montar_menu(cfg, caminho_atual, raiz):
    linhas = []
    for rotulo, alvo in cfg["menu"]:
        atual = (alvo == "" and caminho_atual == "") or (alvo and caminho_atual.startswith(alvo))
        aria = ' aria-current="page"' if atual else ""
        linhas.append(f'        <li><a href="{raiz}{alvo}"{aria}>{html.escape(rotulo)}</a></li>')
    return "\n".join(linhas)


def substituir(texto, valores):
    def troca(m):
        chave = m.group(1)
        if chave not in valores:
            sys.exit(f"marcador desconhecido: {{{{{chave}}}}}")
        return valores[chave]

    return re.sub(r"\{\{(\w+)\}\}", troca, texto)


def pagina_redirecionamento(cfg, destino, raiz):
    url = f"{cfg['url']}/{destino}"
    alvo = raiz + destino
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8">
<title>Página movida – {html.escape(cfg['nome'])}</title>
<meta name="robots" content="noindex">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={alvo}">
</head><body><p>Esta página mudou de endereço: <a href="{alvo}">{url}</a></p></body></html>
"""


def gerar():
    cfg = carregar_config()
    layout = (SRC / "layout.html").read_text(encoding="utf-8")
    if SAIDA.exists():
        shutil.rmtree(SAIDA)
    shutil.copytree(SRC / "static", SAIDA)

    comuns = {
        "nome": html.escape(cfg["nome"]),
        "url": cfg["url"],
        "telefone": cfg["telefone"],
        "telefone_link": cfg["telefone_link"],
        "email": cfg["email"],
        "endereco": html.escape(cfg["endereco"]),
        "instagram_usuario": cfg["instagram"]["usuario"],
        "facebook": cfg["facebook"],
        "youtube_canal": cfg["youtube"]["canal"],
        "ano": str(datetime.date.today().year),
        "youtube": bloco_youtube(cfg),
        "instagram": bloco_instagram(cfg),
        "galerias": bloco_galerias(cfg),
        "secao_formulario_contato": (
            '<section class="secao secao--cinza"><div class="container" style="max-width:820px">'
            '<div class="titulo-secao"><h2>Escreva para nós</h2></div>'
            + bloco_formulario(cfg["formulario_contato"], "Formulário de contato")
            + "</div></section>"
            if cfg["formulario_contato"]
            else ""
        ),
        "formulario_residencia": bloco_formulario(cfg["formulario_residencia"], "Ficha de interesse na residência"),
        "mapa": bloco_mapa(cfg),
    }

    urls_sitemap = []
    for arquivo in sorted((SRC / "paginas").rglob("*.html")):
        meta, corpo = ler_pagina(arquivo)
        caminho = caminho_web(arquivo)
        # o 404 é servido em qualquer endereço, então precisa de caminhos absolutos
        raiz = "/" if caminho == "404.html" else prefixo_raiz(caminho)
        valores = dict(comuns, raiz=raiz)
        conteudo = substituir(corpo, valores)
        titulo = meta["titulo"]
        valores.update(
            conteudo=conteudo,
            titulo_completo=html.escape(cfg["nome"] if not caminho else f"{titulo} – {cfg['nome']}"),
            descricao=html.escape(meta.get("descricao", cfg["descricao_padrao"])),
            url_pagina=f"{cfg['url']}/{caminho}",
            menu=montar_menu(cfg, caminho, raiz),
        )
        destino = SAIDA / (caminho + "index.html" if caminho == "" or caminho.endswith("/") else caminho)
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(substituir(layout, valores), encoding="utf-8")
        if not caminho.endswith(".html"):
            urls_sitemap.append(f"{cfg['url']}/{caminho}")

    for antigo, novo in cfg["redirecionamentos"].items():
        destino = SAIDA / antigo / "index.html"
        if destino.exists():
            sys.exit(f"redirecionamento {antigo} colide com uma página real")
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(pagina_redirecionamento(cfg, novo, prefixo_raiz(antigo)), encoding="utf-8")

    hoje = datetime.date.today().isoformat()
    (SAIDA / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "".join(f"  <url><loc>{u}</loc><lastmod>{hoje}</lastmod></url>\n" for u in urls_sitemap)
        + "</urlset>\n",
        encoding="utf-8",
    )
    (SAIDA / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {cfg['url']}/sitemap.xml\n", encoding="utf-8")
    (SAIDA / ".nojekyll").write_text("", encoding="utf-8")
    # domínio próprio do GitHub Pages
    (SAIDA / "CNAME").write_text(urllib.parse.urlparse(cfg["url"]).hostname + "\n", encoding="utf-8")
    print(f"ok: {len(urls_sitemap)} páginas, {len(cfg['redirecionamentos'])} redirecionamentos em {SAIDA}")


if __name__ == "__main__":
    gerar()
    if "--servir" in sys.argv:
        import functools
        import http.server

        manipulador = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(SAIDA))
        print("servindo em http://localhost:8000 (Ctrl+C para parar)")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8000), manipulador).serve_forever()
