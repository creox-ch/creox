"""/ein-klick — live demo: one piece of content goes to every channel (web, social, newsletter, print, letters)."""


def build(p, hero, sec_head, page):
    L = p.L
    img = lambda n: p.asset(f"img/demo/{n}.jpg")

    presets = [
        ("event", L("Foto vom Event", "Event photo"), "foto-fmx",
         "Vorderrad hoch. Saison los.",
         L("MOTO-ZÜRICH 2027 · 19.–21. Februar · StageOne & Halle 550", "MOTO-ZÜRICH 2027 · 19–21 February · StageOne & Halle 550")),
        ("news", "News", "plakat-tacho",
         "Vollgas im Februar.",
         L("MOTO-ZÜRICH 2027 · Drei Tage Saisonstart in Zürich-Oerlikon", "MOTO-ZÜRICH 2027 · Three days of season start in Zurich-Oerlikon")),
        ("ankuendigung", L("Ankündigung", "Announcement"), "plakat-loewe",
         "Grrr-üezi.",
         L("MOTO-ZÜRICH 2027 · 19.–21. Februar · Tickets auf motozuerich.ch", "MOTO-ZÜRICH 2027 · 19–21 February · Tickets at motozuerich.ch")),
    ]
    chips = "".join(
        f'<label><input type="radio" name="ek-preset" value="{k}" data-photo="{img(ph)}" data-title="{t}" data-sub="{s}"{" checked" if i == 0 else ""}><span>{lab}</span></label>'
        for i, (k, lab, ph, t, s) in enumerate(presets))
    thumbs = "".join(
        f'<button type="button" class="ek-thumb{" on" if i == 0 else ""}" data-photo="{img(n)}" aria-label="{a}"><img src="{img(n)}" alt="" width="60" height="80"></button>'
        for i, (n, a) in enumerate([("foto-fmx", L("Foto FMX-Show", "FMX show photo")), ("plakat-tacho", "Key Visual Tacho"),
                                    ("plakat-loewe", L("Key Visual Löwe", "Key visual lion"))]))

    steps = [
        ("ds", L("Designsystem der Marke geladen", "Brand design system loaded")),
        ("fmt", L("Formate: 4:5 · 9:16 · 1.91:1 · A2 · A5 · C5", "Formats: 4:5 · 9:16 · 1.91:1 · A2 · A5 · C5")),
        ("txt", L("Text je Kanal von Claude", "Copy per channel by Claude")),
        ("typo", L("Typografie und Fakten geprüft", "Typography and facts checked")),
        ("ok", L("Freigabe durch einen Menschen", "Approved by a person")),
    ]
    steps_html = "".join(f'<li data-step="{k}"><span class="ek-dot" aria-hidden="true"></span>{t}</li>' for k, t in steps)

    d_title, d_sub = presets[0][3], presets[0][4]
    T = f'<span data-f="title">{d_title}</span>'
    S = f'<span data-f="sub">{d_sub}</span>'
    PH = '<div class="mk-ph" aria-hidden="true"></div>'
    channels = [
        ("web", "Website", L("Beitrag online", "Post online"),
         f'<div class="mk mk-web"><div class="mk-bar"><i></i><i></i><i></i><b>motozuerich.ch/news</b></div>{PH}<div class="mk-pad"><small>News</small><strong>{T}</strong><p>{S}</p></div></div>'),
        ("ig", "Instagram · Post", L("veröffentlicht", "published"),
         f'<div class="mk mk-ig"><div class="mk-igwrap">{PH}<div class="mk-igband"><strong>{T}</strong></div></div><p class="mk-cap" data-f="cap-ig">{d_title} #motozuerich</p></div>'),
        ("story", "Instagram · Story", L("veröffentlicht", "published"),
         f'<div class="mk mk-story">{PH}<div class="mk-st"><span class="mk-logo">MOTO ZÜRICH</span><strong>{T}</strong><em>19.–21.</em><span class="mk-link">Tickets ↗</span></div></div>'),
        ("fb", "Facebook", L("veröffentlicht", "published"),
         f'<div class="mk mk-feed"><div class="mk-head"><span class="mk-av">MZ</span><b>MOTO-ZÜRICH</b></div><p data-f="cap-fb">{d_title} {d_sub}</p><div class="mk-wide">{PH}</div></div>'),
        ("li", "LinkedIn", L("veröffentlicht", "published"),
         f'<div class="mk mk-feed"><div class="mk-head"><span class="mk-av">MZ</span><b>MOTO-ZÜRICH · Creox GmbH</b></div><p data-f="cap-li">Save the Date: {d_sub}</p><div class="mk-wide">{PH}</div></div>'),
        ("tg", "Telegram", L("im Kanal", "in channel"),
         f'<div class="mk mk-tg"><div class="mk-bubble"><div class="mk-wide">{PH}</div><p data-f="cap-tg">{d_title} {d_sub}</p><span class="mk-time">12:00 ✓✓</span></div></div>'),
        ("mail", "Newsletter", L("an Abonnent:innen", "sent to subscribers"),
         f'<div class="mk mk-mail"><div class="mk-mhead"><b>{L("Betreff", "Subject")}:</b> {T}</div><div class="mk-mbody">{PH}<strong>{T}</strong><p>{S}</p><span class="mk-btn">{L("Tickets sichern", "Get tickets")}</span></div></div>'),
        ("poster", L("Plakat A2", "Poster A2"), L("Druck-PDF bereit", "Print PDF ready"),
         f'<div class="mk mk-poster">{PH}<span class="mk-logo">MOTO ZÜRICH</span><strong>{T}</strong><em>19.–21. FEBRUAR 2027</em><div class="mk-foot">STAGEONE · HALLE 550 <i>TICKETS →</i></div></div>'),
        ("flyer", L("Flyer A5", "Flyer A5"), L("Druck-PDF bereit", "Print PDF ready"),
         f'<div class="mk mk-flyer"><div class="mk-fdate"><b>19</b><b>20</b><b>21</b><small>FEBRUAR 2027</small></div><div class="mk-fimg">{PH}<strong>{T}</strong></div></div>'),
        ("letter", L("Brief & Kuvert C5", "Letter & C5 envelope"), L("Serienbrief bereit", "Mail merge ready"),
         f'<div class="mk mk-letter"><div class="mk-paper"><span class="mk-logo">MOTO ZÜRICH</span><small>Muster Motos AG · Industriestrasse 12 · 8050 Zürich</small><p>{L("Sehr geehrte Frau Muster", "Dear Ms Muster")},</p><strong>{T}</strong><p>{S}</p><i class="mk-lines"></i></div><div class="mk-env"><span>19.–21.</span><b>Muster Motos AG</b></div></div>'),
    ]
    cards = "".join(
        f'<article class="ek-card" data-ch="{k}"><header><b>{name}</b><span class="ek-st" data-done="{done}">{L("wartet", "waiting")}</span></header>{mock}</article>'
        for k, name, done, mock in channels)

    print_items = [("plakat-loewe", "«Grrr-üezi.»"), ("plakat-tacho", "«Vollgas im Februar.»"), ("plakat-datum", "«19.–21. Februar 2027»"),
                   ("flyer-wheelie", "«Vorderrad hoch. Saison los.»"), ("flyer-info", "«Drei Tage Saisonstart»")]
    print_html = "".join(f'<figure><img src="{img(n)}" alt="{c}" loading="lazy"><figcaption>{c}</figcaption></figure>' for n, c in print_items)
    print_html += f'<figure class="wide"><img src="{img("kuvert")}" alt="{L("Kuvert C5", "C5 envelope")}" loading="lazy"><figcaption>{L("Kuvert C5 mit Adressfenster", "C5 envelope with address window")}</figcaption></figure>'

    body = hero(p, L("Marketing-Maschine &middot; Live-Demo", "Marketing machine &middot; Live demo"),
                L('Ein Inhalt. <span class="accent">Jeder Kanal.</span>', 'One piece of content. <span class="accent">Every channel.</span>'),
                L("Ein Foto vom Event, eine News, eine Ankündigung: Sie laden es einmal hoch. Das Designsystem der Marke baut daraus den Beitrag auf der Website, Posts für alle Social-Media-Kanäle, den Newsletter, Plakat, Flyer und Brief. Ein Mensch gibt frei, dann geht alles gleichzeitig raus. Probieren Sie es unten aus.",
                  "An event photo, a news item, an announcement: you upload it once. The brand&#39;s design system turns it into the website post, posts for every social channel, the newsletter, poster, flyer and letter. A person approves, then everything goes out at once. Try it below."),
                [("#demo", L("Demo starten", "Start the demo")), (p.href("marketing-assistant"), "Marketing Assistant")])

    body += f'''<section id="film" class="ek-film">
  <div class="wrap">
    {sec_head(L("Der ganze Weg in 20 Sekunden", "The whole path in 20 seconds"), L("Social, Website, Newsletter, Brief, Plakat.", "Social, website, newsletter, letter, poster."),
              L("Ein Foto geht ins System. Erst Social Media, dann die Website, der Newsletter, der Brief per Post und das Plakat an der Wand. Mit Ton.",
                "One photo goes into the system. First social media, then the website, the newsletter, the letter by post and the poster on the wall. With sound."))}
    <div class="ek-video reveal"><video controls preload="metadata" playsinline poster="{p.asset("media/ein-klick.jpg")}" width="1080" height="1350">
      <source src="{p.asset("media/ein-klick.mp4")}" type="video/mp4"></video></div>
  </div>
</section>
<section id="demo" class="ek-sec">
  <div class="wrap">
    {sec_head(L("Ausprobieren", "Try it"), L("Ein Klick. Elf Ausgaben.", "One click. Eleven outputs."),
              L("Wählen Sie einen Inhalt oder laden Sie ein eigenes Foto hoch, ändern Sie den Titel und klicken Sie auf «Freigeben». Beispiel: MOTO-ZÜRICH 2027.",
                "Pick a piece of content or upload your own photo, change the title and click «Approve». Example: MOTO-ZÜRICH 2027."))}
    <div class="ek reveal" data-lang="{p.lang}" style="--photo:url('{img("foto-fmx")}')">
      <div class="ek-in">
        <div class="ek-k">1 &middot; {L("Inhalt", "Content")}</div>
        <div class="types ek-presets" role="radiogroup" aria-label="{L("Art des Inhalts", "Type of content")}">{chips}</div>
        <div class="ek-thumbs">{thumbs}<label class="ek-thumb ek-up"><input type="file" id="ek-file" accept="image/*"><span>+ {L("Eigenes Foto", "Your photo")}</span></label></div>
        <label for="ek-title">{L("Titel", "Title")}</label><input id="ek-title" type="text" maxlength="60" value="{d_title}">
        <label for="ek-sub">{L("Untertitel", "Subtitle")}</label><input id="ek-sub" type="text" maxlength="90" value="{d_sub}">
        <button type="button" class="btn btn-primary ek-go" id="ek-go">{L("Freigeben &amp; veröffentlichen", "Approve &amp; publish")}</button>
        <button type="button" class="ek-reset" id="ek-reset" hidden>{L("Nochmal", "Run again")}</button>
      </div>
      <div class="ek-sys">
        <div class="ek-k">2 &middot; System</div>
        <div class="ek-core"><b>CREOX.</b><span>Claude + MCP</span></div>
        <ul class="ek-steps">{steps_html}</ul>
        <div class="ek-count"><b id="ek-n">0</b>/<span id="ek-total">11</span> {L("Ausgaben", "outputs")}<small id="ek-t"></small></div>
      </div>
      <div class="ek-out">
        <div class="ek-k">3 &middot; {L("Überall", "Everywhere")}</div>
        <div class="ek-grid">{cards}</div>
      </div>
    </div>
    <p class="note">{L("Die Demo zeigt das Prinzip direkt im Browser, es wird nichts veröffentlicht. Im Betrieb gehen die Inhalte über unsere Anbindungen an Website, Social Media und Newsletter; Plakat, Flyer und Briefe kommen als druckfertige PDF.",
                        "The demo shows the principle right in your browser; nothing is published. In production the content goes out through our connections to the website, social media and newsletter; poster, flyer and letters come as print-ready PDFs.")}</p>
  </div>
</section>
<section id="druck">
  <div class="wrap">
    {sec_head(L("Druck aus derselben Linie", "Print from the same line"), L("Vom Plakat bis zum Brief.", "From poster to letter."),
              L("Echte Arbeiten für MOTO-ZÜRICH 2027: Plakate, Flyer und Kuvert entstehen aus demselben Designsystem wie die Posts und die Website.",
                "Real work for MOTO-ZÜRICH 2027: posters, flyers and the envelope come from the same design system as the posts and the website."))}
    <div class="ek-print reveal">{print_html}</div>
  </div>
</section>
<section id="ablauf">
  <div class="wrap">
    {sec_head(L("So läuft es", "How it runs"), L("Hochladen, freigeben, fertig.", "Upload, approve, done."))}
    <div class="steps reveal ek-steps4">
      <div><div class="k">1</div><h4>{L("Hochladen", "Upload")}</h4><p>{L("Foto, Video oder News kommen ins System, per Upload, aus Google Drive oder direkt vom Event.", "Photo, video or news go into the system by upload, from Google Drive or straight from the event.")}</p></div>
      <div><div class="k">2</div><h4>{L("System baut", "System builds")}</h4><p>{L("Claude schreibt den Text je Kanal, das Designsystem setzt alle Formate. Typografie und Fakten werden geprüft.", "Claude writes the copy per channel, the design system lays out every format. Typography and facts are checked.")}</p></div>
      <div><div class="k">3</div><h4>{L("Freigabe", "Approval")}</h4><p>{L("Ein Mensch sieht alle Ausgaben auf einen Blick und gibt mit einem Klick frei.", "A person sees every output at a glance and approves with one click.")}</p></div>
      <div><div class="k">4</div><h4>{L("Überall", "Everywhere")}</h4><p>{L("Website, Social Media und Newsletter gehen sofort raus. Plakat, Flyer und Briefe kommen als druckfertige PDF.", "Website, social media and newsletter go out at once. Poster, flyer and letters arrive as print-ready PDFs.")}</p></div>
    </div>
  </div>
</section>
<section class="dark">
  <div class="wrap">
    {sec_head(L("Für Ihre Marke", "For your brand"), L("Das gleiche System, Ihr Design.", "The same system, your design."),
              L("Wir richten das Designsystem Ihrer Marke ein und verbinden Ihre Kanäle. Ab dann reicht ein Foto.",
                "We set up your brand&#39;s design system and connect your channels. From then on, one photo is enough."))}
    <a class="btn btn-primary" href="{p.href("marketing-assistant", "demo")}">{L("Demo anfragen", "Request a demo")} &rarr;</a>
  </div>
</section>'''
    return page(p, L("Marketing-Maschine — ein Klick, jeder Kanal | Creox", "Marketing machine — one click, every channel | Creox"),
                L("Live-Demo der Creox Marketing-Maschine: Ein Foto oder eine News wird mit einem Klick zu Website-Beitrag, Social-Media-Posts, Newsletter, Plakat, Flyer und Brief — gebaut mit Claude.",
                  "Live demo of the Creox marketing machine: one photo or news item becomes a website post, social media posts, newsletter, poster, flyer and letter in one click — built with Claude."),
                body, extra_js='demo.js')
