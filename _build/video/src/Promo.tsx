import React from "react";
import {
  AbsoluteFill, Img, staticFile, useCurrentFrame, interpolate, spring, Easing, useVideoConfig, delayRender, continueRender, Sequence,
} from "remotion";
import { Audio } from "@remotion/media";
// @ts-ignore — plain JS module (Typograf v2)
import { typo } from "./typo.js";

/* ---------- fonts ---------- */
const fontHandle = delayRender("fonts");
const faces: [string, string, string][] = [
  ["Grotesk", "space-grotesk-latin-500-normal.woff2", "500"], ["Grotesk", "space-grotesk-latin-700-normal.woff2", "700"],
  ["Grotesk", "space-grotesk-latin-ext-700-normal.woff2", "700"],
  ["SMono", "space-mono-latin-400-normal.woff2", "400"], ["SMono", "space-mono-latin-700-normal.woff2", "700"],
  ["Body", "ibm-plex-mono-latin-400-normal.woff2", "400"], ["Body", "ibm-plex-mono-latin-500-normal.woff2", "500"],
  ["Inter", "inter-latin-500-normal.woff2", "500"], ["Inter", "inter-latin-700-normal.woff2", "700"],
  ["Plex", "IBMPlexSans-VF.ttf", "100 900"], ["PlexMono", "IBMPlexMono-Bold.ttf", "700"],
];
Promise.all(faces.map(([f, file, w]) => new FontFace(f, `url(${staticFile("fonts/" + file)})`, { weight: w }).load().then((ff) => document.fonts.add(ff))))
  .then(() => continueRender(fontHandle)).catch(() => continueRender(fontHandle));

/* ---------- tokens ---------- */
const C = {
  paper: "#F4F4F1", paper2: "#ECECE7", ink: "#0E0E0E", mut: "#3A3A37", mut2: "#6A6A67", cblue: "#2E44D6", neon: "#C6FF3A", white: "#FFFFFF",
  navy: "#0e2a4a", night: "#0a1929", blue: "#2F65A0", yellow: "#FAF143", red: "#C10D0D",
};
const HEAD = "Grotesk, sans-serif", LABEL = "SMono, monospace", BODY = "Body, monospace";
const UI = "Inter, sans-serif", BRAND = "Plex, sans-serif", MONO = "PlexMono, monospace";
const ease = Easing.bezier(0.16, 1, 0.3, 1);
const clamp = { extrapolateLeft: "clamp" as const, extrapolateRight: "clamp" as const };
const t = (s: string) => typo(s);
const ramp = (f: number, a: number, b: number) => interpolate(f, [a, b], [0, 1], { ...clamp, easing: ease });

/* ---------- timeline (frames @30fps) ---------- */
export const T = {
  drop: 25, edit: 48, sys: 168, chips: [176, 184, 192], click: 210,
  soc: 225, web: 345, nl: 420, brief: 495, poster: 580, save: 665, end: 785, total: 870,
};
export const SOC_CARD = (i: number) => T.soc + 6 + i * 8;      // 6 feed cards
export const SOC_TILE = (i: number) => T.soc + 52 + i * 6;     // 8 channel tiles
/* edit scene, local frames from T.edit */
export const ED = { cuts: [18, 26, 34, 42], pack: [44, 54], sub: 56, logo: 66, tag: 72, music: 78, fmt: [90, 96, 102], done: [54, 64, 76, 86, 106] };
export const STAGES = ["Video", "Social", "Website", "Newsletter", "Brief", "Plakat"];
const STAGE_DONE = [T.edit + 104, T.soc + 100, T.web + 50, T.nl + 52, T.brief + 70, T.poster + 52];

/* ---------- header copy ---------- */
type Phase = { from: number; eyebrow: string; a: string; b: string; box?: boolean; sub: string };
const PHASES: Phase[] = [
  { from: 0, eyebrow: "Creox · Marketing-Maschine", a: "Foto oder Video ", b: "hochladen.", sub: "Jede Grösse, jede Qualität." },
  { from: T.edit, eyebrow: "00 · Video · automatischer Schnitt", a: "Das System ", b: "schneidet.", sub: "Schnitt, Untertitel, Overlays, Musik: nach Ihren Vorgaben, im Markendesign." },
  { from: T.sys, eyebrow: "Creox · Marketing-Maschine", a: "Das System ", b: "baut.", sub: "Texte DE/EN, alle Formate, jeder Kanal." },
  { from: T.soc, eyebrow: "01 · Social Media · sofort", a: "Sofort ", b: "überall.", sub: "Jeder Kanal im eigenen Format." },
  { from: T.web, eyebrow: "02 · Website · nach 2 Minuten", a: "Die Website ", b: "zieht nach.", sub: "News-Beitrag in DE und EN." },
  { from: T.nl, eyebrow: "03 · Newsletter · geplant", a: "Der Newsletter ", b: "ist bereit.", sub: "Versand am Freitag um 18:00." },
  { from: T.brief, eyebrow: "04 · Brief · per Post", a: "Der Brief ", b: "geht raus.", sub: "Serienbrief an alle Aussteller." },
  { from: T.poster, eyebrow: "05 · Plakat · Druck", a: "Das Plakat ", b: "hängt.", sub: "Druck-PDF direkt an die Druckerei." },
  { from: T.save, eyebrow: "Zeit · vorher / nachher", a: "Ein Arbeitstag ", b: "gespart.", sub: "Schätzung: ein Event-Beitrag, alle Kanäle." },
  { from: T.end, eyebrow: "Creox · Marketing Assistant", a: "Ein Inhalt. ", b: "Jeder Kanal.", box: true, sub: "Für Ihre Marke: creox.ch" },
];

const Header: React.FC = () => {
  const f = useCurrentFrame();
  const idx = PHASES.reduce((acc, p, i) => (f >= p.from ? i : acc), 0);
  const p = PHASES[idx];
  const inn = ramp(f, p.from, p.from + 10);
  return (
    <div style={{ position: "absolute", left: 80, right: 80, top: 140 }}>
      <div style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 30, letterSpacing: "0.1em", textTransform: "uppercase", color: C.cblue, opacity: inn }}>{t(p.eyebrow)}</div>
      <div style={{ marginTop: 20, opacity: inn, transform: `translateY(${(1 - inn) * 28}px)` }}>
        <div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 84, lineHeight: 0.98, letterSpacing: "-0.03em", textTransform: "uppercase", color: C.ink }}>
          {t(p.a)}
          {p.box ? <span style={{ background: C.neon, padding: "0 12px", boxDecorationBreak: "clone", WebkitBoxDecorationBreak: "clone" }}>{t(p.b)}</span>
                 : <span style={{ color: C.cblue }}>{t(p.b)}</span>}
        </div>
        <div style={{ fontFamily: BODY, fontSize: 34, color: C.mut, marginTop: 18, lineHeight: 1.3 }}>{t(p.sub)}</div>
      </div>
    </div>
  );
};

