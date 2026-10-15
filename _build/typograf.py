#!/usr/bin/env python3
"""Типограф v2 — неразрывные пробелы и неразрывные слова через дефис (RU / DE / EN).

  python3 typograf.py --selftest              эталонные тесты → «ВСЕ ТЕСТЫ ПРОЙДЕНЫ»
  python3 typograf.py --check  файлы...       найти нарушения (exit 1, если есть)
  python3 typograf.py --fix    файлы...       исправить на месте
  echo "текст" | python3 typograf.py -        простой текст → текст с U+00A0 (для Canva, Figma, постов)
  echo "текст" | python3 typograf.py --html - простой текст → безопасный HTML (дефисные слова в nowrap)

Что правится в файлах:
  .html .htm .vue .astro .svg  — только видимый текст; теги, атрибуты, script/style/code/pre не трогаются;
                                 стыки через inline-теги учитываются (<b>не</b> сделал)
  .md .txt                     — текст; код, ссылки и разметка не трогаются; **жирный** не мешает
  .jsx .tsx                    — только JSX-текст и UI-атрибуты (title, alt, placeholder, aria-label, label)
  .js .ts .json                — НЕ правятся: строки в коде бывают данными. Текст из данных → typo() при рендере
Принцип: меняются только пробелы (U+0020 → U+00A0), длина текста сохраняется, повторный запуск ничего не меняет.
"""
import re, sys, pathlib, html as _html

NB, NBHY = "\u00a0", "‑"
MAX_CHAIN = 24

W = {
 "prepositions": "в во к ко с со у о об обо от ото до из изо на над надо под подо по за для без безо при про пред предо перед передо через сквозь между меж среди средь около возле вокруг вдоль после кроме ради против мимо вне внутри поверх позади вместо вроде насчёт насчет благодаря согласно навстречу из-за из-под по-над по-за",
 "conjunctions": "и а но да или либо ни не нет то что чтоб чтобы как так будто словно точно дабы кабы ибо коли коль раз ежели если хоть хотя пусть пускай едва лишь зато однако причём причем притом тоже также когда пока покуда где куда откуда кто чем чей чья чьё чьи ведь вот вон уж уже ещё еще даже разве неужели вряд дескать мол",
 "pronouns": "я ты он она оно мы вы они их его её ее им ей ему нам вам мне сам это эта эту эти этот этой этом те та ту тот той том тут там мой моя моё мои наш ваш",
 "de_en": "im am an ab auf aus bei bis für mit nach von vor zu zum zur und oder aber den dem der die das des ein eine einen einem einer a an the of to in on at by for and or but with from as",
 "particles_prev": "же ж ли ль бы б",
 "phrases": "само собой|так как|потому что|оттого что|так что|то есть|как будто|всё равно|все равно|до сих пор|в том числе|тем не менее|друг друга|друг другу|друг с другом|друг о друге|как раз|не только|не то чтобы|на самом деле|в общем|по крайней мере|в конце концов|как минимум|как максимум|в первую очередь|прежде всего|кроме того|как правило|в итоге|скорее всего|по сути|без проблем|с нуля|под ключ|на связи|в любом случае|и так далее|и тому подобное|разве что|только что|один на один|день в день|с глазу на глаз|Свои Люди|z. B.|d. h.|u. a.|zum Beispiel|e. g.|i. e.",
 "abbr": "т. е. д. п. к. ч. г. гг. ж. ул. пр. пл. д. кв. корп. стр. оф. гл. им. см. рис. ок. тел. тыс. руб. проф. акад. доц. св. оз. обл. z. d. u. S. Nr. ca. St. Dr. Fr. Hr. bzw. inkl. exkl. No. Mr. Mrs. Ms. vs.",
 "units_after_num": "CHF Fr. EUR USD € $ ₽ % ‰ °C °F ° млн млрд тыс. Mio. Mrd.",
 "prefix_before_num": "CHF EUR USD Fr. € $ £ ₽ № § Nr. No. p. с. S. ca. ок. тел. Tel. кв. д. гл. ~ ≈",
}
L = "A-Za-zÀ-ÖØ-öø-ɏА-Яа-яЁё"
CYR = "А-Яа-яЁё"
S = r"([ \t]+)"
_w = lambda k: W[k].split()
BIND_NEXT = _w("prepositions") + _w("conjunctions") + _w("pronouns") + _w("de_en")
BIND_PREV = _w("particles_prev")
PHRASES = W["phrases"].split("|")
_alt = lambda ws: "|".join(sorted({re.escape(w) for w in ws}, key=len, reverse=True))
NOT_BEFORE = r"(?<![%s\-.@/_\d'’<>=&#])" % L          # слово не часть url, почты, кода, «don't»
nb = lambda g: NB * len(g)                              # длина текста сохраняется

