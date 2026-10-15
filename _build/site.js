// Creox — progressive enhancement only. All content is in the HTML.
(function () {
  // mobile menu
  var mt = document.getElementById('menutoggle'), nl = document.getElementById('navlinks');
  if (mt && nl) {
    mt.addEventListener('click', function () {
      var open = nl.classList.toggle('open');
      mt.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  // reveal on scroll
  var els = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('in'); io.unobserve(e.target); } });
    }, { threshold: 0.12 });
    els.forEach(function (el) { io.observe(el); });
    var lines = Array.prototype.slice.call(document.querySelectorAll('.intro-line'));
    var lio = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (!e.isIntersecting) return;
        var i = lines.indexOf(e.target);
        setTimeout(function () { e.target.classList.add('in'); }, i * 180);
        lio.unobserve(e.target);
      });
    }, { threshold: 0.6 });
    lines.forEach(function (el) { lio.observe(el); });
  } else {
    els.forEach(function (el) { el.classList.add('in'); });
    document.querySelectorAll('.intro-line').forEach(function (el) { el.classList.add('in'); });
  }

  // forms: send to the shared Creox forms endpoint (Supabase + notification to main@creox.ch)
  var FORMS_ENDPOINT = 'https://slswiss-tickets.vercel.app/api/forms';
  var opened = Date.now();
  document.querySelectorAll('form.leadform').forEach(function (f) {
    var note = f.querySelector('.form-note'), ok = f.querySelector('.form-ok'), btn = f.querySelector('button[type=submit]');
    var en = f.dataset.lang === 'en';
    var v = function (n) { var el = f.querySelector('[name="' + n + '"]'); return el ? el.value.trim() : ''; };
    var fail = function (t) { note.classList.add('form-err'); note.textContent = t; };
    f.addEventListener('submit', function (ev) {
      ev.preventDefault();
      var email = v('email');
      if (!v('name') || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email) || !v('phone')) {
        fail(en ? 'Please enter your name, a valid email and your phone number.' : 'Bitte Name, eine gültige E-Mail und Telefonnummer eingeben.'); return;
      }
      if (!f.querySelector('[name="consent"]').checked) {
        fail(en ? 'Please accept the processing of your data.' : 'Bitte stimmen Sie der Bearbeitung Ihrer Daten zu.'); return;
      }
      var topics = Array.prototype.map.call(f.querySelectorAll('input[name="topic"]:checked'), function (x) { return x.value; });
      var phone = (v('dial') ? v('dial') + ' ' : '') + v('phone');
      btn.disabled = true; note.classList.remove('form-err');
      note.textContent = en ? 'Sending…' : 'Wird gesendet…';
      fetch(FORMS_ENDPOINT, {
        method: 'POST', headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          source: 'creox', form_key: f.dataset.key, source_url: location.href, kind: 'lead',
          role: topics.length ? topics.join(', ') : (f.dataset.key === 'demo' ? 'Demo Marketing Assistant' : null),
          name: v('name'), email: email, phone: phone, consent: true,
          hp: v('hp'), elapsed_ms: Date.now() - opened,
          payload: { company: v('company') || null, website: v('site') || null, topics: topics, message: v('message') || null, lang: en ? 'en' : 'de' }
        })
      }).then(function (res) {
        return res.json().catch(function () { return {}; }).then(function (data) {
          if (!res.ok || !data.ok) throw new Error(data.error || ('HTTP ' + res.status));
          ok.hidden = false; btn.hidden = true; note.hidden = true;
        });
      }).catch(function (err) {
        console.error('[form] send failed', err);
        btn.disabled = false;
        fail(en ? 'Sending failed. Please try again or email main@creox.ch.' : 'Senden fehlgeschlagen. Bitte erneut versuchen oder an main@creox.ch schreiben.');
      });
    });
  });
})();