/* ---------- frame: top bar, stage tracker, footer ---------- */
const Frame: React.FC = () => {
  const f = useCurrentFrame();
  const trackIn = ramp(f, T.edit, T.edit + 12) * interpolate(f, [T.save - 4, T.save + 6], [1, 0], clamp);
  const starts = [T.edit, T.soc, T.web, T.nl, T.brief, T.poster];
  const cur = f >= T.sys && f < T.soc ? -1 : starts.reduce((acc, s, i) => (f >= s ? i : acc), -1);
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 0, right: 0, top: 0, height: 96, borderBottom: `3px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 80px" }}>
        <span style={{ background: C.neon, color: C.ink, fontFamily: HEAD, fontWeight: 700, fontSize: 34, padding: "8px 16px", lineHeight: 1 }}>CREOX.</span>
        <span style={{ fontFamily: LABEL, fontSize: 24, letterSpacing: "0.08em", color: C.mut2, textTransform: "uppercase" }}>Marketing-Maschine</span>
      </div>
      {/* stage tracker: shows the order of the channels */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 1166, display: "flex", gap: 10, opacity: trackIn }}>
        {STAGES.map((s, i) => {
          const done = f >= STAGE_DONE[i];
          const active = i === cur;
          return (
            <div key={s} style={{ flex: 1, border: `3px solid ${C.ink}`, background: done ? C.neon : active ? C.white : "transparent",
              color: done || active ? C.ink : C.mut2, fontFamily: LABEL, fontWeight: 700, fontSize: 17, textTransform: "uppercase", letterSpacing: "0",
              padding: "10px 0", textAlign: "center", whiteSpace: "nowrap" }}>
              {done ? "✓ " : ""}{s}
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 0, right: 0, top: 1254, height: 96, borderTop: `3px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "space-between", padding: "0 80px" }}>
        <span style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 34, color: C.ink }}>creox.ch</span>
        <span style={{ fontFamily: LABEL, fontSize: 24, letterSpacing: "0.08em", color: C.mut2, textTransform: "uppercase" }}>Built with Claude</span>
      </div>
    </AbsoluteFill>
  );
};

/* ---------- cursor ---------- */
const Cursor: React.FC<{ x: number; y: number; down: boolean; opacity: number }> = ({ x, y, down, opacity }) => (
  <svg width="54" height="54" viewBox="0 0 24 24" style={{ position: "absolute", left: x, top: y, opacity, transform: `scale(${down ? 0.85 : 1})`, transformOrigin: "0 0" }}>
    <path d="M4 2 L4 20 L9 15 L12.5 22 L15.5 20.6 L12 14 L19 14 Z" fill={C.ink} stroke={C.white} strokeWidth="1.3" strokeLinejoin="round" />
  </svg>
);

const CENTER = { x: 540, y: 800 };

/* ---------- scene 0: upload photo + video ---------- */
const FileCard: React.FC<{ src: string; video?: boolean; w: number; h: number }> = ({ src, video, w, h }) => (
  <div style={{ position: "relative", width: w, height: h, border: `4px solid ${C.ink}`, boxShadow: `12px 12px 0 ${C.ink}`, background: C.ink, overflow: "hidden" }}>
    <Img src={staticFile(src)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: video ? "brightness(.75)" : "none" }} />
    {video && (
      <>
        <div style={{ position: "absolute", left: "50%", top: "50%", width: 84, height: 84, marginLeft: -42, marginTop: -42, background: C.neon, border: `3px solid ${C.ink}`,
          display: "flex", alignItems: "center", justifyContent: "center" }}>
          <div style={{ width: 0, height: 0, borderTop: "18px solid transparent", borderBottom: "18px solid transparent", borderLeft: `30px solid ${C.ink}`, marginLeft: 8 }} />
        </div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, padding: "8px 14px", background: C.ink, color: C.white, fontFamily: LABEL, fontSize: 22, display: "flex", justifyContent: "space-between" }}>
          <span>4K · 2,3 GB</span><span>03:42</span>
        </div>
      </>
    )}
  </div>
);