RULES = [
 # 1. устойчивые сочетания
 (re.compile(r"(?<![%s\-])(%s)(?![%s\-])" % (L, "|".join(re.escape(p).replace(r"\ ", r"[ \t]+") for p in PHRASES), L), re.I),
  lambda m: re.sub(r"[ \t]", NB, m.group(1))),
 # 2. предлог / союз / короткое местоимение → к следующему слову
 (re.compile(NOT_BEFORE + r"(%s)%s(?=[^\s—–\-]|-\d)" % (_alt(BIND_NEXT), S), re.I), lambda m: m.group(1) + nb(m.group(2))),
 # 3. любое 1–2-буквенное кириллическое слово → к следующему (кроме частиц же/ли/бы)
 (re.compile(NOT_BEFORE + r"(?!(?:%s)[ \t])([%s]{1,2})%s(?=[%s«„\"“(\d])" % (_alt(BIND_PREV), CYR, S, L), re.I), lambda m: m.group(1) + nb(m.group(2))),
 # 4. частицы же/ли/бы → к предыдущему слову (но не «б) оплата»)
 (re.compile(r"(?<=[%s\d»\"”)?!])%s(%s)(?![%s\-).])" % (L, S, _alt(BIND_PREV), L), re.I), lambda m: nb(m.group(1)) + m.group(2)),
 # 5. тире и дефис-вместо-тире не начинают строку: «Баден — город», «Баден - город»
 (re.compile(r"(?<=\S)%s([—–]|-(?=[ \t]))(?=[ \t]|$)" % S, re.M), lambda m: nb(m.group(1)) + m.group(2)),
 # 6. диалоговое тире в начале строки: «— Привет»
 (re.compile(r"(?:^|(?<=\n))([—–])%s(?=\S)" % S), lambda m: m.group(1) + nb(m.group(2))),
 # 7. телефон целиком: +41 79 123 45 67, +41 (0)44 123 45 67, 079 123 45 67
 (re.compile(r"(?<![\d\w])(\+\d{1,3}[ \t]\(0\)\d{2}(?:[ \t]\d{2,3}){3}|0\d{2}[ \t]\d{3}[ \t]\d{2}[ \t]\d{2})(?!\d)"), lambda m: re.sub(r"[ \t]", NB, m.group(1))),
 (re.compile(r"(?<![\d\w])(\+\d{1,3}(?:[ \t]\(?\d{1,4}\)?)(?:[ \t]\d{2,4}){2,4})(?!\d)"), lambda m: re.sub(r"[ \t]", NB, m.group(1))),
 # 8. число + единица / кириллическое слово (25 CHF, 12 сентября, −5 °C); + латинское слово, если это не год
 (re.compile(r"(?<![%s.,'’])(\d(?:[\d'’.,]*\d)?)%s(?=(?:%s)(?![%s])|(?!(?:%s)(?![%s]))[%s])" % (L, S, _alt(_w("units_after_num")), L, _alt(BIND_NEXT + BIND_PREV), L, CYR), re.I),
  lambda m: m.group(1) + nb(m.group(2))),
 (re.compile(r"(?<![%s\d.,'’])(?!(?:19|20)\d\d(?!\d))(\d{1,3}(?:['’]\d{3})*)%s(?=[A-Za-zÄÖÜäöü]{3,}(?![%s]))(?!(?:%s)[ \t\n\u00a0.,;:!?]|(?:%s)$)" % (L, S, L, _alt(BIND_NEXT), _alt(BIND_NEXT)), re.I),
  lambda m: m.group(1) + nb(m.group(2))),
 (re.compile(r"(\d[.,][–—-])%s(?=(?:%s)(?![%s]))" % (S, _alt(_w("units_after_num")), L)), lambda m: m.group(1) + nb(m.group(2))),
 # 9. CHF 25, № 5, § 3, тел. +41
 (re.compile(r"(?<![%s])(%s)%s(?=[+\d])" % (L, _alt(_w("prefix_before_num")), S), re.I), lambda m: m.group(1) + nb(m.group(2))),
 # 10. разряды 12 000
 (re.compile(r"(?<=\d)([ \t])(?=\d{3}(?!\d))"), lambda m: NB),
 # 11. инициалы: К. Н. Чудина; А. Пушкин (фамилия от 4 букв, не местоимение)
 (re.compile(r"(?<![%s])([А-ЯЁA-ZÄÖÜ]\.)%s(?=[А-ЯЁA-ZÄÖÜ]\.)" % (L, S)), lambda m: m.group(1) + nb(m.group(2))),
 (re.compile(r"(?<![%s])([А-ЯЁA-ZÄÖÜ]\.)%s(?=[А-ЯЁA-ZÄÖÜ][%s]{3,})(?!(?:%s)(?![%s]))" % (L, S, L, _alt(BIND_NEXT), L)), lambda m: m.group(1) + nb(m.group(2))),
 # 12. фамилия + К. Н.
 (re.compile(r"(?<=[%s]{2})%s(?=[А-ЯЁA-ZÄÖÜ]\.[ \t\u00a0]?[А-ЯЁA-ZÄÖÜ]\.(?![ \t\u00a0]*[А-ЯЁA-ZÄÖÜ][%s]))" % (L, S, L)), lambda m: nb(m.group(1))),
 # 13. сокращения: т. е., т. к., г. Баден, См. выше, z. B.
 (re.compile(r"(?<![%s])(%s)%s(?=\S)" % (L, _alt(_w("abbr")), S), re.I), lambda m: m.group(1) + nb(m.group(2))),
 # 14. немецкие даты: 16. September
 (re.compile(r"(?<![\d.])(\d{1,2}\.)%s(?=[A-ZÄÖÜ][a-zäöü]+)" % S), lambda m: m.group(1) + nb(m.group(2))),
]

