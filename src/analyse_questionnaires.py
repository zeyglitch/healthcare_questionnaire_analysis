"""
Analyse des questionnaires hospitaliers — Mission 2.

Ce script lit le fichier CSV d'export des questionnaires hospitaliers,
vérifie la complétude des réponses pour les questions obligatoires,
et génère un rapport PDF professionnel avec graphiques et tableaux.

Usage :
  python analyse_questionnaires.py
  python analyse_questionnaires.py --input mon_export.csv --output rapport.pdf
  python analyse_questionnaires.py --obligatoires "Score de Glasgow" "Consentement éclairé"
"""

import csv
import json
import argparse
import tempfile
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

import matplotlib
matplotlib.use("Agg")  # Backend non-interactif
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from fpdf import FPDF


# ──────────────────────────────────────────────
#  Palette de couleurs
# ──────────────────────────────────────────────

COULEURS = {
    "bleu_fonce":   "#1B2A4A",
    "bleu":         "#2E5090",
    "bleu_clair":   "#4A90D9",
    "vert":         "#27AE60",
    "vert_clair":   "#2ECC71",
    "orange":       "#F39C12",
    "rouge":        "#E74C3C",
    "gris_clair":   "#ECF0F1",
    "gris":         "#BDC3C7",
    "blanc":        "#FFFFFF",
    "noir":         "#2C3E50",
}

# Couleurs pour les barres de graphiques
COULEURS_BARRES = [
    "#2E5090", "#27AE60", "#E74C3C", "#F39C12", "#8E44AD",
    "#1ABC9C", "#D35400", "#2C3E50", "#C0392B", "#16A085",
]


# ──────────────────────────────────────────────
#  Chargement de la configuration
# ──────────────────────────────────────────────

