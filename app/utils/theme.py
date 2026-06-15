# COPYRIGHT ILINE TECH 2026 BY FERAK ALADDIN
"""
Système de thème visuel — EPSP ES-SENIA
Palette institutionnelle sobre, lisible, professionnelle.
"""

# ── Palette principale ─────────────────────────────────────────────
COULEURS = {
    # Fonds
    "bg_principal":    "#1A1F2E",   # Bleu nuit profond (fond fenêtre)
    "bg_sidebar":      "#141824",   # Sidebar encore plus sombre
    "bg_carte":        "#222840",   # Cartes / panneaux internes
    "bg_champ":        "#2C3354",   # Champs de saisie
    "bg_hover":        "#2E3A5C",   # Survol boutons sidebar

    # Accents
    "accent_bleu":     "#2563EB",   # Bleu institutionnel (boutons primaires)
    "accent_bleu_clair":"#3B82F6",  # Bleu clair (hover)
    "accent_vert":     "#10B981",   # Vert succès / solde positif
    "accent_orange":   "#F59E0B",   # Orange avertissement
    "accent_rouge":    "#EF4444",   # Rouge erreur / solde épuisé

    # Textes
    "texte_principal": "#F0F4FF",   # Blanc bleuté (titres)
    "texte_secondaire":"#94A3B8",   # Gris bleu (labels)
    "texte_discret":   "#4A5568",   # Très discret

    # Bordures
    "bordure":         "#2D3748",
    "bordure_active":  "#2563EB",

    # Sidebar active
    "sidebar_active_bg":  "#2563EB",
    "sidebar_active_txt": "#FFFFFF",
    "sidebar_inact_txt":  "#94A3B8",
}

# ── Typographie ────────────────────────────────────────────────────
POLICES = {
    "titre_app":   ("Segoe UI", 15, "bold"),
    "titre_page":  ("Segoe UI", 20, "bold"),
    "sous_titre":  ("Segoe UI", 13, "bold"),
    "corps":       ("Segoe UI", 12),
    "corps_bold":  ("Segoe UI", 12, "bold"),
    "petit":       ("Segoe UI", 10),
    "nav":         ("Segoe UI", 12, "bold"),
    "stat_chiffre":("Segoe UI", 28, "bold"),
    "stat_label":  ("Segoe UI", 10),
    "bouton":      ("Segoe UI", 12, "bold"),
    "tableau":     ("Segoe UI", 11),
    "tableau_head":("Segoe UI", 11, "bold"),
}

# ── Dimensions ────────────────────────────────────────────────────
DIMENSIONS = {
    "fenetre_w":      1200,
    "fenetre_h":      750,
    "fenetre_min_w":  1000,
    "fenetre_min_h":  650,
    "sidebar_w":      220,
    "rayon_carte":    10,
    "rayon_bouton":   6,
    "padding_page":   24,
    "padding_carte":  16,
}