HAS_TEXT = re.compile(r"[%s\d]" % L)
URLISH = re.compile(r"(?:https?://|www\.)\S+|[\w.+-]+@[\w-]+(?:\.[\w-]+)+|(?<![\w@])@[\w.]+|#[\w%s]+|\b[\w-]+\.(?:ch|com|me|ru|de|org|net|io|swiss|app)\b(?:/\S*)?" % CYR)
HYPH = re.compile(r"(?<![%s\d\-‑–@./:#_])([%s\d]+(?:[-‑][%s\d]+)+|\d+–\d+)(?![%s\d\-‑–@_]|\.[%s])" % (L, L, L, L, L))
HYPH_MAX = 24

def _limit_chains(text):
    def fix(m):
        run = m.group(0)
        if len(run) <= MAX_CHAIN: return run
        parts, seps = re.split(r"\u00a0+", run), re.findall(r"\u00a0+", run)
        out, cur = parts[0], len(parts[0])
        for prev, sep, nxt in zip(parts, seps, parts[1:]):
            weak = (len(prev.strip("«»\"„“()")) >= 4 and not re.search(r"[\d.]$", prev)
                    and nxt.lower().strip(",.!?:;») ") not in BIND_PREV and nxt not in ("—", "–", "-")
                    and not re.match(r"[\d%€$°]", nxt))
            if cur + len(sep) + len(nxt) > MAX_CHAIN and weak:
                out += " " * len(sep) + nxt; cur = len(nxt)
            else:
                out += sep + nxt; cur += len(sep) + len(nxt)
        return out
    return re.sub(r"[^\s]+(?:\u00a0+[^\s]+)+", fix, text)

def typo(text: str) -> str:
    """Простой текст → текст с U+00A0. Меняет только пробелы; длина сохраняется; идемпотентна.
    Не для HTML-строк: HTML — через fix_html()."""
    if not isinstance(text, str) or not HAS_TEXT.search(text): return text
    masked = URLISH.sub(lambda m: "" * len(m.group(0)), text)
    prev = None
    while prev != masked:
        prev = masked
        for rx, fn in RULES: masked = rx.sub(fn, masked)
    masked = _limit_chains(masked)
    if len(masked) != len(text): return text          # страховка: правила обязаны сохранять длину
    return "".join(NB if (mm == NB and o in " \t") else o for o, mm in zip(text, masked))

# ---------------- проекция: разметка → чистый текст → пробелы обратно ----------------
def _project(pieces, newline_is_space=False):
    """pieces: список (строка, kind). kind: 'text' — текст (правится), 'inline' — невидимая разметка (прозрачна),
    'break' — граница блока, 'atom' — непрозрачный объект (код, {expr}). Возвращает собранную строку."""
    plain, index = [], []          # символ чистого текста → (номер куска, позиция)
    for pi, (s, kind) in enumerate(pieces):
        if kind == "text":
            for ci, ch in enumerate(s):
                plain.append(" " if (newline_is_space and ch in "\r\n") else ch); index.append((pi, ci, ch))
        elif kind == "break": plain.append("\n"); index.append(None)
        elif kind == "atom": plain.append(""); index.append(None)
    fixed = typo("".join(plain))
    out = [list(s) for s, _ in pieces]
    for ch, orig, ix in zip(fixed, plain, index):
        if ix and ch == NB and orig in " \t" and ix[2] in " \t":
            out[ix[0]][ix[1]] = NB
    return ["".join(o) for o in out]

# ---------------- HTML ----------------
SKIP = {"script", "style", "code", "pre", "textarea", "kbd", "samp", "noscript", "template", "math"}
ATOM_SKIP = {"code", "kbd", "samp"}
OPT_OUT = re.compile(r"""\bdata-typograf\s*=\s*["']?off""", re.I)   # <div data-typograf="off"> — намеренно «плохой» пример
INLINE = {"a", "abbr", "b", "bdi", "bdo", "cite", "data", "dfn", "em", "i", "mark", "q", "s", "small", "span",
          "strong", "sub", "sup", "time", "u", "var", "font", "wbr", "tspan"}
TAG = re.compile(r"<!--.*?-->|<![^>]*>|<\?.*?\?>|</?[A-Za-z][\w:-]*(?:[^>\"']|\"[^\"]*\"|'[^']*')*>", re.S)
ENT = re.compile(r"&(?:nbsp|#160|#xa0|mdash|#8212|#x2014|ndash|#8211|#x2013|amp|lt|gt|quot|laquo|raquo|#\d+|#x[0-9a-f]+);", re.I)

def _tokens_html(src):
    pos = 0
    for m in TAG.finditer(src):
        if m.start() > pos: yield "text", src[pos:m.start()]
        yield "tag", m.group(0); pos = m.end()
    if pos < len(src): yield "text", src[pos:]

