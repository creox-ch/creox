// /ein-klick — live demo. Everything happens in the browser; nothing is sent anywhere.
import { typoHtml as th } from './typo.js';
// keep date ranges like «19.–21.» on one line
const typoHtml = s => th(s).replace(/(\d{1,2}\.?[–-]\d{1,2}\.?)/g, '<span style="white-space:nowrap">$1</span>');

const root = document.querySelector('.ek');
if (root) {
  const en = root.dataset.lang === 'en';
  const $ = (s, el = document) => el.querySelector(s);
  const $$ = (s, el = document) => Array.from(el.querySelectorAll(s));
  const title = $('#ek-title'), sub = $('#ek-sub'), go = $('#ek-go'), reset = $('#ek-reset');
  const nEl = $('#ek-n'), tEl = $('#ek-t');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  let photo = '', timers = [];

  // the same message, written for each channel
  const caps = {
    'cap-ig': (t, s) => `${t} ${s.split('·').slice(1).join('·').trim()} 🏍️ #motozuerich #motorrad #zürich`,
    'cap-fb': (t, s) => en ? `${t} ${s}. Save the date and tell your riding crew.` : `${t} ${s}. Datum speichern und der Crew Bescheid geben.`,
    'cap-li': (t, s) => en ? `Save the date: ${s}. ${t} Exhibitors and partners: let's talk.` : `Save the Date: ${s}. ${t} Aussteller und Partner: Sprechen Sie uns an.`,
    'cap-tg': (t, s) => `${t}\n${s}`,
  };

  function render() {
    const t = title.value.trim() || '…', s = sub.value.trim();
    $$('[data-f="title"]', root).forEach(el => { el.innerHTML = typoHtml(t); });
    $$('[data-f="sub"]', root).forEach(el => { el.innerHTML = typoHtml(s); });
    Object.entries(caps).forEach(([k, fn]) => $$(`[data-f="${k}"]`, root).forEach(el => { el.innerHTML = typoHtml(fn(t, s)); }));
    root.style.setProperty('--photo', photo ? `url("${photo}")` : 'none');
  }

  function setPhoto(src, btn) {
    photo = src;
    $$('.ek-thumb', root).forEach(b => b.classList.toggle('on', b === btn));
    render();
  }

  function applyPreset(input) {
    title.value = input.dataset.title;
    sub.value = input.dataset.sub;
    const thumb = $$('.ek-thumb[data-photo]', root).find(b => b.dataset.photo === input.dataset.photo);
    setPhoto(input.dataset.photo, thumb);
    clearRun();
  }

  function clearRun() {
    timers.forEach(clearTimeout); timers = [];
    root.classList.remove('run', 'done');
    $$('.ek-steps li', root).forEach(li => li.classList.remove('ok'));
    $$('.ek-card', root).forEach(c => { c.classList.remove('live'); $('.ek-st', c).textContent = en ? 'waiting' : 'wartet'; });
    nEl.textContent = '0'; tEl.textContent = '';
    go.disabled = false; reset.hidden = true;
  }

  function run() {
    clearRun();
    go.disabled = true;
    root.classList.add('run');
    const steps = $$('.ek-steps li', root), cards = $$('.ek-card', root);
    const stepMs = reduce ? 0 : 320, cardMs = reduce ? 0 : 230;
    let n = 0;
    steps.forEach((li, i) => timers.push(setTimeout(() => li.classList.add('ok'), stepMs * (i + 1))));
    const start = stepMs * (steps.length + 1);
    cards.forEach((c, i) => timers.push(setTimeout(() => {
      c.classList.add('live');
      $('.ek-st', c).textContent = $('.ek-st', c).dataset.done;
      n += c.dataset.ch === 'letter' ? 2 : 1;
      nEl.textContent = String(n);
      tEl.textContent = (en ? ' · after ' : ' · nach ') + (1.2 + i * 0.4).toFixed(1).replace('.', en ? '.' : ',') + ' s';
    }, start + cardMs * i)));
    timers.push(setTimeout(() => {
      root.classList.remove('run'); root.classList.add('done');
      reset.hidden = false; go.disabled = false;
    }, start + cardMs * cards.length));
  }

  $$('input[name="ek-preset"]', root).forEach(r => r.addEventListener('change', () => applyPreset(r)));
  $$('.ek-thumb[data-photo]', root).forEach(b => b.addEventListener('click', () => { setPhoto(b.dataset.photo, b); clearRun(); }));
  $('#ek-file').addEventListener('change', e => {
    const f = e.target.files && e.target.files[0];
    if (!f || !f.type.startsWith('image/')) return;
    const r = new FileReader();
    r.onload = () => { setPhoto(r.result, e.target.closest('.ek-thumb')); clearRun(); };
    r.readAsDataURL(f);
  });
  [title, sub].forEach(el => el.addEventListener('input', () => { render(); if (root.classList.contains('done')) clearRun(); }));
  go.addEventListener('click', run);
  reset.addEventListener('click', run);

  applyPreset($('input[name="ek-preset"]:checked', root));
}
