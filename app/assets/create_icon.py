# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Génère une icône .ico simple pour l'application EPSP ES-SENIA.
Nécessite Pillow.
"""
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("[!] Pillow non installé. pip install pillow")
    sys.exit(1)


def creer_icone(chemin_sortie: str = None):
    if chemin_sortie is None:
        base = os.path.dirname(os.path.abspath(__file__))
        chemin_sortie = os.path.join(base, "epsp_icon.ico")

    tailles = [256, 128, 64, 48, 32, 16]
    images  = []

    for taille in tailles:
        img  = Image.new("RGBA", (taille, taille), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Fond cercle bleu institutionnel
        marge = taille // 10
        draw.ellipse(
            [marge, marge, taille - marge, taille - marge],
            fill=(30, 58, 95, 255)
        )

        # Bande accent orange
        cy   = taille // 2
        band = max(2, taille // 20)
        draw.rectangle(
            [marge, cy - band, taille - marge, cy + band],
            fill=(240, 165, 0, 255)
        )

        # Texte "ES"
        texte    = "ES"
        font_size = max(8, taille // 3)
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except Exception:
            font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), texte, font=font)
        tw   = bbox[2] - bbox[0]
        th   = bbox[3] - bbox[1]
        tx   = (taille - tw) // 2
        ty   = (taille - th) // 2 - band

        draw.text((tx, ty), texte, font=font, fill=(255, 255, 255, 255))
        images.append(img)

    images[0].save(
        chemin_sortie,
        format="ICO",
        sizes=[(t, t) for t in tailles],
        append_images=images[1:]
    )
    print(f"[OK] Icône générée : {chemin_sortie}")
    return chemin_sortie


if __name__ == "__main__":
    creer_icone()