def fix_html(src: str, hyphens=True) -> str:
    """HTML-документ или фрагмент → с неразрывными пробелами в видимом тексте."""
    toks = list(_tokens_html(src))
    pieces, kinds, skip_stack, svg = [], [], [], 0
    for kind, s in toks:
        if kind == "tag":
            m = re.match(r"<(/)?([A-Za-z][\w:-]*)", s)
            name = m.group(2).lower() if m else ""
            closing = bool(m and m.group(1)); selfclose = s.endswith("/>")
            if skip_stack:
                pieces.append((s, "skip"))
                if name == skip_stack[-1]:
                    if closing: skip_stack.pop()
                    elif not selfclose: skip_stack.append(name)
                if not skip_stack and name in ATOM_SKIP: pieces[-1] = (s, "atomclose")
                continue
            if (name in SKIP or OPT_OUT.search(s)) and not closing and not selfclose:
                skip_stack.append(name); pieces.append((s, "atomopen" if name in ATOM_SKIP else "break")); continue
            if name == "svg": svg += -1 if closing else (0 if selfclose else 1)
            pieces.append((s, "inline" if (name in INLINE and name != "br") or s.startswith("<!--") else "break"))
        else:
            pieces.append((s, "skip" if skip_stack else "text"))
    # собираем куски для проекции: текст раскрываем от сущностей в символы
    proj, back = [], []
    for s, k in pieces:
        if k == "text":
            chars, spans = [], []
            for part in re.split("(%s)" % ENT.pattern, s, flags=re.I):
                if not part: continue
                if ENT.fullmatch(part):
                    u = _html.unescape(part); chars.append(u if len(u) == 1 else ""); spans.append(part)
                else:
                    chars.extend(part); spans.extend(part)
            proj.append(("".join(chars), "text")); back.append(spans)
        elif k in ("inline",): proj.append(("", "inline")); back.append(s)
        elif k in ("atomopen", "atomclose", "skip"):
            proj.append(("", "atom" if k == "atomopen" else "inline")); back.append(s)
        else: proj.append(("", "break")); back.append(s)
    fixed = _project(proj, newline_is_space=True)
    out, svg = [], 0
    for (s, k), f, b in zip(proj, fixed, back):
        if k == "text":
            t = "".join(NB if ch == NB and orig in (" ", "\t") else orig for ch, orig in zip(f, b))
            out.append(t)
        else:
            out.append(b)
    html = "".join(out)
    return _nowrap_html(html) if hyphens else html

def _nowrap_html(html):
    """Слова через дефис → <span style="white-space:nowrap"> (не внутри svg/math/code, не в атрибутах)."""
    out, skip, svg, nowrap, nospan, spans = [], [], 0, False, False, []
    for kind, s in _tokens_html(html):
        if kind == "tag":
            m = re.match(r"<(/)?([A-Za-z][\w:-]*)", s); name = m.group(2).lower() if m else ""
            closing = bool(m and m.group(1)); selfclose = s.endswith("/>")
            if skip and name == skip[-1] and not selfclose:
                if closing: skip.pop()
                else: skip.append(name)
            elif (name in SKIP or OPT_OUT.search(s)) and not closing and not selfclose:
                skip.append(name)
            if name in ("svg", "math") and not selfclose: svg = max(svg + (-1 if closing else 1), 0)
            # внутри title / option / textarea span недопустим; закрывающие теги у option и head необязательны
            if name in ("title", "option", "textarea"): nospan = not closing
            elif name in ("select", "optgroup", "head") and closing: nospan = False
            elif name in ("body", "optgroup") and not closing: nospan = False
            if name == "span" and not selfclose:
                if closing: spans.pop() if spans else None
                else: spans.append("nowrap" in s or "nobr" in s)
            nowrap = any(spans)
            out.append(s)
        elif skip or svg > 0 or nowrap or nospan:
            out.append(s)
        else:
            out.append(nowrap_hyphens_html(s))
    return "".join(out)

EMAIL = r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+"
URL_NOEMAIL = re.compile(r"(?:https?://|www\.)\S+|(?<![\w@.+-])@[\w.]+|#[\w%s]+|(?<![@\w.-])\b[\w-]+\.(?:ch|com|me|ru|de|org|net|io|swiss|app)\b(?:/\S*)?" % CYR)
HYPH_CHAIN = re.compile(r"((?:[^\s<>\u00a0]+\u00a0)*)(?:%s|(?<![\w.+-])(%s)(?![\w-]))((?:\u00a0[^\s<>\u00a0]+)*)" % (HYPH.pattern, EMAIL))

HY_OPEN = '<span style="display:inline-block;max-width:100%">'
NW_OPEN = '<span style="white-space:nowrap">'

def _wrap_chain(chain, word_is_hyphenated):
    """Целиком, если помещается; если нет — перенос ТОЛЬКО перед дефисом, дефис уходит на новую строку:
    «на⍽MOTO» / «-ZÜRICH». inline-block переносит группу целиком, <wbr> разрешает разрыв только перед дефисом."""
    if not word_is_hyphenated:                       # e-mail, диапазон 2025–2026 — просто не рвём
        return NW_OPEN + chain + "</span>"
    parts = re.split(r"(?=[-‑](?=[%s\d]))" % L, chain)
    return HY_OPEN + parts[0] + "".join("<wbr>" + NW_OPEN + p + "</span>" for p in parts[1:]) + "</span>"

