#!/usr/bin/env python3
"""Creox site generator: writes a static DE/EN site into ../dist.
Every number, the legal entity and the product descriptions are plain HTML (no JS needed)."""
import json, pathlib, re, shutil

ROOT = pathlib.Path(__file__).resolve().parent
DIST = ROOT.parent / "dist"
SITE = "https://creox.ch"

# slug -> nav label
PAGES = ["index", "marketing-assistant", "ein-klick", "produkt", "projekte", "team", "kontakt", "impressum", "datenschutz", "agb"]

ORG = {
    "name": "Creox GmbH", "street": "Grabenstrasse 15b", "zip": "6340", "city": "Baar",
    "region": "ZG", "uid": "CHE-169.690.018", "email": "main@creox.ch",
}


def amp(s):
    """Elegant ampersand inside headings."""
    return s.replace(" &amp; ", ' <span class="amp">&amp;</span> ')


class Page:
    def __init__(self, lang, slug):
        self.lang, self.slug = lang, slug

    def L(self, de, en):
        return de if self.lang == "de" else en

    # relative link to another page in the same language
    def href(self, slug, anchor=""):
        name = "index.html" if slug == "index" else f"{slug}.html"
        return name + (f"#{anchor}" if anchor else "")

    def other_lang_href(self):
        name = "index.html" if self.slug == "index" else f"{self.slug}.html"
        return f"en/{name}" if self.lang == "de" else f"../{name}"

    def asset(self, name):
        return name if self.lang == "de" else f"../{name}"

    def url(self, lang=None, slug=None):
        lang = lang or self.lang
        slug = slug or self.slug
        path = "" if slug == "index" else slug
        return f"{SITE}/{'en/' if lang == 'en' else ''}{path}".rstrip("/") or SITE


def nav(p):
    items = [("index", p.L("Agentur", "Agency")), ("produkt", p.L("Produkte", "Products")),
             ("projekte", p.L("Projekte", "Work")), ("team", "Team"), ("kontakt", p.L("Kontakt", "Contact"))]
    cur = "produkt" if p.slug == "marketing-assistant" else p.slug
    links = "".join(
        f'<a href="{p.href(s)}"{" class=\"cur\" aria-current=\"page\"" if s == cur else ""}>{t}</a>' for s, t in items)
    other = "EN" if p.lang == "de" else "DE"
    return f'''<nav class="top" aria-label="{p.L('Hauptnavigation', 'Main navigation')}">
  <div class="wrap nav-in">
    <a href="{p.href('index')}" class="logo" aria-label="Creox — {p.L('Startseite', 'Home')}">CREOX.</a>
    <div class="nav-links" id="navlinks">{links}<a class="langbtn" href="{p.other_lang_href()}" hreflang="{other.lower()}" lang="{other.lower()}">{other}</a></div>
    <button class="menu-toggle" id="menutoggle" aria-label="Menu" aria-controls="navlinks" aria-expanded="false">&#9776;</button>
  </div>
</nav>'''


def footer(p):
    nav_links = "".join(f'<a href="{p.href(s)}">{t}</a>' for s, t in [
        ("marketing-assistant", "Marketing Assistant"), ("ein-klick", p.L("Marketing-Maschine", "Marketing machine")), ("produkt", p.L("Produkte", "Products")),
        ("projekte", p.L("Projekte", "Work")), ("team", "Team"), ("kontakt", p.L("Kontakt", "Contact"))])
    legal = "".join(f'<a href="{p.href(s)}">{t}</a>' for s, t in [
        ("impressum", p.L("Impressum", "Legal notice")), ("datenschutz", p.L("Datenschutz", "Privacy")),
        ("agb", p.L("AGB", "Terms"))])
    return f'''<footer>
  <div class="wrap foot-in">
    <div>
      <a href="{p.href('index')}" class="logo">CREOX.</a>
      <div class="foot-nav">{nav_links}</div>
    </div>
    <div>
      <div class="foot-meta">&copy; 2026 Creox GmbH &middot; Grabenstrasse 15b &middot; 6340 Baar &middot; UID CHE-169.690.018<br>
      {p.L('Eigene Marken', 'Own brands')}: MOTO-Z&Uuml;RICH &middot; SVOI &middot; Frankenplatz &middot; Cadre (ex&nbsp;Kunstwerkstube)</div>
      <div class="foot-legal">{legal}<a href="mailto:main@creox.ch">main@creox.ch</a></div>
    </div>
  </div>
</footer>'''


def org_jsonld():
    return {
        "@context": "https://schema.org", "@type": "Organization", "@id": f"{SITE}/#org",
        "name": "Creox GmbH", "legalName": "Creox GmbH", "url": SITE, "email": ORG["email"],
        "description": "Swiss event marketing and technology company building marketing automation and event products on Claude.",
        "address": {"@type": "PostalAddress", "streetAddress": ORG["street"], "postalCode": ORG["zip"],
                    "addressLocality": ORG["city"], "addressRegion": ORG["region"], "addressCountry": "CH"},
        "identifier": {"@type": "PropertyValue", "propertyID": "UID", "value": ORG["uid"]},
        "alternateName": "Vollenweider & Schweizer GmbH (until June 2026)",
        "founder": [{"@type": "Person", "name": "Yves Vollenweider"}, {"@type": "Person", "name": "Kseniia Chudina"}],
        "sameAs": ["https://motozuerich.ch", "https://frankenplatz.ch", "https://svoi.ch", "https://www.le-cadre.ch"],
    }


def page(p, title, desc, body, jsonld=None, extra_js=None):
    alt_de, alt_en = p.url("de"), p.url("en")
    ld = [org_jsonld()] + (jsonld or [])
    ld_html = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    return f'''<!DOCTYPE html>
<html lang="{p.lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{p.url()}">
<link rel="alternate" hreflang="de" href="{alt_de}">
<link rel="alternate" hreflang="en" href="{alt_en}">
<link rel="alternate" hreflang="x-default" href="{alt_de}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:url" content="{p.url()}">
<meta property="og:site_name" content="Creox">
<meta property="og:locale" content="{p.L('de_CH', 'en_GB')}">
<meta property="og:image" content="{SITE}/og.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{SITE}/og.png">
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<script>document.documentElement.classList.add('js')</script>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Space+Mono:wght@400;700&family=IBM+Plex+Mono:wght@400;500&family=Fraunces:ital,opsz,wght@1,9..144,500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{p.asset('style.css')}">
{ld_html}
</head>
<body>
{nav(p)}
<main>
{body}
</main>
{footer(p)}
<script src="{p.asset('site.js')}" defer></script>{f'<script type="module" src="{p.asset(extra_js)}"></script>' if extra_js else ''}
<!-- Vercel Web Analytics — cookie-free, ohne Consent-Banner (siehe Datenschutz) -->
<script>window.va=window.va||function(){{(window.vaq=window.vaq||[]).push(arguments);}};</script>
<script defer src="/_vercel/insights/script.js"></script>
</body>
</html>
'''


def hero(p, eyebrow, h1, lead, ctas, sub=True):
    btns = ""
    for i, (href, label) in enumerate(ctas):
        cls = "btn btn-primary" if i == 0 else "btn btn-ghost"
        btns += f'<a href="{href}" class="{cls}">{label}</a>'
    return f'''<header class="hero{' sub' if sub else ''}">
  <div class="wrap">
    <span class="eyebrow reveal">{eyebrow}</span>
    <h1 class="reveal">{h1}</h1>
    <p class="lead reveal">{lead}</p>
    {f'<div class="hero-cta reveal">{btns}</div>' if btns else ''}
  </div>
</header>'''


def sec_head(eyebrow, h2, p=""):
    return f'''<div class="sec-head reveal"><span class="eyebrow">{eyebrow}</span><h2>{amp(h2)}</h2>{f'<p>{p}</p>' if p else ''}</div>'''


# ------------------------------------------------------------------ content blocks