const Upload: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f > T.edit + 6) return null;
  const boxIn = ramp(f, 4, 14);
  const out = interpolate(f, [T.edit - 4, T.edit + 4], [1, 0], clamp);
  const flyA = spring({ frame: f - 6, fps, config: { damping: 16, stiffness: 130 } });
  const flyB = spring({ frame: f - 11, fps, config: { damping: 16, stiffness: 130 } });
  const ax = interpolate(flyA, [0, 1], [-420, CENTER.x - 300]), ay = interpolate(flyA, [0, 1], [1200, CENTER.y - 150]);
  const bx = interpolate(flyB, [0, 1], [1100, CENTER.x + 10]), by = interpolate(flyB, [0, 1], [1220, CENTER.y - 110]);
  const dropped = f >= T.drop;
  const prog = ramp(f, T.drop, T.drop + 16);
  const cx = bx + 260, cy = by + 170;
  const curOp = interpolate(f, [8, 12, T.drop + 4, T.drop + 10], [0, 1, 1, 0], clamp);
  const W = 640, H = 420;
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <div style={{ position: "absolute", left: CENTER.x - W / 2, top: CENTER.y - H / 2, width: W, height: H, opacity: boxIn,
        border: dropped ? `3px solid ${C.ink}` : `3px dashed ${C.mut2}`, background: dropped ? C.ink : C.white,
        boxShadow: dropped ? `10px 10px 0 ${C.ink}` : "none", overflow: "hidden" }}>
        {!dropped && (
          <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 10, color: C.mut, fontFamily: LABEL, fontWeight: 700, fontSize: 30, textTransform: "uppercase", letterSpacing: "0.04em" }}>
            <div style={{ fontFamily: HEAD, fontSize: 90, lineHeight: 1, color: C.cblue }}>+</div>{t("Foto oder Video hierher")}
          </div>
        )}
        {dropped && (
          <div style={{ position: "absolute", inset: 0, display: "flex", gap: 3 }}>
            {[["img/hall.jpg", "eroeffnung.jpg", false], ["img/racers.jpg", "rohmaterial.mov", true]].map(([src, name, vid]) => (
              <div key={name as string} style={{ flex: 1, position: "relative" }}>
                <Img src={staticFile(src as string)} style={{ width: "100%", height: "100%", objectFit: "cover", filter: vid ? "brightness(.75)" : "none" }} />
                {vid && <div style={{ position: "absolute", right: 12, top: 12, background: C.neon, color: C.ink, fontFamily: LABEL, fontWeight: 700, fontSize: 20, padding: "4px 8px" }}>4K · 2,3 GB</div>}
                <div style={{ position: "absolute", left: 0, right: 0, bottom: 0, background: C.ink, color: C.white, fontFamily: LABEL, fontSize: 21, padding: "10px 14px" }}>
                  <div style={{ display: "flex", justifyContent: "space-between" }}><span>{name as string}</span><span style={{ color: C.neon }}>{prog >= 1 ? "✓" : `${Math.round(prog * 100)}%`}</span></div>
                  <div style={{ height: 6, background: "#333", marginTop: 6 }}><div style={{ height: 6, width: `${prog * 100}%`, background: C.neon }} /></div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      {!dropped && (
        <>
          <div style={{ position: "absolute", left: ax, top: ay, transform: `rotate(${interpolate(flyA, [0, 1], [-12, -3])}deg)` }}><FileCard src="img/hall.jpg" w={420} h={280} /></div>
          <div style={{ position: "absolute", left: bx, top: by, transform: `rotate(${interpolate(flyB, [0, 1], [14, 3])}deg)` }}><FileCard src="img/racers.jpg" video w={420} h={280} /></div>
        </>
      )}
      <Cursor x={cx} y={cy} down={f > 12 && f < T.drop} opacity={curOp} />
    </AbsoluteFill>
  );
};

/* ---------- scene 0b: automatic video edit in the brand's template ---------- */
const SEGS = [
  { a: 0, b: 0.14, keep: true, img: "img/hall.jpg" },
  { a: 0.14, b: 0.36, keep: false, img: "img/racers.jpg" },
  { a: 0.36, b: 0.52, keep: true, img: "img/fmx.jpg" },
  { a: 0.52, b: 0.74, keep: false, img: "img/ducati.jpg" },
  { a: 0.74, b: 1, keep: true, img: "img/party.jpg" },
];
const PACKED = (() => { let x = 0; return SEGS.map((s) => { const p = x; if (s.keep) x += s.b - s.a; return p; }); })();
const PACK_LEN = SEGS.filter((s) => s.keep).reduce((acc, s) => acc + s.b - s.a, 0);

const Edit: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.edit - 4 || f >= T.sys + 6) return null;
  const E = f - T.edit;
  const inn = spring({ frame: E, fps, config: { damping: 18, stiffness: 120 } });
  const out = interpolate(f, [T.sys - 6, T.sys + 4], [1, 0], clamp);
  const pk = ramp(E, ED.pack[0], ED.pack[1]);
  const packed = E >= ED.pack[1];
  // playhead: sweeps the raw clip, then loops over the finished cut
  const ph = E < ED.pack[0] ? interpolate(E, [6, ED.pack[0]], [0, 0.999], clamp)
    : E < ED.pack[1] + 2 ? 0 : interpolate(E, [ED.pack[1] + 2, 118], [0, PACK_LEN - 0.001], clamp);
  const segX = (i: number) => SEGS[i].a + (PACKED[i] - SEGS[i].a) * pk;
  const segW = (i: number) => (SEGS[i].b - SEGS[i].a) * (SEGS[i].keep ? 1 : 1 - pk);
  const under = SEGS.findIndex((s, i) => {
    if (!packed) return ph >= s.a && ph < s.b;
    return s.keep && ph >= PACKED[i] && ph < PACKED[i] + (s.b - s.a);
  });
  const cur = SEGS[Math.max(0, under)];
  const local = packed ? ph - PACKED[Math.max(0, under)] : ph - cur.a;
  const cutIdx = ED.cuts.filter((c) => E >= c).length;
  const flash = ED.cuts.some((c) => E >= c && E < c + 3) ? 0.6 : 0;
  const subIn = ramp(E, ED.sub, ED.sub + 6), logo = spring({ frame: E - ED.logo, fps, config: { damping: 10, stiffness: 200 } }), tag = ramp(E, ED.tag, ED.tag + 6);
  const PW = 560, PH_ = 315, TX = 180, TW = 800, TOP = 890;
  const checks: [string, number][] = [["Schnitt", 0], ["Untertitel DE/EN", 1], ["Logo & Overlays", 2], ["Musik", 3], ["Formate", 4]];
  const cutPos = [0.14, 0.36, 0.52, 0.74];
  return (
    <AbsoluteFill style={{ opacity: out }}>
      {/* preview monitor */}
      <div style={{ position: "absolute", left: 80, top: interpolate(inn, [0, 1], [1300, 540]), width: PW, height: PH_, border: `3px solid ${C.ink}`, boxShadow: `10px 10px 0 ${C.ink}`, overflow: "hidden", background: C.night }}>
        <Img src={staticFile(cur.img)} style={{ position: "absolute", inset: 0, width: "100%", height: "100%", objectFit: "cover", transform: `scale(${1.04 + local * 0.6})`, filter: "brightness(.8)" }} />
        <div style={{ position: "absolute", inset: 0, background: C.white, opacity: flash }} />
        <div style={{ position: "absolute", right: 10, top: 10, background: packed ? C.neon : C.ink, color: packed ? C.ink : C.white, fontFamily: LABEL, fontWeight: 700, fontSize: 17, padding: "3px 8px" }}>
          {packed ? "REEL · 00:30" : "ROH · 4K · 03:42"}
        </div>
        <div style={{ position: "absolute", left: 14, top: 14, transform: `scale(${E >= ED.logo ? logo : 0})`, transformOrigin: "0 0" }}><Logo s={20} /></div>
        <div style={{ position: "absolute", left: 14, top: 168, opacity: tag, transform: `translateX(${(1 - tag) * -20}px)`, background: C.yellow, color: C.navy, fontFamily: BRAND, fontWeight: 700, fontSize: 24, padding: "2px 10px", whiteSpace: "nowrap" }}>19.–21. FEBRUAR</div>
        <div style={{ position: "absolute", left: 0, right: 0, bottom: 16, textAlign: "center", opacity: subIn, transform: `translateY(${(1 - subIn) * 12}px)` }}>
          <span style={{ background: "rgba(10,25,41,.85)", color: C.white, fontFamily: BRAND, fontWeight: 700, fontSize: 25, padding: "4px 12px" }}>{t("Saisonstart 2027: wir sind zurück.")}</span>
          <div style={{ marginTop: 6 }}><span style={{ background: "rgba(10,25,41,.85)", color: "#cfd8e6", fontFamily: BRAND, fontSize: 18, padding: "2px 10px" }}>Season opener 2027: we’re back.</span></div>
        </div>
      </div>
      {/* template + checklist */}
      <div style={{ position: "absolute", left: 670, top: 540, width: 330, opacity: inn }}>
        <div style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 18, color: C.cblue, textTransform: "uppercase", marginBottom: 10, whiteSpace: "nowrap" }}>Vorlage: Ihre Marke</div>
        {checks.map(([label, i]) => {
          const done = E >= ED.done[i];
          const k = spring({ frame: E - ED.done[i], fps, config: { damping: 10, stiffness: 220 } });
          return (
            <div key={label} style={{ height: 46, marginBottom: 8, border: `3px solid ${C.ink}`, background: done ? C.neon : C.white, display: "flex", alignItems: "center", gap: 10, padding: "0 12px",
              fontFamily: LABEL, fontWeight: 700, fontSize: 19, textTransform: "uppercase", color: C.ink, whiteSpace: "nowrap" }}>
              <span style={{ width: 22, textAlign: "center", fontFamily: HEAD, transform: `scale(${done ? k : 1})` }}>{done ? "✓" : "·"}</span>{label}
              {i === 4 && (
                <span style={{ marginLeft: "auto", display: "flex", alignItems: "flex-end", gap: 6 }}>
                  {[[13, 23], [18, 23], [30, 17]].map(([w, h], j) => (
                    <span key={j} style={{ width: w, height: h, border: `2px solid ${C.ink}`, background: E >= ED.fmt[j] ? C.ink : "transparent", transform: `scale(${E >= ED.fmt[j] ? 1 : 0.4})`, opacity: E >= ED.fmt[j] ? 1 : 0.3 }} />
                  ))}
                </span>
              )}
            </div>
          );
        })}
      </div>
      {/* timeline */}
      <div style={{ position: "absolute", left: 80, top: interpolate(inn, [0, 1], [1400, TOP]), width: 920, height: 250, border: `3px solid ${C.ink}`, background: C.white, overflow: "hidden" }}>
        <div style={{ position: "absolute", left: 16, right: 16, top: 10, display: "flex", justifyContent: "space-between", fontFamily: LABEL, fontWeight: 700, fontSize: 18, textTransform: "uppercase", color: C.mut2 }}>
          <span>Timeline · automatisch</span><span style={{ color: packed ? C.ink : C.mut2 }}>{packed ? "03:42 → 00:30" : "03:42"}</span>
        </div>
        {[["V1", 52, 58], ["T1", 122, 40], ["A1", 174, 50]].map(([n, y, h]) => (
          <div key={n as string} style={{ position: "absolute", left: 16, top: (y as number) + (h as number) / 2 - 12, fontFamily: LABEL, fontWeight: 700, fontSize: 20, color: C.ink }}>{n as string}</div>
        ))}
        {/* V1: clip segments */}
        {SEGS.map((s, i) => {
          const dropOn = !s.keep && cutIdx >= (i === 1 ? 2 : 4);
          return (
            <div key={i} style={{ position: "absolute", top: 52, height: 58, left: TX - 80 + segX(i) * TW, width: segW(i) * TW, overflow: "hidden", opacity: s.keep ? 1 : 1 - pk,
              borderRight: s.keep ? `2px solid ${C.ink}` : "none", background: `url(${staticFile(s.img)}) center/cover`, filter: dropOn ? "grayscale(1) brightness(.7)" : "none" }}>
              {dropOn && <div style={{ position: "absolute", inset: 0, background: `repeating-linear-gradient(45deg, rgba(193,13,13,.55) 0 8px, transparent 8px 16px)` }} />}
              {dropOn && <div style={{ position: "absolute", left: 6, top: 4, fontFamily: LABEL, fontWeight: 700, fontSize: 15, color: C.white, background: C.red, padding: "1px 5px" }}>RAUS</div>}
            </div>
          );
        })}
        {cutPos.map((x, i) => (
          <div key={i} style={{ position: "absolute", left: TX - 80 + x * TW - 2, top: 44, width: 4, height: 74, background: C.red, opacity: E >= ED.cuts[i] ? 1 - pk : 0,
            transform: `scaleY(${E >= ED.cuts[i] ? ramp(E, ED.cuts[i], ED.cuts[i] + 3) : 0})` }} />
        ))}
        {/* T1: subtitles */}
        {SEGS.map((s, i) => s.keep && (
          <div key={i} style={{ position: "absolute", top: 122, height: 40, left: TX - 80 + PACKED[i] * TW + 2, width: (s.b - s.a) * TW - 4, background: C.cblue, color: C.white,
            fontFamily: LABEL, fontSize: 15, display: "flex", alignItems: "center", padding: "0 8px", whiteSpace: "nowrap", overflow: "hidden",
            opacity: ramp(E, ED.sub + i * 2, ED.sub + i * 2 + 5) }}>DE / EN</div>
        ))}
        {/* A1: music waveform */}
        <div style={{ position: "absolute", top: 174, height: 50, left: TX - 80, width: PACK_LEN * TW * ramp(E, ED.music, ED.music + 10), overflow: "hidden", display: "flex", alignItems: "center", gap: 3 }}>
          {Array.from({ length: 64 }).map((_, j) => (
            <span key={j} style={{ flex: "none", width: 4, height: 8 + Math.abs(Math.sin(j * 1.7) * 30 + Math.sin(j * 0.45) * 10), background: C.ink }} />
          ))}
        </div>
        {/* playhead */}
        <div style={{ position: "absolute", top: 40, height: 200, width: 3, background: C.cblue, left: TX - 80 + ph * TW, opacity: E >= ED.pack[0] && E < ED.pack[1] + 2 ? 0 : 1 }} />
      </div>
    </AbsoluteFill>
  );
};