def nowrap_hyphens_html(text):
    """Слово через дефис → группа, которая переносится целиком, а если не помещается в строку — только перед дефисом.
    E-mail и числовой диапазон → nowrap целиком. Привязанные неразрывным пробелом слова входят в группу."""
    masked = URL_NOEMAIL.sub(lambda m: "\ue000" * len(m.group(0)), text)
    pos, out = 0, []
    for m in HYPH_CHAIN.finditer(masked):
        word = m.group(2) or m.group(3)
        if not word or len(word) > 40 or "\ue000" in m.group(0): continue
        if m.group(3) and len(m.group(0)) > len(word) + 8: continue
        chain = text[m.start():m.end()]
        hyphenated = bool(m.group(2)) and re.search(r"[-‑]", m.group(2)) is not None
        out.append(text[pos:m.start()]); out.append(_wrap_chain(chain, hyphenated)); pos = m.end()
    out.append(text[pos:]); return "".join(out)

def typo_html(plain: str) -> str:
    """Простой текст → безопасный HTML: экранирование & < > + неразрывные пробелы + nowrap для дефисных слов."""
    return nowrap_hyphens_html(_html.escape(typo(plain), quote=False))

def nbhyphen(text: str) -> str:
    """Canva / Figma / SVG: дефис → U+2011, только если шрифт содержит этот знак (проверка в CHECKLIST)."""
    masked = URLISH.sub(lambda m: "" * len(m.group(0)), text)
    chars = list(text)
    for m in HYPH.finditer(masked):
        if len(m.group(1)) <= HYPH_MAX:
            for i in range(m.start(1), m.end(1)):
                if chars[i] == "-": chars[i] = NBHY
    return "".join(chars)

# ---------------- Markdown ----------------
MD_ATOM = re.compile(r"```.*?```|(?:(?<=\n\n)|(?<=\A))(?:(?: {4}|\t)[^\n]*(?:\n|\Z))+|`[^`\n]*`|!\[[^\]]*\]\([^)]*\)|<[^>\n]+>|\]\([^)]*\)", re.S)
MD_INLINE = re.compile(r"\*\*|__|~~|(?<![\w*])\*(?=\S)|(?<=\S)\*(?![\w*])|(?<![\w_])_(?=\S)|(?<=\S)_(?![\w_])|\[")

def fix_md(src: str) -> str:
    pieces, pos = [], 0
    for m in re.finditer("%s|%s" % (MD_ATOM.pattern, MD_INLINE.pattern), src, re.S):
        if m.start() > pos: pieces.append((src[pos:m.start()], "text"))
        tok = m.group(0)
        kind = "inline" if tok in ("*", "_", "**", "__", "~~", "[") or tok.startswith("](") else "atom"
        if tok.startswith("```"): kind = "break"
        pieces.append((tok, kind)); pos = m.end()
    if pos < len(src): pieces.append((src[pos:], "text"))
    proj = [(s if k == "text" else "", k) for s, k in pieces]
    fixed = _project(proj)
    # переводы строк в markdown значимы: _project превращает их в пробел только для анализа, обратно не пишет NB в \n
    return "".join(f if k == "text" else s for (s, k), f in zip(pieces, fixed))

# ---------------- JSX / TSX ----------------
# JSX-текст берётся ТОЛЬКО между парными тегами одного имени: <p …>текст {expr} текст</p>.
# Стрелки =>, сравнения a > b, дженерики <string> и строки в коде не затрагиваются.
_JI = r"(?:b|strong|em|i|a|span|mark|small|u|s|sup|sub|br)"
_JATTR = r"(?:\s(?:[^<>{}\"']|\"[^\"]*\"|'[^']*'|\{[^{}]*\})*)?"
JSX_ELEM = re.compile(r"(<([A-Za-z][\w.]*)%s>)((?:[^<>{}]|\{[^{}]*\}|<%s%s/?>|</%s>)*)(</\2\s*>)" % (_JATTR, _JI, _JATTR, _JI))
JSX_PART = re.compile(r"\{[^{}]*\}|</?%s%s/?>" % (_JI, _JATTR))
JSX_ATTR = re.compile(r"(\b(?:title|alt|placeholder|aria-label|label|subtitle|caption|description)=)(\"[^\"\n]*\"|'[^'\n]*')")

def fix_jsx(src: str) -> str:
    def text_of(s):
        if not re.search("[%s]" % CYR, re.sub(r"\{[^{}]*\}", "", s)): return s
        pieces, pos = [], 0
        for e in JSX_PART.finditer(s):
            if e.start() > pos: pieces.append((s[pos:e.start()], "text"))
            tok = e.group(0)
            pieces.append((tok, "atom" if tok.startswith("{") else ("break" if re.match(r"<br\b", tok) else "inline"))); pos = e.end()
        if pos < len(s): pieces.append((s[pos:], "text"))
        fixed = _project([(p if k == "text" else "", k) for p, k in pieces])
        return "".join(f if k == "text" else p for (p, k), f in zip(pieces, fixed))
    prev = None
    while prev != src:       # вложенные элементы: изнутри наружу по одному уровню за проход не нужны — текст только в листовых узлах
        prev = src
        src = JSX_ELEM.sub(lambda m: m.group(1) + (text_of(m.group(3)) if re.search("[%s]" % CYR, m.group(3)) else m.group(3)) + m.group(4), src)
    return JSX_ATTR.sub(lambda m: m.group(1) + m.group(2)[0] + typo(m.group(2)[1:-1]) + m.group(2)[-1]
                        if re.search("[%s]" % CYR, m.group(2)) else m.group(0), src)