def services(p):
    items = [
        (p.L("Strategie &amp; Markenentwicklung", "Strategy &amp; brand development"),
         p.L("Jedes erfolgreiche Projekt beginnt mit einer klaren Vision. Wir entwickeln Strategien, Eventformate und Marken mit einer starken Positionierung &ndash; und setzen sie visuell um: Brandbooks, Kataloge, Brosch&uuml;ren sowie Design f&uuml;r Websites und Social Media, alles in einem einheitlichen Stil.",
             "Every successful project starts with a clear vision. We develop strategies, event formats and brands with strong positioning &ndash; and bring them to life visually: brand books, catalogues, brochures and design for websites and social media, all in one consistent style.")),
        (p.L("Marketing &amp; Wachstum", "Marketing &amp; growth"),
         p.L("Sichtbarkeit entsteht nicht zuf&auml;llig. Mit kreativen Kampagnen, datenbasiertem Marketing, Content, Performance Advertising und Community-Aufbau schaffen wir Reichweite, gewinnen Zielgruppen und f&ouml;rdern nachhaltiges Wachstum.",
             "Visibility doesn&#39;t happen by chance. With creative campaigns, data-driven marketing, content, performance advertising and community building we create reach, win audiences and drive sustainable growth.")),
        (p.L("Digitale L&ouml;sungen &amp; KI", "Digital solutions &amp; AI"),
         p.L("Digitale L&ouml;sungen schaffen effiziente Prozesse und bessere Erlebnisse. Wir entwickeln Websites, Eventplattformen, Ticketing-Systeme, CRM und Dateninfrastruktur (Next.js, Supabase, Stripe) sowie KI-gest&uuml;tzte Automationen. Zielgruppen und Daten bleiben durchg&auml;ngig bei uns.",
             "Digital solutions create efficient processes and better experiences. We build websites, event platforms, ticketing systems, CRM and data infrastructure (Next.js, Supabase, Stripe) plus AI-powered automations. Audiences and data stay ours end to end.")),
        (p.L("Produktion &amp; Eventmanagement", "Production &amp; event management"),
         p.L("Von der Location bis zum letzten Gast koordinieren wir alle operativen Abl&auml;ufe. Projektmanagement, Infrastruktur, Technik, Logistik, Sicherheit und Vor-Ort-Betreuung sorgen daf&uuml;r, dass Ideen zu perfekt organisierten Erlebnissen werden.",
             "From the venue to the last guest we coordinate all operational processes. Project management, infrastructure, technology, logistics, safety and on-site support turn ideas into perfectly organised experiences.")),
        (p.L("Kommunikation &amp; Partnerschaften", "Communication &amp; partnerships"),
         p.L("Erfolgreiche Projekte leben von starken Beziehungen. Wir entwickeln Kommunikationsstrategien, PR-Konzepte, Sponsoring-Partnerschaften und Kooperationen, die Marken sichtbar machen und langfristige Wirkung entfalten.",
             "Successful projects thrive on strong relationships. We develop communication strategies, PR concepts, sponsoring partnerships and collaborations that make brands visible and create long-term impact.")),
        (p.L("Beratung &amp; Projektbegleitung", "Consulting &amp; project support"),
         p.L("Nicht jedes Projekt ben&ouml;tigt eine vollst&auml;ndige Umsetzung. Wir unterst&uuml;tzen Unternehmen, Veranstalter und Organisationen mit strategischer Beratung, Projektmanagement und operativer Begleitung &ndash; flexibel, effizient und genau dort, wo zus&auml;tzliche Kompetenz gefragt ist.",
             "Not every project needs full delivery. We support companies, organisers and organisations with strategic consulting, project management and operational support &ndash; flexible, efficient and exactly where extra expertise is needed.")),
    ]
    cells = ""
    for i, (h, txt) in enumerate(items, 1):
        n = f"{i:02d}"
        cells += (f'<div class="cell svc"><div class="bn" aria-hidden="true">{n}</div>'
                  f'<div class="cover" aria-hidden="true"><div class="cn">{n}</div><div class="ct">{amp(h)}</div></div>'
                  f'<div class="n">{n}</div><h3>{amp(h)}</h3><p>{txt}</p></div>')
    return cells


def products_data(p):
    """Single source for the four products (hub page + teaser)."""
    return [
        dict(id="marketing-assistant", name="Marketing Assistant",
             short=p.L("Ein Claude-Kern auf Ihren Markendaten: Content, Kommunikation und Recherche &mdash; mit Ihrer Freigabe vor jeder Ver&ouml;ffentlichung.",
                       "One Claude core on your brand data: content, communication and research &mdash; with your approval before anything is published."),
             status=p.L("Im Einsatz", "In use"),
             problem=p.L("KMU, Event-Veranstalter und Communities haben zu wenig Leute f&uuml;r st&auml;ndigen, markengerechten Content auf allen Kan&auml;len.",
                         "SMEs, event organisers and communities lack the people for steady, on-brand content across every channel."),
             what=p.L("Claude, per MCP mit Markendaten, Designsystem und Kan&auml;len verbunden. Agenten f&uuml;r Content, Kommunikation und Recherche bereiten vor &mdash; ein Mensch gibt frei.",
                      "Claude, connected via MCP to brand data, design system and channels. Agents for content, communication and research prepare the work &mdash; a person approves it."),
             where=p.L("MOTO-Z&Uuml;RICH, SVOI, Frankenplatz, Cadre (ex&nbsp;Kunstwerkstube).",
                       "MOTO-Z&Uuml;RICH, SVOI, Frankenplatz, Cadre (ex&nbsp;Kunstwerkstube)."),
             claude=p.L("Der Kern des Produkts: Texte, Karussells, Mailings, Artikel, Klassifikation von Community-Nachrichten, Reports.",
                        "The core of the product: copy, carousels, mailings, articles, classification of community messages, reports."),
             when=p.L("L&auml;uft auf unseren Marken; erste externe Kund:innen im Onboarding.", "Running on our brands; first external clients onboarding."),
             cta=(p.href("marketing-assistant"), p.L("Zum Marketing Assistant", "Explore Marketing Assistant"))),
        dict(id="antrix", name="Antrix",
             short=p.L("Ticketing und Loyalit&auml;t auf der eigenen Website: Tickets, QR-Einlass, Zeitslots, CRM und Ambassador-Codes &mdash; ohne Plattformprovision.",
                       "Ticketing and loyalty on your own website: tickets, QR entry, time slots, CRM and ambassador codes &mdash; without platform commission."),
             status=p.L("MVP Oktober 2026", "MVP October 2026"),
             problem=p.L("Fremde Ticketplattformen nehmen Provision und behalten die Daten der G&auml;ste.",
                         "Third-party ticketing platforms take a commission and keep the guest data."),
             what=p.L("Ticketverkauf auf der eigenen Website, QR-Einlass, Zeitslots, Zahlung, CRM, Promo-Codes, Ambassador-Codes, Loyalit&auml;tsprogramm f&uuml;r wiederkehrende G&auml;ste.",
                      "Ticket sales on your own site, QR entry, time slots, payment, CRM, promo and ambassador codes, a loyalty programme for returning guests."),
             where=p.L("Tickets f&uuml;r MOTO-Z&Uuml;RICH (22&#39;117 Besucher:innen 2026), Frankenplatz mit Ambassador-Programm, FASHION REBORN.",
                       "Tickets for MOTO-Z&Uuml;RICH (22&#39;117 visitors in 2026), Frankenplatz with an ambassador programme, FASHION REBORN."),
             claude=p.L("Segmentierung der G&auml;ste nach Kaufumfrage, pers&ouml;nliche Mails vor und nach dem Event, Antworten auf G&auml;stefragen, Verkaufsreport.",
                        "Guest segmentation from the purchase survey, personal emails before and after the event, answers to guest questions, sales reports."),
             when=p.L("MVP Oktober 2026.", "MVP October 2026."),
             cta=(p.href("kontakt"), p.L("Demo f&uuml;r Veranstalter", "Demo for organisers"))),
        dict(id="motogen", name="MotoGen",
             short=p.L("Die Plattform f&uuml;r Motorradfahrer:innen in der Schweiz &mdash; und die digitale Basis von MOTO-Z&Uuml;RICH.",
                       "The platform for motorcyclists in Switzerland &mdash; and the digital backbone of MOTO-Z&Uuml;RICH."),
             status=p.L("In Entwicklung", "In development"),
             problem=p.L("Motorradfahrer:innen in der Schweiz haben keinen gemeinsamen Ort f&uuml;r Bike, Routen, Clubs, Events und Services.",
                         "Motorcyclists in Switzerland have no single place for their bike, routes, clubs, events and services."),
             what=p.L("Digitale Garage, Strassenkarte, Challenges und Badges, Clubs, gemeinsame Ausfahrten, Events, Katalog f&uuml;r Service und Teile, QR-Profil. F&uuml;r MOTO-Z&Uuml;RICH: Ausstellerportal (Vertrag mit einem Klick), interaktiver Hallenplan, Besucherkonto.",
                      "Digital garage, road map, challenges and badges, clubs, group rides, events, a catalogue of services and parts, QR profile. For MOTO-Z&Uuml;RICH: exhibitor portal (contract in one click), interactive hall plan, visitor account."),
             where=p.L("MOTO-Z&Uuml;RICH 2027 (<span class='nobr'>19.&ndash;21. Februar</span>) &mdash; Ausstellerportal und Hallenplan.", "MOTO-Z&Uuml;RICH 2027 (<span class='nobr'>19&ndash;21 February</span>) &mdash; exhibitor portal and hall plan."),
             claude=p.L("Empfehlungen f&uuml;r Routen und Events, Antworten an Aussteller zum Reglement, Akquise-Mails an Aussteller, Leads f&uuml;r H&auml;ndler aus der Besucherbasis.",
                        "Route and event suggestions, answers to exhibitors on the regulations, exhibitor acquisition emails, dealer leads from the visitor base."),
             when=p.L("Ausstellerportal zur Ausgabe 2027.", "Exhibitor portal for the 2027 edition."),
             cta=(p.asset("motogen.html"), p.L("MotoGen im Detail", "MotoGen in detail"))),
        dict(id="audio-guide", name="Audio Guide",
             short=p.L("QR-Code am Werk &rarr; Geschichte des Werks und eigens daf&uuml;r geschriebene Musik. Verbunden mit dem Kunstkatalog <span class='nobr'>le-cadre.ch</span>.",
                       "QR code at the artwork &rarr; the story of the work and music written for it. Connected to the art catalogue <span class='nobr'>le-cadre.ch</span>."),
             status="MVP",
             problem=p.L("Kleine Galerien haben keine Mittel f&uuml;r mehrsprachige Vermittlung jedes Werks.",
                         "Small galleries lack the means to explain every work in several languages."),
             what=p.L("QR-Code am Werk &rarr; Geschichte des Werks und Musik dazu; eine Seite pro K&uuml;nstler:in im Katalog <span class='nobr'>le-cadre.ch</span>, auf Deutsch, Englisch und Russisch.",
                      "QR code at the artwork &rarr; its story and music; one page per artist in the <span class='nobr'>le-cadre.ch</span> catalogue, in German, English and Russian."),
             where=p.L("Galerie Cadre (ex&nbsp;Kunstwerkstube) in Baden, Partnerausstellungen im Waldgasthaus Baldegg.",
                       "Gallery Cadre (ex&nbsp;Kunstwerkstube) in Baden, partner exhibitions at Waldgasthaus Baldegg."),
             claude=p.L("Texte zu den Werken in drei Sprachen aus dem Material der K&uuml;nstler:innen, Etiketten, Katalogkarten.",
                        "Texts about the works in three languages from the artists&#39; material, labels, catalogue cards."),
             when="MVP.",
             cta=(p.href("kontakt"), p.L("Anfragen", "Get in touch"))),
    ]


