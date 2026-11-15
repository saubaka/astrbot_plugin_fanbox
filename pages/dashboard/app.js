/* FANBOX 推送面板（AstrBot Plugin Page）。
   样式和动效照搬作者自建 FxTwitter API 的账号统计面板（_stats）：入场错开、数字滚动、刷新时原地更新不闪、滚动渐隐。
   数据走 window.AstrBotPluginPage 桥：apiGet/apiPost 到插件注册的接口。 */
(function () {
  "use strict";
  var bridge = window.AstrBotPluginPage;

  var ICON = {
    check: '<svg viewBox="0 0 16 16" fill="none"><path d="M3.5 8.5l3 3 6-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    lock: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3.2" y="7" width="9.6" height="6.8" rx="2"/><path d="M5.3 7V5.2a2.7 2.7 0 0 1 5.4 0V7"/></svg>',
    alert: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M8 2.2 14.3 13.4H1.7z" stroke-linejoin="round"/><path d="M8 6.6v3M8 11.6v.1"/></svg>',
    dash: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 8h8"/></svg>',
    search: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="7" cy="7" r="4.3"/><path d="m10.3 10.3 3.2 3.2"/></svg>',
    user: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="5.6" r="2.8"/><path d="M2.8 14c.6-2.8 2.7-4.3 5.2-4.3s4.6 1.5 5.2 4.3" stroke-linecap="round"/></svg>',
    clock: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="5.8"/><path d="M8 4.8V8l2.2 1.4"/></svg>',
    cal: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2.5" y="3.4" width="11" height="10.1" rx="2.2"/><path d="M2.5 6.6h11M5.6 2v2.6M10.4 2v2.6" stroke-linecap="round"/></svg>',
    sum: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H4.5L9 8l-4.5 5H12"/></svg>',
    send: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M14 2 7.2 8.8M14 2 9.6 14l-2.4-5.2L2 6.4z"/></svg>',
    gear: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="8" cy="8" r="2.2"/><path d="M8 1.8v1.6M8 12.6v1.6M14.2 8h-1.6M3.4 8H1.8M12.4 3.6l-1.1 1.1M4.7 11.3l-1.1 1.1M12.4 12.4l-1.1-1.1M4.7 4.7 3.6 3.6" stroke-linecap="round"/></svg>',
    flag: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 14V2.5M3.5 3h8l-1.6 2.8L11.5 8.6h-8"/></svg>',
    layers: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M8 2 14 5.2 8 8.4 2 5.2z"/><path d="m2 8.2 6 3.2 6-3.2M2 11l6 3.2 6-3.2"/></svg>',
    sliders: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.5 4.5h7M12.5 4.5h1M2.5 11.5h2M7.5 11.5h6"/><circle cx="11" cy="4.5" r="1.6"/><circle cx="6" cy="11.5" r="1.6"/></svg>',
    image: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="2" y="3" width="12" height="10" rx="2"/><circle cx="6" cy="6.6" r="1.2"/><path d="m2.5 12 3.6-3.6 2.6 2.4 2-1.8 2.8 2.6"/></svg>',
    eye: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1.6 8s2.4-4.6 6.4-4.6S14.4 8 14.4 8 12 12.6 8 12.6 1.6 8 1.6 8z"/><circle cx="8" cy="8" r="2"/></svg>',
    trash: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.8 4.2h10.4M6.4 4.2V2.8h3.2v1.4M4.2 4.2l.6 9h6.4l.6-9"/></svg>',
    heart: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 14s-5.6-3.4-5.6-7.4A3.1 3.1 0 0 1 8 4.7a3.1 3.1 0 0 1 5.6 1.9C13.6 10.6 8 14 8 14z"/></svg>'
  };
  var GROUP_ICON = { basic: "gear", start: "flag", style: "layers", content: "sliders", card: "image" };
  var OPTION_LABELS = {
    push_style: { text: "文字模板", card: "卡片图" },
    start_from: { deploy: "部署时间", subscribe: "订阅时间", custom: "自定义时间" }
  };
  var UNITS = {
    poll_interval_minutes: "分钟", max_new_posts_per_poll: "篇", max_post_age_hours: "小时",
    excerpt_max_chars: "字", max_tags: "个", timezone_offset_hours: "小时",
    card_excerpt_lines: "行", card_title_lines: "行"
  };
  var RANGES = {
    poll_interval_minutes: [5, 1440], max_new_posts_per_poll: [1, 20], max_post_age_hours: [0, 8760],
    excerpt_max_chars: [0, 2000], max_tags: [0, 30], timezone_offset_hours: [-12, 14],
    card_excerpt_lines: [0, 6], card_title_lines: [1, 4]
  };
  var MONO = { proxy: 1, start_time: 1, time_format: 1, card_font_path: 1, card_bold_font_path: 1 };
  var OUT = [["ok", "成功", "var(--c-ok)"], ["not_found", "未找到", "var(--c-nf)"], ["blocked", "被拦截", "var(--c-rl)"], ["error", "出错", "var(--c-au)"]];
  var PERIODS = [["p_hour", "1 小时"], ["p_day", "24 小时"], ["p_week", "7 天"], ["p_total", "总计"]];
  var ERR_KIND = {
    blocked: ["被拦截", "lock", "o-blocked", "FANBOX 返回 403，出口 IP 或客户端被它的规则拦了，本轮跳过"],
    not_found: ["未找到", "search", "o-not_found", "创作者不存在或已删除"],
    list_failed: ["获取失败", "alert", "o-error", "获取帖子列表失败，下次检查会重试"],
    send_failed: ["发送失败", "send", "o-fail", "消息没有发出去，下次检查会重试"],
    card_failed: ["卡片渲染失败", "image", "o-card_failed", "卡片图没画出来，已改发文字模板"],
    image_failed: ["图片下载失败", "image", "o-image_failed", "封面或头像没下载下来，消息里会少这张图"]
  };

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var EASE = "cubic-bezier(.22,1,.36,1)", NBSP = String.fromCharCode(160);
  var REFRESH_MS = 30000;
  var data = null, groupNames = {}, platforms = [], cards = {}, firstRender = true;
  var pushRows = {}, errRows = {};
  var settingsBuilt = false, savedValues = null, draft = null, controls = {};
  var tip = document.getElementById("tip"), bar = document.getElementById("topbar");

  /* ---------- helpers（和 _stats 面板一致） ---------- */
  function settle(node) { function h(ev) { if (ev.target !== node) return; node.removeEventListener("animationend", h); node.classList.remove("enter"); node.style.animationDelay = ""; } node.addEventListener("animationend", h); }
  function el(tag, cls, text) { var e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined && text !== null) e.textContent = text; if (cls && cls.indexOf("enter") >= 0) settle(e); return e; }
  function later(node, ms) { node.style.animationDelay = ms + "ms"; return node; }
  function counter(tag, cls) { var n = el(tag, cls); n.setAttribute("data-v", "0"); n._fresh = true; return n; }
  function place(parent, node, index) { var at = parent.children[index]; if (at !== node) parent.insertBefore(node, at || null); }
  function iconEl(name, cls) { var s = el("span", cls || ""); s.innerHTML = ICON[name] || ""; return s; }
  function fx(node, frames, opts) { if (reduce || !node || !node.animate) return; try { node.animate(frames, opts); } catch (err) { /* ignore */ } }
  function drop(node) { node.classList.remove("enter"); if (reduce) { node.remove(); measureSoon(); return; } node.classList.add("leave"); function h(ev) { if (ev.target !== node) return; node.removeEventListener("animationend", h); node.remove(); measureSoon(); } node.addEventListener("animationend", h); }
  function flip(nodes, mutate) { if (reduce || !nodes.length) { mutate(); return; } var before = nodes.map(function (n) { return n.offsetTop; }); mutate(); nodes.forEach(function (n, i) { if (!n.isConnected) return; var d = before[i] - n.offsetTop; if (Math.abs(d) >= 1) fx(n, [{ translate: "0 " + d + "px", offset: 0 }], { duration: 700, easing: EASE }); }); }
  function setText(node, text) { if (node.textContent === text) return; var had = node.textContent.trim() !== ""; node.textContent = text; if (had && !firstRender) fx(node, [{ opacity: 0, offset: 0 }], { duration: 520, easing: EASE }); }
  function full(n) { return (Number(n) || 0).toLocaleString("zh-CN"); }
  function compact(n) { n = Number(n) || 0; if (n < 10000) return full(n); var v = n / 1000; return (v >= 100 ? Math.round(v) : Math.round(v * 10) / 10) + "K"; }
  function setNum(node, value, mode, wait) {
    value = Number(value) || 0; var fmt = mode === "compact" ? compact : full;
    var has = node.hasAttribute("data-v"), from = Number(node.getAttribute("data-v")); node.setAttribute("data-v", String(value));
    if (!has || reduce || from === value) { node.textContent = fmt(value); node._fresh = false; return; }
    var slow = firstRender || node._fresh; if (!slow) fx(node, [{ color: "#2f80d8", offset: 0 }], { duration: 1600, easing: EASE }); node._fresh = false;
    var t0 = performance.now() + (slow ? (wait || 0) : 0), dur = slow ? 1300 : 800, id = (node._nid || 0) + 1; node._nid = id;
    function step(t) { if (node._nid !== id) return; var k = Math.min(1, Math.max(0, (t - t0) / dur)), e = 1 - Math.pow(1 - k, 4); node.textContent = fmt(Math.round(from + (value - from) * e)); if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  function left(ms) { var s = Math.max(0, Math.round((ms - Date.now()) / 1000)); var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), r = s % 60; if (h) return h + " 小时 " + m + " 分"; return m + ":" + (r < 10 ? "0" : "") + r; }
  function ago(ms) { if (!ms) return "—"; var s = Math.max(0, Math.round((Date.now() - ms) / 1000)); if (s < 45) return "刚刚"; if (s < 3600) return Math.round(s / 60) + " 分钟前"; if (s < 86400) return Math.round(s / 3600) + " 小时前"; return Math.round(s / 86400) + " 天前"; }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  function stamp(ms) { var d = new Date(ms); return pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()) + " " + pad2(d.getHours()) + ":" + pad2(d.getMinutes()) + ":" + pad2(d.getSeconds()); }
  function isoAgo(iso) { var t = Date.parse(iso || ""); return isNaN(t) ? "" : ago(t); }
  function clone(v) { return JSON.parse(JSON.stringify(v)); }

  /* ---------- 滚动：内容从底边升起、在顶栏处溶解（照搬 _stats） ---------- */
  var rvList = [], docH = 0, barH = 64, frameQueued = false, measureQueued = false;
  function docTop(n) { var y = 0; while (n) { y += n.offsetTop; n = n.offsetParent; } return y; }
  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function measure() {
    measureQueued = false; rvList = [];
    var nodes = document.querySelectorAll(".rv");
    for (var i = 0; i < nodes.length; i++) { var n = nodes[i]; if (n.classList.contains("leave") || n.hidden) continue; var h = n.offsetHeight; if (!h) continue; rvList.push({ n: n, t: docTop(n), h: h }); }
    docH = document.documentElement.scrollHeight; barH = bar.offsetHeight; frame();
  }
  function measureSoon() { if (!measureQueued) { measureQueued = true; requestAnimationFrame(measure); } }
  function frame() {
    frameQueued = false;
    var sy = Math.max(0, window.pageYOffset || 0), sp = Math.round(Math.min(1, sy / 56) * 1000) / 1000;
    if (bar._sp !== sp) { bar._sp = sp; bar.style.setProperty("--sp", String(sp)); }
    if (reduce) return;
    var vh = window.innerHeight, remain = Math.max(0, docH - sy - vh);
    var bb = Math.min(150, vh * .22, remain), tb = Math.min(100, vh * .14, sy);
    for (var i = 0; i < rvList.length; i++) {
      var r = rvList[i], top = r.t - sy, bot = top + r.h;
      var e = bb < 1 ? 1 : clamp01((vh - top) / bb), x = tb < 1 ? 1 : clamp01((bot - barH) / tb);
      var p = Math.min(e, x), o = Math.round(p * p * (3 - 2 * p) * 1000) / 1000;
      var y = Math.round((e < x ? (1 - e) * 30 : -(1 - x) * 14) * 10) / 10, s = Math.round((.96 + .04 * p) * 1000) / 1000;
      var st = r.n._rv || (r.n._rv = {});
      if (st.o !== o) { st.o = o; r.n.style.setProperty("--rv", String(o)); }
      if (st.y !== y) { st.y = y; r.n.style.setProperty("--ry", y + "px"); }
      if (st.s !== s) { st.s = s; r.n.style.setProperty("--rs", String(s)); }
    }
  }
  function onScroll() { if (tip.classList.contains("show")) hideTip(); if (!frameQueued) { frameQueued = true; requestAnimationFrame(frame); } }

  /* ---------- tooltip / toast / live ---------- */
  function showTip(target, value, label) { tip.className = "tip"; tip.textContent = ""; tip.appendChild(el("b", "", value)); tip.appendChild(el("span", "", label)); var r = target.getBoundingClientRect(); tip.classList.add("show"); var w = tip.offsetWidth, hgt = tip.offsetHeight; var x = Math.min(window.innerWidth - w - 8, Math.max(8, r.left + r.width / 2 - w / 2)); var y = r.top - hgt - 10; if (y < 8) y = r.bottom + 10; tip.style.left = x + "px"; tip.style.top = y + "px"; }
  function hideTip() { tip.classList.remove("show"); }
  function bindTip(node, getter) { node.addEventListener("pointerenter", function () { var t = getter(); showTip(node, t[0], t[1]); }); node.addEventListener("pointerleave", hideTip); node.addEventListener("focus", function () { var t = getter(); showTip(node, t[0], t[1]); }); node.addEventListener("blur", hideTip); }
  function setLive(ok, msg) { var live = document.getElementById("live"), txt = document.getElementById("liveText"), ring = document.getElementById("ringFg"); live.classList.toggle("err", !ok); if (ok) { txt.setAttribute("data-ago", String(Date.now())); txt.textContent = "实时 · 刚刚更新"; ring.classList.remove("run"); void ring.getBoundingClientRect(); ring.classList.add("run"); } else { txt.removeAttribute("data-ago"); txt.textContent = msg || "连接中断，重试中"; } }
  function toast(msg, ok) { var t = document.getElementById("toast"); t.textContent = msg; t.classList.toggle("ok", !!ok); t.classList.add("show"); clearTimeout(toast.timer); toast.timer = setTimeout(function () { t.classList.remove("show"); }, ok ? 2800 : 4200); }
  function busy(btn, on, label) { if (on) { btn._label = btn.textContent; btn.disabled = true; btn.textContent = ""; btn.appendChild(el("span", "spin")); btn.appendChild(el("span", "", label || btn._label)); } else { btn.disabled = false; btn.textContent = btn._label || btn.textContent; } }

  function api(method, endpoint, payload) {
    if (!bridge) return Promise.reject(new Error("当前页面没有运行在 AstrBot 管理面板里"));
    return method === "GET" ? bridge.apiGet(endpoint, payload) : bridge.apiPost(endpoint, payload || {});
  }
  function errMsg(e) { var m = e && e.message ? e.message : String(e || "未知错误"); try { var j = JSON.parse(m); if (j && j.message) return j.message; } catch (x) { /* plain text */ } return m; }

  /* ---------- 会话名字 ---------- */
  function parseUmo(umo) { var p = String(umo || "").split(":"); if (p.length < 3) return null; return { platform: p[0], type: p[1], id: p.slice(2).join(":") }; }
  function sessionLabel(umo) {
    var p = parseUmo(umo); if (!p) return umo;
    if (p.type === "GroupMessage") { var n = groupNames[p.platform + ":" + p.id]; return n ? n : "群 " + p.id; }
    if (p.type === "FriendMessage") return "私聊 " + p.id;
    return "会话 " + p.id;
  }
  function sessionSub(umo) { var p = parseUmo(umo); if (!p) return ""; return (p.type === "GroupMessage" ? "群号 " : p.type === "FriendMessage" ? "QQ " : "") + p.id + " · " + p.platform; }

  /* ---------- hero + tiles ---------- */
  var TILE_DEFS = [["creators", "订阅创作者", "user"], ["checks", "近 24 小时检查", "search"], ["next", "下次检查", "clock"], ["week", "近 7 天推送", "cal"], ["errors", "近 24 小时报错", "alert"], ["total", "总推送", "sum"]];
  var tileRefs = {};
  function buildTiles() { var box = document.getElementById("tiles"); box.textContent = ""; TILE_DEFS.forEach(function (d, i) { var t = later(el("div", "tile enter"), 180 + i * 55); var l = el("span", "lbl"); l.appendChild(iconEl(d[2], "ic")); l.appendChild(el("span", "", d[1])); var v = el("span", "val sk", "0000"); v.setAttribute("data-v", "0"); var n = el("span", "note", NBSP); t.appendChild(l); t.appendChild(v); t.appendChild(n); box.appendChild(t); tileRefs[d[0]] = { val: v, note: n }; }); }
  function renderHero() {
    var st = data.stats, ser = st.series, pl = data.plugin, hero = document.getElementById("heroNum");
    if (hero.classList.contains("sk")) { hero.classList.remove("sk"); fx(hero, [{ opacity: 0, filter: "blur(10px)", transform: "translateY(10px)", offset: 0 }], { duration: 1000, easing: EASE }); }
    setNum(hero, ser.pushes.periods.day, "full");
    Object.keys(tileRefs).forEach(function (k, i) { var v = tileRefs[k].val; if (v.classList.contains("sk")) { v.classList.remove("sk"); fx(v, [{ opacity: 0, filter: "blur(6px)", transform: "translateY(6px)", offset: 0 }], { duration: 800, delay: i * 45, easing: EASE, fill: "backwards" }); } });
    var hourly = ser.pushes.hourly, peak = Math.max.apply(null, hourly), peakAt = hourly.lastIndexOf(peak);
    setText(document.getElementById("heroMeta"), peak > 0 ? ("每小时峰值 " + full(peak) + " 篇 · " + (peakAt === 23 ? "最近 1 小时" : "约 " + (23 - peakAt) + " 小时前")) : ("最近 24 小时还没有新帖 · 检查了 " + full(ser.checks.periods.day) + " 次"));
    drawSpark(hourly.some(function (v) { return v > 0; }) ? hourly : ser.checks.hourly);
    var bad = 0; data.creators.forEach(function (c) { var od = (c.stats && c.stats.outcomes_day) || {}; bad += (od.not_found || 0) + (od.blocked || 0) + (od.error || 0); });
    setNum(tileRefs.creators.val, data.creators.length, "compact"); setText(tileRefs.creators.note, data.sessions.length + " 个会话");
    setNum(tileRefs.checks.val, ser.checks.periods.day, "compact"); setText(tileRefs.checks.note, bad ? ("其中 " + bad + " 次没成功") : "全部成功");
    var nv = tileRefs.next.val; nv.removeAttribute("data-v");
    if (pl.polling) { nv.removeAttribute("data-until"); nv.textContent = "检查中"; }
    else if (pl.next_poll_at) { nv.setAttribute("data-until", String(pl.next_poll_at)); nv.textContent = left(pl.next_poll_at); }
    else { nv.textContent = "—"; }
    setText(tileRefs.next.note, "每 " + pl.poll_interval + " 分钟一次");
    setNum(tileRefs.week.val, ser.pushes.periods.week, "compact"); setText(tileRefs.week.note, "约 " + full(Math.round(ser.pushes.periods.week / 7)) + " 篇 / 天");
    setNum(tileRefs.errors.val, ser.errors.periods.day, "compact"); setText(tileRefs.errors.note, full(ser.errors.periods.week) + " 条 / 7 天");
    setNum(tileRefs.total.val, ser.pushes.periods.total, "compact"); setText(tileRefs.total.note, st.since ? ("自 " + new Date(st.since * 1000).toLocaleDateString("zh-CN") + " 起统计") : "还没有统计数据");
  }
  var sparkVals = null, sparkRun = 0;
  function paintSpark(vals) {
    var W = 300, H = 60, pad = 6, max = Math.max(1, Math.max.apply(null, vals)), stepX = W / (vals.length - 1);
    var pts = vals.map(function (v, i) { return [i * stepX, H - pad - (v / max) * (H - pad * 2)]; });
    var d = "M" + pts[0][0].toFixed(1) + " " + pts[0][1].toFixed(1); for (var i = 1; i < pts.length; i++) { var p0 = pts[i - 1], p1 = pts[i], cx = (p0[0] + p1[0]) / 2; d += " C" + cx.toFixed(1) + " " + p0[1].toFixed(1) + " " + cx.toFixed(1) + " " + p1[1].toFixed(1) + " " + p1[0].toFixed(1) + " " + p1[1].toFixed(1); }
    document.getElementById("sparkLine").setAttribute("d", d); document.getElementById("sparkArea").setAttribute("d", d + " L" + W + " " + H + " L0 " + H + " Z");
    var last = pts[pts.length - 1], dot = document.getElementById("sparkDot"); dot.style.left = (last[0] / W * 100).toFixed(2) + "%"; dot.style.top = (last[1] / H * 100).toFixed(2) + "%";
  }
  function drawSpark(vals) {
    var from = sparkVals; sparkVals = vals.slice(); var svg = document.getElementById("spark");
    if (!from || reduce) { paintSpark(vals); if (!svg.classList.contains("drawn")) { svg.classList.add("drawn"); document.getElementById("sparkDot").classList.add("on"); } return; }
    var id = ++sparkRun, t0 = performance.now();
    function step(t) { if (id !== sparkRun) return; var k = Math.min(1, Math.max(0, (t - t0) / 900)), e = 1 - Math.pow(1 - k, 3); paintSpark(vals.map(function (v, i) { return from[i] + (v - from[i]) * e; })); if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }

  /* ---------- pills ---------- */
  function setPill(node, p) {
    var sig = p.cls + "|" + p.icon + "|" + p.text;
    if (node._sig === sig) return;
    var changed = !!node._sig; node._sig = sig; node.className = p.cls; node.textContent = "";
    node.appendChild(iconEl(p.icon)); node.appendChild(el("span", "", p.text));
    if (changed) { fx(node, [{ transform: "scale(.9)", offset: 0 }], { duration: 650, easing: "cubic-bezier(.34,1.56,.64,1)" }); }
  }
  function creatorPill(st) {
    var o = st && st.last_outcome;
    if (!o) return { cls: "pill p-muted", icon: "dash", text: "等待首次检查" };
    if (o === "ok") return { cls: "pill p-good", icon: "check", text: "正常" };
    if (o === "blocked") return { cls: "pill p-warn", icon: "lock", text: "被 FANBOX 拦截" };
    if (o === "not_found") return { cls: "pill p-blue", icon: "search", text: "未找到" };
    return { cls: "pill p-bad", icon: "alert", text: "获取失败" };
  }
  function hourLabel(i) { return i === 23 ? "最近 1 小时" : "约 " + (23 - i) + " 小时前"; }

  /* ---------- 创作者卡片 ---------- */
  function setAvatar(av, name, url) {
    if (av._url === url) return; av._url = url; av.textContent = ""; av.classList.remove("has-img");
    if (url) {
      var img = document.createElement("img"); img.alt = ""; img.referrerPolicy = "no-referrer"; img.loading = "lazy"; img.src = url;
      img.addEventListener("error", function () { av.classList.remove("has-img"); av.textContent = (name || "?").slice(0, 2); });
      av.classList.add("has-img"); av.appendChild(img);
    } else { av.textContent = (name || "?").slice(0, 2); }
  }
  function buildCard(c, index) {
    var base = firstRender ? 60 + index * 120 : 0;
    var card = later(el("article", "acct card enter"), base);
    var head = later(el("header", "acct-head rv enter"), base + 90); var av = el("div", "avatar"); var title = el("div", "acct-title"); var h3 = el("h3", ""); var sub = el("span", "acct-sub"); title.appendChild(h3); title.appendChild(sub); var pill = el("span", "pill"); head.appendChild(av); head.appendChild(title); head.appendChild(pill); card.appendChild(head);
    var body = el("div", "acct-body"); var col = later(el("div", "acct-col rv enter"), base + 160);
    var ph = el("div", "mix-head"); ph.appendChild(el("span", "", "推送篇数")); var phs = el("small", ""); ph.appendChild(phs); col.appendChild(ph); var periods = el("div", "periods four"); var pRefs = {}; PERIODS.forEach(function (p) { var cell = el("div", "period"); var b = counter("b", ""); cell.appendChild(b); cell.appendChild(el("span", "", p[1])); periods.appendChild(cell); pRefs[p[0]] = b; }); col.appendChild(periods);
    var mix = el("div", "mix"); var mh = el("div", "mix-head"); mh.appendChild(el("span", "", "近 24 小时检查结果")); var mhs = el("small", ""); mh.appendChild(mhs);
    var seg = el("div", "segbar"); seg.setAttribute("role", "img"); var segRefs = {}; OUT.forEach(function (o) { var i = el("i", ""); i.style.background = o[2]; i.style.flexGrow = "0"; seg.appendChild(i); segRefs[o[0]] = i; });
    var lg = el("div", "legend"); var lgRefs = {}; OUT.forEach(function (o) { var s = el("span", ""); var sw = el("i", ""); sw.style.background = o[2]; s.appendChild(sw); s.appendChild(el("span", "", o[1])); var b = counter("b", ""); s.appendChild(b); lg.appendChild(s); lgRefs[o[0]] = b; });
    mix.appendChild(mh); mix.appendChild(seg); mix.appendChild(lg); col.appendChild(mix);
    var right = later(el("div", "chart-box rv enter"), base + 230); var ch = el("div", "chart-head"); ch.appendChild(el("span", "", "近 24 小时 · 每小时检查")); var chs = el("small", ""); ch.appendChild(chs);
    var bars = el("div", "bars"); bars.setAttribute("role", "img"); var barRefs = [];
    for (var i = 0; i < 24; i++) { (function (i) { var b = el("div", "bar"); b.tabIndex = 0; var f = el("i", ""); b.appendChild(f); bars.appendChild(b); barRefs.push({ wrap: b, fill: f }); bindTip(b, function () { var v = card._hc ? card._hc[i] : 0, pv = card._hp ? card._hp[i] : 0; return [full(v) + " 次检查" + (pv ? " · " + pv + " 篇推送" : ""), hourLabel(i)]; }); })(i); }
    var axis = el("div", "axis"); axis.appendChild(el("span", "", "24 小时前")); axis.appendChild(el("span", "", "12 小时前")); axis.appendChild(el("span", "", "现在"));
    right.appendChild(ch); right.appendChild(bars); right.appendChild(axis);
    body.appendChild(col); body.appendChild(right); card.appendChild(body);

    var postBlock = later(el("div", "sub-block rv enter"), base + 300); var pt = el("div", "sub-title"); pt.appendChild(el("span", "", "最新帖子")); var pts = el("small", ""); pt.appendChild(pts); postBlock.appendChild(pt);
    var post = el("div", "post"); var thumb = el("div", "thumb"); var pm = el("div", "post-main"); var pa = el("a", ""); pa.target = "_blank"; pa.rel = "noopener noreferrer"; var ps = el("span", ""); pm.appendChild(pa); pm.appendChild(ps); var side = el("div", "post-side"); var feePill = el("span", "pill"); var likePill = el("span", "pill p-muted"); side.appendChild(feePill); side.appendChild(likePill);
    post.appendChild(thumb); post.appendChild(pm); post.appendChild(side); postBlock.appendChild(post); card.appendChild(postBlock);

    var sessBlock = later(el("div", "sub-block rv enter"), base + 340); var stt = el("div", "sub-title"); stt.appendChild(el("span", "", "订阅会话")); var sts = el("small", ""); stt.appendChild(sts); sessBlock.appendChild(stt); var sessList = el("div", ""); sessBlock.appendChild(sessList); card.appendChild(sessBlock);
    return { el: card, base: base, fresh: true, phs: phs, av: av, h3: h3, sub: sub, pill: pill, pRefs: pRefs, mhs: mhs, seg: seg, segRefs: segRefs, lgRefs: lgRefs, chs: chs, bars: bars, barRefs: barRefs, pts: pts, thumb: thumb, pa: pa, ps: ps, feePill: feePill, likePill: likePill, sts: sts, sessList: sessList, sessRows: {} };
  }
  function updateThumb(ref, latest) {
    var key = latest ? (latest.adult && !coverAllowedAdult() ? "hidden:" + latest.id : latest.cover_url || "none") : "none";
    if (ref.thumb._key === key) return; ref.thumb._key = key; ref.thumb.textContent = ""; ref.thumb.className = "thumb";
    if (!latest || !latest.cover_url) { ref.thumb.classList.add("hidden"); ref.thumb.textContent = "无封面"; return; }
    if (key.indexOf("hidden:") === 0) { ref.thumb.classList.add("hidden"); ref.thumb.textContent = "R-18"; return; }
    var img = document.createElement("img"); img.alt = ""; img.referrerPolicy = "no-referrer"; img.loading = "lazy"; img.src = latest.cover_url;
    img.addEventListener("error", function () { ref.thumb.textContent = ""; ref.thumb.classList.add("hidden"); ref.thumb.textContent = "封面加载失败"; });
    ref.thumb.appendChild(img);
  }
  function coverAllowedAdult() { var v = savedValues && savedValues.style; return !!(v && v.send_adult_cover); }
  function buildSess(delay) {
    var r = later(el("div", "sess rv enter"), delay); var name = el("div", "sess-name"); var nb = el("b", ""); var ns = el("span", ""); name.appendChild(nb); name.appendChild(ns);
    var meta = el("div", "sess-meta"); var mt = el("span", ""); var ms = el("small", ""); meta.appendChild(mt); meta.appendChild(ms);
    var act = el("div", "sess-act"); var pv = el("button", "btn sm ghost"); pv.type = "button"; pv.appendChild(iconEl("eye")); pv.appendChild(el("span", "", "预览")); var rm = el("button", "btn sm ghost danger"); rm.type = "button"; rm.appendChild(iconEl("trash")); var rml = el("span", "", "取消订阅"); rm.appendChild(rml); act.appendChild(pv); act.appendChild(rm);
    r.appendChild(name); r.appendChild(meta); r.appendChild(act);
    return { el: r, nb: nb, ns: ns, mt: mt, ms: ms, pv: pv, rm: rm, rml: rml };
  }
  function updateSess(row, cid, cname, umo, info) {
    row.nb.textContent = sessionLabel(umo); row.ns.textContent = sessionSub(umo);
    row.mt.textContent = "订阅于 " + (info.subscribed_at ? new Date(info.subscribed_at).toLocaleString("zh-CN", { hour12: false }) : "—");
    row.ms.textContent = "推送起点 " + (info.floor_at ? new Date(info.floor_at).toLocaleString("zh-CN", { hour12: false }) : "—") + " · 已推送 " + info.pushed_count + " 篇";
    row.pv.onclick = function () { openPreview(cid); };
    row.rm.onclick = function () {
      if (!row.rm._armed) { row.rm._armed = true; row.rml.textContent = "再点一次确认"; clearTimeout(row.rm._t); row.rm._t = setTimeout(function () { row.rm._armed = false; row.rml.textContent = "取消订阅"; }, 3000); return; }
      clearTimeout(row.rm._t); row.rm._armed = false; row.rm.disabled = true; row.rml.textContent = "正在取消…";
      api("POST", "subscriptions/remove", { umo: umo, creator: cid }).then(function () { toast("已取消订阅 " + cname + "（" + sessionLabel(umo) + "）", true); load(); }).catch(function (e) { row.rm.disabled = false; row.rml.textContent = "取消订阅"; toast("取消失败：" + errMsg(e)); });
    };
  }
  function updateCard(ref, c) {
    var st = c.stats || {}, name = c.name || c.creator;
    if (ref.h3.textContent !== name) ref.h3.textContent = name;
    setAvatar(ref.av, name, st.icon_url || "");
    var subBits = [c.creator]; if (st.last_check_at) subBits.push("最近检查 " + ago(st.last_check_at * 1000)); if (st.avg_latency_ms != null) subBits.push("平均 " + st.avg_latency_ms + " ms");
    ref.sub.textContent = subBits.join(" · "); ref.sub.title = st.last_error || "";
    setPill(ref.pill, creatorPill(st));
    var w = ref.fresh ? ref.base + 200 : 0, pu = st.pushes || {}, chk = st.checks || {};
    var vals = { p_hour: pu.hour, p_day: pu.day, p_week: pu.week, p_total: pu.total };
    setText(ref.phs, st.last_push_at ? ("最近一次 " + ago(st.last_push_at * 1000)) : "还没有推送过"); void chk;
    PERIODS.forEach(function (p, i) { setNum(ref.pRefs[p[0]], vals[p[0]] || 0, "compact", w + i * 50); });
    var od = st.outcomes_day || {}, sum = 0; OUT.forEach(function (o) { sum += od[o[0]] || 0; });
    setText(ref.mhs, sum ? ("共 " + full(sum) + " 次") : "暂无检查");
    OUT.forEach(function (o) { var v = od[o[0]] || 0; ref.segRefs[o[0]].style.flexGrow = String(sum ? v : 0); ref.segRefs[o[0]].style.display = v ? "block" : "none"; setNum(ref.lgRefs[o[0]], v, "full", w + 120); });
    if (ref.fresh) fx(ref.seg, [{ clipPath: "inset(0 100% 0 0 round 999px)" }, { clipPath: "inset(0 0% 0 0 round 999px)" }], { duration: 1300, delay: ref.base + 320, easing: EASE, fill: "backwards" });
    var hc = st.hourly_checks || [], hp = st.hourly_pushes || []; ref.el._hc = hc; ref.el._hp = hp;
    var peak = Math.max.apply(null, hc.concat([0])), max = Math.max(1, peak), pushedHours = hp.filter(function (v) { return v > 0; }).length;
    setText(ref.chs, pushedHours ? ("有 " + pushedHours + " 个小时推送了新帖") : ("峰值 " + full(peak) + " 次"));
    ref.barRefs.forEach(function (b, i) { var v = hc[i] || 0, pv = hp[i] || 0; b.wrap.className = "bar" + (pv > 0 || i === 23 ? " now" : "") + (v === 0 ? " zero" : ""); b.wrap.setAttribute("aria-label", hourLabel(i) + "：检查 " + v + " 次，推送 " + pv + " 篇"); b.fill.style.height = v === 0 ? "2px" : (Math.max(4, Math.round(v / max * 100)) + "%"); if (ref.fresh) fx(b.fill, [{ height: "0px", offset: 0 }], { duration: 950, delay: ref.base + 340 + i * 22, easing: EASE, fill: "backwards" }); });
    ref.bars.setAttribute("aria-label", "近 24 小时每小时检查次数，峰值 " + peak + " 次");

    var latest = st.latest;
    setText(ref.pts, st.post_count != null ? ("列表里最近 " + st.post_count + " 篇") : "");
    updateThumb(ref, latest);
    if (latest) {
      ref.pa.textContent = latest.title || "（无标题）"; ref.pa.href = latest.url || ("https://" + c.creator + ".fanbox.cc");
      ref.ps.textContent = "发布于 " + (isoAgo(latest.published) || "—") + (latest.published ? " · " + new Date(latest.published).toLocaleString("zh-CN", { hour12: false }) : "");
      setPill(ref.feePill, latest.fee > 0 ? { cls: "pill p-blue", icon: "lock", text: latest.fee + " 日元" + (latest.adult ? " · R-18" : "") } : { cls: "pill p-good", icon: "check", text: "免费" + (latest.adult ? " · R-18" : "") });
      ref.likePill.hidden = false; ref.likePill.textContent = ""; ref.likePill.appendChild(iconEl("heart")); ref.likePill.appendChild(el("span", "", full(latest.like_count || 0)));
    } else {
      ref.pa.textContent = "还没有检查过"; ref.pa.removeAttribute("href"); ref.ps.textContent = "下一次检查后显示"; setPill(ref.feePill, { cls: "pill p-muted", icon: "dash", text: "—" }); ref.likePill.hidden = true;
    }

    var subsByUmo = {}; data.sessions.forEach(function (s) { s.subscriptions.forEach(function (r) { if (r.creator === c.creator) subsByUmo[s.umo] = r; }); });
    var umos = Object.keys(subsByUmo); setText(ref.sts, umos.length + " 个");
    var existing = Object.keys(ref.sessRows).map(function (k) { return ref.sessRows[k].el; }), seen = {};
    flip(existing, function () { umos.forEach(function (umo, i) { var row = ref.sessRows[umo]; if (!row) { row = buildSess(ref.fresh ? ref.base + 380 + i * 45 : 0); ref.sessRows[umo] = row; } place(ref.sessList, row.el, i); updateSess(row, c.creator, name, umo, subsByUmo[umo]); seen[umo] = 1; }); });
    Object.keys(ref.sessRows).forEach(function (k) { if (!seen[k]) { drop(ref.sessRows[k].el); delete ref.sessRows[k]; } });
    ref.fresh = false;
  }
  function renderCreators() {
    var box = document.getElementById("creators"); var ghost = box.querySelector(":scope > .ghost"); if (ghost) ghost.remove();
    var pl = data.plugin;
    setText(document.getElementById("creatorHint"), "推送起点：" + pl.floor_text + (pl.max_post_age_hours ? " · 不推 " + pl.max_post_age_hours + " 小时前的帖子" : "") + " · 每 30 秒自动刷新");
    if (!data.creators.length) {
      Object.keys(cards).forEach(function (k) { drop(cards[k].el); delete cards[k]; });
      if (!box.querySelector(":scope > .empty")) { var e = el("div", "card empty enter"); e.appendChild(el("b", "", "还没有订阅")); e.appendChild(document.createElement("br")); e.appendChild(el("span", "", "点右上角「添加订阅」，或在 QQ 里发 /fanbox关注 <创作者ID>")); box.appendChild(e); }
      return;
    }
    var emptyNode = box.querySelector(":scope > .empty"); if (emptyNode) emptyNode.remove();
    var existing = Object.keys(cards).map(function (k) { return cards[k].el; }), seen = {};
    flip(existing, function () { data.creators.forEach(function (c, i) { var ref = cards[c.creator]; if (!ref) { ref = buildCard(c, i); cards[c.creator] = ref; } place(box, ref.el, i); updateCard(ref, c); seen[c.creator] = 1; }); });
    Object.keys(cards).forEach(function (k) { if (!seen[k]) { drop(cards[k].el); delete cards[k]; } });
  }

  /* ---------- 推送记录、报错（复用 _stats 的报错行） ---------- */
  function buildLogRow(delay) {
    var r = later(el("article", "err rv enter"), delay); var ic = el("div", "err-ic"); ic.setAttribute("aria-hidden", "true");
    var main = el("div", "err-main"); var top = el("div", "err-top"); var kind = el("b", ""); var ep = el("span", "ep"); var desc = el("span", "dim"); top.appendChild(kind); top.appendChild(ep); top.appendChild(desc);
    var why = el("div", "err-why"); var msg = el("code", "err-msg"); var meta = el("div", "err-meta"); main.appendChild(top); main.appendChild(why); main.appendChild(msg); main.appendChild(meta);
    var side = el("div", "err-side"); var res = el("span", "pill"); var t = el("time", ""); var abs = el("small", ""); side.appendChild(res); side.appendChild(t); side.appendChild(abs);
    r.appendChild(ic); r.appendChild(main); r.appendChild(side);
    return { el: r, ic: ic, kind: kind, ep: ep, desc: desc, why: why, msg: msg, meta: meta, res: res, t: t, abs: abs };
  }
  function setIcon(node, cls, icon) { var sig = cls + "|" + icon; if (node._sig === sig) return; node._sig = sig; node.className = "err-ic " + cls; node.innerHTML = ICON[icon]; }
  function setTime(row, atSec) { var ms = atSec * 1000; row.t.setAttribute("data-ago", String(ms)); row.t.setAttribute("datetime", new Date(ms).toISOString()); row.t.textContent = ago(ms); row.abs.textContent = stamp(ms); }
  function creatorName(cid) { for (var i = 0; i < data.creators.length; i++) if (data.creators[i].creator === cid) return data.creators[i].name; return cid; }
  function updatePushRow(row, p) {
    setIcon(row.ic, p.ok ? "o-push" : "o-fail", p.ok ? "send" : "alert");
    row.kind.textContent = p.ok ? "已推送" : "推送失败";
    row.ep.textContent = ""; var a = el("a", "", p.title || "（无标题）"); if (p.url) { a.href = p.url; a.target = "_blank"; a.rel = "noopener noreferrer"; } row.ep.appendChild(a);
    row.desc.textContent = p.name || p.creator;
    row.why.textContent = "推送到 " + sessionLabel(p.umo) + " · " + (p.style === "card" ? "卡片图" : "文字模板");
    row.msg.hidden = p.ok; if (!p.ok) { row.msg.className = "err-msg"; row.msg.textContent = p.error || "没有错误说明"; }
    row.meta.textContent = p.creator + " · 帖子 " + p.post_id;
    setPill(row.res, p.ok ? { cls: "pill p-good", icon: "check", text: "已送达" } : { cls: "pill p-bad", icon: "alert", text: "下次重试" });
    setTime(row, p.at);
  }
  function updateErrRow(row, e) {
    var k = ERR_KIND[e.kind] || ERR_KIND.list_failed;
    setIcon(row.ic, k[2], k[1]); row.kind.textContent = k[0];
    row.ep.textContent = e.creator ? creatorName(e.creator) : ""; row.desc.textContent = e.creator || "";
    var why = k[3]; if (e.umo) why += " · " + sessionLabel(e.umo); row.why.textContent = why;
    row.msg.hidden = false; row.msg.className = "err-msg" + (e.message ? "" : " none"); row.msg.textContent = e.message || "没有错误文字";
    row.meta.textContent = e.post_id ? ("帖子 " + e.post_id) : "";
    var res = e.kind === "card_failed" ? { cls: "pill p-good", icon: "check", text: "已改发文字" } : e.kind === "send_failed" || e.kind === "list_failed" || e.kind === "blocked" ? { cls: "pill p-muted", icon: "clock", text: "下次重试" } : { cls: "pill p-muted", icon: "dash", text: "已跳过" };
    setPill(row.res, res); setTime(row, e.at);
  }
  function renderLog(boxId, items, rows, update, emptyTitle, emptyText) {
    var box = document.getElementById(boxId); var ghost = box.querySelector(":scope > .err-ghost"); if (ghost) ghost.remove();
    var empty = box.querySelector(":scope > .mini-empty");
    if (!items.length) { if (!empty) { var d = el("div", "mini-empty enter"); d.appendChild(iconEl("check", "err-ic o-ok")); var t = el("div", ""); t.appendChild(el("b", "", emptyTitle)); t.appendChild(el("span", "", emptyText)); d.appendChild(t); box.appendChild(d); } }
    else if (empty) { empty.remove(); }
    var existing = Object.keys(rows).map(function (k) { return rows[k].el; }), seen = {};
    flip(existing, function () { items.forEach(function (it, i) { var row = rows[it.id]; if (!row) { row = buildLogRow(firstRender ? 120 + Math.min(i, 8) * 50 : 0); rows[it.id] = row; } place(box, row.el, i); update(row, it); seen[it.id] = 1; }); });
    Object.keys(rows).forEach(function (k) { if (!seen[k]) { drop(rows[k].el); delete rows[k]; } });
  }
  function renderLogs() {
    var st = data.stats, now = Date.now();
    var pushes = (st.pushes || []).slice(0, 20), errors = (st.errors || []).slice(0, 20);
    var day = (st.pushes || []).filter(function (p) { return now - p.at * 1000 < 86400000; }).length;
    setText(document.getElementById("pushHint"), (st.pushes || []).length ? ("近 24 小时 " + day + " 条 · 最多显示 20 条") : "最近推送到 QQ 的帖子");
    renderLog("pushes", pushes, pushRows, updatePushRow, "还没有推送记录", "有新帖推送后，每一条都会列在这里：推给了哪个会话、用的什么样式、有没有送达");
    var eday = (st.errors || []).filter(function (e) { return now - e.at * 1000 < 86400000; }).length;
    setText(document.getElementById("errHint"), ((st.errors || []).length ? ("近 24 小时 " + eday + " 条 · ") : "") + "保留 30 天，最多显示 20 条");
    renderLog("errors", errors, errRows, updateErrRow, "暂无报错记录", "被 FANBOX 拦截、获取失败、消息没发出去、卡片图渲染失败，都会在这里列出原因和插件的处理结果");
  }

  /* ---------- 设置（按 schema 生成，全部配置项） ---------- */
  function countDirty() { var n = 0; Object.keys(draft).forEach(function (g) { Object.keys(draft[g]).forEach(function (k) { if (JSON.stringify(draft[g][k]) !== JSON.stringify(savedValues[g][k])) n++; }); }); return n; }
  function diffPatch() { var patch = {}; Object.keys(draft).forEach(function (g) { Object.keys(draft[g]).forEach(function (k) { if (JSON.stringify(draft[g][k]) !== JSON.stringify(savedValues[g][k])) { (patch[g] = patch[g] || {})[k] = draft[g][k]; } }); }); return patch; }
  function refreshDirty() {
    var n = countDirty(); document.getElementById("dirtyCount").textContent = String(n);
    document.getElementById("savebar").classList.toggle("show", n > 0);
    Object.keys(controls).forEach(function (id) { var c = controls[id]; c.row.classList.toggle("changed", JSON.stringify(draft[c.g][c.k]) !== JSON.stringify(savedValues[c.g][c.k])); });
    updateStartRows();
  }
  function setDraft(g, k, v) { draft[g][k] = v; refreshDirty(); }
  function updateStartRows() {
    var c = controls["start.start_time"]; if (!c) return;
    var custom = draft.start.start_from === "custom"; c.row.style.opacity = custom ? "" : ".55";
    var ex = controls["start.start_from"]; if (ex && ex.extra) ex.extra.textContent = draft.start.start_from === "deploy" && data ? ("部署时间：" + data.plugin.deployed_text) : draft.start.start_from === "subscribe" ? "每个订阅各自从订阅那一刻开始" : "按下面填写的时间";
  }
  function buildControl(g, k, item) {
    var row = el("div", "set-row"); var lab = el("div", "set-label"); var b = el("b", ""); b.appendChild(el("span", "", item.description || k)); b.appendChild(el("i", "dirty")); lab.appendChild(b);
    var hint = el("p", ""); if (item.hint) hint.textContent = item.hint; var code = el("code", "", g + "." + k); hint.appendChild(document.createTextNode(item.hint ? " " : "")); hint.appendChild(code); lab.appendChild(hint);
    var ctl = el("div", "set-ctl"); var ref = { row: row, g: g, k: k, item: item };
    if (item.type === "bool") {
      var sw = el("button", "switch"); sw.type = "button"; sw.setAttribute("role", "switch"); sw.setAttribute("aria-label", item.description || k);
      sw.addEventListener("click", function () { setDraft(g, k, !draft[g][k]); ref.set(draft[g][k]); });
      ref.set = function (v) { sw.setAttribute("aria-checked", v ? "true" : "false"); }; ctl.appendChild(sw);
    } else if (item.type === "int") {
      var nf = el("div", "num-field"); var minus = el("button", "", "−"); minus.type = "button"; var inp = document.createElement("input"); inp.type = "number"; inp.inputMode = "numeric"; var plus = el("button", "", "+"); plus.type = "button"; var rg = RANGES[k] || [null, null];
      if (rg[0] != null) inp.min = rg[0]; if (rg[1] != null) inp.max = rg[1];
      function commit(v) { v = parseInt(v, 10); if (isNaN(v)) v = savedValues[g][k]; if (rg[0] != null) v = Math.max(rg[0], v); if (rg[1] != null) v = Math.min(rg[1], v); setDraft(g, k, v); ref.set(v); }
      minus.addEventListener("click", function () { commit((draft[g][k] || 0) - 1); }); plus.addEventListener("click", function () { commit((draft[g][k] || 0) + 1); });
      inp.addEventListener("change", function () { commit(inp.value); }); inp.addEventListener("input", function () { var v = parseInt(inp.value, 10); if (!isNaN(v)) { draft[g][k] = v; refreshDirty(); } });
      nf.appendChild(minus); nf.appendChild(inp); nf.appendChild(plus); if (UNITS[k]) nf.appendChild(el("span", "unit", UNITS[k]));
      ref.set = function (v) { if (document.activeElement !== inp) inp.value = String(v); }; ctl.appendChild(nf);
    } else if (item.options && item.options.length) {
      var seg = el("div", "seg"); seg.setAttribute("role", "group"); var btns = {};
      item.options.forEach(function (opt) { var bt = el("button", "", (OPTION_LABELS[k] && OPTION_LABELS[k][opt]) || opt); bt.type = "button"; bt.title = opt; bt.addEventListener("click", function () { setDraft(g, k, opt); ref.set(opt); }); seg.appendChild(bt); btns[opt] = bt; });
      ref.set = function (v) { Object.keys(btns).forEach(function (o) { btns[o].setAttribute("aria-pressed", o === v ? "true" : "false"); }); }; ctl.appendChild(seg);
      ref.extra = el("div", "set-extra"); lab.appendChild(ref.extra);
    } else if (item.type === "text") {
      row.classList.add("wide"); ref.set = buildTemplateEditor(ctl, g, k, item);
    } else {
      var ti = document.createElement("input"); ti.className = "input" + (MONO[k] ? " mono" : ""); ti.type = "text"; ti.spellcheck = false; ti.placeholder = k === "start_time" ? "例如 2026-11-15 08:00" : k === "proxy" ? "例如 http://127.0.0.1:7890" : k === "time_format" ? "%Y-%m-%d %H:%M" : "留空使用默认值";
      ti.addEventListener("input", function () { setDraft(g, k, ti.value); });
      ref.set = function (v) { if (document.activeElement !== ti) ti.value = v == null ? "" : String(v); }; ctl.appendChild(ti);
    }
    row.appendChild(lab); row.appendChild(ctl); controls[g + "." + k] = ref; return row;
  }
  function insertAtCursor(ta, text) { var s = ta.selectionStart, e = ta.selectionEnd, v = ta.value; ta.value = v.slice(0, s) + text + v.slice(e); ta.selectionStart = ta.selectionEnd = s + text.length; ta.focus(); ta.dispatchEvent(new Event("input")); }
  var preview = {};
  function buildTemplateEditor(ctl, g, k, item) {
    var tplData = data.template, wrap = el("div", "tpl");
    var leftCol = el("div", ""); var ta = el("textarea", "textarea"); ta.spellcheck = false; ta.rows = 10; ta.setAttribute("aria-label", "推送模板");
    ta.addEventListener("input", function () { setDraft(g, k, ta.value === tplData["default"] ? "" : ta.value); });
    leftCol.appendChild(ta);
    var tools = el("div", "tpl-tools"); var tl = el("span", "hint", "清空或恢复默认，都使用默认模板"); var reset = el("button", "btn sm", "恢复默认模板"); reset.type = "button";
    reset.addEventListener("click", function () { ta.value = tplData["default"]; setDraft(g, k, ""); }); tools.appendChild(tl); tools.appendChild(reset); leftCol.appendChild(tools);
    var vars = el("div", "vars"); vars.appendChild(el("h4", "", "文字变量（" + Object.keys(tplData.text_variables).length + " 个，点一下插入到光标处）"));
    var chips = el("div", "chips"); Object.keys(tplData.text_variables).forEach(function (name) { var c = el("button", "chip", "{" + name + "}"); c.type = "button"; c.addEventListener("click", function () { insertAtCursor(ta, "{" + name + "}"); }); bindTip(c, function () { return ["{" + name + "}", tplData.text_variables[name]]; }); chips.appendChild(c); }); vars.appendChild(chips);
    vars.appendChild(el("h4", "", "图片变量（写在哪儿，图片就出现在哪儿）"));
    var ichips = el("div", "chips"); Object.keys(tplData.image_variables).forEach(function (name) { var c = el("button", "chip img", "{" + name + "}"); c.type = "button"; c.addEventListener("click", function () { insertAtCursor(ta, "{" + name + "}"); }); bindTip(c, function () { return ["{" + name + "}", tplData.image_variables[name]]; }); ichips.appendChild(c); }); vars.appendChild(ichips);
    var rules = el("ul", "rules"); [["{{ 和 }}", " 表示花括号本身"], ["", "一行里的变量全为空、这一行又没有其他文字时，整行自动删掉"], ["?", " 开头的行：只要行里有一个变量为空，整行就删掉"], ["", "不认识的 {xxx} 原样显示；推送样式选「卡片图」时不用模板"]].forEach(function (r) { var li = el("li", ""); if (r[0]) li.appendChild(el("code", "", r[0])); li.appendChild(document.createTextNode(r[1])); rules.appendChild(li); }); vars.appendChild(rules);
    leftCol.appendChild(vars);

    var pv = el("div", "preview"); var ph = el("div", "preview-head"); var sel = el("select", "select"); sel.setAttribute("aria-label", "预览用的创作者"); var other = document.createElement("input"); other.className = "input mono"; other.placeholder = "其他创作者 ID"; other.hidden = true; other.style.flex = "1";
    var go = el("button", "btn sm primary", "生成预览"); go.type = "button";
    ph.appendChild(sel); ph.appendChild(other); ph.appendChild(go); pv.appendChild(ph);
    var pb = el("div", "preview-body"); pb.appendChild(el("div", "preview-empty", "选一位创作者，看看按当前设置（包括还没保存的修改）推送出来是什么样")); pv.appendChild(pb);
    sel.addEventListener("change", function () { other.hidden = sel.value !== "__other"; if (!other.hidden) other.focus(); });
    go.addEventListener("click", function () { runPreview(); });
    preview = { sel: sel, other: other, go: go, body: pb, box: pv };
    wrap.appendChild(leftCol); wrap.appendChild(pv); ctl.appendChild(wrap);
    fillPreviewCreators();
    return function (v) { if (document.activeElement !== ta) ta.value = v ? v : tplData["default"]; };
  }
  function fillPreviewCreators() {
    if (!preview.sel || !data) return; var cur = preview.sel.value; preview.sel.textContent = "";
    data.creators.forEach(function (c) { var o = el("option", "", c.name + "（" + c.creator + "）"); o.value = c.creator; preview.sel.appendChild(o); });
    var o2 = el("option", "", data.creators.length ? "其他创作者…" : "填写创作者 ID…"); o2.value = "__other"; preview.sel.appendChild(o2);
    if (cur && [].some.call(preview.sel.options, function (o) { return o.value === cur; })) preview.sel.value = cur;
    preview.other.hidden = preview.sel.value !== "__other";
  }
  function openPreview(cid) {
    if (!preview.sel) return; var has = [].some.call(preview.sel.options, function (o) { return o.value === cid; });
    if (has) { preview.sel.value = cid; preview.other.hidden = true; } else { preview.sel.value = "__other"; preview.other.hidden = false; preview.other.value = cid; }
    preview.box.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "center" }); runPreview();
  }
  function runPreview() {
    var cid = preview.sel.value === "__other" ? preview.other.value.trim() : preview.sel.value;
    if (!cid) { toast("先选择或填写一位创作者"); return; }
    busy(preview.go, true, "生成中"); preview.body.textContent = ""; preview.body.appendChild(el("div", "preview-empty", "正在向 FANBOX 获取最新一篇并生成消息…"));
    api("POST", "preview", { creator: cid, values: diffPatch() }).then(function (res) {
      preview.body.textContent = "";
      res.pieces.forEach(function (p, i) {
        var b;
        if (p.type === "text") { b = el("div", "bubble", p.text); }
        else { b = el("div", "bubble img"); var img = document.createElement("img"); img.alt = "预览图片"; img.src = p.src; b.appendChild(img); }
        preview.body.appendChild(b); fx(b, [{ opacity: 0, transform: "translateY(8px) scale(.98)", offset: 0 }], { duration: 600, delay: i * 70, easing: EASE, fill: "backwards" });
      });
      var imgs = res.pieces.filter(function (p) { return p.type === "image"; });
      preview.body.appendChild(el("div", "preview-meta", (res.style === "card" ? "卡片图" : "文字模板") + " · 《" + res.post.title + "》 · " + res.pieces.length + " 段" + (imgs.length ? "（" + imgs.length + " 张图，共 " + Math.round(imgs.reduce(function (s, p) { return s + p.bytes; }, 0) / 1024) + " KB）" : "") + " · 用时 " + res.ms + " ms"));
      measureSoon();
    }).catch(function (e) { preview.body.textContent = ""; preview.body.appendChild(el("div", "preview-empty", "预览失败：" + errMsg(e))); }).then(function () { busy(preview.go, false); });
  }
  function renderSettings() {
    var set = data.settings, box = document.getElementById("settings");
    if (settingsBuilt && countDirty() > 0) { fillPreviewCreators(); return; }  // 正在编辑时不覆盖
    var changed = !savedValues || JSON.stringify(savedValues) !== JSON.stringify(set.values);
    savedValues = clone(set.values); draft = clone(set.values);
    if (!settingsBuilt) {
      box.textContent = ""; controls = {};
      Object.keys(set.schema).forEach(function (g, gi) {
        var body = set.schema[g]; var card = later(el("section", "card set-group rv enter"), firstRender ? 120 + gi * 70 : 0);
        var head = el("div", "set-head"); head.appendChild(iconEl(GROUP_ICON[g] || "gear", "ic")); var ht = el("div", ""); ht.appendChild(el("h3", "", body.description || g)); if (body.hint) ht.appendChild(el("p", "", body.hint)); head.appendChild(ht); card.appendChild(head);
        Object.keys(body.items).forEach(function (k) { card.appendChild(buildControl(g, k, body.items[k])); });
        box.appendChild(card);
      });
      settingsBuilt = true; changed = true;
    }
    if (changed) Object.keys(controls).forEach(function (id) { var c = controls[id]; c.set(draft[c.g][c.k]); });
    fillPreviewCreators(); refreshDirty();
    var w = set.warnings || []; setText(document.getElementById("setHint"), w.length ? ("注意：" + w.join("；")) : "全部设置都能在这里改，保存后立即生效，不用重启");
  }
  function saveSettings() {
    var btn = document.getElementById("saveBtn"), patch = diffPatch(), n = countDirty(); if (!n) return;
    busy(btn, true, "保存中");
    api("POST", "settings/save", { values: patch }).then(function (res) {
      savedValues = clone(draft); refreshDirty();
      toast("已保存 " + n + " 项设置，立即生效" + (res && res.warnings && res.warnings.length ? "（" + res.warnings.join("；") + "）" : ""), true);
      load();
    }).catch(function (e) { toast("没有保存：" + errMsg(e)); }).then(function () { busy(btn, false); });
  }
  function discardSettings() { draft = clone(savedValues); Object.keys(controls).forEach(function (id) { var c = controls[id]; c.set(draft[c.g][c.k]); }); refreshDirty(); toast("已撤销未保存的修改", true); }

  /* ---------- 添加订阅 ---------- */
  function fillSessionSelect() {
    var sel = document.getElementById("addSession"), cur = sel.value; sel.textContent = "";
    var seen = {};
    platforms.forEach(function (p) {
      if (!p.groups.length) return; var og = document.createElement("optgroup"); og.label = "QQ 群（" + p.id + "）";
      p.groups.forEach(function (gr) { var umo = p.id + ":GroupMessage:" + gr.group_id; var o = el("option", "", (gr.group_name || "群 " + gr.group_id) + "（" + gr.group_id + "）"); o.value = umo; og.appendChild(o); seen[umo] = 1; });
      sel.appendChild(og);
    });
    var known = (data ? data.sessions : []).filter(function (s) { return !seen[s.umo]; });
    if (known.length) { var og2 = document.createElement("optgroup"); og2.label = "已有订阅的会话"; known.forEach(function (s) { var o = el("option", "", sessionLabel(s.umo)); o.value = s.umo; og2.appendChild(o); }); sel.appendChild(og2); }
    var pids = platforms.map(function (p) { return p.id; }); if (!pids.length && data) data.sessions.forEach(function (s) { var p = parseUmo(s.umo); if (p && pids.indexOf(p.platform) < 0) pids.push(p.platform); });
    if (pids.length) { var og3 = document.createElement("optgroup"); og3.label = "私聊"; pids.forEach(function (pid) { var o = el("option", "", "私聊（填 QQ 号）· " + pid); o.value = "__friend:" + pid; og3.appendChild(o); }); sel.appendChild(og3); }
    if (!sel.options.length) { var o = el("option", "", "没有可用的会话（QQ 端未连接）"); o.value = ""; sel.appendChild(o); }
    if (cur && [].some.call(sel.options, function (o) { return o.value === cur; })) sel.value = cur;
    document.getElementById("addQQ").hidden = sel.value.indexOf("__friend:") !== 0;
  }
  function loadSessions() {
    return api("GET", "sessions").then(function (res) {
      platforms = (res && res.platforms) || []; groupNames = {};
      platforms.forEach(function (p) { p.groups.forEach(function (gr) { if (gr.group_name) groupNames[p.id + ":" + gr.group_id] = gr.group_name; }); });
      fillSessionSelect(); if (data) { renderCreators(); renderLogs(); }
    }).catch(function () { fillSessionSelect(); });
  }

  /* ---------- 主流程 ---------- */
  function renderFoot() { var pl = data.plugin; document.getElementById("foot").textContent = "astrbot_plugin_fanbox " + (data.version || "") + " · 部署于 " + pl.deployed_text + " · 生成于 " + new Date(data.generated_at).toLocaleString("zh-CN", { hour12: false }); }
  function render() {
    document.getElementById("brandSub").textContent = "astrbot_plugin_fanbox · " + (data.version || "") + " · " + (data.plugin.push_style === "card" ? "卡片图" : "文字模板");
    renderHero(); renderCreators(); renderLogs(); renderSettings(); renderFoot(); fillSessionSelect();
    firstRender = false; tick(); measureSoon();
  }
  function tick() {
    var now = Date.now();
    document.querySelectorAll("[data-until]").forEach(function (n) { var u = Number(n.getAttribute("data-until")); n.textContent = u > now ? left(u) : "即将检查"; });
    document.querySelectorAll("[data-ago]").forEach(function (n) { var v = Number(n.getAttribute("data-ago")); if (!v) return; if (n.id === "liveText") { var s = Math.round((now - v) / 1000); n.textContent = s < 5 ? "实时 · 刚刚更新" : ("实时 · " + s + " 秒前更新"); } else n.textContent = ago(v); });
  }
  var loading = false;
  function load() {
    if (loading) return Promise.resolve(); loading = true;
    return api("GET", "overview").then(function (j) { data = j; render(); setLive(true); }).catch(function (e) { setLive(false); toast("数据加载失败（" + errMsg(e) + "），30 秒后重试"); }).then(function () { loading = false; });
  }

  function wire() {
    document.getElementById("refreshBtn").addEventListener("click", function () { load(); loadSessions(); });
    document.getElementById("saveBtn").addEventListener("click", saveSettings);
    document.getElementById("discardBtn").addEventListener("click", discardSettings);
    var addPanel = document.getElementById("addPanel"), toggle = document.getElementById("addToggle");
    toggle.addEventListener("click", function () { addPanel.hidden = !addPanel.hidden; toggle.textContent = addPanel.hidden ? "添加订阅" : "收起"; if (!addPanel.hidden) { fx(addPanel, [{ opacity: 0, transform: "translateY(-8px) scale(.98)", offset: 0 }], { duration: 600, easing: EASE }); document.getElementById("addCreator").focus(); } measureSoon(); });
    document.getElementById("addSession").addEventListener("change", function () { document.getElementById("addQQ").hidden = this.value.indexOf("__friend:") !== 0; });
    document.getElementById("addForm").addEventListener("submit", function (ev) {
      ev.preventDefault(); var btn = document.getElementById("addSubmit"), creator = document.getElementById("addCreator").value.trim(), sv = document.getElementById("addSession").value, payload = { creator: creator };
      if (!creator) { toast("填一下创作者 ID 或主页链接"); return; }
      if (!sv) { toast("没有可推送的会话"); return; }
      if (sv.indexOf("__friend:") === 0) { var qq = document.getElementById("addQQ").value.trim(); if (!/^\d{5,12}$/.test(qq)) { toast("QQ 号格式不对"); return; } payload.platform = sv.slice(9); payload.type = "FriendMessage"; payload.target = qq; } else { payload.umo = sv; }
      busy(btn, true, "订阅中");
      api("POST", "subscriptions/add", payload).then(function (r) {
        toast("已订阅 " + r.name + " · 推送起点 " + r.floor + (r.pending ? " · 下次检查推送 " + r.will_push + " 篇" : ""), true);
        document.getElementById("addCreator").value = ""; load();
      }).catch(function (e) { toast("订阅失败：" + errMsg(e)); }).then(function () { busy(btn, false); });
    });
    var check = document.getElementById("checkBtn");
    check.addEventListener("click", function () {
      busy(check, true, "检查中");
      api("POST", "check").then(function (r) { toast("检查完成，推送了 " + r.sent + " 篇新帖", true); load(); }).catch(function (e) { toast("检查失败：" + errMsg(e)); }).then(function () { busy(check, false); });
    });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", function () { hideTip(); measureSoon(); });
    if (window.ResizeObserver) new ResizeObserver(function () { measureSoon(); }).observe(document.getElementById("main"));
    document.addEventListener("visibilitychange", function () { if (!document.hidden) load(); });
    window.addEventListener("beforeunload", function (ev) { if (draft && countDirty() > 0) { ev.preventDefault(); ev.returnValue = ""; } });
  }

  document.querySelectorAll(".enter").forEach(function (n) { settle(n); });
  buildTiles(); measure(); wire();
  if (!bridge) { setLive(false, "请从 AstrBot 管理面板打开"); toast("这个页面需要在 AstrBot 管理面板的插件页里打开"); return; }
  bridge.ready().then(function () {
    load(); loadSessions();
    setInterval(load, REFRESH_MS); setInterval(tick, 1000);
  });
})();