def process(path: str, text: str):
    ext = pathlib.Path(path).suffix.lower()
    if ext in {".html", ".htm", ".vue", ".astro", ".njk", ".hbs", ".svg"}: return fix_html(text, hyphens=ext != ".svg")
    if ext in {".jsx", ".tsx"}: return fix_jsx(text)
    if ext in {".md", ".mdx", ".txt"}: return fix_md(text) if ext != ".txt" else typo(text)
    return None

# ---------------- эталонные тесты ----------------
GOLDEN = [  # ⍽ = U+00A0
 ("Мы не сделали", "Мы⍽не⍽сделали"),
 ("Живём в стране гор", "Живём в⍽стране гор"),
 ("Это само собой разумеется", "Это⍽само⍽собой разумеется"),
 ("Пришёл, дабы помочь", "Пришёл, дабы⍽помочь"),
 ("Сказал бы, кабы знал", "Сказал⍽бы, кабы⍽знал"),
 ("Молчу, ибо нечего сказать", "Молчу, ибо⍽нечего сказать"),
 ("Хотя было поздно, пусть приходят", "Хотя⍽было поздно, пусть⍽приходят"),
 ("Ежели честно, едва успели", "Ежели⍽честно, едва⍽успели"),
 ("Идём через парк после работы", "Идём через⍽парк после⍽работы"),
 ("Будто никто не заметил", "Будто⍽никто не⍽заметил"),
 ("Разве ли это важно", "Разве⍽ли это⍽важно"),
 ("Он же сказал", "Он⍽же сказал"),
 ("Мы же не из тех, кто сдаётся", "Мы⍽же не⍽из⍽тех, кто⍽сдаётся"),
 ("Вряд ли получится", "Вряд⍽ли получится"),
 ("Баден — город курортов", "Баден⍽— город курортов"),
 ("Баден - город курортов", "Баден⍽- город курортов"),
 ("— Привет, это мы", "—⍽Привет, это⍽мы"),
 ("Вход 25 CHF, CHF 30 для пар", "Вход 25⍽CHF, CHF⍽30 для⍽пар"),
 ("Встреча 12 сентября в 18:00", "Встреча 12⍽сентября в⍽18:00"),
 ("До 1 250 000 гостей", "До⍽1⍽250⍽000⍽гостей"),
 ("Звоните +41 79 123 45 67", "Звоните +41⍽79⍽123⍽45⍽67"),
 ("Ночью −5 °C, днём +20 °C", "Ночью −5⍽°C, днём +20⍽°C"),
 ("Скидка 50 % до конца", "Скидка 50⍽% до⍽конца"),
 ("Автор К. Н. Чудина", "Автор К.⍽Н.⍽Чудина"),
 ("Чудина К. Н. пишет", "Чудина⍽К.⍽Н. пишет"),
 ("План Б. Мы готовы", "План Б. Мы⍽готовы"),
 ("т. е. рядом, и т. д.", "т.⍽е.⍽рядом, и⍽т.⍽д."),
 ("Т. е. рядом, т. к. удобно", "Т.⍽е.⍽рядом, т.⍽к.⍽удобно"),
 ("См. выше, г. Баден, ул. Бахштрассе, д. 12, кв. 5", "См.⍽выше, г.⍽Баден, ул.⍽Бахштрассе, д.⍽12, кв.⍽5"),
 ("в том числе и для вас", "в⍽том⍽числе и⍽для⍽вас"),
 ("На самом деле всё иначе", "На⍽самом⍽деле всё иначе"),
 ("Am 16. September ab 18:00 Uhr", "Am⍽16.⍽September ab⍽18:00⍽Uhr"),
 ("Am 12. Oktober 2026 findet die Messe statt", "Am⍽12.⍽Oktober 2026 findet die⍽Messe statt"),
 ("5 Minuten bis zum Start", "5⍽Minuten bis⍽zum⍽Start"),
 ("z. B. mit CHF 30 für alle", "z.⍽B. mit⍽CHF⍽30 für⍽alle"),
 ("The best of the show", "The⍽best of⍽the⍽show"),
 ("It is so up to me", "It is so up to⍽me"),
 ("№ 5 и § 3", "№⍽5 и⍽§⍽3"),
 ("Скидка до -30 % на всё", "Скидка до⍽-30⍽% на⍽всё"),
 ("Tel. 044 123 45 67, 079 123 45 67, +41 (0)44 123 45 67", "Tel.⍽044⍽123⍽45⍽67, 079⍽123⍽45⍽67, +41⍽(0)44⍽123⍽45⍽67"),
 ("Цена $ 100, € 90, 25.– CHF, 1'000 Plätze", "Цена $⍽100, €⍽90, 25.–⍽CHF, 1'000⍽Plätze"),
 ("Уже пора", "Уже⍽пора"),
 ("Уж если решили — действуйте", "Уж⍽если⍽решили⍽— действуйте"),
 ("Приходите из-за погоды", "Приходите из-за⍽погоды"),
 ("2025–2026 сезон", "2025–2026⍽сезон"),
 ("SVOI.ch и chudina.me", "SVOI.ch и⍽chudina.me"),
 ("Пишите на info@moto-zuerich.ch и в @svoi", "Пишите на⍽info@moto-zuerich.ch и⍽в⍽@svoi"),
 ("Список: а) регистрация; б) оплата", "Список: а) регистрация; б) оплата"),
 ("строка\nне трогаем перенос", "строка\nне⍽трогаем перенос"),
 ("Стоимость от 500 CHF", "Стоимость от⍽500⍽CHF"),
 ("НЕ ПРОПУСТИ: В ЭТУ СУББОТУ", "НЕ⍽ПРОПУСТИ: В⍽ЭТУ⍽СУББОТУ"),
]
GOLDEN_HTML_TEXT = [  # typo_html: [..] = nowrap span
 ("Приходите на MOTO-ZÜRICH", "Приходите [на⍽MOTO|-ZÜRICH]"),
 ("кто-то из-за погоды", "[кто|-то] [из|-за⍽погоды]"),
 ("сезон 2025–2026", "сезон [2025–2026]"),
 ("бизнес-клуб по-русски", "[бизнес|-клуб] [по|-русски]"),
 ("Баден-Баден-Кур", "[Баден|-Баден|-Кур]"),
 ("социально-экономическо-политический", "[социально|-экономическо|-политический]"),
 ("info@moto-zuerich.ch и https://moto-zuerich.ch/ru-ru/", "[info@moto-zuerich.ch] и⍽https://moto-zuerich.ch/ru-ru/"),
 ("Пишите на team@motozuerich.ch", "Пишите [на⍽team@motozuerich.ch]"),
 ("Tom & Jerry <3 в доме", "Tom &amp; Jerry &lt;3 в⍽доме"),
]
GOLDEN_MARKUP = [
 ("<p><b>не</b> сделал</p>", "<p><b>не</b>⍽сделал</p>"),
 ("<p>в <a href=\"#\">Бадене</a></p>", "<p>в⍽<a href=\"#\">Бадене</a></p>"),
 ("<p><strong>25</strong> CHF</p>", "<p><strong>25</strong>⍽CHF</p>"),
 ("<p><b>12 000</b> CHF</p>", "<p><b>12⍽000</b>⍽CHF</p>"),
 ("<script>var s = \"в доме\";</script><p>в доме</p>", "<script>var s = \"в доме\";</script><p>в⍽доме</p>"),
 ("<p>в&nbsp;доме и сад</p>", "<p>в&nbsp;доме и⍽сад</p>"),
 ("<p>Баден &mdash; город</p>", "<p>Баден⍽&mdash; город</p>"),
 ("<img alt=\"в доме\"><p>на MOTO-ZÜRICH</p>", "<img alt=\"в доме\"><p>[на⍽MOTO|-ZÜRICH]</p>"),
 ("<p title=\"a > b в доме\">в доме</p>", "<p title=\"a > b в доме\">в⍽доме</p>"),
 ("<p>5 &lt; 10 и в доме</p>", "<p>5 &lt; 10 и⍽в⍽доме</p>"),
 ("<p>в</p><p>доме</p>", "<p>в</p><p>доме</p>"),
 ("<p>Мы<br>не сдаёмся</p>", "<p>Мы<br>не⍽сдаёмся</p>"),
 ("<p>Живём в\nстране</p>", "<p>Живём в\nстране</p>"),
 ("<p style=\"white-space:pre-line\">кв. 12\nтел. +41 79 123 45 67</p>", "<p style=\"white-space:pre-line\">кв.⍽12\nтел.⍽+41⍽79⍽123⍽45⍽67</p>"),
 ("<head><title>Шоу</title><body><p>на MOTO-ZÜRICH</p>", "<head><title>Шоу</title><body><p>[на⍽MOTO|-ZÜRICH]</p>"),
 ("<select><option>А<option>Б</select><p>на MOTO-ZÜRICH</p>", "<select><option>А<option>Б</select><p>[на⍽MOTO|-ZÜRICH]</p>"),
 ("<p>Мы не <!-- x --> сделали</p>", "<p>Мы⍽не⍽<!-- x -->⍽сделали</p>"),
 ("<svg><text>Кто-то из-за погоды</text></svg>", "<svg><text>Кто-то из-за⍽погоды</text></svg>"),
 ("<p>Пишите <code>в код</code> и в чат</p>", "<p>Пишите <code>в код</code> и⍽в⍽чат</p>"),
 ("<p>Пишите на info@moto-zuerich.ch</p>", "<p>Пишите [на⍽info@moto-zuerich.ch]</p>"),
 ("<!-- в доме --><p>в доме</p>", "<!-- в доме --><p>в⍽доме</p>"),
 ("<title>Дизайн-система на MOTO-ZÜRICH</title><p>на MOTO-ZÜRICH</p>", "<title>Дизайн-система на⍽MOTO-ZÜRICH</title><p>[на⍽MOTO|-ZÜRICH]</p>"),
 ("<select><option>кто-то из-за</option></select>", "<select><option>кто-то из-за</option></select>"),
 ("<div data-typograf=\"off\"><div>в доме</div> и не</div><p>в доме</p>", "<div data-typograf=\"off\"><div>в доме</div> и не</div><p>в⍽доме</p>"),
]
GOLDEN_MD = [
 ("Мы **не** сделали в **Цюрихе**", "Мы⍽**не**⍽сделали в⍽**Цюрихе**"),
 ("**Не** пропустите", "**Не**⍽пропустите"),
 ("Идём *в* город, мы _не_ сделали", "Идём *в*⍽город, мы⍽_не_⍽сделали"),
 ("Текст в доме\n\n    код в пути\n\nи в доме", "Текст в⍽доме\n\n    код в пути\n\nи⍽в⍽доме"),
 ("Итог:\n- **Новые** слова и\n- список в\nстроках", "Итог:\n- **Новые** слова и\n- список в\nстроках"),
 ("[ссылка в доме](https://x.ch/в доме) и `в коде`", "[ссылка в⍽доме](https://x.ch/в доме) и⍽`в коде`"),
]
GOLDEN_JSX = [
 ('<h1>Мы не сделали</h1>', '<h1>Мы⍽не⍽сделали</h1>'),
 ('<p>{name} и не {x} в доме</p>', '<p>{name} и⍽не⍽{x} в⍽доме</p>'),
 ('const t = "в доме и не только";', 'const t = "в доме и не только";'),
 ('if (status === "в работе") {}', 'if (status === "в работе") {}'),
 ('<input placeholder="Имя и фамилия" />', '<input placeholder="Имя и⍽фамилия" />'),
 ('if (a > b && c < d) return <b>в доме</b>;', 'if (a > b && c < d) return <b>в⍽доме</b>;'),
 ('<p>Мы <b>не</b> сделали <a href="/x">в Бадене</a></p>', '<p>Мы⍽<b>не</b>⍽сделали <a href="/x">в⍽Бадене</a></p>'),
 ('items.filter(i => i.name === "Билет на день")', 'items.filter(i => i.name === "Билет на день")'),
 ('const [v, setV] = useState<string>("в пути"); if (v === "в пути") {}', 'const [v, setV] = useState<string>("в пути"); if (v === "в пути") {}'),
 ('const msg = err => `Ошибка в запросе`; const re = /в пути и не/g;', 'const msg = err => `Ошибка в запросе`; const re = /в пути и не/g;'),
 ('const x = a < b && c > d ? "в городе и не только" : <p>и не {n} в доме</p>', 'const x = a < b && c > d ? "в городе и не только" : <p>и⍽не⍽{n} в⍽доме</p>'),
]

