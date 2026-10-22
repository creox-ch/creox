// Типограф v2 — typo.js. Без зависимостей: браузер, Node, React, Remotion, билдеры писем.
//
//   import { typo, typoHtml, splitNowrap, nbhyphen, selftest } from './typo.js';
//
//   typo(text)        простой текст → текст с U+00A0 (props, Google Sheets, CMS, Telegram). Меняет только пробелы.
//   typoHtml(text)    простой текст → безопасный HTML: экранирует & < >; слово через дефис переносится целиком,
//                     а если не помещается в строку — только ПЕРЕД дефисом («на⍽MOTO» / «-ZÜRICH»).
//   splitNowrap(t)    typo-текст → [{ t, nowrap, parts }] для React (компонент <T> — в CHECKLIST.md);
//                     parts — куски, разрезанные перед дефисами (null у e-mail и диапазонов).
//   nbhyphen(text)    дефис → U+2011 для Canva / Figma / SVG (только если шрифт содержит U+2011).
//   selftest()        эталонные тесты → { total, fails }; fails должен быть 0.
//
// НЕ передавайте в typo() HTML-строки: HTML правится через typograf.py --fix.
const NB = '\u00A0', NBHY = '‑', MAX_CHAIN = 24, HYPH_MAX = 24, MASK = '';
const W = {
 "prepositions": "в во к ко с со у о об обо от ото до из изо на над надо под подо по за для без безо при про пред предо перед передо через сквозь между меж среди средь около возле вокруг вдоль после кроме ради против мимо вне внутри поверх позади вместо вроде насчёт насчет благодаря согласно навстречу из-за из-под по-над по-за",
 "conjunctions": "и а но да или либо ни не нет то что чтоб чтобы как так будто словно точно дабы кабы ибо коли коль раз ежели если хоть хотя пусть пускай едва лишь зато однако причём причем притом тоже также когда пока покуда где куда откуда кто чем чей чья чьё чьи ведь вот вон уж уже ещё еще даже разве неужели вряд дескать мол",
 "pronouns": "я ты он она оно мы вы они их его её ее им ей ему нам вам мне сам это эта эту эти этот этой этом те та ту тот той том тут там мой моя моё мои наш ваш",
 "de_en": "im am an ab auf aus bei bis für mit nach von vor zu zum zur und oder aber den dem der die das des ein eine einen einem einer a an the of to in on at by for and or but with from as",
 "particles_prev": "же ж ли ль бы б",
 "phrases": "само собой|так как|потому что|оттого что|так что|то есть|как будто|всё равно|все равно|до сих пор|в том числе|тем не менее|друг друга|друг другу|друг с другом|друг о друге|как раз|не только|не то чтобы|на самом деле|в общем|по крайней мере|в конце концов|как минимум|как максимум|в первую очередь|прежде всего|кроме того|как правило|в итоге|скорее всего|по сути|без проблем|с нуля|под ключ|на связи|в любом случае|и так далее|и тому подобное|разве что|только что|один на один|день в день|с глазу на глаз|Свои Люди|z. B.|d. h.|u. a.|zum Beispiel|e. g.|i. e.",
 "abbr": "т. е. д. п. к. ч. г. гг. ж. ул. пр. пл. д. кв. корп. стр. оф. гл. им. см. рис. ок. тел. тыс. руб. проф. акад. доц. св. оз. обл. z. d. u. S. Nr. ca. St. Dr. Fr. Hr. bzw. inkl. exkl. No. Mr. Mrs. Ms. vs.",
 "units_after_num": "CHF Fr. EUR USD € $ ₽ % ‰ °C °F ° млн млрд тыс. Mio. Mrd.",
 "prefix_before_num": "CHF EUR USD Fr. € $ £ ₽ № § Nr. No. p. с. S. ca. ок. тел. Tel. кв. д. гл. ~ ≈"
};
const L = 'A-Za-zÀ-ÖØ-öø-ɏА-Яа-яЁё', CYR = 'А-Яа-яЁё', S = '([ \\t]+)';
const w = k => W[k].split(/\s+/).filter(Boolean);
const esc = s => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const alt = a => [...new Set(a)].sort((x, y) => y.length - x.length).map(esc).join('|');
const BIND_NEXT = [...w('prepositions'), ...w('conjunctions'), ...w('pronouns'), ...w('de_en')];
const BIND_PREV = w('particles_prev');
const PHRASES = W.phrases.split('|');
const NOT_BEFORE = `(?<![${L}\\-.@/_\\d'’<>=&#])`;
const nb = g => NB.repeat(g.length);
const R = (p, f = 'gu') => new RegExp(p, f);
const RULES = [
  [R(`(?<![${L}\\-])(${PHRASES.map(p => esc(p).replace(/ /g, '[ \\t]+')).join('|')})(?![${L}\\-])`, 'giu'), (m, a) => a.replace(/[ \t]/g, NB)],
  [R(`${NOT_BEFORE}(${alt(BIND_NEXT)})${S}(?=[^\\s—–\\-]|-\\d)`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`${NOT_BEFORE}(?!(?:${alt(BIND_PREV)})[ \\t])([${CYR}]{1,2})${S}(?=[${L}«„"“(\\d${MASK}])`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`(?<=[${L}\\d»"”)?!])${S}(${alt(BIND_PREV)})(?![${L}\\-).])`, 'giu'), (m, s, a) => nb(s) + a],
  [R(`(?<=\\S)${S}([—–]|-(?=[ \\t]))(?=[ \\t]|$)`, 'gmu'), (m, s, a) => nb(s) + a],
  [R(`(?:^|(?<=\\n))([—–])${S}(?=\\S)`, 'gu'), (m, a, s) => a + nb(s)],
  [R(`(?<![\\d\\w])(\\+\\d{1,3}[ \\t]\\(0\\)\\d{2}(?:[ \\t]\\d{2,3}){3}|0\\d{2}[ \\t]\\d{3}[ \\t]\\d{2}[ \\t]\\d{2})(?!\\d)`, 'gu'), (m, a) => a.replace(/[ \t]/g, NB)],
  [R(`(?<![\\d\\w])(\\+\\d{1,3}(?:[ \\t]\\(?\\d{1,4}\\)?)(?:[ \\t]\\d{2,4}){2,4})(?!\\d)`, 'gu'), (m, a) => a.replace(/[ \t]/g, NB)],
  [R(`(?<![${L}.,'’])(\\d(?:[\\d'’.,]*\\d)?)${S}(?=(?:${alt(w('units_after_num'))})(?![${L}])|(?!(?:${alt([...BIND_NEXT, ...BIND_PREV])})(?![${L}]))[${CYR}])`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`(?<![${L}\\d.,'’])(?!(?:19|20)\\d\\d(?!\\d))(\\d{1,3}(?:['’]\\d{3})*)${S}(?=[A-Za-zÄÖÜäöü]{3,}(?![${L}]))(?!(?:${alt(BIND_NEXT)})[ \\t\\n\\u00a0.,;:!?]|(?:${alt(BIND_NEXT)})$)`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`(\\d[.,][–—-])${S}(?=(?:${alt(w('units_after_num'))})(?![${L}]))`, 'gu'), (m, a, s) => a + nb(s)],
  [R(`(?<![${L}])(${alt(w('prefix_before_num'))})${S}(?=[+\\d])`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`(?<=\\d)([ \\t])(?=\\d{3}(?!\\d))`, 'gu'), () => NB],
  [R(`(?<![${L}])([А-ЯЁA-ZÄÖÜ]\\.)${S}(?=[А-ЯЁA-ZÄÖÜ]\\.)`, 'gu'), (m, a, s) => a + nb(s)],
  [R(`(?<![${L}])([А-ЯЁA-ZÄÖÜ]\\.)${S}(?=[А-ЯЁA-ZÄÖÜ][${L}]{3,})(?!(?:${alt(BIND_NEXT)})(?![${L}]))`, 'gu'), (m, a, s) => a + nb(s)],
  [R(`(?<=[${L}]{2})${S}(?=[А-ЯЁA-ZÄÖÜ]\\.[ \\t\\u00a0]?[А-ЯЁA-ZÄÖÜ]\\.(?![ \\t\\u00a0]*[А-ЯЁA-ZÄÖÜ][${L}]))`, 'gu'), (m, s) => nb(s)],
  [R(`(?<![${L}])(${alt(w('abbr'))})${S}(?=\\S)`, 'giu'), (m, a, s) => a + nb(s)],
  [R(`(?<![\\d.])(\\d{1,2}\\.)${S}(?=[A-ZÄÖÜ][a-zäöü]+)`, 'gu'), (m, a, s) => a + nb(s)],
];
const HAS_TEXT = R(`[${L}\\d]`, 'u');
const URLISH = R(`(?:https?://|www\\.)\\S+|[\\p{L}\\p{N}_.+-]+@[\\p{L}\\p{N}_-]+(?:\\.[\\p{L}\\p{N}_-]+)+|(?<![\\p{L}\\p{N}_@])@[\\p{L}\\p{N}_.]+|#[\\p{L}\\p{N}_${CYR}]+|(?<![\\p{L}\\p{N}_])[\\p{L}\\p{N}_-]+\\.(?:ch|com|me|ru|de|org|net|io|swiss|app)(?![\\p{L}\\p{N}_])(?:/\\S*)?`, 'gu');
const HYPH_SRC = `(?<![${L}\\d\\-‑–@./:#_${MASK}])([${L}\\d]+(?:[-‑][${L}\\d]+)+|\\d+–\\d+)(?![${L}\\d\\-‑–@_${MASK}]|\\.[${L}])`;
const HYPH = R(HYPH_SRC, 'gu');
const EMAIL = `[\\p{L}\\p{N}_.+-]+@[\\p{L}\\p{N}_-]+(?:\\.[\\p{L}\\p{N}_-]+)+`;
const URL_NOEMAIL = R(`(?:https?://|www\\.)\\S+|(?<![\\p{L}\\p{N}_@.+-])@[\\p{L}\\p{N}_.]+|#[\\p{L}\\p{N}_${CYR}]+|(?<![@\\p{L}\\p{N}_.-])(?<![\\p{L}\\p{N}_])[\\p{L}\\p{N}_-]+\\.(?:ch|com|me|ru|de|org|net|io|swiss|app)(?![\\p{L}\\p{N}_])(?:/\\S*)?`, 'gu');
const HYPH_CHAIN = R(`((?:[^\\s<>\\u00A0]+\\u00A0)*)(?:${HYPH_SRC}|(?<![\\p{L}\\p{N}_.+-])(${EMAIL})(?![\\p{L}\\p{N}_-]))((?:\\u00A0[^\\s<>\\u00A0]+)*)`, 'gu');
const mask = t => t.replace(URLISH, m => MASK.repeat(m.length));