/* ---------- scene 0c: system builds + approve ---------- */
const System: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.sys - 4 || f > T.soc + 8) return null;
  const nodeIn = spring({ frame: f - T.sys, fps, config: { damping: 14, stiffness: 140 } });
  const out = interpolate(f, [T.soc - 2, T.soc + 8], [1, 0], clamp);
  const pulse = f >= T.soc - 4 ? spring({ frame: f - (T.soc - 4), fps, config: { damping: 12 } }) : 0;
  const W = 340, H = 300;
  const chipLabels = ["Designsystem der Marke", "Texte DE/EN · Claude", "Alle Formate"];
  const btnIn = ramp(f, T.chips[2] + 4, T.chips[2] + 12);
  const clicked = f >= T.click;
  const cx = interpolate(f, [T.sys + 4, T.click - 8], [900, 330], { ...clamp, easing: ease });
  const cy = interpolate(f, [T.sys + 4, T.click - 8], [1150, CENTER.y + 245], { ...clamp, easing: ease });
  const curOp = interpolate(f, [T.sys + 4, T.sys + 10, T.click + 6, T.click + 12], [0, 1, 1, 0], clamp);
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <div style={{ position: "absolute", left: CENTER.x - W / 2, top: CENTER.y - H / 2, width: W, height: H, background: C.ink, border: `3px solid ${C.ink}`, boxShadow: `10px 10px 0 ${C.ink}`,
        transform: `scale(${interpolate(nodeIn, [0, 1], [0.6, 1]) + pulse * 0.08})`, opacity: nodeIn, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <div style={{ background: C.neon, color: C.ink, fontFamily: HEAD, fontWeight: 700, fontSize: 56, padding: "8px 18px", lineHeight: 1 }}>CREOX.</div>
        <div style={{ color: C.white, fontFamily: LABEL, fontSize: 26, marginTop: 16, letterSpacing: "0.06em" }}>CLAUDE + MCP</div>
        <div style={{ display: "flex", gap: 8, marginTop: 22 }}>
          {["img/hall.jpg", "img/fmx.jpg"].map((s, i) => (
            <div key={s} style={{ position: "relative", width: 96, height: 64, border: `2px solid ${C.neon}` }}>
              <Img src={staticFile(s)} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
              {i === 1 && <div style={{ position: "absolute", right: 0, bottom: 0, background: C.neon, fontFamily: LABEL, fontSize: 12, fontWeight: 700, padding: "0 4px" }}>REEL</div>}
            </div>
          ))}
        </div>
      </div>
      {chipLabels.map((c, i) => {
        const k = ramp(f, T.chips[i], T.chips[i] + 8);
        const pos = [{ x: 80, y: CENTER.y - 255 }, { x: 600, y: CENTER.y - 255 }, { x: 640, y: CENTER.y + 205 }][i];
        return (
          <div key={c} style={{ position: "absolute", left: pos.x, top: pos.y, opacity: k, transform: `translateY(${(1 - k) * 20}px)`,
            background: C.white, border: `3px solid ${C.ink}`, color: C.ink, fontFamily: LABEL, fontWeight: 700, fontSize: 25, textTransform: "uppercase",
            padding: "12px 18px", display: "flex", gap: 12, alignItems: "center" }}>
            <span style={{ width: 18, height: 18, background: C.cblue, display: "inline-block" }} />{t(c)}
          </div>
        );
      })}
      <div style={{ position: "absolute", left: 120, top: CENTER.y + 200, opacity: btnIn, transform: `scale(${clicked ? 0.95 : 1})`,
        background: clicked ? C.neon : C.cblue, color: clicked ? C.ink : C.white, border: `3px solid ${C.ink}`, fontFamily: LABEL, fontWeight: 700, fontSize: 32,
        textTransform: "uppercase", letterSpacing: "0.05em", padding: "18px 32px" }}>
        {clicked ? "✓ Freigegeben" : "Freigeben"}
      </div>
      <Cursor x={cx} y={cy} down={f >= T.click - 2 && f < T.click + 4} opacity={curOp} />
    </AbsoluteFill>
  );
};

/* ---------- MOTO-ZÜRICH mockup bits ---------- */
const PH: React.FC<{ h: number | string; dim?: number; src?: string; pos?: string }> = ({ h, dim = 1, src = "img/hall.jpg", pos = "center" }) => (
  <Img src={staticFile(src)} style={{ width: "100%", height: h, objectFit: "cover", objectPosition: pos, display: "block", filter: `brightness(${dim})` }} />
);
const Title: React.FC<{ s: number; c?: string; children: React.ReactNode }> = ({ s, c = C.navy, children }) => (
  <div style={{ fontFamily: BRAND, fontWeight: 700, fontSize: s, lineHeight: 1, textTransform: "uppercase", color: c, letterSpacing: "-0.01em" }}>{children}</div>
);
const Logo: React.FC<{ c?: string; s?: number }> = ({ c = C.white, s = 13 }) => (
  <div style={{ fontFamily: BRAND, fontWeight: 700, fontSize: s, letterSpacing: "0.08em", color: c, lineHeight: 1 }}>MOTO<br />ZÜRICH</div>
);
const Line: React.FC<{ w: string; c?: string; h?: number }> = ({ w, c = "#d9d9d9", h = 7 }) => <div style={{ height: h, width: w, background: c, marginTop: 6 }} />;
const Check: React.FC<{ k: number; size?: number; style?: React.CSSProperties }> = ({ k, size = 44, style }) => (
  <div style={{ position: "absolute", width: size, height: size, background: C.neon, color: C.ink, border: `3px solid ${C.ink}`, display: "flex", alignItems: "center",
    justifyContent: "center", fontFamily: HEAD, fontWeight: 700, fontSize: size * 0.56, transform: `scale(${k})`, ...style }}>✓</div>
);