def _brackets(h):
    """HTML обёрток → компактная запись для тестов: [группа|-часть] и [nowrap]."""
    h = h.replace("<wbr>" + NW_OPEN, "|")
    h = re.sub(r"\|([^<|]*)</span>", r"|\1", h)
    return h.replace(HY_OPEN, "[").replace(NW_OPEN, "[").replace("</span>", "]")

def selftest(verbose=True):
    show = lambda s: s.replace(NB, "⍽")
    fails, total = 0, 0
    def check(name, got, exp):
        nonlocal fails, total
        total += 1
        if show(got) != exp:
            fails += 1; print(f"✘ {name}\n   ожидали:  {exp}\n   получили: {show(got)}")
    for i, e in GOLDEN:
        check(i, typo(i), e); check("повтор: " + i, typo(typo(i)), show(typo(i)))
        check("длина: " + i, str(len(typo(i))), str(len(i)))
    for i, e in GOLDEN_HTML_TEXT:
        check("html-текст: " + i, _brackets(typo_html(i)), e)
    for i, e in GOLDEN_MARKUP:
        check("разметка: " + i, _brackets(fix_html(i)), e); check("повтор разметки: " + i, fix_html(fix_html(i)), show(fix_html(i)))
    for i, e in GOLDEN_MD: check("markdown: " + i, fix_md(i), e)
    for i, e in GOLDEN_JSX: check("jsx: " + i, fix_jsx(i), e)
    long = typo("Мы же и не из тех, кто для своих на самом деле всегда")
    check("цепочки ≤ %d" % MAX_CHAIN, "OK" if max(len(x) for x in long.split()) <= MAX_CHAIN else long, "OK")
    print(f"Тестов: {total}. " + ("ВСЕ ТЕСТЫ ПРОЙДЕНЫ" if not fails else f"ПРОВАЛЕНО: {fails}"))
    return 1 if fails else 0

