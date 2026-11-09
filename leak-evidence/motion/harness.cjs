// Exercises the REAL vendored motion.min.mjs (v13.2.0) inside jsdom with a fake WAAPI
// (jsdom has no Element.prototype.animate) to see when animate() promises settle.
const fs = require("fs"), path = require("path"), vm = require("vm");
const { JSDOM } = require("jsdom");
const src = fs.readFileSync(path.join(__dirname, "../../src/zen/vendor/motion.min.mjs"), "utf8");

const dom = new JSDOM("<!doctype html><body></body>", { pretendToBeVisual: true, runScripts: "outside-only" });
const w = dom.window;
// Fake WAAPI Animation: finishes only if test calls .finish(); cancel() fires NO onfinish (like real: fires 'cancel' event only).
const made = [];
w.Element.prototype.animate = function (kf, opts) {
  const a = { playState: "running", currentTime: 0, startTime: 0, playbackRate: 1, onfinish: null,
    effect: { getComputedTiming: () => ({ duration: opts.duration }), updateTiming() {} },
    play() {}, pause() {}, commitStyles() {},
    cancel() { this.playState = "idle"; this.cancelled = true; /* real WAAPI dispatches 'cancel', never 'finish' */ },
    finish() { this.playState = "finished"; this.onfinish && this.onfinish(); } };
  made.push(a); return a;
};
// Run the UMD bundle inside the jsdom realm (as Zen does via loadSubScript onto the window).
const ctx = dom.getInternalVMContext();
vm.runInContext(src, ctx);
const M = w.Motion;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const settle = (p) => { const s = { v: "PENDING" }; p.then(() => (s.v = "resolved"), (e) => (s.v = "rejected:" + e)); return s; };

async function t(name, fn) {
  const r = await fn(); await sleep(150);
  console.log(name.padEnd(62), "->", r.s.v);
}
(async () => {
  const mk = () => { const e = w.document.createElement("div"); w.document.body.append(e); return e; };
  const props = { opacity: [1, 0], transform: ["scale(1)", "scale(0.95)"] };
  const opts = { duration: 0.1, easing: "easeOut" };

  await t("WAAPI: animate, fake finish fires", async () => {
    const c = M.animate(mk(), props, opts); const s = settle(c); await sleep(50); made.forEach(a=>a.finish()); return { s };
  });
  await t("WAAPI: animate, then ctrl.stop()", async () => {
    const c = M.animate(mk(), props, opts); const s = settle(c); await sleep(50); c.stop(); return { s };
  });
  await t("WAAPI: animate, then ctrl.cancel()", async () => {
    const c = M.animate(mk(), props, opts); const s = settle(c); await sleep(50); c.cancel(); return { s };
  });
  await t("WAAPI: external anim.cancel() (element removed/style reset)", async () => {
    made.length = 0; const e = mk(); const c = M.animate(e, props, opts); const s = settle(c); await sleep(50);
    made.forEach(a=>a.cancel()); return { s };
  });
  await t("WAAPI: element removed from DOM mid-animation (no finish)", async () => {
    made.length = 0; const e = mk(); const c = M.animate(e, props, opts); const s = settle(c); await sleep(50);
    e.remove(); return { s };
  });
  await t("2nd animate() same element+prop supersedes 1st (1st promise)", async () => {
    made.length = 0; const e = mk(); const c1 = M.animate(e, props, opts); const s1 = settle(c1); await sleep(50);
    const c2 = M.animate(e, { opacity: [1, 0] }, opts); const s2 = settle(c2);
    await sleep(20); made.filter(a=>!a.cancelled).forEach(a=>a.finish());
    console.log("   (2nd animate promise:", (await sleep(50), s2.v) + ")"); return { s: s1 };
  });
  await t("JS path (marginBottom, rAF-driven): completes", async () => {
    const e = mk(); const c = M.animate(e, { marginBottom: ["0px", "-20px"] }, opts); return { s: settle(c) };
  });
  await t("JS path: ctrl.stop() mid-way", async () => {
    const e = mk(); const c = M.animate(e, { marginBottom: ["0px", "-20px"] }, { duration: 1 }); const s = settle(c);
    await sleep(60); c.stop(); return { s };
  });
  await t("JS path: ctrl.cancel() mid-way", async () => {
    const e = mk(); const c = M.animate(e, { marginBottom: ["0px", "-20px"] }, { duration: 1 }); const s = settle(c);
    await sleep(60); c.cancel(); return { s };
  });
  await t("JS path: 2nd animate() same prop supersedes 1st (1st promise)", async () => {
    const e = mk(); const c = M.animate(e, { marginBottom: ["0px", "-20px"] }, { duration: 1 }); const s = settle(c);
    await sleep(60); M.animate(e, { marginBottom: ["0px", "-30px"] }, { duration: 0.05 }); return { s };
  });
  await t("animate(0,100,{duration:1}) value: stop()", async () => {
    const c = M.animate(0, 100, { duration: 1, onUpdate() {} }); const s = settle(c); await sleep(60); c.stop(); return { s };
  });
  await t("animate(0,100,{duration:1}) value: cancel()", async () => {
    const c = M.animate(0, 100, { duration: 1, onUpdate() {} }); const s = settle(c); await sleep(60); c.cancel(); return { s };
  });
  await t("animate(0,100,{duration:1}) value: complete()", async () => {
    const c = M.animate(0, 100, { duration: 1, onUpdate() {} }); const s = settle(c); await sleep(60); c.complete(); return { s };
  });
  await t("animate(el, opacity:[1,1]) already at target (no-op)", async () => {
    const c = M.animate(mk(), { opacity: [1, 1] }, opts); return { s: settle(c) };
  });
  // No-rAF (hidden/occluded window): fresh realm whose rAF never fires. Use a longer settle to show it stays pending,
  // then restore frames to show it resumes (i.e. delayed, not lost) -- unless stop()/cancel() intervened.
  {
    const d2 = new JSDOM("<body></body>", { pretendToBeVisual: true, runScripts: "outside-only" });
    const w2 = d2.window; const realRaf = w2.requestAnimationFrame.bind(w2); let frozen = true; const queue = [];
    w2.requestAnimationFrame = (cb) => { if (frozen) { queue.push(cb); return 0; } return realRaf(cb); };
    vm.runInContext(src, d2.getInternalVMContext());
    const e = w2.document.createElement("div"); w2.document.body.append(e);
    const c = w2.Motion.animate(e, { marginBottom: ["0px", "-20px"] }, { duration: 0.05 }); const s = settle(c);
    await sleep(300); console.log("JS path, rAF frozen 300ms                                      ->", s.v);
    frozen = false; queue.splice(0).forEach((cb) => realRaf(cb)); await sleep(300);
    console.log("JS path, rAF restored (queued frames replayed)                 ->", s.v);
  }
  process.exit(0);
})();