/* vertical video frame (Reels / TikTok / Shorts) — generic UI, no platform logos */
const Vertical: React.FC<{ src: string; dim?: number; title: string; tag: string }> = ({ src, dim = 0.55, title, tag }) => (
  <div style={{ position: "relative", height: "100%", background: C.night }}>
    <PH h="100%" dim={dim} src={src} />
    <div style={{ position: "absolute", inset: 0, padding: 12, display: "flex", flexDirection: "column" }}>
      <Logo s={11} />
      <div style={{ marginTop: "auto", paddingRight: 30 }}>
        <Title s={19} c="#fff">{title}</Title>
        <div style={{ fontFamily: BRAND, fontWeight: 700, fontSize: 24, color: C.yellow, marginTop: 4, whiteSpace: "nowrap" }}>19.–21.</div>
        <div style={{ fontFamily: UI, fontSize: 10, color: "#ddd", marginTop: 6 }}>{tag}</div>
      </div>
      <div style={{ position: "absolute", right: 8, bottom: 40, display: "flex", flexDirection: "column", gap: 10 }}>
        {[0, 1, 2].map((i) => <span key={i} style={{ width: 18, height: 18, borderRadius: 9, border: "2px solid #fff" }} />)}
      </div>
    </div>
  </div>
);

const FEED: { label: string; el: React.ReactNode }[] = [
  { label: "Instagram", el: (
    <div style={{ background: "#fff", height: "100%" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 8px", fontFamily: UI, fontWeight: 700, fontSize: 11 }}>
        <span style={{ width: 18, height: 18, borderRadius: 9, background: C.blue }} />motozuerich</div>
      <div style={{ position: "relative" }}><PH h={180} />
        <div style={{ position: "absolute", left: 8, bottom: 10 }}><span style={{ background: C.yellow, padding: "2px 5px", fontFamily: BRAND, fontWeight: 700, fontSize: 17, color: C.navy, textTransform: "uppercase" }}>Saisonstart 2027</span></div>
      </div>
      <div style={{ padding: "6px 8px", fontFamily: UI, fontSize: 11, color: "#333" }}>♡  ○  ▷</div>
    </div>) },
  { label: "Reels", el: <Vertical src="img/racers.jpg" title="Saisonstart 2027" tag="#motozuerich" /> },
  { label: "TikTok", el: <Vertical src="img/fmx.jpg" dim={0.6} title="Vollgas im Februar" tag="StageOne · Halle 550" /> },
  { label: "YouTube", el: <Vertical src="img/party.jpg" title="So war 2026" tag="Shorts · 0:15" /> },
  { label: "Facebook", el: (
    <div style={{ background: "#fff", height: "100%", padding: 9 }}>
      <div style={{ display: "flex", gap: 6, alignItems: "center", fontFamily: UI, fontWeight: 700, fontSize: 11 }}><span style={{ width: 20, height: 20, borderRadius: 10, background: C.blue }} />MOTO-ZÜRICH</div>
      <div style={{ fontFamily: UI, fontSize: 11, color: "#333", margin: "8px 0", lineHeight: 1.35 }}>Save the Date: 19.–21. Februar 2027 in Zürich-Oerlikon.</div>
      <PH h={130} /><Line w="80%" /><Line w="55%" />
    </div>) },
  { label: "LinkedIn", el: (
    <div style={{ background: "#fff", height: "100%", padding: 9 }}>
      <div style={{ display: "flex", gap: 6, alignItems: "center", fontFamily: UI, fontWeight: 700, fontSize: 10 }}><span style={{ width: 20, height: 20, background: C.blue }} />Creox GmbH</div>
      <div style={{ fontFamily: UI, fontSize: 10.5, color: "#333", margin: "8px 0", lineHeight: 1.35 }}>Aussteller und Partner: MOTO-ZÜRICH 2027, 19.–21. Februar.</div>
      <PH h={120} src="img/racers.jpg" /><Line w="70%" /><Line w="45%" />
    </div>) },
];

const TILES: [string, string][] = [["IG", "Instagram"], ["FB", "Facebook"], ["IN", "LinkedIn"], ["TT", "TikTok"], ["YT", "YouTube"], ["TG", "Telegram"], ["WA", "WhatsApp"], ["PI", "Pinterest"]];

/* ---------- scene 1: social ---------- */
const Social: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.soc || f >= T.web + 6) return null;
  const out = interpolate(f, [T.web - 6, T.web + 4], [1, 0], clamp);
  const CW = 142, CH = 270, GAP = 14, X0 = (1080 - (6 * CW + 5 * GAP)) / 2, Y = 570;
  return (
    <AbsoluteFill style={{ opacity: out, transform: `translateY(${(1 - out) * -30}px)` }}>
      {FEED.map((m, i) => {
        const st = SOC_CARD(i);
        if (f < st) return null;
        const s = spring({ frame: f - st, fps, config: { damping: 15, stiffness: 150, mass: 0.8 } });
        const x = interpolate(s, [0, 1], [CENTER.x - CW / 2, X0 + i * (CW + GAP)]);
        const y = interpolate(s, [0, 1], [CENTER.y - CH / 2, Y]);
        const k = spring({ frame: f - st - 12, fps, config: { damping: 10, stiffness: 200 } });
        return (
          <div key={m.label} style={{ position: "absolute", left: x, top: y, width: CW, transform: `scale(${interpolate(s, [0, 1], [0.2, 1])}) rotate(${interpolate(s, [0, 1], [(i % 2 ? 14 : -14), 0])}deg)` }}>
            <div style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 19, textTransform: "uppercase", color: C.ink, marginBottom: 10, whiteSpace: "nowrap" }}>{m.label}</div>
            <div style={{ width: CW, height: CH, overflow: "hidden", border: `3px solid ${C.ink}`, boxShadow: `7px 7px 0 ${C.ink}`, position: "relative" }}>{m.el}</div>
            <Check k={f >= st + 12 ? k : 0} size={40} style={{ right: -12, top: 26 }} />
          </div>
        );
      })}
      {/* channel tiles */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 940, display: "flex", justifyContent: "space-between" }}>
        {TILES.map(([mono, name], i) => {
          const st = SOC_TILE(i);
          const s = spring({ frame: f - st, fps, config: { damping: 11, stiffness: 180 } });
          const live = f >= st + 8;
          return (
            <div key={mono} style={{ width: 104, height: 104, position: "relative", transform: `scale(${f >= st ? s : 0})`, border: `3px solid ${C.ink}`,
              background: live ? C.ink : C.white, color: live ? C.neon : C.ink, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
              <div style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 40, lineHeight: 1 }}>{mono}</div>
              <div style={{ fontFamily: LABEL, fontSize: 13, marginTop: 6, color: live ? C.white : C.mut2 }}>{name}</div>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 80, top: 1080, fontFamily: LABEL, fontWeight: 700, fontSize: 28, textTransform: "uppercase", color: C.ink,
        opacity: ramp(f, SOC_TILE(7), SOC_TILE(7) + 8) }}>
        <span style={{ fontFamily: HEAD, fontSize: 52, color: C.cblue, marginRight: 14 }}>8</span>{t("Kanäle live · in 2,4 Sekunden")}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- scene 2: website ---------- */
const Website: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.web - 4 || f >= T.nl + 6) return null;
  const s = spring({ frame: f - T.web, fps, config: { damping: 18, stiffness: 110 } });
  const out = interpolate(f, [T.nl - 6, T.nl + 4], [1, 0], clamp);
  const scroll = interpolate(f, [T.web + 24, T.web + 60], [0, -120], { ...clamp, easing: ease });
  const badge = spring({ frame: f - (T.web + 20), fps, config: { damping: 9, stiffness: 200 } });
  const k = spring({ frame: f - (T.web + 44), fps, config: { damping: 10, stiffness: 200 } });
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <div style={{ position: "absolute", left: 80, top: interpolate(s, [0, 1], [1300, 540]), width: 920, height: 580, border: `3px solid ${C.ink}`, boxShadow: `12px 12px 0 ${C.ink}`, background: "#fff", overflow: "hidden" }}>
        <div style={{ height: 52, background: C.paper2, borderBottom: `3px solid ${C.ink}`, display: "flex", alignItems: "center", gap: 10, padding: "0 18px" }}>
          {[0, 1, 2].map((i) => <span key={i} style={{ width: 14, height: 14, borderRadius: 7, background: "#bdbdb8" }} />)}
          <span style={{ marginLeft: 14, flex: 1, background: "#fff", border: `2px solid ${C.ink}`, padding: "4px 14px", fontFamily: LABEL, fontSize: 20, color: C.mut }}>motozuerich.ch/news/saisonstart-2027</span>
        </div>
        <div style={{ transform: `translateY(${scroll}px)` }}>
          <div style={{ background: C.navy, padding: "14px 24px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <Logo s={20} />
            <div style={{ display: "flex", gap: 22, fontFamily: BRAND, fontWeight: 600, fontSize: 17, color: "#fff", textTransform: "uppercase" }}><span>Programm</span><span>Aussteller</span><span style={{ background: C.red, padding: "4px 10px" }}>Tickets</span></div>
          </div>
          <div style={{ position: "relative" }}>
            <PH h={330} />
            <div style={{ position: "absolute", left: 24, top: 22, transform: `scale(${f >= T.web + 20 ? badge : 0})`, background: C.yellow, color: C.navy, fontFamily: BRAND, fontWeight: 700, fontSize: 22, padding: "4px 12px" }}>NEU</div>
          </div>
          <div style={{ padding: "22px 28px" }}>
            <div style={{ fontFamily: MONO, fontSize: 16, color: C.blue }}>NEWS · DE / EN</div>
            <Title s={46}>Saisonstart 2027</Title>
            <div style={{ fontFamily: BRAND, fontSize: 22, color: "#4a5570", marginTop: 10 }}>19.–21. Februar 2027 · StageOne & Halle 550 · Zürich-Oerlikon</div>
            <Line w="92%" h={10} c="#e5e5e1" /><Line w="86%" h={10} c="#e5e5e1" /><Line w="64%" h={10} c="#e5e5e1" />
          </div>
        </div>
      </div>
      <Check k={f >= T.web + 44 ? k : 0} size={56} style={{ left: 960, top: 520 }} />
    </AbsoluteFill>
  );
};

/* ---------- scene 3: newsletter (mail app) ---------- */
const Newsletter: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.nl - 4 || f >= T.brief + 6) return null;
  const s = spring({ frame: f - T.nl, fps, config: { damping: 18, stiffness: 110 } });
  const out = interpolate(f, [T.brief - 6, T.brief + 4], [1, 0], clamp);
  const row = spring({ frame: f - (T.nl + 16), fps, config: { damping: 14, stiffness: 160 } });
  const open = ramp(f, T.nl + 32, T.nl + 46);
  const k = spring({ frame: f - (T.nl + 50), fps, config: { damping: 10, stiffness: 200 } });
  const others = ["Ihr Wochenrückblick", "Rechnung Oktober", "Einladung Vernissage"];
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <div style={{ position: "absolute", left: 80, top: interpolate(s, [0, 1], [1300, 540]), width: 920, height: 580, border: `3px solid ${C.ink}`, boxShadow: `12px 12px 0 ${C.ink}`, background: "#fff", overflow: "hidden", display: "flex" }}>
        <div style={{ width: 380, borderRight: `3px solid ${C.ink}`, background: C.paper }}>
          <div style={{ padding: "14px 18px", borderBottom: `3px solid ${C.ink}`, fontFamily: LABEL, fontWeight: 700, fontSize: 22, textTransform: "uppercase" }}>Posteingang</div>
          <div style={{ height: interpolate(row, [0, 1], [0, 96]), overflow: "hidden" }}>
            <div style={{ padding: "14px 18px", background: open > 0.5 ? "#e6eafb" : "#fff", borderBottom: "2px solid #ddd", display: "flex", gap: 12 }}>
              <span style={{ width: 14, height: 14, borderRadius: 7, background: C.cblue, marginTop: 8, flex: "none" }} />
              <div><div style={{ fontFamily: UI, fontWeight: 700, fontSize: 21 }}>MOTO-ZÜRICH</div><div style={{ fontFamily: UI, fontSize: 18, color: C.mut }}>Saisonstart 2027: Save the Date</div></div>
            </div>
          </div>
          {others.map((o) => (
            <div key={o} style={{ padding: "14px 18px 14px 44px", borderBottom: "2px solid #ddd" }}>
              <div style={{ fontFamily: UI, fontSize: 19, color: C.mut2 }}>{o}</div><Line w="70%" c="#e1e1dc" />
            </div>
          ))}
        </div>
        <div style={{ flex: 1, background: "#ecebe6", padding: 22, opacity: open, transform: `translateX(${(1 - open) * 40}px)` }}>
          <div style={{ fontFamily: UI, fontSize: 16, color: C.mut, marginBottom: 12 }}><b>Betreff:</b> Saisonstart 2027: Save the Date</div>
          <div style={{ background: "#fff", textAlign: "center", paddingBottom: 20 }}>
            <div style={{ background: C.navy, padding: "10px 0" }}><Logo s={14} /></div>
            <PH h={170} />
            <div style={{ padding: "16px 12px 6px" }}><Title s={34}>Saisonstart 2027</Title></div>
            <div style={{ fontFamily: BRAND, fontSize: 18, color: "#4a5570" }}>19.–21. Februar · StageOne & Halle 550</div>
            <div style={{ display: "inline-block", marginTop: 14, background: C.red, color: "#fff", fontFamily: BRAND, fontWeight: 700, fontSize: 16, padding: "8px 16px" }}>TICKETS SICHERN</div>
          </div>
        </div>
      </div>
      <Check k={f >= T.nl + 50 ? k : 0} size={56} style={{ left: 960, top: 520 }} />
      <div style={{ position: "absolute", right: 80, top: 1100, opacity: open, fontFamily: LABEL, fontWeight: 700, fontSize: 24, textTransform: "uppercase", background: C.ink, color: C.neon, padding: "8px 14px" }}>Geplant: Fr 18:00</div>
    </AbsoluteFill>
  );
};