function limitChains(text) {
  return text.replace(/[^\s]+(?:\u00A0+[^\s]+)+/gu, run => {
    if (run.length <= MAX_CHAIN) return run;
    const parts = run.split(/\u00A0+/), seps = run.match(/\u00A0+/g);
    let out = parts[0], cur = parts[0].length;
    for (let i = 1; i < parts.length; i++) {
      const prev = parts[i - 1], nxt = parts[i], sep = seps[i - 1];
      const weak = prev.replace(/^[«»"„“()]+|[«»"„“()]+$/g, '').length >= 4 && !/[\d.]$/.test(prev)
        && !BIND_PREV.includes(nxt.toLowerCase().replace(/^[,.!?:;») ]+|[,.!?:;») ]+$/g, ''))
        && !['—', '–', '-'].includes(nxt) && !/^[\d%€$°]/.test(nxt);
      if (cur + sep.length + nxt.length > MAX_CHAIN && weak) { out += ' '.repeat(sep.length) + nxt; cur = nxt.length; }
      else { out += sep + nxt; cur += sep.length + nxt.length; }
    }
    return out;
  });
}

export function typo(text) {
  if (typeof text !== 'string' || !HAS_TEXT.test(text)) return text;
  let m = mask(text), prev;
  do { prev = m; for (const [rx, fn] of RULES) m = m.replace(rx, fn); } while (m !== prev);
  m = limitChains(m);
  if (m.length !== text.length) return text;
  let out = '';
  for (let i = 0; i < text.length; i++) out += (m[i] === NB && (text[i] === ' ' || text[i] === '\t')) ? NB : text[i];
  return out;
}
export function splitNowrap(text) {
  text = String(text); const masked = text.replace(URL_NOEMAIL, m => MASK.repeat(m.length)), out = []; let last = 0;
  for (const mt of masked.matchAll(HYPH_CHAIN)) {
    const whole = mt[0], word = mt[2] || mt[3];
    if (!word || word.length > 40 || whole.includes(MASK)) continue;
    if (mt[3] && whole.length > word.length + 8) continue;
    if (mt.index > last) out.push({ t: text.slice(last, mt.index), nowrap: false });
    const chain = text.slice(mt.index, mt.index + whole.length);
    const parts = mt[2] && /[-‑]/.test(mt[2]) ? chain.split(new RegExp(`(?=[-‑](?=[${L}\\d]))`, 'u')) : null;
    out.push({ t: chain, nowrap: true, parts }); last = mt.index + whole.length;
  }
  if (last < text.length) out.push({ t: text.slice(last), nowrap: false });
  return out;
}
const escHtml = s => s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const HY_OPEN = '<span style="display:inline-block;max-width:100%">', NW_OPEN = '<span style="white-space:nowrap">';
export function typoHtml(plainText) {
  return splitNowrap(typo(String(plainText))).map(p => !p.nowrap ? escHtml(p.t)
    : p.parts ? HY_OPEN + escHtml(p.parts[0]) + p.parts.slice(1).map(x => '<wbr>' + NW_OPEN + escHtml(x) + '</span>').join('') + '</span>'
    : NW_OPEN + escHtml(p.t) + '</span>').join('');
}
export function nbhyphen(text) {
  text = String(text); const chars = [...text]; const masked = mask(text);
  if (chars.length !== text.length) return text.replace(HYPH, (m0, w0) => w0.length <= HYPH_MAX ? w0.replace(/-/g, NBHY) : w0);
  for (const mt of masked.matchAll(HYPH)) if (mt[1].length <= HYPH_MAX)
    for (let i = mt.index; i < mt.index + mt[1].length; i++) if (chars[i] === '-') chars[i] = NBHY;
  return chars.join('');
}
const GOLDEN = [
 [
  "Мы не сделали",
  "Мы⍽не⍽сделали"
 ],
 [
  "Живём в стране гор",
  "Живём в⍽стране гор"
 ],
 [
  "Это само собой разумеется",
  "Это⍽само⍽собой разумеется"
 ],
 [
  "Пришёл, дабы помочь",
  "Пришёл, дабы⍽помочь"
 ],
 [
  "Сказал бы, кабы знал",
  "Сказал⍽бы, кабы⍽знал"
 ],
 [
  "Молчу, ибо нечего сказать",
  "Молчу, ибо⍽нечего сказать"
 ],
 [
  "Хотя было поздно, пусть приходят",
  "Хотя⍽было поздно, пусть⍽приходят"
 ],
 [
  "Ежели честно, едва успели",
  "Ежели⍽честно, едва⍽успели"
 ],
 [
  "Идём через парк после работы",
  "Идём через⍽парк после⍽работы"
 ],
 [
  "Будто никто не заметил",
  "Будто⍽никто не⍽заметил"
 ],
 [
  "Разве ли это важно",
  "Разве⍽ли это⍽важно"
 ],
 [
  "Он же сказал",
  "Он⍽же сказал"
 ],
 [
  "Мы же не из тех, кто сдаётся",
  "Мы⍽же не⍽из⍽тех, кто⍽сдаётся"
 ],
 [
  "Вряд ли получится",
  "Вряд⍽ли получится"
 ],
 [
  "Баден — город курортов",
  "Баден⍽— город курортов"
 ],
 [
  "Баден - город курортов",
  "Баден⍽- город курортов"
 ],
 [
  "— Привет, это мы",
  "—⍽Привет, это⍽мы"
 ],
 [
  "Вход 25 CHF, CHF 30 для пар",
  "Вход 25⍽CHF, CHF⍽30 для⍽пар"
 ],
 [
  "Встреча 12 сентября в 18:00",
  "Встреча 12⍽сентября в⍽18:00"
 ],
 [
  "До 1 250 000 гостей",
  "До⍽1⍽250⍽000⍽гостей"
 ],
 [
  "Звоните +41 79 123 45 67",
  "Звоните +41⍽79⍽123⍽45⍽67"
 ],
 [
  "Ночью −5 °C, днём +20 °C",
  "Ночью −5⍽°C, днём +20⍽°C"
 ],
 [
  "Скидка 50 % до конца",
  "Скидка 50⍽% до⍽конца"
 ],
 [
  "Автор К. Н. Чудина",
  "Автор К.⍽Н.⍽Чудина"
 ],
 [
  "Чудина К. Н. пишет",
  "Чудина⍽К.⍽Н. пишет"
 ],
 [
  "План Б. Мы готовы",
  "План Б. Мы⍽готовы"
 ],
 [
  "т. е. рядом, и т. д.",
  "т.⍽е.⍽рядом, и⍽т.⍽д."
 ],
 [
  "Т. е. рядом, т. к. удобно",
  "Т.⍽е.⍽рядом, т.⍽к.⍽удобно"
 ],
 [
  "См. выше, г. Баден, ул. Бахштрассе, д. 12, кв. 5",
  "См.⍽выше, г.⍽Баден, ул.⍽Бахштрассе, д.⍽12, кв.⍽5"
 ],
 [
  "в том числе и для вас",
  "в⍽том⍽числе и⍽для⍽вас"
 ],
 [
  "На самом деле всё иначе",
  "На⍽самом⍽деле всё иначе"
 ],
 [
  "Am 16. September ab 18:00 Uhr",
  "Am⍽16.⍽September ab⍽18:00⍽Uhr"
 ],
 [
  "Am 12. Oktober 2026 findet die Messe statt",
  "Am⍽12.⍽Oktober 2026 findet die⍽Messe statt"
 ],
 [
  "5 Minuten bis zum Start",
  "5⍽Minuten bis⍽zum⍽Start"
 ],
 [
  "z. B. mit CHF 30 für alle",
  "z.⍽B. mit⍽CHF⍽30 für⍽alle"
 ],
 [
  "The best of the show",
  "The⍽best of⍽the⍽show"
 ],
 [
  "It is so up to me",
  "It is so up to⍽me"
 ],
 [
  "№ 5 и § 3",
  "№⍽5 и⍽§⍽3"
 ],
 [
  "Скидка до -30 % на всё",
  "Скидка до⍽-30⍽% на⍽всё"
 ],
 [
  "Tel. 044 123 45 67, 079 123 45 67, +41 (0)44 123 45 67",
  "Tel.⍽044⍽123⍽45⍽67, 079⍽123⍽45⍽67, +41⍽(0)44⍽123⍽45⍽67"
 ],
 [
  "Цена $ 100, € 90, 25.– CHF, 1'000 Plätze",
  "Цена $⍽100, €⍽90, 25.–⍽CHF, 1'000⍽Plätze"
 ],
 [
  "Уже пора",
  "Уже⍽пора"
 ],
 [
  "Уж если решили — действуйте",
  "Уж⍽если⍽решили⍽— действуйте"
 ],
 [
  "Приходите из-за погоды",
  "Приходите из-за⍽погоды"
 ],
 [
  "2025–2026 сезон",
  "2025–2026⍽сезон"
 ],
 [
  "SVOI.ch и chudina.me",
  "SVOI.ch и⍽chudina.me"
 ],
 [
  "Пишите на info@moto-zuerich.ch и в @svoi",
  "Пишите на⍽info@moto-zuerich.ch и⍽в⍽@svoi"
 ],
 [
  "Список: а) регистрация; б) оплата",
  "Список: а) регистрация; б) оплата"
 ],
 [
  "строка\nне трогаем перенос",
  "строка\nне⍽трогаем перенос"
 ],
 [
  "Стоимость от 500 CHF",
  "Стоимость от⍽500⍽CHF"
 ],
 [
  "НЕ ПРОПУСТИ: В ЭТУ СУББОТУ",
  "НЕ⍽ПРОПУСТИ: В⍽ЭТУ⍽СУББОТУ"
 ]
];
const GOLDEN_HTML_TEXT = [
 [
  "Приходите на MOTO-ZÜRICH",
  "Приходите [на⍽MOTO|-ZÜRICH]"
 ],
 [
  "кто-то из-за погоды",
  "[кто|-то] [из|-за⍽погоды]"
 ],
 [
  "сезон 2025–2026",
  "сезон [2025–2026]"
 ],
 [
  "бизнес-клуб по-русски",
  "[бизнес|-клуб] [по|-русски]"
 ],
 [
  "Баден-Баден-Кур",
  "[Баден|-Баден|-Кур]"
 ],
 [
  "социально-экономическо-политический",
  "[социально|-экономическо|-политический]"
 ],
 [
  "info@moto-zuerich.ch и https://moto-zuerich.ch/ru-ru/",
  "[info@moto-zuerich.ch] и⍽https://moto-zuerich.ch/ru-ru/"
 ],
 [
  "Пишите на team@motozuerich.ch",
  "Пишите [на⍽team@motozuerich.ch]"
 ],
 [
  "Tom & Jerry <3 в доме",
  "Tom &amp; Jerry &lt;3 в⍽доме"
 ]
];
export function selftest(log = console.log) {
  const show = s => s.replace(/\u00A0/g, '⍽'); let fails = 0, total = 0;
  const check = (name, got, exp) => { total++; if (show(got) !== exp) { fails++; log(`✘ ${name}\n   ожидали:  ${exp}\n   получили: ${show(got)}`); } };
  for (const [i, e] of GOLDEN) { check(i, typo(i), e); check('повтор: ' + i, typo(typo(i)), show(typo(i))); check('длина: ' + i, String(typo(i).length), String(i.length)); }
  const brackets = h => h.split('<wbr>' + NW_OPEN).join('|').replace(/\|([^<|]*)<\/span>/g, '|$1').split(HY_OPEN).join('[').split(NW_OPEN).join('[').split('</span>').join(']');
  for (const [i, e] of GOLDEN_HTML_TEXT) check('html-текст: ' + i, brackets(typoHtml(i)), e);
  log(`Тестов: ${total}. ` + (fails ? `ПРОВАЛЕНО: ${fails}` : 'ВСЕ ТЕСТЫ ПРОЙДЕНЫ'));
  return { total, fails };
}
export default typo;