def charger_config(chemin: str) -> dict[str, list[str]]:
    """Charge le fichier JSON de configuration des questions obligatoires.

    Le fichier doit être un dict JSON :
        { "NOM DU QUESTIONNAIRE": ["question obligatoire 1", ...], ... }

    Retourne ce dict.
    """
    with open(chemin, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config


# ──────────────────────────────────────────────
#  Lecture et analyse des données
# ──────────────────────────────────────────────

COLONNES = [
    "NIP", "NDA", "NOM", "PRENOM", "DATE NAIS", "DATEVALEUR",
    "QUESTIONNAIRE", "Responsable", "Métier", "QUESTION", "REPONSE",
]


def lire_csv(chemin: str) -> list[dict]:
    """Lit le fichier CSV bloc par bloc.

    Gère les lignes vides et les en-têtes répétés entre chaque bloc.
    Retourne une liste plate de dicts (un par ligne de données).
    """
    lignes = []
    with open(chemin, "r", encoding="utf-8-sig") as f:
        for raw_line in f:
            raw_line = raw_line.strip()
            if not raw_line:
                continue
            # Ignorer les lignes d'en-tête répétées
            if raw_line.startswith('"NIP"'):
                continue
            # Parser la ligne avec le module csv
            parsed = next(csv.reader([raw_line], delimiter="|", quotechar='"'))
            if len(parsed) == len(COLONNES):
                lignes.append(dict(zip(COLONNES, parsed)))
    return lignes


def analyser_completude(
    donnees: list[dict],
    config: dict[str, list[str]],
) -> dict:
    """Analyse la complétude des réponses pour les questions obligatoires.

    Args:
        donnees: liste de dicts (sortie de lire_csv).
        config: dict { QUESTIONNAIRE: [questions obligatoires] }.

    Retourne un dict :
        { (questionnaire, question): { total, vides, taux_completion } }
    """
    stats = {}

    for row in donnees:
        questionnaire = row.get("QUESTIONNAIRE", "").strip()
        question = row.get("QUESTION", "").strip()
        reponse = row.get("REPONSE", "").strip()

        # Ce questionnaire a-t-il des questions obligatoires définies ?
        if questionnaire not in config:
            continue

        # Cette question est-elle obligatoire pour ce questionnaire ?
        if question not in config[questionnaire]:
            continue

        cle = (questionnaire, question)

        if cle not in stats:
            stats[cle] = {"total": 0, "vides": 0}

        stats[cle]["total"] += 1
        if reponse == "":
            stats[cle]["vides"] += 1

    for cle in stats:
        total = stats[cle]["total"]
        vides = stats[cle]["vides"]
        stats[cle]["taux_completion"] = (
            ((total - vides) / total * 100) if total > 0 else 0.0
        )

    return stats


def regrouper_par_service(stats: dict) -> dict:
    """Regroupe les stats par questionnaire (service)."""
    services = defaultdict(list)
    for (questionnaire, question), data in sorted(stats.items()):
        services[questionnaire].append((question, data))
    return dict(sorted(services.items()))


# ──────────────────────────────────────────────
#  Génération des graphiques (matplotlib)
# ──────────────────────────────────────────────

def _configurer_style():
    """Configure le style matplotlib pour un rendu professionnel."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Segoe UI", "Arial", "Helvetica", "DejaVu Sans"],
        "font.size": 10,
        "axes.titlesize": 13,
        "axes.labelsize": 11,
        "figure.facecolor": "white",
        "axes.facecolor": "#FAFBFC",
        "axes.edgecolor": "#DEE2E6",
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.color": "#DEE2E6",
    })


def generer_camembert_global(stats: dict, chemin: str) -> None:
    """Génère un camembert des réponses complètes vs vides (global)."""
    _configurer_style()

    total = sum(d["total"] for d in stats.values())
    vides = sum(d["vides"] for d in stats.values())
    completes = total - vides

    fig, ax = plt.subplots(figsize=(5, 4))

    valeurs = [completes, vides]
    labels = [f"Complétées\n({completes})", f"Cases vides\n({vides})"]
    couleurs = [COULEURS["vert"], COULEURS["rouge"]]
    explode = (0, 0.08)

    wedges, texts, autotexts = ax.pie(
        valeurs,
        labels=labels,
        colors=couleurs,
        explode=explode,
        autopct="%1.1f%%",
        startangle=90,
        textprops={"fontsize": 11},
        pctdistance=0.6,
    )
    for autotext in autotexts:
        autotext.set_fontweight("bold")
        autotext.set_color("white")
        autotext.set_fontsize(13)

    ax.set_title(
        f"Taux de complétude global\n({total} réponses analysées)",
        fontsize=14,
        fontweight="bold",
        color=COULEURS["bleu_fonce"],
        pad=15,
    )

    plt.tight_layout()
    fig.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(fig)


def generer_barres_par_service(services: dict, chemin: str) -> None:
    """Génère un graphique à barres horizontales : taux de complétion par service."""
    _configurer_style()

    noms = []
    taux = []
    for nom_service, items in services.items():
        total_s = sum(d["total"] for _, d in items)
        vides_s = sum(d["vides"] for _, d in items)
        t = ((total_s - vides_s) / total_s * 100) if total_s > 0 else 0
        noms.append(nom_service)
        taux.append(t)

    # Trier par taux croissant
    indices = sorted(range(len(taux)), key=lambda i: taux[i])
    noms = [noms[i] for i in indices]
    taux = [taux[i] for i in indices]

    fig, ax = plt.subplots(figsize=(8, max(4, len(noms) * 0.45 + 1.5)))

    couleurs_b = []
    for t in taux:
        if t >= 98:
            couleurs_b.append(COULEURS["vert"])
        elif t >= 90:
            couleurs_b.append(COULEURS["orange"])
        else:
            couleurs_b.append(COULEURS["rouge"])

    bars = ax.barh(noms, taux, color=couleurs_b, height=0.6, edgecolor="white")

    for bar, t in zip(bars, taux):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{t:.1f}%",
            va="center",
            ha="left",
            fontsize=10,
            fontweight="bold",
            color=COULEURS["noir"],
        )

    ax.set_xlim(0, 110)
    ax.set_xlabel("Taux de complétion (%)")
    ax.set_title(
        "Taux de complétion par service",
        fontsize=14,
        fontweight="bold",
        color=COULEURS["bleu_fonce"],
        pad=15,
    )
    ax.axvline(x=100, color=COULEURS["gris"], linestyle="--", linewidth=0.8, alpha=0.5)

    ax.xaxis.set_major_formatter(mticker.PercentFormatter())
    plt.tight_layout()
    fig.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(fig)


def generer_barres_service_detail(
    nom_service: str,
    items: list[tuple[str, dict]],
    chemin: str,
) -> None:
    """Génère un graphique à barres pour un service donné."""
    _configurer_style()

    questionnaires = []
    taux = []
    for q, d in items:
        # Tronquer les noms longs
        q_court = q if len(q) <= 35 else q[:32] + "..."
        questionnaires.append(q_court)
        taux.append(d["taux_completion"])

    # Trier par taux croissant
    indices = sorted(range(len(taux)), key=lambda i: taux[i])
    questionnaires = [questionnaires[i] for i in indices]
    taux = [taux[i] for i in indices]

    fig, ax = plt.subplots(figsize=(7, max(3, len(questionnaires) * 0.5 + 1)))

    couleurs_b = []
    for t in taux:
        if t >= 98:
            couleurs_b.append(COULEURS["vert"])
        elif t >= 90:
            couleurs_b.append(COULEURS["orange"])
        else:
            couleurs_b.append(COULEURS["rouge"])

    bars = ax.barh(questionnaires, taux, color=couleurs_b, height=0.55, edgecolor="white")

    for bar, t in zip(bars, taux):
        ax.text(
            bar.get_width() + 0.5,
            bar.get_y() + bar.get_height() / 2,
            f"{t:.1f}%",
            va="center",
            ha="left",
            fontsize=9,
            fontweight="bold",
        )

    ax.set_xlim(0, 115)
    ax.set_xlabel("Taux de complétion (%)")
    ax.set_title(
        f"{nom_service}",
        fontsize=13,
        fontweight="bold",
        color=COULEURS["bleu_fonce"],
        pad=10,
    )
    ax.axvline(x=100, color=COULEURS["gris"], linestyle="--", linewidth=0.8, alpha=0.5)

    plt.tight_layout()
    fig.savefig(chemin, dpi=200, bbox_inches="tight")
    plt.close(fig)


# ──────────────────────────────────────────────
#  Classe PDF personnalisée (fpdf2)
# ──────────────────────────────────────────────

class RapportPDF(FPDF):
    """PDF personnalisé avec en-tête et pied de page."""

    def __init__(self, titre: str = "Rapport de completude"):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.titre_rapport = titre
        self.set_auto_page_break(auto=True, margin=25)

        # Enregistrer DejaVu Sans (fournie avec matplotlib) pour le support Unicode
        font_dir = os.path.join(
            os.path.dirname(matplotlib.matplotlib_fname()),
            "fonts", "ttf",
        )
        self.add_font("DejaVuSans", "", os.path.join(font_dir, "DejaVuSans.ttf"))
        self.add_font("DejaVuSans", "B", os.path.join(font_dir, "DejaVuSans-Bold.ttf"))
        self.add_font("DejaVuSans", "I", os.path.join(font_dir, "DejaVuSans-Oblique.ttf"))
        self.add_font("DejaVuSans", "BI", os.path.join(font_dir, "DejaVuSans-BoldOblique.ttf"))

    def header(self):
        if self.page_no() == 1:
            return  # Pas d'en-tête sur la page de garde

        self.set_font("DejaVuSans", "B", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, self.titre_rapport, align="L")
        self.cell(0, 8, f"Page {self.page_no()}", align="R", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(46, 80, 144)
        self.set_line_width(0.5)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVuSans", "I", 8)
        self.set_text_color(150, 150, 150)
        date_str = datetime.now().strftime("%d/%m/%Y à %H:%M")
        self.cell(0, 10, f"Généré le {date_str}", align="C")

    # ── Méthodes utilitaires ──

    def page_de_garde(self, nb_lignes: int, nb_services: int, nb_questions: int):
        """Crée la page de garde du rapport."""
        self.add_page()

        # Bande bleue en haut
        self.set_fill_color(27, 42, 74)
        self.rect(0, 0, 210, 90, "F")

        # Titre principal
        self.set_y(25)
        self.set_font("DejaVuSans", "B", 28)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, "Rapport de Complétude", align="C", new_x="LMARGIN", new_y="NEXT")

        self.set_font("DejaVuSans", "", 18)
        self.cell(
            0, 12, "Questionnaires Obligatoires",
            align="C", new_x="LMARGIN", new_y="NEXT",
        )

        # Ligne décorative
        self.set_draw_color(74, 144, 217)
        self.set_line_width(1)
        self.line(60, 65, 150, 65)

        # Sous-titre
        self.set_y(72)
        self.set_font("DejaVuSans", "I", 12)
        self.set_text_color(200, 210, 230)
        self.cell(0, 8, "CH Cahors", align="C", new_x="LMARGIN", new_y="NEXT")

        # Informations clés
        self.set_y(110)
        self.set_text_color(44, 62, 80)
        self.set_font("DejaVuSans", "", 12)

        infos = [
            ("Date du rapport", datetime.now().strftime("%d/%m/%Y")),
            ("Lignes analysées", str(nb_lignes)),
            ("Services concernés", str(nb_services)),
            ("Questionnaires vérifiés", str(nb_questions)),
        ]

        for label, valeur in infos:
            self.set_font("DejaVuSans", "", 11)
            self.set_text_color(100, 100, 100)
            self.cell(95, 10, label, align="R")
            self.set_font("DejaVuSans", "B", 11)
            self.set_text_color(44, 62, 80)
            self.cell(95, 10, f"  {valeur}", align="L", new_x="LMARGIN", new_y="NEXT")

    def section_titre(self, titre: str, sous_titre: str = ""):
        """Ajoute un titre de section avec style."""
        self.set_font("DejaVuSans", "B", 16)
        self.set_text_color(27, 42, 74)
        self.cell(0, 12, titre, new_x="LMARGIN", new_y="NEXT")

        # Ligne sous le titre
        self.set_draw_color(46, 80, 144)
        self.set_line_width(0.8)
        self.line(10, self.get_y(), 80, self.get_y())
        self.ln(3)

        if sous_titre:
            self.set_font("DejaVuSans", "I", 10)
            self.set_text_color(100, 100, 100)
            self.multi_cell(0, 6, sous_titre, new_x="LMARGIN", new_y="NEXT")
            self.ln(2)

    def paragraphe(self, texte: str):
        """Ajoute un paragraphe de texte."""
        self.set_font("DejaVuSans", "", 10)
        self.set_text_color(44, 62, 80)
        self.multi_cell(0, 6, texte, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def texte_important(self, texte: str, couleur: str = "bleu"):
        """Ajoute du texte mis en valeur."""
        c = COULEURS.get(couleur, COULEURS["bleu"])
        r, g, b = int(c[1:3], 16), int(c[3:5], 16), int(c[5:7], 16)
        self.set_font("DejaVuSans", "B", 11)
        self.set_text_color(r, g, b)
        self.multi_cell(0, 7, texte, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def metrique_encadree(self, label: str, valeur: str, couleur_hex: str):
        """Ajoute une métrique dans un cadre coloré."""
        r, g, b = int(couleur_hex[1:3], 16), int(couleur_hex[3:5], 16), int(couleur_hex[5:7], 16)

        x_start = self.get_x()
        y_start = self.get_y()

        # Fond
        self.set_fill_color(r, g, b)
        self.rect(x_start, y_start, 58, 22, "F")

        # Valeur
        self.set_xy(x_start, y_start + 2)
        self.set_font("DejaVuSans", "B", 16)
        self.set_text_color(255, 255, 255)
        self.cell(58, 10, valeur, align="C", new_x="LMARGIN", new_y="NEXT")

        # Label
        self.set_xy(x_start, y_start + 12)
        self.set_font("DejaVuSans", "", 8)
        self.set_text_color(230, 230, 230)
        self.cell(58, 8, label, align="C")

    def tableau_service(self, items: list[tuple[str, dict]]):
        """Crée un tableau pour un service donné."""
        # En-tête du tableau
        self.set_font("DejaVuSans", "B", 9)
        self.set_fill_color(27, 42, 74)
        self.set_text_color(255, 255, 255)

        col_widths = [80, 25, 25, 30, 30]
        headers = ["Questionnaire", "Total", "Vides", "Complétion", "Statut"]

        for i, (h, w) in enumerate(zip(headers, col_widths)):
            last = i == len(headers) - 1
            self.cell(
                w, 8, h, border=1, align="C",
                fill=True,
                new_x="LMARGIN" if last else "RIGHT",
                new_y="NEXT" if last else "TOP",
            )

        # Lignes de données
        trié = sorted(items, key=lambda x: x[1]["taux_completion"])
        for idx, (q, d) in enumerate(trié):
            # Alternance de couleurs
            if idx % 2 == 0:
                self.set_fill_color(245, 247, 250)
            else:
                self.set_fill_color(255, 255, 255)

            taux = d["taux_completion"]

            # Couleur du statut
            if taux >= 98:
                statut = "OK"
                statut_couleur = COULEURS["vert"]
            elif taux >= 90:
                statut = "Attention"
                statut_couleur = COULEURS["orange"]
            else:
                statut = "Critique"
                statut_couleur = COULEURS["rouge"]

            q_affiche = q if len(q) <= 40 else q[:37] + "..."

            self.set_font("DejaVuSans", "", 9)
            self.set_text_color(44, 62, 80)

            self.cell(80, 7, q_affiche, border=1, fill=True)
            self.cell(25, 7, str(d["total"]), border=1, align="C", fill=True)
            self.cell(25, 7, str(d["vides"]), border=1, align="C", fill=True)
            self.cell(30, 7, f"{taux:.1f}%", border=1, align="C", fill=True)

            # Cellule statut colorée
            r, g, b = (
                int(statut_couleur[1:3], 16),
                int(statut_couleur[3:5], 16),
                int(statut_couleur[5:7], 16),
            )
            self.set_text_color(r, g, b)
            self.set_font("DejaVuSans", "B", 9)
            self.cell(
                30, 7, statut, border=1, align="C", fill=True,
                new_x="LMARGIN", new_y="NEXT",
            )

        self.ln(3)


# ──────────────────────────────────────────────
#  Génération du rapport PDF complet
# ──────────────────────────────────────────────

def generer_rapport_pdf(
    donnees: list[dict],
    stats: dict,
    questions: list[str],
    chemin_sortie: str,
) -> None:
    """Génère le rapport PDF complet."""

    services = regrouper_par_service(stats)
    total_global = sum(d["total"] for d in stats.values())
    vides_global = sum(d["vides"] for d in stats.values())
    taux_global = (
        ((total_global - vides_global) / total_global * 100)
        if total_global > 0 else 0.0
    )

    # Répertoire temporaire pour les graphiques
    tmp_dir = tempfile.mkdtemp()

    print("  > Generation des graphiques...")

    # Graphique 1 : Camembert global
    chemin_camembert = os.path.join(tmp_dir, "camembert_global.png")
    generer_camembert_global(stats, chemin_camembert)

    # Graphique 2 : Barres par service
    chemin_barres = os.path.join(tmp_dir, "barres_services.png")
    generer_barres_par_service(services, chemin_barres)

    # Graphiques détaillés par service
    chemins_detail = {}
    for nom_service, items in services.items():
        chemin_detail = os.path.join(tmp_dir, f"detail_{nom_service}.png")
        generer_barres_service_detail(nom_service, items, chemin_detail)
        chemins_detail[nom_service] = chemin_detail

    # ── Construction du PDF ──
    print("  > Construction du PDF...")

    pdf = RapportPDF("Rapport de Completude - CH Cahors")

    # Page de garde
    pdf.page_de_garde(
        nb_lignes=total_global,
        nb_services=len(services),
        nb_questions=len(questions),
    )

    # ── Page synthèse globale ──
    pdf.add_page()
    pdf.section_titre(
        "Synthèse Globale",
        "Vue d'ensemble de la complétude des questionnaires obligatoires "
        "sur l'ensemble des services.",
    )

    # Métriques encadrées
    y_metriques = pdf.get_y() + 2
    pdf.set_xy(10, y_metriques)
    pdf.metrique_encadree("Réponses analysées", str(total_global), COULEURS["bleu"])
    pdf.set_xy(72, y_metriques)
    pdf.metrique_encadree("Cases vides", str(vides_global), COULEURS["rouge"])
    pdf.set_xy(134, y_metriques)

    couleur_taux = (
        COULEURS["vert"] if taux_global >= 95
        else COULEURS["orange"] if taux_global >= 85
        else COULEURS["rouge"]
    )
    pdf.metrique_encadree("Taux global", f"{taux_global:.1f}%", couleur_taux)

    pdf.set_y(y_metriques + 30)

    # Texte d'analyse
    if taux_global >= 95:
        appreciation = (
            f"Le taux de complétude global est de {taux_global:.1f}%, ce qui est "
            f"un résultat satisfaisant. Sur les {total_global} réponses attendues "
            f"aux questionnaires obligatoires, seules {vides_global} cases sont restées "
            f"vides."
        )
    elif taux_global >= 85:
        appreciation = (
            f"Le taux de complétude global est de {taux_global:.1f}%. "
            f"Sur les {total_global} réponses attendues, {vides_global} cases sont "
            f"restées vides. Des efforts restent nécessaires pour atteindre l'objectif "
            f"de 100% de complétude sur les questions obligatoires."
        )
    else:
        appreciation = (
            f"Le taux de complétude global est de {taux_global:.1f}%, ce qui est "
            f"insuffisant. Sur les {total_global} réponses attendues, {vides_global} "
            f"cases sont restées vides. Une action corrective est recommandée "
            f"pour améliorer le remplissage des questionnaires obligatoires."
        )

    pdf.paragraphe(appreciation)

    # Camembert
    pdf.image(chemin_camembert, x=30, w=150)
    pdf.ln(5)

    # ── Page comparaison inter-services ──
    pdf.add_page()
    pdf.section_titre(
        "Comparaison entre services",
        "Taux de complétion des questionnaires obligatoires par service hospitalier.",
    )

    # Identifier les services problématiques
    services_critiques = []
    services_ok = []
    for nom_service, items in services.items():
        total_s = sum(d["total"] for _, d in items)
        vides_s = sum(d["vides"] for _, d in items)
        taux_s = ((total_s - vides_s) / total_s * 100) if total_s > 0 else 0
        if taux_s < 95:
            services_critiques.append((nom_service, taux_s, vides_s, total_s))
        else:
            services_ok.append((nom_service, taux_s))

    if services_critiques:
        services_critiques.sort(key=lambda x: x[1])
        texte_critique = (
            f"{len(services_critiques)} service(s) présentent un taux de complétude "
            f"inférieur à 95% et nécessitent une attention particulière :"
        )
        pdf.paragraphe(texte_critique)

        for nom, taux_s, vides_s, total_s in services_critiques:
            pdf.texte_important(
                f"  • {nom} : {taux_s:.1f}% ({vides_s} cases vides sur {total_s})",
                "rouge",
            )
        pdf.ln(2)
    else:
        pdf.texte_important(
            "Tous les services ont un taux de complétude supérieur ou égal à 95%.",
            "vert",
        )
        pdf.ln(2)

    # Graphique barres par service
    pdf.image(chemin_barres, x=10, w=190)

    # ── Pages détaillées par service ──
    for nom_service, items in services.items():
        pdf.add_page()

        pdf.section_titre(
            nom_service,
            f"Détail des questions obligatoires",
        )

        total_s = sum(d["total"] for _, d in items)
        vides_s = sum(d["vides"] for _, d in items)
        taux_s = ((total_s - vides_s) / total_s * 100) if total_s > 0 else 0

        # Phrase résumé
        nb_questionnaires_presents = len(items)
        nb_problemes = sum(1 for _, d in items if d["taux_completion"] < 100)

        if nb_problemes == 0:
            resume = (
                f"Le questionnaire {nom_service} présente un taux de complétude de "
                f"{taux_s:.1f}% sur {total_s} réponses analysées portant sur "
                f"{nb_questionnaires_presents} question(s) obligatoire(s). "
                f"Toutes les questions obligatoires ont été remplies."
            )
        else:
            resume = (
                f"Le questionnaire {nom_service} présente un taux de complétude de "
                f"{taux_s:.1f}% sur {total_s} réponses analysées. "
                f"{nb_problemes} question(s) obligatoire(s) sur {nb_questionnaires_presents} "
                f"présentent au moins une case vide ({vides_s} case(s) vide(s) au total)."
            )

        pdf.paragraphe(resume)

        # Tableau
        pdf.tableau_service(items)

        # Graphique détaillé
        if nom_service in chemins_detail:
            y_restant = 297 - pdf.get_y() - 25
            if y_restant < 50:
                pdf.add_page()
            pdf.image(chemins_detail[nom_service], x=15, w=180)

    # ── Page conclusion ──
    pdf.add_page()
    pdf.section_titre("Conclusion et recommandations")

    pdf.paragraphe(
        f"Ce rapport a analysé {total_global} réponses aux questionnaires obligatoires "
        f"réparties sur {len(services)} service(s) de l'établissement. "
        f"Le taux de complétude global est de {taux_global:.1f}%."
    )

    # Questionnaires vérifiés
    pdf.ln(5)
    pdf.texte_important("Questionnaires obligatoires vérifiés :", "bleu_fonce")
    for q in questions:
        pdf.paragraphe(f"  • {q}")

    # ── Sauvegarde ──
    pdf.output(chemin_sortie)
    print(f"[OK] Rapport PDF genere : {Path(chemin_sortie).resolve()}")

    # Nettoyage des fichiers temporaires
    for f in os.listdir(tmp_dir):
        os.remove(os.path.join(tmp_dir, f))
    os.rmdir(tmp_dir)


# ──────────────────────────────────────────────
#  Rapport console (conservé pour le debug)
# ──────────────────────────────────────────────

def generer_rapport_console(stats: dict) -> None:
    """Affiche le rapport dans la console."""
    services = regrouper_par_service(stats)

    print("=" * 90)
    print("  RAPPORT DE COMPLETUDE DES QUESTIONNAIRES OBLIGATOIRES")
    print("=" * 90)
    print()

    total_global = 0
    vides_global = 0

    for nom_service in sorted(services.keys()):
        items = services[nom_service]

        print(f"  Questionnaire : {nom_service}")
        print("-" * 90)
        print(
            f"  {'Question obligatoire':<50} {'Total':>7} {'Vides':>7} "
            f"{'Completion':>12}"
        )
        print("-" * 90)

        for questionnaire, data in sorted(items, key=lambda x: x[1]["taux_completion"]):
            total = data["total"]
            vides = data["vides"]
            taux = data["taux_completion"]
            total_global += total
            vides_global += vides

            if taux == 100.0:
                indicateur = "[OK]"
            elif taux >= 95.0:
                indicateur = "[!]"
            else:
                indicateur = "[!!]"

            print(
                f"  {questionnaire:<50} {total:>7} {vides:>7} "
                f"{taux:>10.1f}%  {indicateur}"
            )
        print()

    taux_global = (
        ((total_global - vides_global) / total_global * 100)
        if total_global > 0 else 0.0
    )
    print("=" * 90)
    print(f"  TOTAL GLOBAL : {total_global} reponses analysees")
    print(f"  CASES VIDES  : {vides_global}")
    print(f"  TAUX GLOBAL  : {taux_global:.1f}%")
    print("=" * 90)


# ──────────────────────────────────────────────
#  Point d'entrée CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Analyse la completude des questionnaires obligatoires "
            "et genere un rapport PDF professionnel."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples :
  python analyse_questionnaires.py
  python analyse_questionnaires.py --input export.csv --output rapport.pdf
  python analyse_questionnaires.py --config ma_config.json
  python analyse_questionnaires.py --format console
        """,
    )
    parser.add_argument(
        "--input", "-i",
        default="export_questionnaires_mock.csv",
        help="Fichier CSV d'entree (defaut: export_questionnaires_mock.csv)",
    )
    parser.add_argument(
        "--output", "-o",
        default="rapport_completude.pdf",
        help="Fichier PDF de sortie (defaut: rapport_completude.pdf)",
    )
    parser.add_argument(
        "--config", "-c",
        default="config_obligatoires.json",
        help="Fichier JSON de configuration (defaut: config_obligatoires.json)",
    )
    parser.add_argument(
        "--format", "-f",
        choices=["pdf", "console", "both"],
        default="pdf",
        help="Format de sortie : pdf, console, ou both (defaut: pdf)",
    )

    args = parser.parse_args()

    # Charger la configuration
    print(f"Chargement de la configuration : {args.config}")
    config = charger_config(args.config)
    nb_q_total = sum(len(v) for v in config.values())
    print(f"  > {len(config)} questionnaire(s) configures")
    print(f"  > {nb_q_total} question(s) obligatoire(s) au total")
    print()

    # Lecture des données
    print(f"Lecture du fichier : {args.input}")
    donnees = lire_csv(args.input)
    print(f"  > {len(donnees)} lignes de donnees lues")
    print()

    # Analyse
    stats = analyser_completude(donnees, config)

    questions_analysees = list(set(q for _, q in stats.keys()))

    if args.format in ("console", "both"):
        generer_rapport_console(stats)
        print()

    if args.format in ("pdf", "both"):
        generer_rapport_pdf(donnees, stats, questions_analysees, args.output)


if __name__ == "__main__":
    main()