def product_teaser(p):
    cells = ""
    for i, d in enumerate(products_data(p), 1):
        link = (p.href("marketing-assistant") if d["id"] == "marketing-assistant"
                else p.asset("motogen.html") if d["id"] == "motogen" else p.href("produkt", d["id"]))
        cells += (f'<div class="cell"><span class="tag">{d["status"]}</span><div class="n">P{i}</div><h3>{d["name"]}</h3>'
                  f'<p>{d["short"]}</p><a class="more" href="{link}">{p.L("Mehr", "More")} &rarr;</a></div>')
    return f'<div class="grid2 reveal">{cells}</div>'


def metrics(items, blue=False):
    cells = "".join(f'<div><div class="mv">{v}</div><div class="ml">{l}</div></div>' for v, l in items)
    return f'<div class="metrics{" metrics-blue" if blue else ""} reveal">{cells}</div>'


def cases(p, full=True):
    moto = f'''<article class="case feature reveal" id="moto-zuerich">
  <div class="meta"><div class="yr">FEB 2026 &middot; 2027: 19.&ndash;21.02.</div><div class="loc">StageOne &middot; Halle 550 &middot; Z&uuml;rich</div></div>
  <div>
    <span class="role">{p.L('Eigenes Event &middot; Inhouse', 'Our event &middot; Produced in-house')}</span>
    <h3><a href="https://motozuerich.ch/" target="_blank" rel="noopener" class="caselink">MOTO-Z&Uuml;RICH <span class="arr">&rarr;</span></a></h3>
    <p>{p.L('Als die SWISS-MOTO in Z&uuml;rich und im Anschluss das motofestival in Bern eingestellt wurden, entstand eine L&uuml;cke im Schweizer Markt. Creox entwickelte daraus innerhalb weniger Monate eine neue Eventmarke &ndash; inklusive Strategie, Markenentwicklung, Marketing, Ticketing, Sponsoring und Gesamtproduktion. Moto Z&uuml;rich zeigt, wie aus einer Idee eine erfolgreiche Plattform entsteht.',
            'When SWISS-MOTO in Zurich and subsequently the motofestival in Bern were discontinued, a gap opened in the Swiss market. Within a few months Creox developed a new event brand from it &ndash; including strategy, brand development, marketing, ticketing, sponsoring and full production. Moto Z&uuml;rich shows how a single idea becomes a successful platform.')}</p>
    {metrics([("22&#39;117", p.L("Besucher:innen", "Visitors")), ("2.5", p.L("Tage, ausverkauft", "Days, sold out")), ("10&#39;000&nbsp;m&sup2;", p.L("Fl&auml;che", "Floor space")), ("80", p.L("Aussteller", "Exhibitors"))])}
    <p class="uses"><b>{p.L('Creox-Produkte im Einsatz', 'Creox products in use')}</b>Antrix (Tickets) &middot; {p.L('Ausstellerportal und Hallenplan', 'exhibitor portal and hall plan')} &middot; {p.L('personalisierte Aussteller-Mailings', 'personalised exhibitor mailings')} &middot; {p.L('Analytics-Reports', 'analytics reports')}</p>
  </div>
</article>'''
    gallery = f'''<article class="case reveal" id="cadre">
  <div class="meta"><div class="yr">{p.L('LAUFEND', 'ONGOING')}</div><div class="loc">Baden (AG)</div></div>
  <div>
    <span class="role">{p.L('Eigenes Projekt &middot; Galerie', 'Our project &middot; Gallery')}</span>
    <h3><a href="https://www.le-cadre.ch/" target="_blank" rel="noopener" class="caselink">Cadre (ex&nbsp;Kunstwerkstube) <span class="arr">&rarr;</span></a></h3>
    <p>{p.L('Aus der Galerie Kunstwerkstube wurde Cadre: gleiches Haus von 1829 im B&auml;derquartier Baden, jetzt Galerie mit Brunch, Ap&eacute;ro und geladenen Dinnern. Seit Juni 2024 &uuml;ber 30 Ausstellungen mit mehr als 100 K&uuml;nstler:innen und verkaufte Werke im Wert von mehr als 150&#39;000&nbsp;CHF.',
            'Galerie Kunstwerkstube has become Cadre: the same 1829 house in Baden&#39;s bath quarter, now a gallery with brunch, ap&eacute;ro and invited dinners. Since June 2024: more than 30 exhibitions with over 100 artists, and works sold for more than CHF&nbsp;150&#39;000.')}</p>
    {metrics([("30+", p.L("Ausstellungen", "Exhibitions")), ("100+", p.L("K&uuml;nstler:innen", "Artists")), ("150&#39;000+", p.L("CHF Werke verkauft", "CHF in works sold")), ("2", p.L("Partnerausstellungen", "Partner shows"))], blue=True)}
    <p class="uses"><b>{p.L('Creox-Produkte im Einsatz', 'Creox products in use')}</b>{p.L('Kunstkatalog <span class="nobr">le-cadre.ch</span> &middot; Audio Guide &middot; QR-Etiketten', 'Art catalogue <span class="nobr">le-cadre.ch</span> &middot; Audio Guide &middot; QR labels')}</p>
  </div>
</article>'''
    svoi = f'''<article class="case reveal" id="svoi">
  <div class="meta"><div class="yr">{p.L('LAUFEND', 'ONGOING')}</div><div class="loc">{p.L('Ganze Schweiz', 'All of Switzerland')}</div></div>
  <div>
    <span class="role">{p.L('Eigenes Projekt &middot; Community', 'Our project &middot; Community')}</span>
    <h3><a href="https://svoi.ch/" target="_blank" rel="noopener" class="caselink">SVOI <span class="arr">&rarr;</span></a></h3>
    <p>{p.L('Plattform f&uuml;r Community und Events der russischsprachigen Schweiz: 17 kantonale Chats, ein Veranstaltungsregister und eigene Events. Ein einziger Beitrag zum 1. August brachte &uuml;ber 100 neue Follower an einem Tag.',
            'Community and events platform for Russian speakers in Switzerland: 17 cantonal chats, an events registry and our own events. A single post for 1 August brought more than 100 new followers in one day.')}</p>
    <p class="uses"><b>{p.L('Creox-Produkte im Einsatz', 'Creox products in use')}</b>Marketing Assistant &middot; {p.L('Community-Listener &middot; Eventregister &middot; Karussell-Builder &middot; Lead-Erfassung aus Threads', 'community listener &middot; events registry &middot; carousel builder &middot; lead capture from Threads')}</p>
  </div>
</article>'''
    fp = f'''<article class="case reveal" id="frankenplatz">
  <div class="meta"><div class="yr">14.&ndash;15.11.2026</div><div class="loc">Lausanne</div></div>
  <div>
    <span class="role">{p.L('Eigenes Event &middot; Forum', 'Our event &middot; Forum')}</span>
    <h3><a href="https://frankenplatz.ch/" target="_blank" rel="noopener" class="caselink">Frankenplatz <span class="arr">&rarr;</span></a></h3>
    <p>{p.L('Forum &uuml;ber pers&ouml;nliche Finanzen in der Schweiz. Erste Ausgabe im November 2026, f&uuml;r 2027 sind drei Daten geplant. Content, Ticketing und Ambassador-Programm laufen &uuml;ber unsere eigenen Systeme.',
            'A forum on personal finance in Switzerland. First edition in November 2026, three dates planned for 2027. Content, ticketing and the ambassador programme run on our own systems.')}</p>
    <p class="uses"><b>{p.L('Creox-Produkte im Einsatz', 'Creox products in use')}</b>Marketing Assistant &middot; Antrix &middot; {p.L('Artikel-Fabrik &middot; Rechner &middot; Mailings &middot; Ambassador-Codes &middot; Analytics-Cockpit', 'article factory &middot; calculators &middot; mailings &middot; ambassador codes &middot; analytics cockpit')}</p>
  </div>
</article>'''
    return moto + gallery + (svoi + fp if full else "")


# ------------------------------------------------------------------ pages

