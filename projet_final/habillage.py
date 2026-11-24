"""L'habillage visuel du jeu : un blog des années 2000, avec ses publicités. Aucune règle ici."""

# ===== Les couleurs et polices, façon 2004 =====
CSS = """
/* Fond étoilé, comme sur les pages perso de l'époque */
body, gradio-app, .gradio-container {
    background-color: #000033 !important;
    background-image:
        radial-gradient(white 1px, transparent 1px),
        radial-gradient(#ffff66 1px, transparent 1px) !important;
    background-size: 40px 40px, 70px 70px !important;
    background-position: 0 0, 20px 35px !important;
}
.gradio-container { max-width: 1400px !important; }
.gradio-container, .gradio-container * {
    font-family: "Comic Sans MS", "Comic Neue", "Chalkboard SE", cursive !important;
}

/* La page centrale : une feuille blanche avec un cadre en relief */
#page-centrale {
    background: #ffffcc !important;
    border: 6px ridge #c0c0c0 !important;
    padding: 12px !important;
}
#page-centrale .block, #page-centrale .form {
    background: #ffffff !important;
    border: 3px outset #c0c0c0 !important;
    border-radius: 0 !important;
}
#page-centrale h1, #page-centrale h2, #page-centrale h3 {
    font-family: "Times New Roman", serif !important;
    color: #990000 !important;
    text-decoration: underline;
}

/* Les boutons, façon Windows 98 */
.bouton-retro, .bouton-retro button {
    background: #c0c0c0 !important;
    color: #000000 !important;
    border: 3px outset #ffffff !important;
    border-radius: 0 !important;
    font-weight: bold !important;
    box-shadow: none !important;
}
.bouton-retro:active, .bouton-retro button:active { border-style: inset !important; }
.bouton-rouge, .bouton-rouge button {
    background: #ff0000 !important;
    color: #ffff00 !important;
    border: 4px outset #ff9999 !important;
    border-radius: 0 !important;
    font-size: 1.3em !important;
    text-transform: uppercase;
}

/* Les onglets */
#page-centrale button[role="tab"] {
    background: #c0c0c0 !important;
    border: 2px outset #ffffff !important;
    border-radius: 0 !important;
    color: #000080 !important;
    font-weight: bold !important;
    margin-right: 4px;
}
#page-centrale button[role="tab"][aria-selected="true"] { background: #ffffcc !important; }

/* Les colonnes de publicités */
.colonne-pub { background: transparent !important; }
.pub {
    background: #ffffff;
    border: 3px outset #c0c0c0;
    margin-bottom: 14px;
    padding: 8px;
    text-align: center;
    cursor: pointer;
    font-size: 13px;
    color: #000000;
}
.pub:hover { border-style: inset; }
.pub .gros { font-size: 34px; display: block; }
.pub .titre-pub { font-weight: bold; color: #0000cc; text-decoration: underline; display: block; margin: 4px 0; }
.pub .prix { color: #ff0000; font-weight: bold; font-size: 16px; }
.pub-jaune { background: #ffff00; }
.pub-rose { background: #ff99cc; }
.pub-verte { background: #99ff99; }
.pub-bleue { background: #99ccff; }
.mini { font-size: 9px; color: #666666; display: block; margin-top: 4px; }
.texte-blanc { color: #ffffff; font-size: 11px; text-align: center; }

/* Les animations qui piquent les yeux */
@keyframes clignote { 50% { opacity: 0; } }
.clignote { animation: clignote 0.8s step-start infinite; }
@keyframes arc-en-ciel {
    0% { color: #ff0000; } 20% { color: #ff9900; } 40% { color: #ffff00; }
    60% { color: #00ff00; } 80% { color: #00ccff; } 100% { color: #ff00ff; }
}
.arc-en-ciel { animation: arc-en-ciel 2s linear infinite; }

/* L'en-tête */
.entete { text-align: center; padding: 6px 0; }
.entete, .entete div, .pied, .pied b, .texte-blanc, .texte-blanc b { color: #ffffff !important; }
.entete .grand-titre {
    font-size: 46px; font-weight: bold; letter-spacing: 3px;
    text-shadow: 3px 3px 0 #000000, 5px 5px 0 #ff00ff;
}
.bandeau {
    background: #000080; color: #ffff00; border: 2px inset #c0c0c0;
    font-weight: bold; padding: 4px 0;
}
.chantier {
    display: inline-block; margin: 6px; padding: 4px 12px; color: #000000; font-weight: bold;
    background: repeating-linear-gradient(45deg, #ffcc00 0 12px, #000000 12px 24px);
    border: 2px solid #000000;
}
.chantier span { background: #ffcc00; padding: 0 6px; }

/* Le compteur de visiteurs */
.compteur {
    display: inline-block; background: #000000; color: #00ff00;
    font-family: "Courier New", monospace !important; font-size: 20px;
    padding: 2px 8px; border: 3px inset #c0c0c0; letter-spacing: 4px;
}

/* Le pied de page */
.pied { text-align: center; color: #ffffff; font-size: 12px; padding: 10px; }
.pied a { color: #00ffff; }
"""


