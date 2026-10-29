"""Baixa do site WordPress antigo as imagens usadas no site novo e as reduz para a web.

Uso (uma vez só, a partir da pasta site/):
    python scripts/baixar_imagens.py

Requer Pillow. As imagens vão para src/static/img/.
"""
import io
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from PIL import Image

BASE = "https://ccbv.org.br/wp-content/uploads/"
DESTINO = Path(__file__).resolve().parent.parent / "src" / "static" / "img"
LARGURA_MAX = 1600

# nome local -> caminho em wp-content/uploads
IMAGENS = {
    "logo.png": "2019/06/Logo-CCBV-SiteRetangulo-Top2-1.png",
    "icone.png": "2019/06/cropped-Icone-do-Site-270x270.png",
    "aces.png": "2019/06/Logo-Acesbranco-1024x296.png",
    "capa.jpg": "2019/08/slide-de-entreada.jpg",
    "estrutura.jpg": "2019/06/sala1.jpg",
    "formacao-academica.jpg": "2019/08/Formação-Academica2.jpg",
    "formacao-cultural.jpg": "2019/06/FORMAÇÃO-CULTURAL-1.jpg",
    "formacao-espiritual.jpg": "2020/01/FORMAÇÃO-ESPIRITUAL-min-1.jpg",
    "residencia.jpg": "2020/02/Residencia3.jpg",
    "sala-estudo.jpg": "2019/08/sala-de-estudo.jpg",
    "sala-estudo-2.jpg": "2019/08/sala-de-estudo-2.jpg",
    "tertulia.jpg": "2019/08/terturlia.jpg",
    "fachada.jpg": "2019/08/vista-de-fora.jpg",
    "depoimento-rafael.jpg": "2019/09/rafael.jpg",
    "depoimento-marcelo.jpg": "2019/09/marcelo.jpg",
    "depoimento-robson.jpg": "2015/11/Robson.jpg",
    "mercado-financeiro.jpg": "2021/05/Mercado-Financeiro2.jpg",
    "mercado-financeiro-1.jpg": "2019/09/IMG_2735-768x512.jpg",
    "mercado-financeiro-2.jpg": "2019/09/IMG_27354-768x512.jpg",
    "mercado-financeiro-3.jpg": "2019/09/IMG_27357-768x512.jpg",
    "business-case.jpg": "2021/03/Slide-Bussiness-Case-2021.jpg",
    "reforma-aerea.jpg": "2021/09/Vista-Aérea-Reforma-CCBV.jpg",
    "reforma-frontal.jpg": "2021/09/Vista-Frontal-Reforma-CCBV-1024x540.jpg",
    "reforma-lateral.jpg": "2021/09/Vista-Lateral-Reforma-CCVB-1.jpg",
    "reforma-posterior.jpg": "2021/09/Vista-Posterior-Reforma-CCBV-1024x540.jpg",
}


def baixar(caminho):
    url = BASE + urllib.parse.quote(caminho)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (migracao CCBV)"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def main():
    DESTINO.mkdir(parents=True, exist_ok=True)
    falhas = 0
    for nome, caminho in IMAGENS.items():
        alvo = DESTINO / nome
        if alvo.exists():
            continue
        try:
            img = Image.open(io.BytesIO(baixar(caminho)))
        except Exception as e:  # noqa: BLE001 - relatar e seguir com as outras
            print(f"FALHOU {nome}: {e}")
            falhas += 1
            continue
        if img.width > LARGURA_MAX:
            img = img.resize((LARGURA_MAX, round(img.height * LARGURA_MAX / img.width)), Image.LANCZOS)
        if nome.endswith(".jpg"):
            img.convert("RGB").save(alvo, "JPEG", quality=82, optimize=True, progressive=True)
        else:
            img.save(alvo, optimize=True)
        print(f"ok {nome} {img.width}x{img.height} {alvo.stat().st_size // 1024} KB")
    sys.exit(1 if falhas else 0)


if __name__ == "__main__":
    main()