def p_index(p):
    body = hero(p,
                p.L("Strategie &middot; Kreativit&auml;t &middot; Technologie", "Strategy &middot; Creativity &middot; Technology"),
                p.L('Wir schaffen <span class="accent">Erlebnisse mit Wirkung</span>.', 'We create <span class="accent">experiences with impact</span>.'),
                p.L("Creox verbindet Strategie, Kreativit&auml;t und Technologie. Wir entwickeln Erlebnisse, digitale L&ouml;sungen und Marken, die Menschen begeistern und Unternehmen nachhaltig voranbringen. Aus unseren eigenen Events entstehen Produkte: Ticketing, Plattformen und ein Marketing Assistant auf Basis von Claude.",
                    "Creox combines strategy, creativity and technology. We develop experiences, digital solutions and brands that inspire people and move companies forward for the long term. Our own events give rise to products: ticketing, platforms and a Marketing Assistant built on Claude."),
                [(p.href("kontakt"), p.L("Event anfragen", "Brief us on your event")), (p.href("marketing-assistant"), "Marketing Assistant")], sub=False)

    lines = [p.L("Jedes erfolgreiche Projekt beginnt mit einer Herausforderung.", "Every successful project starts with a challenge."),
             p.L("Vielleicht planen Sie Ihr erstes Projekt.", "Maybe you&#39;re planning your first project."),
             p.L("Vielleicht m&ouml;chten Sie ein bestehendes Projekt weiterentwickeln.", "Maybe you want to evolve an existing project."),
             p.L("Vielleicht suchen Sie einen Partner f&uuml;r Marketing, digitale L&ouml;sungen oder die komplette Umsetzung.", "Maybe you&#39;re looking for a partner for marketing, digital solutions or the complete delivery."),
             p.L("Oder Sie ben&ouml;tigen ein Team, das Strategie, Kreativit&auml;t und Technologie nahtlos miteinander verbindet.", "Or you need a team that seamlessly connects strategy, creativity and technology.")]
    body += f'''<section class="intro">
  <div class="wrap">
    <span class="eyebrow reveal">{p.L('Wo Sie gerade stehen', 'Where you are now')}</span>
    <div class="intro-lines">{''.join(f'<p class="intro-line">{l}</p>' for l in lines)}</div>
    <p class="intro-punch reveal">{p.L('Genau daf&uuml;r gibt es <span class="box">Creox.</span>', 'That&#39;s exactly what <span class="box">Creox is for.</span>')}</p>
  </div>
</section>
<section id="leistungen">
  <div class="wrap">
    {sec_head(p.L('Was wir tun', 'What we do'), p.L('Ein Partner. Alle Kompetenzen.', 'One partner. Every capability.'),
              p.L('Von der ersten Idee &uuml;ber Strategie, Kreativit&auml;t und Marketing bis hin zu Technologie, Produktion und Betrieb begleiten wir Projekte ganzheitlich. So entstehen L&ouml;sungen, die nachhaltig wirken &ndash; mit einem Ansprechpartner und einem eingespielten Team.',
                  'From the first idea through strategy, creativity and marketing to technology, production and operations, we support projects holistically. The result: solutions that have lasting impact &ndash; with one contact and one well-rehearsed team.'))}
    <div class="grid3 reveal">{services(p)}</div>
  </div>
</section>
<section id="produkte">
  <div class="wrap">
    {sec_head(p.L('Produkte', 'Products'), p.L('Aus unseren Events entstanden.', 'Born at our own events.'),
              p.L('Was bei MOTO-Z&Uuml;RICH, SVOI, Frankenplatz und in der Galerie funktioniert, machen wir zum Produkt. Claude ist dabei der gemeinsame Kern.',
                  'What works at MOTO-Z&Uuml;RICH, SVOI, Frankenplatz and the gallery becomes a product. Claude is the shared core.'))}
    {product_teaser(p)}
    <div class="sec-more"><a class="btn btn-line" href="{p.href('ein-klick')}">{p.L('Marketing-Maschine: ein Foto, jeder Kanal', 'Marketing machine: one photo, every channel')} &rarr;</a></div>
  </div>
</section>
<section id="projekte">
  <div class="wrap">
    {sec_head(p.L('Projekte mit Wirkung', 'Projects with impact'), p.L('Beweise statt Versprechen.', 'Proof, not promises.'),
              p.L('Unsere Erfahrung basiert auf eigenen Projekten. Wir entwickeln Marken, Veranstaltungen und digitale L&ouml;sungen &ndash; und bringen dieses Wissen in jedes Kundenprojekt ein.', 'Our experience is built on our own projects. We develop brands, events and digital solutions &ndash; and bring that knowledge into every client project.'))}
    {cases(p, full=False)}
    <div class="sec-more"><a class="btn btn-line" href="{p.href('projekte')}">{p.L('Alle Projekte', 'All projects')} &rarr;</a></div>
  </div>
</section>
<section class="dark">
  <div class="wrap">
    {sec_head(p.L('Kontakt', 'Contact'), p.L('Erz&auml;hlen Sie uns, woran Sie denken.', 'Tell us what you have in mind.'),
              p.L('Kein fertiges Briefing n&ouml;tig. Ein paar Zeilen gen&uuml;gen &ndash; wir melden uns und schauen gemeinsam, was m&ouml;glich ist.',
                  'No finished brief needed. A few lines are enough &ndash; we&#39;ll get back to you and figure out together what&#39;s possible.'))}
    <a class="btn btn-primary" href="{p.href('kontakt')}">{p.L('Kontakt aufnehmen', 'Get in touch')} &rarr;</a>
  </div>
</section>'''
    return page(p,
                p.L("Creox — Event-Agentur & KI-Marketing mit Claude | Schweiz", "Creox — Event agency & AI marketing built on Claude | Switzerland"),
                p.L("Creox GmbH, Baar: Full-Service-Eventagentur und Produktfirma. Eigenes Ticketing, MotoGen und der Marketing Assistant auf Basis von Claude (KI) — erprobt an MOTO-ZÜRICH, SVOI und Frankenplatz.",
                    "Creox GmbH, Baar (Switzerland): full-service event agency and product company. Own ticketing, MotoGen and the Marketing Assistant built on Claude (AI) — proven at MOTO-ZÜRICH, SVOI and Frankenplatz."),
                body)


