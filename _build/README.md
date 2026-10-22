# creox.ch — Quellen

Die Seiten im Repo-Root werden aus diesem Ordner erzeugt.

1. Texte und Seiten ändern in `build.py`, Styles in `style.css`, Formular/Animation in `site.js`.
2. Bauen: `python3 build.py` (schreibt nach `../dist`), danach Typograf: `python3 typograf.py --fix ../dist/*.html ../dist/en/*.html` und `python3 postfix.py ../dist/*.html ../dist/en/*.html`.
3. Inhalt von `dist/` in den Repo-Root kopieren und committen.

`static/motogen.html` ist die bisherige Produktseite (MotoGen, Antrix, Audio Guide mit Newsletter-Anmeldung); sie wird unverändert als `/motogen` ausgeliefert.
Formulare senden an `https://slswiss-tickets.vercel.app/api/forms` (source `creox`, form_key `brief` bzw. `demo`).
Dieser Ordner wird über `.vercelignore` nicht veröffentlicht.

`page_einklick.py` + `demo.js` + `typo.js` bauen die Seite `/ein-klick` (Marketing-Maschine, Live-Demo).
`media/ein-klick.mp4` ist der Film; seine Quellen (Remotion) liegen in `video/`, Musik wird mit `video/tools/music.py` synthetisiert.