def main(argv):
    if argv[:1] == ["--selftest"]: return selftest()
    html_mode = "--html" in argv; argv = [a for a in argv if a != "--html"]
    mode = "--check"
    if argv and argv[0] in ("--check", "--fix"): mode, argv = argv[0], argv[1:]
    if argv == ["-"] or not argv:
        t = sys.stdin.read(); sys.stdout.write(typo_html(t) if html_mode else typo(t)); return 0
    bad = skipped = 0
    for f in argv:
        p = pathlib.Path(f)
        if not p.is_file(): continue
        old = p.read_text(encoding="utf-8"); new = process(f, old)
        if new is None:
            skipped += 1; continue
        if new == old: continue
        a, b = old.splitlines(), new.splitlines()
        hits = [(i + 1, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
        bad += len(hits)
        if mode == "--fix":
            p.write_text(new, encoding="utf-8"); print(f"✔ {f}: исправлено строк — {len(hits)}")
        else:
            print(f"✘ {f}: строк с нарушениями — {len(hits)}")
            for n, y in hits[:20]: print(f"   {n}: " + y.strip().replace(NB, "⍽")[:180])
    if skipped: print(f"Пропущено файлов кода/данных (.js .ts .json и т. п.): {skipped} — их текст выводить через typo() при рендере")
    if mode == "--check":
        print("OK — нарушений нет" if not bad else f"Итого строк: {bad}. Исправить: --fix")
        return 1 if bad else 0
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