def p_ma(p):
    flow = [
        ("01", p.L("Markendaten", "Brand data"), p.L("Tonalit&auml;t, Produkte, Designsystem, Zielgruppen, Beispiele.", "Tone of voice, products, design system, audiences, examples."), ""),
        ("02", "Claude + MCP", p.L("Ein Kern, per MCP mit Ihren Daten und Tools verbunden.", "One core, connected to your data and tools via MCP."), ""),
        ("03", p.L("Agenten", "Agents"), p.L("Content, Kommunikation, Recherche &mdash; bereiten Entw&uuml;rfe vor.", "Content, communication, research &mdash; prepare drafts."), ""),
        ("04", p.L("Freigabe", "Approval"), p.L("Ein Mensch pr&uuml;ft und dr&uuml;ckt &laquo;Ver&ouml;ffentlichen&raquo;.", "A person reviews and presses &ldquo;publish&rdquo;."), " human"),
        ("05", p.L("Kan&auml;le", "Channels"), p.L("Website, Newsletter, Social Media, Messenger, Reports.", "Website, newsletters, social media, messengers, reports."), ""),
    ]
    flow_html = "".join(f'<div class="{c.strip()}"><div class="k">{k}</div><h4>{h}</h4><p>{t}</p></div>' for k, h, t, c in flow)

    machines = [
        (p.L("Karussell-Builder", "Carousel builder"), p.L("Posts 1080&times;1350 im Designsystem der Marke: zwei bis drei Slides mit Humor, grosse Zahlen, eine Frage an die Leser:innen.", "1080&times;1350 posts in the brand&#39;s design system: two or three slides with humour, big numbers, a question for readers."), "SVOI, Frankenplatz, chudina.me"),
        (p.L("HTML-Mailing-Builder", "HTML mailing builder"), p.L("Reiche Mailings im Stil der Marke, direkt versandfertig.", "Rich, on-brand mailings, ready to send."), p.L("Alle Projekte", "All projects")),
        (p.L("Aussteller-Mailings", "Exhibitor mailings"), p.L("Personalisierte Briefe an Aussteller und automatischer Versand aus der Datenbank.", "Personalised letters to exhibitors and automated sending from the database."), "MOTO-Z&Uuml;RICH"),
        (p.L("Video-Maschine", "Video machine"), p.L("Werbeclips von 5 bis 10 Sekunden und Reels 1080&times;1920 aus Karussells und Fotos der Website.", "5 to 10 second ads and 1080&times;1920 reels from carousels and website photos."), p.L("chudina.me, SVOI, Event-Plakate", "chudina.me, SVOI, event posters")),
        (p.L("Artikel-Fabrik", "Article factory"), p.L("SEO-Artikel nach einheitlicher Vorlage: kurz &rarr; Analyse &rarr; Checkliste &rarr; Datum der Quellenpr&uuml;fung.", "SEO articles on one template: summary &rarr; analysis &rarr; checklist &rarr; date the sources were checked."), "Frankenplatz, SVOI"),
        (p.L("Rechner", "Calculators"), p.L("Interaktive Rechner f&uuml;r Artikel und Lead-Generierung.", "Interactive calculators for articles and lead generation."), "Frankenplatz"),
        (p.L("SEO-Profile und Etiketten", "SEO profiles and labels"), p.L("Profile von Organisationen, Etiketten und QR-Codes f&uuml;r Werke in der Galerie.", "Organisation profiles, labels and QR codes for works in the gallery."), "Cadre"),
    ]
    mach_html = "".join(f'<div class="cell"><div class="n">M{i:02d}</div><h3>{h}</h3><p>{t}</p><div class="where">{w}</div></div>' for i, (h, t, w) in enumerate(machines, 1))
    mach_html += f'<div class="cell cta-cell"><div class="n">M08</div><h3>{p.L("Ihre Maschine fehlt?", "Missing your machine?")}</h3><p>{p.L("Wir bauen sie auf Ihrem Designsystem und Ihren Daten &mdash; mit derselben Freigabe-Logik.", "We build it on your design system and data &mdash; with the same approval logic.")}</p><a class="more" href="#demo">{p.L("Demo anfragen", "Request a demo")} &rarr;</a></div>'

    autos = [
        (p.L("Community-Listener", "Community listener"), p.L("Liest die 17 kantonalen Chats von SVOI, Claude klassifiziert die Nachrichten, alles landet strukturiert in einer Tabelle.", "Reads the 17 cantonal SVOI chats; Claude classifies the messages and everything lands structured in a table.")),
        (p.L("Event-Parser", "Event parser"), p.L("Sammelt Veranstaltungen und Veranstalter in ein Register mit Status Entwurf / ver&ouml;ffentlichen / ausblenden f&uuml;r Website und Social Media.", "Collects events and organisers into a registry with draft / publish / hide status for website and social media.")),
        (p.L("Lead-Radar Threads", "Threads lead radar"), p.L("Beobachtet Konten, sammelt Leads und liefert t&auml;glich einen Digest. Ein neues Projekt ist eine neue Zeile.", "Watches accounts, collects leads and delivers a daily digest. A new project is one new row.")),
        (p.L("Content-Fabrik Social Media", "Social media content factory"), p.L("Aus einem Thema entstehen Posts, Karussells, Reels und Stories f&uuml;r alle Social-Media-Kan&auml;le, je Kanal passend formuliert und nach Freigabe eingeplant.", "One topic becomes posts, carousels, reels and stories for every social channel, written for each channel and scheduled after approval.")),
        (p.L("Community-Bot", "Community bot"), p.L("Onboarding neuer Mitglieder mit Captcha und Versand von Inhalten in ausgew&auml;hlte Chats.", "Onboarding of new members with a captcha and sending content to selected chats.")),
        (p.L("Wettbewerbs-Radar", "Competitor radar"), p.L("W&ouml;chentliches Monitoring von Foren und Workshops zu Finanzthemen in der Schweiz.", "Weekly monitoring of finance forums and workshops in Switzerland.")),
        (p.L("Cockpits", "Cockpits"), p.L("Analytics-Dashboards pro Projekt, Reports aus GA4, Google Ads und Instagram.", "Analytics dashboards per project, reports from GA4, Google Ads and Instagram.")),
        (p.L("Partner-Datenbanken", "Partner databases"), p.L("Kataloge von Guides, &Auml;rzt:innen und Instagram-Konten f&uuml;r Partnerschaften.", "Catalogues of guides, doctors and Instagram accounts for partnerships.")),
    ]
    auto_html = "".join(f'<div class="cell"><div class="n">A{i:02d}</div><h3>{h}</h3><p>{t}</p></div>' for i, (h, t) in enumerate(autos, 1))

    brands = [("MOTO-Z&Uuml;RICH", p.L("22&#39;117 Besucher:innen, 80 Aussteller", "22&#39;117 visitors, 80 exhibitors"), "moto-zuerich"),
              ("SVOI", p.L("17 kantonale Chats, 100+ Follower an einem Tag", "17 cantonal chats, 100+ followers in one day"), "svoi"),
              ("Frankenplatz", p.L("Forum 14.&ndash;15.11.2026, Lausanne", "Forum 14&ndash;15 Nov 2026, Lausanne"), "frankenplatz"),
              ("Cadre (ex&nbsp;Kunstwerkstube)", p.L("30+ Ausstellungen, 150&#39;000+ CHF Werke verkauft", "30+ exhibitions, CHF 150&#39;000+ in works sold"), "cadre")]
    brand_html = "".join(f'<div class="cell"><h3>{n}</h3><p>{t}</p><a class="more" href="{p.href("projekte", a)}">{p.L("Zum Fall", "See the case")} &rarr;</a></div>' for n, t, a in brands)

    stack = ["Claude (Anthropic)", "MCP", "n8n", "Supabase", "Vercel", "Google Workspace", "Resend", "SendPulse", "Metricool"]
    stack_html = "".join(f'<span{" class=\"claude\"" if i == 0 else ""}>{s}</span>' for i, s in enumerate(stack))

    body = hero(p, "Marketing Assistant &middot; Built with Claude",
                p.L('Ihr Marketing-Team mit KI &mdash; auf <span class="accent">Ihren Daten</span>, mit Ihrer Freigabe.',
                    'Your marketing team with AI &mdash; on <span class="accent">your data</span>, with your approval.'),
                p.L("F&uuml;r Schweizer KMU, Event-Veranstalter und Communities. Ein Claude-Kern, per MCP mit Ihren Markendaten verbunden, erstellt Content, f&uuml;hrt Kommunikation und recherchiert. Ver&ouml;ffentlicht wird erst, wenn ein Mensch freigibt. Kein Versprechen: Die Maschinen unten laufen bereits auf unseren eigenen Marken.",
                    "For Swiss SMEs, event organisers and communities. One Claude core, connected to your brand data via MCP, creates content, handles communication and does research. Nothing is published until a person approves it. Not a promise: the machines below already run on our own brands."),
                [("#demo", p.L("Demo anfragen", "Request a demo")), ("#maschinen", p.L("Was schon l&auml;uft", "What already runs"))])
    body += f'''<section class="dark" id="so-funktionierts">
  <div class="wrap">
    {sec_head(p.L('So funktioniert es', 'How it works'), p.L('Daten &rarr; Claude &rarr; Freigabe &rarr; Kanal.', 'Data &rarr; Claude &rarr; approval &rarr; channel.'),
              p.L('Ein Kern f&uuml;r alle Aufgaben, statt zehn einzelner Tools. Der Mensch bleibt im Prozess.', 'One core for every task instead of ten separate tools. A person stays in the loop.'))}
    <div class="flow reveal">{flow_html}</div>
  </div>
</section>
<section id="maschinen">
  <div class="wrap">
    {sec_head(p.L('Content-Maschinen', 'Content machines'), p.L('L&auml;uft bereits.', 'Already running.'),
              p.L('Jede Maschine arbeitet im Designsystem der jeweiligen Marke und liefert Entw&uuml;rfe zur Freigabe.', 'Every machine works inside the brand&#39;s own design system and delivers drafts for approval.'))}
    <div class="grid3 reveal">{mach_html}</div>
    <div class="sec-more"><a class="btn btn-line" href="{p.href('ein-klick')}">{p.L('Marketing-Maschine: Live-Demo und Film', 'Marketing machine: live demo and film')} &rarr;</a></div>
  </div>
</section>
<section id="automatisierung">
  <div class="wrap">
    {sec_head(p.L('Marketing-Automatisierung', 'Marketing automation'), p.L('Workflows mit Claude.', 'Workflows with Claude.'),
              p.L('Automatisierungen auf n8n mit Claude als Entscheidungsschicht: zuh&ouml;ren, sortieren, zusammenfassen, benachrichtigen.', 'Automations on n8n with Claude as the decision layer: listen, sort, summarise, notify.'))}
    <div class="grid2 reveal">{auto_html}</div>
  </div>
</section>
<section id="qualitaet">
  <div class="wrap">
    {sec_head(p.L('Designsysteme &amp; Qualit&auml;t', 'Design systems &amp; quality'), p.L('Markengerecht, gepr&uuml;ft, freigegeben.', 'On-brand, checked, approved.'))}
    <ul class="ticks reveal">
      <li>{p.L('Jede Marke hat ihr eigenes Designsystem. Daraus entstehen Builder f&uuml;r Posts, Mailings und Seiten.', 'Every brand has its own design system. Builders for posts, mailings and pages are generated from it.')}</li>
      <li>{p.L('Anti-Slop-Pr&uuml;fung und Typografie-Regeln: keine generischen Verl&auml;ufe, keine Platzhalter-Icons, keine h&auml;ngenden Pr&auml;positionen.', 'Typography rules and an anti-slop check: no generic gradients, no placeholder icons, no orphaned prepositions.')}</li>
      <li>{p.L('Faktenpr&uuml;fung mit Quellen und Pr&uuml;fdatum bei Artikeln.', 'Fact-checking with sources and a check date on articles.')}</li>
      <li>{p.L('Ver&ouml;ffentlicht wird nur, was ein Mensch freigegeben hat.', 'Only what a person has approved gets published.')}</li>
    </ul>
  </div>
</section>
<section id="marken">
  <div class="wrap">
    {sec_head(p.L('Im Einsatz', 'In production'), p.L('L&auml;uft auf unseren Marken.', 'Running on our own brands.'))}
    <div class="grid2 reveal">{brand_html}</div>
  </div>
</section>
<section id="stack">
  <div class="wrap">
    {sec_head('Stack', 'Built with Claude.', p.L('Claude von Anthropic ist der Kern. Drumherum Werkzeuge, die wir t&auml;glich betreiben.', 'Claude by Anthropic is the core. Around it: tools we operate every day.'))}
    <div class="stack reveal">{stack_html}</div>
  </div>
</section>
<section id="pakete">
  <div class="wrap">
    {sec_head(p.L('Pakete', 'Packages'), p.L('In drei Schritten startklar.', 'Up and running in three steps.'))}
    <div class="steps reveal">
      <div><div class="k">1</div><h4>Pilot</h4><p>{p.L('Interview, Markendaten und Designsystem erfassen, erste Maschine f&uuml;r einen Kanal.', 'Interview, capture brand data and design system, first machine for one channel.')}</p></div>
      <div><div class="k">2</div><h4>{p.L('Kan&auml;le anschliessen', 'Connect channels')}</h4><p>{p.L('Weitere Kan&auml;le, Automatisierungen und Freigabe-Workflow f&uuml;r Ihr Team.', 'More channels, automations and an approval workflow for your team.')}</p></div>
      <div><div class="k">3</div><h4>{p.L('Monatliche Betreuung', 'Monthly support')}</h4><p>{p.L('Pflege, neue Maschinen, Reports und Weiterentwicklung.', 'Maintenance, new machines, reports and ongoing development.')}</p></div>
    </div>
    <p class="note">{p.L('Preise auf Anfrage &mdash; einmalige Einrichtung plus monatliche Betreuung.', 'Prices on request &mdash; one-off setup plus monthly support.')}</p>
  </div>
</section>
<section id="demo">
  <div class="wrap">{form(p, kind="demo")}</div>
</section>'''
    sw = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "Creox Marketing Assistant",
          "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
          "description": "AI marketing assistant built on Claude (Anthropic): content, communication and research agents connected to brand data via MCP, with human approval before publishing.",
          "provider": {"@id": f"{SITE}/#org"}, "url": p.url(),
          "offers": {"@type": "Offer", "description": "Setup plus monthly support, prices on request"}}
    return page(p,
                p.L("Marketing Assistant — KI-Marketing auf Basis von Claude | Creox", "Marketing Assistant — AI marketing built on Claude | Creox"),
                p.L("Der Marketing Assistant von Creox: Claude (KI) per MCP mit Ihren Markendaten verbunden — Content, Kommunikation und Recherche mit menschlicher Freigabe. Im Einsatz bei MOTO-ZÜRICH, SVOI und Frankenplatz.",
                    "Creox Marketing Assistant: Claude (AI) connected to your brand data via MCP — content, communication and research with human approval. In production at MOTO-ZÜRICH, SVOI and Frankenplatz."),
                body, [sw])