/* ---------- scene 4: paper letter into envelope, envelope flies like paper ---------- */
const Brief: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.brief - 4 || f >= T.poster + 4) return null;
  const L = f - T.brief;
  const paperIn = spring({ frame: L, fps, config: { damping: 18, stiffness: 120 } });
  const envIn = spring({ frame: L - 14, fps, config: { damping: 16, stiffness: 120 } });
  const slide = ramp(f, T.brief + 26, T.brief + 42);          // letter slides down into envelope
  const flap = ramp(f, T.brief + 42, T.brief + 50);           // flap closes
  const stamp = spring({ frame: L - 52, fps, config: { damping: 9, stiffness: 220 } });
  const flyT = interpolate(L, [62, 84], [0, 1], { ...clamp, easing: Easing.in(Easing.cubic) });
  const ex = interpolate(flyT, [0, 1], [0, 900]), ey = interpolate(flyT, [0, 1], [0, -260]) + Math.sin(L / 3) * 18 * flyT;
  const erot = flyT * 22 + Math.sin(L / 2.5) * 6 * flyT;
  const envX = 230, envY = 800, envW = 620, envH = 300;
  const paperY = interpolate(paperIn, [0, 1], [1400, 470]) + slide * 330;
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", inset: 0, transform: `translate(${ex}px, ${ey}px) rotate(${erot}deg)`, transformOrigin: "540px 950px" }}>
        {/* envelope back */}
        <div style={{ position: "absolute", zIndex: 1, left: envX, top: envY + (1 - envIn) * 600, width: envW, height: envH, background: "#e9e6dc", border: `3px solid ${C.ink}` }} />
        {/* letter */}
        <div style={{ position: "absolute", zIndex: 3, left: envX + 50, top: paperY, width: envW - 100, height: 400, background: "#fff", border: `3px solid ${C.ink}`, padding: 26,
          clipPath: `inset(0 0 ${Math.max(0, (paperY + 400) - (envY + 40)) * (slide > 0 ? 1 : 0)}px 0)` }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}><Logo c={C.blue} s={18} /><span style={{ fontFamily: UI, fontSize: 14, color: C.mut2 }}>Zürich, 22.10.2026</span></div>
          <div style={{ fontFamily: UI, fontSize: 17, color: "#333", marginTop: 22 }}>Sehr geehrte Frau Muster,</div>
          <div style={{ marginTop: 12 }}><Title s={32}>Saisonstart 2027</Title></div>
          <div style={{ fontFamily: BRAND, fontSize: 17, color: "#4a5570", marginTop: 8 }}>19.–21. Februar · Ihr Stand bei MOTO-ZÜRICH</div>
          <Line w="95%" h={9} c="#e6e6e2" /><Line w="90%" h={9} c="#e6e6e2" /><Line w="72%" h={9} c="#e6e6e2" />
        </div>
        {/* envelope front */}
        <div style={{ position: "absolute", zIndex: 4, left: envX, top: envY + 40 + (1 - envIn) * 600, width: envW, height: envH - 40, background: "#f6f4ee", border: `3px solid ${C.ink}`,
          borderLeft: `14px solid ${C.blue}`, padding: "20px 28px", display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <span style={{ background: C.yellow, fontFamily: BRAND, fontWeight: 700, fontSize: 22, padding: "2px 8px", color: C.navy }}>19.–21.</span>
          <span style={{ border: "2px solid #aaa", fontFamily: UI, fontSize: 18, padding: "10px 14px", color: "#333", lineHeight: 1.35 }}>Muster Motos AG<br />Frau Anna Muster<br />8050 Zürich</span>
        </div>
        {/* flap */}
        <div style={{ position: "absolute", zIndex: flap < 0.5 ? 2 : 5, left: envX, top: envY + (1 - envIn) * 600, width: envW, height: 150, background: "#ddd9cc", border: `3px solid ${C.ink}`,
          clipPath: "polygon(0 0, 100% 0, 50% 100%)", transformOrigin: "top", transform: `scaleY(${interpolate(flap, [0, 1], [-1, 1])})`, opacity: envIn }} />
        {/* stamp */}
        <div style={{ position: "absolute", zIndex: 6, left: envX + envW - 150, top: envY + 58, width: 110, height: 76, border: `3px dashed ${C.red}`, color: C.red,
          fontFamily: LABEL, fontWeight: 700, fontSize: 22, display: "flex", alignItems: "center", justifyContent: "center", transform: `scale(${L >= 52 ? stamp : 0}) rotate(-8deg)` }}>A-POST</div>
      </div>
      <div style={{ position: "absolute", left: 80, top: 1090, opacity: ramp(f, T.brief + 66, T.brief + 76), fontFamily: LABEL, fontWeight: 700, fontSize: 26, textTransform: "uppercase", color: C.ink }}>
        ✓ {t("Unterwegs zu 80 Ausstellern")}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- scene 5: poster pasted on a wall ---------- */
const Poster: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.poster - 4 || f >= T.save + 8) return null;
  const L = f - T.poster;
  const wall = ramp(f, T.poster - 4, T.poster + 8);
  const out = interpolate(f, [T.save - 4, T.save + 6], [1, 0], clamp);
  const slap = (d: number) => {
    const p = interpolate(L, [d, d + 9], [0, 1], { ...clamp, easing: Easing.in(Easing.quad) });
    const settle = spring({ frame: L - d - 9, fps, config: { damping: 8, stiffness: 260 } });
    return { p, sc: interpolate(p, [0, 1], [1.5, 1]) + (L > d + 9 ? (1 - settle) * -0.02 : 0) };
  };
  const a = slap(6), b = slap(22);
  const tapeA = ramp(f, T.poster + 16, T.poster + 20), tapeB = ramp(f, T.poster + 32, T.poster + 36);
  const Tape: React.FC<{ x: number; y: number; r: number; o: number }> = ({ x, y, r, o }) => (
    <div style={{ position: "absolute", left: x, top: y, width: 110, height: 34, background: "rgba(245,240,210,.85)", transform: `rotate(${r}deg)`, opacity: o, border: "1px solid rgba(0,0,0,.08)" }} />
  );
  return (
    <AbsoluteFill style={{ opacity: out }}>
      {/* wall */}
      <div style={{ position: "absolute", left: 80, right: 80, top: 520, height: 620, opacity: wall, border: `3px solid ${C.ink}`, overflow: "hidden",
        background: "repeating-linear-gradient(0deg, #cfc9bd 0 74px, #b9b2a5 74px 77px), #cfc9bd" }}>
        <div style={{ position: "absolute", inset: 0, background: "repeating-linear-gradient(90deg, transparent 0 150px, rgba(0,0,0,.06) 150px 153px)" }} />
        {/* poster 1: event date */}
        <div style={{ position: "absolute", left: 90, top: 52, width: 360, height: 509, opacity: a.p, transform: `scale(${a.sc}) rotate(-2deg)`, boxShadow: `${a.p * 12}px ${a.p * 14}px ${a.p * 18}px rgba(0,0,0,.35)`,
          background: C.navy, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0 }}><PH h="100%" dim={0.45} src="img/fmx.jpg" pos="center 30%" /></div>
          <div style={{ position: "relative", padding: 24, flex: 1, display: "flex", flexDirection: "column" }}>
            <Logo s={22} />
            <div style={{ marginTop: "auto" }}><div style={{ fontFamily: BRAND, fontWeight: 700, fontSize: 82, color: "#fff", lineHeight: 0.95 }}>19.–21.</div>
              <span style={{ background: C.yellow, color: C.navy, fontFamily: BRAND, fontWeight: 700, fontSize: 30, padding: "2px 10px" }}>FEBRUAR 2027</span></div>
          </div>
          <div style={{ position: "relative", background: "#fff", padding: "12px 20px", display: "flex", justifyContent: "space-between", fontFamily: BRAND, fontWeight: 700, fontSize: 16, color: C.navy }}>
            STAGEONE · HALLE 550<span style={{ background: C.red, color: "#fff", padding: "0 6px" }}>TICKETS →</span></div>
        </div>
        {/* poster 2: mascot */}
        <div style={{ position: "absolute", left: 480, top: 52, width: 360, height: 509, opacity: b.p, transform: `scale(${b.sc}) rotate(1.5deg)`, boxShadow: `${b.p * 12}px ${b.p * 14}px ${b.p * 18}px rgba(0,0,0,.35)`,
          background: C.paper, display: "flex", flexDirection: "column", overflow: "hidden" }}>
          <div style={{ position: "relative", flex: 1, display: "flex" }}>
            <div style={{ padding: 22, width: "55%", display: "flex", flexDirection: "column", position: "relative", zIndex: 1 }}>
              <Logo c={C.navy} s={18} />
              <div style={{ marginTop: 34, fontFamily: BRAND, fontWeight: 700, fontSize: 52, color: C.navy, lineHeight: 0.92, textTransform: "uppercase" }}>Grrr-<br />üezi.</div>
              <div style={{ marginTop: "auto" }}><span style={{ background: C.yellow, fontFamily: BRAND, fontWeight: 700, fontSize: 30, color: C.navy, padding: "2px 8px", lineHeight: 1.2 }}>19.–21. Februar</span></div>
            </div>
            <div style={{ position: "absolute", right: 0, top: 0, bottom: 0, width: "55%", background: C.blue }}>
              <Img src={staticFile("img/leu.jpg")} style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center 20%" }} />
            </div>
          </div>
          <div style={{ background: "#fff", padding: "12px 20px", display: "flex", justifyContent: "space-between", fontFamily: BRAND, fontWeight: 700, fontSize: 16, color: C.navy, borderTop: "2px solid #ddd" }}>
            STAGEONE · HALLE 550<span style={{ background: C.red, color: "#fff", padding: "0 6px" }}>TICKETS →</span></div>
        </div>
        <Tape x={110} y={36} r={-14} o={tapeA} /><Tape x={340} y={36} r={12} o={tapeA} />
        <Tape x={500} y={36} r={-10} o={tapeB} /><Tape x={730} y={36} r={14} o={tapeB} />
      </div>
    </AbsoluteFill>
  );
};