def entete(nombre_visites):
    """Renvoie l'en-tête du blog, avec son bandeau défilant."""
    return f"""
<div class="entete">
  <marquee class="bandeau" scrollamount="6">
    ★★★ BIENVENUE SUR LE BLOG OFFICIEL DE LA COLOC !!! ★★★ Dernière mise à jour : 24/11/2006 ★★★
    Signez mon livre d'or !!! ★★★ Qui a mangé le tiramisu ??? On veut des NOMS !!! ★★★
  </marquee>
  <div class="grand-titre arc-en-ciel">~*~ C'est Qui Qui ? ~*~</div>
  <div>💾 Le blog d'enquête n°1 des colocations françaises depuis 2003 💾</div>
  <div class="chantier"><span>🚧 SITE EN CONSTRUCTION 🚧</span></div>
  <div style="margin-top:6px;">
    Vous êtes le visiteur n° <span class="compteur">{nombre_visites:06d}</span>
    <span class="clignote" style="color:#ff0000;font-weight:bold;"> NEW !</span>
  </div>
</div>
"""


PUBS_GAUCHE = """
<div class="pub pub-jaune">
  <span class="gros">🍰</span>
  <span class="titre-pub">TIRAMISU-LOCK™</span>
  Le cadenas pour frigo.<br>Fini le « PAS TOUCHE » au feutre !<br>
  <span class="prix clignote">-50% !!!</span>
  <span class="mini">Offre réservée aux colocataires méfiants</span>
</div>
<div class="pub pub-rose">
  <span class="gros">🧦</span>
  <span class="titre-pub">Chaussettes Daltoniennes</span>
  Elles ne déteignent JAMAIS.<br>Ou presque.<br>
  <span class="prix">9,99 F</span>
</div>
<div class="pub">
  <span class="gros">🔮</span>
  <span class="titre-pub">Madame Irma, voyante</span>
  Elle sait QUI a fait le coup.<br>Elle l'a vu dans le marc de café.<br>
  <span class="prix">0,34 €/min</span>
  <span class="mini">Prix d'un appel + 12 tiramisus</span>
</div>
<div class="pub pub-verte">
  <span class="gros">📟</span>
  <span class="titre-pub">Détecteur de mensonges USB</span>
  Ta coloc te ment ?<br>Branche-la sur ton PC !<br>
  <span class="prix">19,99 €</span>
  <span class="mini">Compatible Windows 98 et ME</span>
</div>
<div class="texte-blanc">🏆 Site élu<br><b class="arc-en-ciel">MEILLEUR BLOG 2005</b><br>par ma mère</div>
"""


PUBS_DROITE = """
<div class="pub pub-jaune">
  <span class="clignote" style="color:#ff0000;font-weight:bold;">🎉 FÉLICITATIONS !!! 🎉</span>
  <span class="titre-pub">Vous êtes le 1 000 000e visiteur !</span>
  Vous avez gagné un<br><b>NAIN DE JARDIN</b> (presque neuf)
  <div class="bouton-retro" style="margin-top:6px;padding:2px;border:3px outset #fff;">CLIQUEZ ICI</div>
  <span class="mini">Le nain est actuellement en forêt</span>
</div>
<div class="pub pub-bleue">
  <span class="gros">⏰</span>
  <span class="titre-pub">Réveil Anti-Fanfare</span>
  Bloque toute musique bretonne avant 8h. Garanti.
</div>
<div class="pub">
  <span class="gros">🐧</span>
  <span class="titre-pub">Linux en 24h chrono</span>
  Changez les mots de passe de vos colocs comme un PRO !
  <span class="mini">Formation non reconnue par l'État</span>
</div>
<div class="pub pub-rose">
  <span class="gros">🍳</span>
  <span class="titre-pub">Poêles Phénix</span>
  Elles ne brûlent jamais.<br>(sauf les crêpes de Romain)<br>
  <span class="prix">2 achetées = 1 alarme offerte</span>
</div>
<div class="texte-blanc">
  📧 Écrivez-moi !<br>
  <span style="color:#00ffff;text-decoration:underline;">lacoloc@caramail.fr</span><br><br>
  🌐 Webring des colocs<br>« Précédent | Suivant »
</div>
"""


PIED = """
<div class="pied">
  <hr style="border:1px dashed #ffff00;">
  📖 <a>Livre d'or</a> | ⭐ <a>Ajouter aux favoris</a> | 🏠 <a>Faire de ce site ma page d'accueil</a><br>
  Ce site est optimisé pour <b>Internet Explorer 6</b> en <b>800×600</b>.<br>
  © 2006 La Coloc — Tous droits réservés — Ne pas copier SVP !!!
  <span class="clignote">✨</span>
</div>
"""