def p_produkt(p):
    rows = ""
    for d in products_data(p):
        feat = " featured" if d["id"] == "marketing-assistant" else ""
        rows += f'''<article class="prod{feat} reveal" id="{d['id']}">
  <div class="prod-side"><span class="eyebrow">{p.L('Produkt', 'Product')}</span><h3>{d['name']}</h3><p>{d['short']}</p><span class="status">{d['status']}</span></div>
  <div class="prod-body">
    <dl>
      <dt>{p.L('Problem', 'Problem')}</dt><dd>{d['problem']}</dd>
      <dt>{p.L('Was es tut', 'What it does')}</dt><dd>{d['what']}</dd>
      <dt>{p.L('Wo es l&auml;uft', 'Where it runs')}</dt><dd>{d['where']}</dd>
      <dt>{p.L('Rolle von Claude', 'Role of Claude')}</dt><dd>{d['claude']}</dd>
      <dt>{p.L('Status', 'Status')}</dt><dd>{d['when']}</dd>
    </dl>
    <a class="btn btn-primary" href="{d['cta'][0]}">{d['cta'][1]} &rarr;</a>
  </div>
</article>'''
    body = hero(p, p.L("Produkte &middot; Creox", "Products &middot; Creox"),
                p.L('Produkte aus <span class="accent">unseren eigenen</span> Events.', 'Products from <span class="accent">our own</span> events.'),
                p.L("Jedes Produkt l&ouml;st ein Problem, das wir selbst hatten &mdash; und wird zuerst bei MOTO-Z&Uuml;RICH, SVOI, Frankenplatz oder in der Galerie eingesetzt. Claude ist in jedem Produkt der gemeinsame Kern.",
                    "Each product solves a problem we had ourselves &mdash; and goes live first at MOTO-Z&Uuml;RICH, SVOI, Frankenplatz or the gallery. Claude is the shared core of every product."),
                [(p.href("marketing-assistant"), "Marketing Assistant"), (p.href("kontakt"), p.L("Demo anfragen", "Request a demo"))])
    body += f'<section><div class="wrap">{rows}</div></section>'
    apps = [{"@context": "https://schema.org", "@type": "SoftwareApplication", "name": f"Creox {d['name']}",
             "applicationCategory": "BusinessApplication", "operatingSystem": "Web",
             "provider": {"@id": f"{SITE}/#org"}, "url": f"{p.url()}#{d['id']}"} for d in products_data(p)]
    return page(p, p.L("Produkte — Marketing Assistant, Antrix, MotoGen, Audio Guide | Creox", "Products — Marketing Assistant, Antrix, MotoGen, Audio Guide | Creox"),
                p.L("Produkte von Creox: Marketing Assistant (KI auf Basis von Claude), Antrix Ticketing, MotoGen Motorrad-Plattform und Audio Guide — entstanden und erprobt an eigenen Events.",
                    "Creox products: Marketing Assistant (AI built on Claude), Antrix ticketing, the MotoGen motorcycle platform and Audio Guide — born and proven at our own events."),
                body, apps)


def p_projekte(p):
    body = hero(p, p.L("Projekte &middot; Creox", "Work &middot; Creox"),
                p.L('Beweise <span class="accent">statt</span> Versprechen.', 'Proof, <span class="accent">not</span> promises.'),
                p.L("Vier eigene Marken, auf denen wir Events machen und unsere Produkte zuerst einsetzen. Zu jedem Fall: was wir gemacht haben, welche Creox-Produkte laufen und welche Zahlen dahinterstehen.",
                    "Four of our own brands, where we run events and put our products to work first. For each: what we did, which Creox products run there and the numbers behind it."),
                [(p.href("kontakt"), p.L("Event anfragen", "Brief us on your event"))])
    body += f'<section><div class="wrap">{cases(p)}</div></section>'
    return page(p, p.L("Projekte — MOTO-ZÜRICH, SVOI, Frankenplatz, Cadre | Creox", "Work — MOTO-ZÜRICH, SVOI, Frankenplatz, Cadre | Creox"),
                p.L("Eigene Events und Marken von Creox: MOTO-ZÜRICH (22'117 Besucher:innen), SVOI, Frankenplatz und die Galerie Cadre (ex Kunstwerkstube) — mit den Creox-Produkten, die dort laufen.",
                    "Creox's own events and brands: MOTO-ZÜRICH (22,117 visitors), SVOI, Frankenplatz and the gallery Cadre (formerly Kunstwerkstube) — with the Creox products running there."),
                body)


def p_team(p):
    members = [
        ("Yves Vollenweider", "yves", p.L("Gesch&auml;ftsf&uuml;hrer &amp; Mitgr&uuml;nder", "Managing director &amp; co-founder"),
         p.L("Als Gesch&auml;ftsf&uuml;hrer der Creox GmbH bringt Yves &uuml;ber 30 Jahre aus Motorrad-, <span class='nobr'>Messe- und Eventwelt</span> zusammen &ndash; von 12 Jahren Director Event-Management an der Messe Z&uuml;rich &uuml;ber die Leitung der SWISS-MOTO bis zum Marketingleiter BMW Motorrad Schweiz. Sein Anspruch: Projekte, die funktionieren, nicht nur gut aussehen.",
             "As managing director of Creox GmbH, Yves brings together 30+ years across the motorcycle, trade-fair and event world &ndash; from 12 years as Director Event Management at Messe Z&uuml;rich and running the SWISS-MOTO to marketing lead at BMW Motorrad Switzerland. His standard: projects that work, not just look good."),
         "yves@creox.ch"),
        ("Kseniia Chudina", "kseniia", p.L("Mitgr&uuml;nderin &middot; Head of Marketing &amp; ICT", "Co-founder &middot; Head of Marketing &amp; ICT"),
         p.L("Als Mitgr&uuml;nderin und Teilhaberin der Creox GmbH ist Kseniia unser Kopf f&uuml;r neue Technologien. Spezialisiert auf <span class='nobr'>CRM- und Web-L&ouml;sungen</span>, entwickelt sie mit ihrem Team digitale Plattformen und setzt bewusst neue Akzente. KI ist f&uuml;r sie kein Schlagwort, sondern Werkzeug &ndash; gezielt eingesetzt, macht sie Projekte schneller, smarter und wirkungsvoller.",
             "As co-founder and partner of Creox GmbH, Kseniia is our mind for new technologies. Specialised in CRM and web solutions, she builds digital platforms with her team and sets bold new accents. For her, AI isn&#39;t a buzzword but a tool &ndash; used deliberately, it makes projects faster, smarter and more effective."),
         ""),
        ("Jasmine Vollenweider", "jasmine", p.L("Event-Management &amp; Office", "Event management &amp; office"),
         p.L("Jasmine kommt aus der Hotellerie und ist die J&uuml;ngste im Team &ndash; sie bringt frischen Wind und neue Ideen. Mit einer erfolgreich abgeschlossenen Zusatzausbildung als Event-Managerin und ihrer ausgepr&auml;gt dienstleistungsorientierten Arbeitsweise sorgt sie daf&uuml;r, dass im Hintergrund alles l&auml;uft.",
             "Jasmine comes from hospitality and is the youngest on the team &ndash; bringing fresh energy and new ideas. With a completed additional qualification as an event manager and her strongly service-oriented approach, she makes sure everything runs smoothly behind the scenes."),
         ""),
    ]
    cells = ""
    for n, img, r, t, mail in members:
        cells += (f'<article class="cell member"><img class="m-img" src="{p.asset("img/team-" + img + ".jpg")}" alt="{n}" width="600" height="780" loading="lazy">'
                  f'<h3>{n}</h3><div class="mrole">{amp(r)}</div><p>{t}</p>'
                  + (f'<a class="more" href="mailto:{mail}">{mail}</a>' if mail else '') + '</article>')
    cells += f'<div class="cell member plus"><h3>{p.L("+&nbsp;5 Spezialist:innen", "+&nbsp;5 specialists")}</h3><p>{p.L("in Marketing, Content, Design und Entwicklung. Insgesamt acht Personen.", "in marketing, content, design and engineering. Eight people in total.")}</p></div>'
    body = hero(p, p.L("Das Team", "The people"),
                p.L('Substanz <span class="accent">statt</span> Show.', 'Substance, <span class="accent">not</span> show.'),
                p.L("Ein kompaktes Kernteam, das Projekte wirklich umsetzt &ndash; mit Erfahrung aus Events, Marketing und Technologie und einem Netzwerk aus Spezialist:innen.",
                    "A compact core team that actually delivers projects &ndash; with experience across events, marketing and technology, and a network of specialists."), [])
    body += f'<section><div class="wrap"><div class="grid2 team reveal">{cells}</div></div></section>'
    return page(p, p.L("Team — Creox GmbH", "Team — Creox GmbH"),
                p.L("Das Team von Creox GmbH: Yves Vollenweider (Geschäftsführer), Kseniia Chudina (Head of Marketing & ICT), Jasmine Vollenweider und Spezialist:innen für Marketing, Content, Design und Entwicklung.",
                    "The Creox GmbH team: Yves Vollenweider (managing director), Kseniia Chudina (Head of Marketing & ICT), Jasmine Vollenweider and specialists in marketing, content, design and engineering."),
                body)