/* ---------- scene 6: time saved (rough estimate, one event post across all channels) ---------- */
export const TASKS: [string, number][] = [
  ["Video: Schnitt, Untertitel, Formate", 3], ["Social Media, 8 Kanäle", 1.5], ["Website-Beitrag DE/EN", 1],
  ["Newsletter", 1], ["Serienbrief", 0.5], ["Plakat, Druck-PDF", 1],
];
const HOURS = TASKS.reduce((a, [, h]) => a + h, 0); // 8
const fmtH = (h: number) => (Number.isInteger(h) ? String(h) : h.toFixed(1).replace(".", ","));
const Savings: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.save - 4 || f >= T.end + 6) return null;
  const S = f - T.save;
  const out = interpolate(f, [T.end - 4, T.end + 4], [1, 0], clamp);
  const before = interpolate(S, [8, 44], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const now = interpolate(S, [50, 62], [0, 1], { ...clamp, easing: Easing.out(Easing.cubic) });
  const badge = spring({ frame: S - 92, fps, config: { damping: 9, stiffness: 180 } });
  const hNow = HOURS * before;
  const Bar: React.FC<{ y: number; label: string; w: number; value: string; neon?: boolean; o: number }> = ({ y, label, w, value, neon, o }) => (
    <div style={{ position: "absolute", left: 80, right: 80, top: y, opacity: o }}>
      <div style={{ fontFamily: LABEL, fontWeight: 700, fontSize: 22, textTransform: "uppercase", color: C.mut, marginBottom: 8 }}>{label}</div>
      <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
        <div style={{ flex: 1, height: 64, border: `3px solid ${C.ink}`, background: C.white, position: "relative" }}>
          <div style={{ position: "absolute", left: 0, top: 0, bottom: 0, width: `${w * 100}%`, background: neon ? C.neon : C.ink, borderRight: w > 0 && w < 1 ? `3px solid ${C.ink}` : "none" }} />
        </div>
        <div style={{ width: 230, fontFamily: HEAD, fontWeight: 700, fontSize: 58, lineHeight: 1, color: neon ? C.ink : C.ink, textAlign: "right", whiteSpace: "nowrap" }}>{value}</div>
      </div>
    </div>
  );
  return (
    <AbsoluteFill style={{ opacity: out }}>
      <Bar y={540} label="Früher · manuell" w={before} value={`${fmtH(Math.round(hNow * 2) / 2)} Std.`} o={ramp(S, 0, 8)} />
      <Bar y={680} label="Jetzt · mit Creox" w={(10 / 60 / HOURS) * now + (now > 0 ? 0.012 : 0)} value={`${Math.round(10 * now)} Min.`} neon o={ramp(S, 44, 50)} />
      <div style={{ position: "absolute", left: 80, right: 80, top: 815, border: `3px solid ${C.ink}`, background: C.white }}>
        {TASKS.map(([task, h], i) => {
          const k = ramp(S, 14 + i * 5, 22 + i * 5);
          return (
            <div key={task} style={{ display: "flex", justifyContent: "space-between", padding: "6px 18px", borderTop: i ? "2px solid #ddd" : "none", opacity: k,
              transform: `translateX(${(1 - k) * -24}px)`, fontFamily: LABEL, fontSize: 22, textTransform: "uppercase", color: C.ink }}>
              <span>{task}</span><span style={{ fontWeight: 700, whiteSpace: "nowrap" }}>{fmtH(h)} Std.</span>
            </div>
          );
        })}
      </div>
      <div style={{ position: "absolute", left: 80, top: 1172, transform: `scale(${S >= 92 ? badge : 0}) rotate(-2deg)`, transformOrigin: "0 50%",
        background: C.neon, border: `3px solid ${C.ink}`, boxShadow: `6px 6px 0 ${C.ink}`, padding: "8px 18px", fontFamily: LABEL, fontWeight: 700, fontSize: 24, textTransform: "uppercase", whiteSpace: "nowrap" }}>
        {t("≈ 98 % weniger Zeit · Sie geben nur frei")}
      </div>
    </AbsoluteFill>
  );
};