def form(p, kind="event"):
    if kind == "demo":
        types = [p.L("Social Media", "Social media"), p.L("Newsletter", "Newsletters"), p.L("Website &amp; Artikel", "Website &amp; articles"),
                 p.L("Community &amp; Messenger", "Community &amp; messengers"), p.L("Reports", "Reports"), p.L("Anderes", "Other")]
        head = (p.L("Demo", "Demo"), p.L("Demo anfragen.", "Request a demo."),
                p.L("Erz&auml;hlen Sie uns kurz, welche Kan&auml;le Sie haben und was Sie automatisieren m&ouml;chten. Wir zeigen Ihnen die passenden Maschinen an einem echten Beispiel.",
                    "Tell us which channels you run and what you want to automate. We&#39;ll show you the matching machines on a real example."))
        type_label = p.L("Was m&ouml;chten Sie automatisieren?", "What do you want to automate?")
        subject = "demo"
    else:
        types = ["Event", p.L("Digitales / Plattform", "Digital / platform"), "Marketing / PR", "Ticketing",
                 p.L("Design / Marke", "Design / brand"), p.L("Produkt-Demo", "Product demo"), p.L("Erst mal eine Idee", "Just an idea"), p.L("Anderes", "Other")]
        head = (p.L("Kontakt", "Contact"), p.L("Erz&auml;hlen Sie uns, woran Sie denken.", "Tell us what you have in mind."),
                p.L("Kein fertiges Briefing n&ouml;tig. Ein paar Zeilen gen&uuml;gen &ndash; wir melden uns und schauen gemeinsam, was m&ouml;glich ist.",
                    "No finished brief needed. A few lines are enough &ndash; we&#39;ll get back to you and figure out together what&#39;s possible."))
        type_label = p.L("Worum geht&#39;s? (optional)", "What&#39;s it about? (optional)")
        subject = "brief"
    chips = "".join(f'<label><input type="checkbox" name="topic" value="{re.sub("&amp;", "&", t)}"><span>{t}</span></label>' for t in types)
    site_field = (f'<div class="field"><label for="f_site_{kind}">{p.L("Ihre Website", "Your website")}</label><input type="url" id="f_site_{kind}" name="site" placeholder="https://"></div>'
                  if kind == "demo" else "")
    dials = ["+41", "+49", "+43", "+33", "+39", "+423", "+44", "+31", "+32", "+34", "+351", "+352", "+45", "+46", "+47", "+358", "+48", "+420", "+30", "+353", "+1", "+7", "+380", "+90"]
    dial_opts = "".join(f'<option value="{d}"{" selected" if d == "+41" else ""}>{d}</option>' for d in dials) + f'<option value="">{p.L("Andere", "Other")}</option>'
    return f'''<div class="contact-grid reveal">
  <div class="contact-left">
    <span class="eyebrow">{head[0]}</span>
    <h2>{head[1]}</h2>
    <p>{head[2]}</p>
    <dl class="facts">
      <dt>E-Mail</dt><dd><a href="mailto:main@creox.ch">main@creox.ch</a></dd>
      <dt>{p.L('Adresse', 'Address')}</dt><dd>Creox GmbH<br>Grabenstrasse 15b<br>6340 Baar (ZG)</dd>
    </dl>
  </div>
  <div>
    <form class="leadform" novalidate data-key="{subject}" data-lang="{p.lang}">
      <div class="frow">
        <div class="field"><label for="f_name_{kind}">Name <span class="req">*</span></label><input type="text" id="f_name_{kind}" name="name" autocomplete="name" required></div>
        <div class="field"><label for="f_co_{kind}">{p.L('Firma', 'Company')}</label><input type="text" id="f_co_{kind}" name="company" autocomplete="organization"></div>
      </div>
      <div class="frow">
        <div class="field"><label for="f_mail_{kind}">E-Mail <span class="req">*</span></label><input type="email" id="f_mail_{kind}" name="email" autocomplete="email" required></div>
        <div class="field"><label for="f_phone_{kind}">{p.L('Telefon', 'Phone')} <span class="req">*</span></label><div class="phone-row"><select id="f_dial_{kind}" name="dial" aria-label="{p.L('L&auml;ndervorwahl', 'Country code')}">{dial_opts}</select><input type="tel" id="f_phone_{kind}" name="phone" inputmode="tel" autocomplete="tel-national" placeholder="79 123 45 67" required></div></div>
      </div>
      {site_field}
      <div class="field" role="group" aria-labelledby="f_types_{kind}"><span class="glabel" id="f_types_{kind}">{type_label}</span><div class="types">{chips}</div></div>
      <div class="field"><label for="f_msg_{kind}">{p.L('Ihre Nachricht', 'Your message')}</label><textarea id="f_msg_{kind}" name="message"></textarea></div>
      <div class="field"><label class="consent"><input type="checkbox" name="consent" required><span>{p.L('Ich habe die <a href="' + p.href('datenschutz') + '">Datenschutzerkl&auml;rung</a> gelesen und bin einverstanden, dass meine Angaben zur Beantwortung der Anfrage bearbeitet werden.', 'I have read the <a href="' + p.href('datenschutz') + '">privacy policy</a> and agree that my details are processed to answer this enquiry.')} <span class="req">*</span></span></label></div>
      <div class="hp" aria-hidden="true"><label for="f_hp_{kind}">Website</label><input type="text" id="f_hp_{kind}" name="hp" tabindex="-1" autocomplete="off"></div>
      <button type="submit" class="btn btn-primary">{p.L('Kontakt aufnehmen', 'Send')}</button>
      <p class="form-note" role="status" aria-live="polite">{p.L('Name, E-Mail und Telefon &ndash; wir antworten innerhalb einer Woche.', 'Name, email and phone &ndash; we&#39;ll reply within a week.')}</p>
      <p class="form-ok" hidden>{p.L('Danke &ndash; Ihre Nachricht ist unterwegs. Wir melden uns in K&uuml;rze.', 'Thanks &ndash; your message is on its way. We&#39;ll be in touch shortly.')}</p>
    </form>
  </div>
</div>'''


def p_kontakt(p):
    body = hero(p, p.L("Kontakt", "Contact"), p.L('Lassen Sie uns <span class="accent">sprechen.</span>', 'Let&#39;s <span class="accent">talk.</span>'),
                p.L("F&uuml;r Events, Produkt-Demos, Partnerschaften und Presse.", "For events, product demos, partnerships and press."), [])
    body += f'<section><div class="wrap">{form(p)}</div></section>'
    return page(p, p.L("Kontakt — Creox GmbH, Baar", "Contact — Creox GmbH, Baar"),
                p.L("Kontakt zu Creox GmbH, Grabenstrasse 15b, 6340 Baar: Events, Produkt-Demos (Marketing Assistant, Antrix), Partnerschaften und Presse.",
                    "Contact Creox GmbH, Grabenstrasse 15b, 6340 Baar, Switzerland: events, product demos (Marketing Assistant, Antrix), partnerships and press."), body)


def legal_page(p, slug, title_de, title_en, de, en, desc_de, desc_en):
    body = hero(p, "Creox GmbH", p.L(title_de, title_en), "", [])
    body += f'<section><div class="wrap"><div class="legal">{p.L(de, en)}</div></div></section>'
    return page(p, f'{p.L(title_de, title_en)} — Creox GmbH', p.L(desc_de, desc_en), body)


def p_impressum(p):
    de = f'''<h2>Angaben zum Unternehmen</h2>
<p><b>Creox GmbH</b><br>Grabenstrasse 15b<br>6340 Baar (ZG)<br>Schweiz</p>
<p>E-Mail: <a href="mailto:main@creox.ch">main@creox.ch</a><br>Website: creox.ch</p>
<h2>Handelsregister</h2>
<p>Eingetragen im Handelsregister des Kantons Zug, Sitz Baar<br>UID: CHE-169.690.018<br>MWST-Nr.: CHE-169.690.018 MWST</p>
<p>Vormals Vollenweider &amp; Schweizer GmbH, Sitz Baden. Seit Juni 2026 Creox GmbH mit Sitz in Baar (Eintrag vom 30.06.2026, publiziert im SHAB am 03.07.2026). Die Firma ist dieselbe juristische Person, die UID ist unver&auml;ndert.</p>
<h2>Vertretung</h2>
<p>Yves Vollenweider, Gesch&auml;ftsf&uuml;hrer (Einzelunterschrift)</p>
<h2>Haftungsausschluss</h2>
<p>Die Inhalte dieser Website wurden mit Sorgfalt erstellt. Es wird keine Gew&auml;hr f&uuml;r Richtigkeit, Vollst&auml;ndigkeit und Aktualit&auml;t &uuml;bernommen. F&uuml;r Inhalte verlinkter Websites sind ausschliesslich deren Betreiber verantwortlich.</p>'''
    en = f'''<h2>Company details</h2>
<p><b>Creox GmbH</b><br>Grabenstrasse 15b<br>6340 Baar (ZG)<br>Switzerland</p>
<p>Email: <a href="mailto:main@creox.ch">main@creox.ch</a><br>Website: creox.ch</p>
<h2>Commercial register</h2>
<p>Registered in the commercial register of the Canton of Zug, seat in Baar<br>UID: CHE-169.690.018<br>VAT no.: CHE-169.690.018 MWST</p>
<p>Formerly Vollenweider &amp; Schweizer GmbH, seat in Baden. Renamed Creox GmbH with its seat in Baar in June 2026 (entry of 30.06.2026, published in the Swiss Official Gazette of Commerce on 03.07.2026). It is the same legal entity; the UID is unchanged.</p>
<h2>Authorised representative</h2>
<p>Yves Vollenweider, managing director (sole signature)</p>
<h2>Disclaimer</h2>
<p>This website has been compiled with care. No warranty is given for accuracy, completeness or timeliness. Operators of linked websites are solely responsible for their content.</p>'''
    return legal_page(p, "impressum", "Impressum", "Legal notice", de, en,
                      "Impressum der Creox GmbH, Grabenstrasse 15b, 6340 Baar, UID CHE-169.690.018. Vormals Vollenweider & Schweizer GmbH.",
                      "Legal notice of Creox GmbH, Grabenstrasse 15b, 6340 Baar, Switzerland, UID CHE-169.690.018. Formerly Vollenweider & Schweizer GmbH.")


def p_datenschutz(p):
    de = '''<h2>Verantwortliche Stelle</h2>
<p>Creox GmbH, Grabenstrasse 15b, 6340 Baar (ZG), Schweiz &middot; <a href="mailto:main@creox.ch">main@creox.ch</a></p>
<p>Die Creox GmbH bearbeitet Personendaten im Einklang mit dem Schweizer DSG und, soweit anwendbar, der EU-DSGVO.</p>
<h2>Formulare</h2>
<p>Bei Nutzung der Formulare bearbeiten wir Name, Firma, E-Mail, Telefon, gew&auml;hlte Themen, gegebenenfalls Ihre Website und Ihre Nachricht ausschliesslich zur Beantwortung Ihrer Anfrage. Sie haben Recht auf Auskunft, Berichtigung und L&ouml;schung Ihrer Daten.</p>
<h2>Reichweitenmessung</h2>
<p>Wir verwenden Vercel Web Analytics (Vercel Inc., USA). Es werden keine Cookies gesetzt und keine Kennungen im Browser gespeichert; Besucher werden &uuml;ber einen aus der Anfrage berechneten Hashwert unterschieden, der nach 24 Stunden verworfen wird. Erfasst werden Zeitpunkt, aufgerufene Seite, verweisende Seite, ungef&auml;hre Herkunft (Land, Region, Ort), Betriebssystem, Browser und Ger&auml;tetyp. Die Auswertung erfolgt aggregiert; eine Zuordnung zu einer Person oder IP-Adresse erfolgt nicht.</p>
<h2>Auftragsverarbeiter</h2>
<p>Diese Website wird bei Vercel (USA) gehostet. Formulardaten werden bei Supabase (Rechenzentrum in der EU) gespeichert; E-Mail-Benachrichtigungen versenden wir &uuml;ber Resend (USA). Schriften werden von Google Fonts (Google, USA) geladen; dabei wird Ihre IP-Adresse an Google &uuml;bermittelt. Bei &Uuml;bermittlungen in die USA st&uuml;tzen wir uns auf geeignete Garantien (Standardvertragsklauseln bzw. Data Privacy Framework).</p>'''
    en = '''<h2>Controller</h2>
<p>Creox GmbH, Grabenstrasse 15b, 6340 Baar (ZG), Switzerland &middot; <a href="mailto:main@creox.ch">main@creox.ch</a></p>
<p>Creox GmbH processes personal data in accordance with the Swiss FADP and, where applicable, the EU GDPR.</p>
<h2>Contact and demo forms</h2>
<p>When you use the forms we process name, company, email, phone, selected topics, your website if given, and your message solely to answer your enquiry. You have the right to access, correct and delete your data.</p>
<h2>Analytics</h2>
<p>We use Vercel Web Analytics (Vercel Inc., USA). No cookies are set and no identifiers are stored in your browser; visitors are distinguished by a hash computed from the incoming request, which is discarded after 24 hours. We record the time of the visit, the page viewed, the referring page, approximate origin (country, region, city), operating system, browser and device type. Analysis is aggregated only; no data is linked to a person or an IP address.</p>
<h2>Processors</h2>
<p>This website is hosted by Vercel (USA). Form data is stored with Supabase (data centre in the EU); e-mail notifications are sent via Resend (USA). Fonts are loaded from Google Fonts (Google, USA), which transmits your IP address to Google. For transfers to the USA we rely on appropriate safeguards (Standard Contractual Clauses or the Data Privacy Framework).</p>'''
    return legal_page(p, "datenschutz", "Datenschutz", "Privacy policy", de, en,
                      "Datenschutzerklärung der Creox GmbH, Baar: Bearbeitung von Personendaten nach DSG und DSGVO.",
                      "Privacy policy of Creox GmbH, Baar: processing of personal data under the Swiss FADP and the GDPR.")


def p_agb(p):
    de = '''<h2>Geltungsbereich</h2>
<p>Diese Bedingungen gelten f&uuml;r alle Leistungen der Creox GmbH, Grabenstrasse 15b, 6340 Baar, sofern nicht schriftlich anders vereinbart.</p>
<h2>Angebot und Leistungsumfang</h2>
<p>Der Leistungsumfang wird im jeweiligen Angebot definiert. Angebote sind bis zur schriftlichen Best&auml;tigung unverbindlich.</p>
<h2>Preise und Zahlung</h2>
<p>Preise in CHF, exkl. MWST. Rechnungen zahlbar innert 30 Tagen.</p>
<h2>Recht und Gerichtsstand</h2>
<p>Es gilt Schweizer Recht. Gerichtsstand ist Baar (Kanton Zug).</p>
<p>F&uuml;r Tickets eigener Veranstaltungen gelten die Bedingungen auf der Website der jeweiligen Veranstaltung.</p>'''
    en = '''<h2>Scope</h2>
<p>These terms apply to all services of Creox GmbH, Grabenstrasse 15b, 6340 Baar, unless otherwise agreed in writing.</p>
<h2>Offers and scope of services</h2>
<p>The scope of services is defined in the individual offer. Offers are non-binding until confirmed in writing.</p>
<h2>Prices and payment</h2>
<p>Prices in CHF, excl. VAT. Invoices payable within 30 days.</p>
<h2>Law and jurisdiction</h2>
<p>Swiss law applies. Place of jurisdiction is Baar (Canton of Zug).</p>
<p>Tickets for our own events are subject to the terms on the respective event website.</p>'''
    return legal_page(p, "agb", "AGB", "Terms &amp; conditions", de, en,
                      "Allgemeine Geschäftsbedingungen der Creox GmbH, Baar.", "General terms and conditions of Creox GmbH, Baar.")


import page_einklick
BUILDERS = {"ein-klick": lambda p: page_einklick.build(p, hero, sec_head, page), "index": p_index, "marketing-assistant": p_ma, "produkt": p_produkt, "projekte": p_projekte,
            "team": p_team, "kontakt": p_kontakt, "impressum": p_impressum, "datenschutz": p_datenschutz, "agb": p_agb}


import html as _h
_KEEP={"&amp;","&lt;","&gt;","&quot;","&nbsp;"}
def decode(t):
    return re.sub(r"&(?:[a-zA-Z]+|#\d+);", lambda m: m.group(0) if m.group(0) in _KEEP else _h.unescape(m.group(0)), t)


def main():
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "en").mkdir(parents=True)
    for lang in ("de", "en"):
        for slug in PAGES:
            p = Page(lang, slug)
            name = "index.html" if slug == "index" else f"{slug}.html"
            out = DIST / ("en" if lang == "en" else "") / name
            out.write_text(decode(BUILDERS[slug](p)), encoding="utf-8")
    shutil.copy(ROOT / "style.css", DIST / "style.css")
    shutil.copy(ROOT / "site.js", DIST / "site.js")
    shutil.copy(ROOT / "demo.js", DIST / "demo.js")
    shutil.copy(ROOT / "typo.js", DIST / "typo.js")
    shutil.copytree(ROOT / "img", DIST / "img")
    shutil.copytree(ROOT / "media", DIST / "media")
    for f in ("og.png", "favicon.svg"):
        shutil.copy(ROOT / "static" / f, DIST / f)
    mg = (ROOT / "static" / "motogen.html").read_text(encoding="utf-8")
    for a, b in (('href="/#services"', 'href="/"'), ('href="/#work"', 'href="/projekte"'), ('href="/#team"', 'href="/team"'),
                 ('href="/#contact"', 'href="/kontakt"'), ('https://creox.ch/produkt"', 'https://creox.ch/motogen"')):
        mg = mg.replace(a, b)
    # pre-existing overflow of the page heading on 320–360 px phones
    mg = mg.replace(".hero h1{font-family:var(--head);font-weight:700;font-size:clamp(42px,8vw,92px);", ".hero h1{font-family:var(--head);font-weight:700;font-size:clamp(34px,8vw,92px);")
    (DIST / "motogen.html").write_text(mg, encoding="utf-8")
    # sitemap with hreflang pairs
    urls = ""
    for slug in PAGES:
        de, en = Page("de", slug).url(), Page("en", slug).url()
        for loc in (de, en):
            urls += (f'  <url><loc>{loc}</loc><lastmod>2026-10-11</lastmod>'
                     f'<xhtml:link rel="alternate" hreflang="de" href="{de}"/>'
                     f'<xhtml:link rel="alternate" hreflang="en" href="{en}"/></url>\n')
    urls += f'  <url><loc>{SITE}/motogen</loc><lastmod>2026-10-15</lastmod></url>\n'
    (DIST / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" '
        'xmlns:xhtml="http://www.w3.org/1999/xhtml">\n' + urls + '</urlset>\n', encoding="utf-8")
    (DIST / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (DIST / "vercel.json").write_text(json.dumps({"cleanUrls": True, "trailingSlash": False, "redirects": [
        {"source": "/produkte", "destination": "/produkt", "permanent": True},
        {"source": "/en/produkte", "destination": "/en/produkt", "permanent": True}]}, indent=2), encoding="utf-8")
    print("built", sum(1 for _ in DIST.rglob("*.html")), "pages")


if __name__ == "__main__":
    main()