/* ---------- scene 7: end ---------- */
const End: React.FC = () => {
  const f = useCurrentFrame();
  const { fps } = useVideoConfig();
  if (f < T.end) return null;
  const items = ["Video-Schnitt", "Social Media", "Website", "Newsletter", "Brief", "Plakat"];
  return (
    <AbsoluteFill>
      <div style={{ position: "absolute", left: 80, right: 80, top: 560, display: "flex", flexDirection: "column", gap: 14 }}>
        {items.map((it, i) => {
          const s = spring({ frame: f - T.end - 4 - i * 4, fps, config: { damping: 16, stiffness: 160 } });
          return (
            <div key={it} style={{ display: "flex", alignItems: "center", gap: 22, border: `3px solid ${C.ink}`, background: C.white, padding: "16px 22px",
              transform: `translateX(${(1 - s) * -60}px)`, opacity: s, boxShadow: `6px 6px 0 ${C.ink}` }}>
              <span style={{ width: 46, height: 46, background: C.neon, border: `3px solid ${C.ink}`, display: "flex", alignItems: "center", justifyContent: "center", fontFamily: HEAD, fontWeight: 700, fontSize: 28 }}>✓</span>
              <span style={{ fontFamily: HEAD, fontWeight: 700, fontSize: 44, textTransform: "uppercase" }}>{it}</span>
              <span style={{ marginLeft: "auto", fontFamily: LABEL, fontSize: 22, color: C.mut2, textTransform: "uppercase" }}>{["auto", "sofort", "2 Min.", "Fr 18:00", "per Post", "Druck"][i]}</span>
            </div>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};

export const Promo: React.FC = () => (
  <AbsoluteFill style={{ background: C.paper }}>
    <Frame />
    <Header />
    <Upload />
    <Edit />
    <System />
    <Social />
    <Website />
    <Newsletter />
    <Brief />
    <Poster />
    <Savings />
    <End />
    <Sequence from={0}><Audio src={staticFile("music.wav")} /></Sequence>
  </AbsoluteFill>
);
