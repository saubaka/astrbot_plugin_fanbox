/* FANBOX 推送面板（AstrBot Plugin Page）。
   样式和动效照搬作者自建 FxTwitter API 的账号统计面板（_stats）；分区切换照着 X 推送面板：
   左上角切换类别（概览 / 推送记录 / 订阅 / 推送样式 / 设置），右侧是当前类别的章节栏，点一下跳到对应小节。
   数据走 window.AstrBotPluginPage 桥：apiGet/apiPost 到插件注册的接口。 */
(function () {
  "use strict";
  var bridge = null; // AstrBot 注入的 window.AstrBotPluginPage，启动时等它就绪

  var ICON = {
    check: '<svg viewBox="0 0 16 16" fill="none"><path d="M3.5 8.5l3 3 6-7" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>',
    lock: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3.2" y="7" width="9.6" height="6.8" rx="2"/><path d="M5.3 7V5.2a2.7 2.7 0 0 1 5.4 0V7"/></svg>',
    alert: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M8 2.2 14.3 13.4H1.7z" stroke-linejoin="round"/><path d="M8 6.6v3M8 11.6v.1"/></svg>',
    dash: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><path d="M4 8h8"/></svg>',
    search: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round"><circle cx="7" cy="7" r="4.3"/><path d="m10.3 10.3 3.2 3.2"/></svg>',
    user: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="8" cy="5.6" r="2.8"/><path d="M2.8 14c.6-2.8 2.7-4.3 5.2-4.3s4.6 1.5 5.2 4.3" stroke-linecap="round"/></svg>',
    users: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="6" cy="5.8" r="2.4"/><path d="M1.8 13.4c.5-2.4 2.2-3.6 4.2-3.6s3.7 1.2 4.2 3.6"/><path d="M10.4 3.6a2.3 2.3 0 0 1 0 4.4M12.2 9.9c1.1.5 1.8 1.6 2 3.1"/></svg>',
    clock: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><circle cx="8" cy="8" r="5.8"/><path d="M8 4.8V8l2.2 1.4"/></svg>',
    cal: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2.5" y="3.4" width="11" height="10.1" rx="2.2"/><path d="M2.5 6.6h11M5.6 2v2.6M10.4 2v2.6" stroke-linecap="round"/></svg>',
    sum: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H4.5L9 8l-4.5 5H12"/></svg>',
    send: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M14 2 7.2 8.8M14 2 9.6 14l-2.4-5.2L2 6.4z"/></svg>',
    gear: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4"><circle cx="8" cy="8" r="2.2"/><path d="M8 1.8v1.6M8 12.6v1.6M14.2 8h-1.6M3.4 8H1.8M12.4 3.6l-1.1 1.1M4.7 11.3l-1.1 1.1M12.4 12.4l-1.1-1.1M4.7 4.7 3.6 3.6" stroke-linecap="round"/></svg>',
    flag: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3.5 14V2.5M3.5 3h8l-1.6 2.8L11.5 8.6h-8"/></svg>',
    layers: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><path d="M8 2 14 5.2 8 8.4 2 5.2z"/><path d="m2 8.2 6 3.2 6-3.2M2 11l6 3.2 6-3.2"/></svg>',
    sliders: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.5 4.5h7M12.5 4.5h1M2.5 11.5h2M7.5 11.5h6"/><circle cx="11" cy="4.5" r="1.6"/><circle cx="6" cy="11.5" r="1.6"/></svg>',
    image: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="2" y="3" width="12" height="10" rx="2"/><circle cx="6" cy="6.6" r="1.2"/><path d="m2.5 12 3.6-3.6 2.6 2.4 2-1.8 2.8 2.6"/></svg>',
    text: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3 3.5h10M8 3.5v9.5M5.5 13h5"/></svg>',
    grid: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="2.3" y="2.3" width="4.6" height="4.6" rx="1.3"/><rect x="9.1" y="2.3" width="4.6" height="4.6" rx="1.3"/><rect x="2.3" y="9.1" width="4.6" height="4.6" rx="1.3"/><rect x="9.1" y="9.1" width="4.6" height="4.6" rx="1.3"/></svg>',
    brush: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M13.6 2.4 7.4 8.6M8.6 9.8 6.2 7.4M6.2 7.4c-1.6-.2-3 .9-3 2.6 0 1.1-.4 2.1-1.2 2.6 2.3.9 4.8.3 5.6-1.6.3-.7.3-1.2.4-1.6"/></svg>',
    eye: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1.6 8s2.4-4.6 6.4-4.6S14.4 8 14.4 8 12 12.6 8 12.6 1.6 8 1.6 8z"/><circle cx="8" cy="8" r="2"/></svg>',
    trash: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M2.8 4.2h10.4M6.4 4.2V2.8h3.2v1.4M4.2 4.2l.6 9h6.4l.6-9"/></svg>',
    copy: '<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"><rect x="5.2" y="5.2" width="8.3" height="8.3" rx="2"/><path d="M10.8 5.2V3.9a1.4 1.4 0 0 0-1.4-1.4H3.9a1.4 1.4 0 0 0-1.4 1.4v5.5a1.4 1.4 0 0 0 1.4 1.4h1.3"/></svg>',
    heart: '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M8 14s-5.6-3.4-5.6-7.4A3.1 3.1 0 0 1 8 4.7a3.1 3.1 0 0 1 5.6 1.9C13.6 10.6 8 14 8 14z"/></svg>'
  };
  var TABS = [["overview", "grid"], ["records", "send"], ["subs", "users"], ["style", "brush"], ["settings", "gear"]];
  var TAB_NAMES = TABS.map(function (t) { return t[0]; });
  var STYLE_GROUPS = ["style", "content", "card"], SETTINGS_GROUPS = ["basic", "start"];
  var GROUP_ICON = { basic: "gear", start: "flag", style: "layers", content: "sliders", card: "image" };
  var OPTION_LABELS = { push_style: { text: "文字模板", card: "卡片图" }, card_text: { merge: "合成一条", separate: "分开发", none: "只发卡片图" }, start_from: { deploy: "部署时间", subscribe: "订阅时间", custom: "自定义时间" } };
  var STYLE_LABELS = { text: "文字模板", card: "卡片图", card_merge: "文字+卡片图（一条）", card_separate: "文字、卡片图分开发" };
  function styleLabel(st) { return STYLE_LABELS[st] || "文字模板"; }
  var CARD_EL = "{card_image}";
  var UNITS = { poll_interval_minutes: "分钟", max_new_posts_per_poll: "篇", max_post_age_hours: "小时", excerpt_max_chars: "字", max_tags: "个", timezone_offset_hours: "小时", card_excerpt_lines: "行", card_title_lines: "行" };
  var RANGES = { poll_interval_minutes: [5, 1440], max_new_posts_per_poll: [1, 20], max_post_age_hours: [0, 8760], excerpt_max_chars: [0, 2000], max_tags: [0, 30], timezone_offset_hours: [-12, 14], card_excerpt_lines: [0, 6], card_title_lines: [1, 4] };
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
  var data = null, groupNames = {}, platforms = [], cards = {}, firstRender = true, currentTab = "overview";
  var errRows = {}, recordView = "cards";
  var settingsBuilt = false, savedValues = null, draft = null, controls = {};
  var tip = document.getElementById("tip"), bar = document.getElementById("topbar");
  function $(id) { return document.getElementById(id); }

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
    var slow = firstRender || node._fresh; if (!slow) fx(node, [{ color: "#f0a0ba", offset: 0 }], { duration: 1600, easing: EASE }); node._fresh = false;
    var t0 = performance.now() + (slow ? (wait || 0) : 0), dur = slow ? 1300 : 800, id = (node._nid || 0) + 1; node._nid = id;
    function step(t) { if (node._nid !== id) return; var k = Math.min(1, Math.max(0, (t - t0) / dur)), e = 1 - Math.pow(1 - k, 4); node.textContent = fmt(Math.round(from + (value - from) * e)); if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  function left(ms) { var s = Math.max(0, Math.round((ms - Date.now()) / 1000)); var h = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), r = s % 60; if (h) return h + " 小时 " + m + " 分"; return m + ":" + (r < 10 ? "0" : "") + r; }
  function ago(ms) { if (!ms) return "—"; var s = Math.max(0, Math.round((Date.now() - ms) / 1000)); if (s < 45) return "刚刚"; if (s < 3600) return Math.round(s / 60) + " 分钟前"; if (s < 86400) return Math.round(s / 3600) + " 小时前"; return Math.round(s / 86400) + " 天前"; }
  function pad2(n) { return (n < 10 ? "0" : "") + n; }
  function stamp(ms) { var d = new Date(ms); return pad2(d.getMonth() + 1) + "-" + pad2(d.getDate()) + " " + pad2(d.getHours()) + ":" + pad2(d.getMinutes()) + ":" + pad2(d.getSeconds()); }
  function cardDate(iso) { var t = Date.parse(iso || ""); if (isNaN(t)) return ""; var d = new Date(t); return d.getFullYear() + "年" + (d.getMonth() + 1) + "月" + d.getDate() + "日 " + pad2(d.getHours()) + ":" + pad2(d.getMinutes()); }
  function isoAgo(iso) { var t = Date.parse(iso || ""); return isNaN(t) ? "" : ago(t); }
  function clone(v) { return JSON.parse(JSON.stringify(v)); }
  function storeGet(k) { try { return window.localStorage.getItem(k); } catch (e) { return null; } }
  function storeSet(k, v) { try { window.localStorage.setItem(k, v); } catch (e) { /* sandbox 里没有 localStorage */ } }
  function copyText(text) {
    function fallback() { var ta = document.createElement("textarea"); ta.value = text; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.left = "-9999px"; document.body.appendChild(ta); ta.select(); var ok = false; try { ok = document.execCommand("copy"); } catch (e) { ok = false; } ta.remove(); return ok; }
    var p;
    try { p = navigator.clipboard && navigator.clipboard.writeText ? navigator.clipboard.writeText(text).then(function () { return true; }, fallback) : Promise.resolve(fallback()); } catch (e) { p = Promise.resolve(fallback()); }
    return p.then(function (ok) { if (ok) toast("已复制链接", true); else toast("复制失败，链接：" + text); });
  }
  function copyBtn(getUrl) { var b = el("button", "copy"); b.type = "button"; b.title = "复制链接"; b.setAttribute("aria-label", "复制链接"); b.innerHTML = ICON.copy; b.addEventListener("click", function (ev) { ev.stopPropagation(); var u = getUrl(); if (u) copyText(u); }); return b; }
  function errMsg(e) { var m = e && e.message ? e.message : String(e || "未知错误"); try { var j = JSON.parse(m); if (j && j.message) return j.message; } catch (x) { /* plain text */ } return m; }
  function img(src, alt) { var i = document.createElement("img"); i.alt = alt || ""; i.referrerPolicy = "no-referrer"; i.loading = "lazy"; i.decoding = "async"; i.src = src; return i; }

  /* ---------- 滚动：内容从底边升起、在顶栏处溶解（照搬 _stats），顺带更新章节栏 ---------- */
  var rvList = [], docH = 0, barH = 120, stickH = 120, frameQueued = false, measureQueued = false;
  var narrowMQ = window.matchMedia ? window.matchMedia("(max-width:1100px)") : null;
  function docTop(n) { var y = 0; while (n) { y += n.offsetTop; n = n.offsetParent; } return y; }
  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }
  function measure() {
    measureQueued = false; rvList = [];
    var nodes = document.querySelectorAll(".rv");
    for (var i = 0; i < nodes.length; i++) { var n = nodes[i]; if (n.classList.contains("leave")) continue; var h = n.offsetHeight; if (!h) continue; rvList.push({ n: n, t: docTop(n), h: h }); }
    docH = document.documentElement.scrollHeight; barH = bar.offsetHeight;
    document.documentElement.style.setProperty("--head-h", barH + "px");
    // 窄屏时章节栏变成吸顶的芯片行，跳转和高亮都要把它的高度一起让开
    var chEl = $("chapters"); stickH = barH + (narrowMQ && narrowMQ.matches && chEl && !chEl.hidden ? chEl.offsetHeight + 12 : 0);
    measureChapters(); frame();
  }
  function measureSoon() { if (!measureQueued) { measureQueued = true; requestAnimationFrame(measure); } }
  function frame() {
    frameQueued = false;
    var sy = Math.max(0, window.pageYOffset || 0), sp = Math.round(Math.min(1, sy / 56) * 1000) / 1000;
    if (bar._sp !== sp) { bar._sp = sp; bar.style.setProperty("--sp", String(sp)); }
    spyChapters(sy);
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
  function onScroll() { if (tip.classList.contains("show")) hideTip(); spyChapters(Math.max(0, window.pageYOffset || 0)); if (!frameQueued) { frameQueued = true; requestAnimationFrame(frame); } }

  /* ---------- tooltip / toast / live ---------- */
  function showTip(target, value, label) { tip.className = "tip"; tip.textContent = ""; tip.appendChild(el("b", "", value)); tip.appendChild(el("span", "", label)); var r = target.getBoundingClientRect(); tip.classList.add("show"); var w = tip.offsetWidth, hgt = tip.offsetHeight; var x = Math.min(window.innerWidth - w - 8, Math.max(8, r.left + r.width / 2 - w / 2)); var y = r.top - hgt - 10; if (y < 8) y = r.bottom + 10; tip.style.left = x + "px"; tip.style.top = y + "px"; }
  function hideTip() { tip.classList.remove("show"); }
  function bindTip(node, getter) { node.addEventListener("pointerenter", function () { var t = getter(); showTip(node, t[0], t[1]); }); node.addEventListener("pointerleave", hideTip); node.addEventListener("focus", function () { var t = getter(); showTip(node, t[0], t[1]); }); node.addEventListener("blur", hideTip); }
  function setLive(ok, msg) { var live = $("live"), txt = $("liveText"), ring = $("ringFg"); live.classList.toggle("err", !ok); if (ok) { txt.setAttribute("data-ago", String(Date.now())); txt.textContent = "实时 · 刚刚更新"; ring.classList.remove("run"); void ring.getBoundingClientRect(); ring.classList.add("run"); } else { txt.removeAttribute("data-ago"); txt.textContent = msg || "连接中断，重试中"; } }
  function toast(msg, ok) { var t = $("toast"); t.textContent = msg; t.classList.toggle("ok", !!ok); t.classList.add("show"); clearTimeout(toast.timer); toast.timer = setTimeout(function () { t.classList.remove("show"); }, ok ? 2800 : 4200); }
  function busy(btn, on, label) { if (on) { btn._label = btn.textContent; btn.disabled = true; btn.textContent = ""; btn.appendChild(el("span", "spin")); btn.appendChild(el("span", "", label || btn._label)); } else { btn.disabled = false; btn.textContent = btn._label || btn.textContent; } }
  function api(method, endpoint, payload) {
    if (!bridge) return Promise.reject(new Error("当前页面没有运行在 AstrBot 管理面板里"));
    return method === "GET" ? bridge.apiGet(endpoint, payload) : bridge.apiPost(endpoint, payload || {});
  }

  /* ---------- 会话名字 ---------- */
  function parseUmo(umo) { var p = String(umo || "").split(":"); if (p.length < 3) return null; return { platform: p[0], type: p[1], id: p.slice(2).join(":") }; }
  function sessionLabel(umo) {
    var p = parseUmo(umo); if (!p) return umo;
    if (p.type === "GroupMessage") { var n = groupNames[p.platform + ":" + p.id]; return n ? n : "群 " + p.id; }
    if (p.type === "FriendMessage") return "私聊 " + p.id;
    return "会话 " + p.id;
  }
  function sessionSub(umo) { var p = parseUmo(umo); if (!p) return ""; return (p.type === "GroupMessage" ? "群号 " : p.type === "FriendMessage" ? "QQ " : "") + p.id + " · " + p.platform; }
  function creatorInfo(cid) { for (var i = 0; data && i < data.creators.length; i++) if (data.creators[i].creator === cid) return data.creators[i]; return null; }
  function creatorName(cid) { var c = creatorInfo(cid); return c ? c.name : cid; }

  /* =================== 分区切换（照着 X 推送面板） =================== */
  function moveIndicator(animate) {
    var active = document.querySelector('.tab[data-tab="' + currentTab + '"]'), ind = $("tabInd"); if (!active) return;
    if (!animate) ind.style.transition = "none";
    ind.style.width = active.offsetWidth + "px"; ind.style.transform = "translateX(" + (active.offsetLeft - 4) + "px)";
    if (!animate) { void ind.offsetWidth; ind.style.transition = ""; }
  }
  function showTab(name, opts) {
    opts = opts || {}; if (TAB_NAMES.indexOf(name) < 0) name = "overview";
    var prev = currentTab; currentTab = name;
    document.querySelectorAll(".tab").forEach(function (t) { var on = t.getAttribute("data-tab") === name; t.setAttribute("aria-selected", on ? "true" : "false"); t.tabIndex = on ? 0 : -1; if (on && opts.focus) t.focus(); });
    TAB_NAMES.forEach(function (t) { var p = $("panel-" + t), vis = t === name; if (p.hidden === !vis) return; p.hidden = !vis; if (vis && !opts.initial) fx(p, [{ opacity: 0, transform: "translateY(10px)", offset: 0 }], { duration: 520, easing: EASE }); });
    moveIndicator(!opts.initial);
    try { if (location.hash !== "#" + name) history.replaceState(null, "", "#" + name); } catch (e) { /* sandbox */ }
    storeSet("fanbox-panel-tab", name);
    if (!opts.keepScroll) window.scrollTo({ top: 0, behavior: opts.initial || reduce ? "auto" : "smooth" });
    if (name === "style" && prev !== "style") onStyleShown();
    rebuildChapters(); measureSoon();
  }
  function wireTabs() {
    var tabs = [].slice.call(document.querySelectorAll(".tab"));
    tabs.forEach(function (t, i) {
      t.insertBefore(iconEl(TABS[i][1], "ic"), t.firstChild);
      t.addEventListener("click", function () { showTab(t.getAttribute("data-tab")); });
      t.addEventListener("keydown", function (ev) { if (ev.key !== "ArrowLeft" && ev.key !== "ArrowRight") return; ev.preventDefault(); var n = tabs[(i + (ev.key === "ArrowRight" ? 1 : tabs.length - 1)) % tabs.length]; showTab(n.getAttribute("data-tab"), { focus: true }); });
    });
    window.addEventListener("hashchange", function () { var n = location.hash.replace(/^#/, ""); if (TAB_NAMES.indexOf(n) >= 0 && n !== currentTab) showTab(n); });
  }

  /* =================== 右侧章节栏 =================== */
  var chapters = [], chapterActive = -1, jumping = 0;
  function rebuildChapters() {
    var panel = $("panel-" + currentTab), list = $("chapterList"), aside = $("chapters");
    // data-chapter-max：只在这个宽度以下才算章节（窄屏时预览排到了表单下面，需要一个跳转入口）
    var nodes = [].slice.call(panel.querySelectorAll("[data-chapter]")).filter(function (n) { var mx = n.getAttribute("data-chapter-max"); return !n.closest("[hidden]") && (!mx || !window.matchMedia || window.matchMedia("(max-width:" + mx + "px)").matches); });
    var sig = currentTab + "|" + nodes.map(function (n) { return n.id + ":" + n.getAttribute("data-chapter"); }).join("|");
    // 内容重画后节点会换成新的，即使章节没变也要更新引用，否则量到的是已经移除的旧节点
    if (list._sig === sig) { nodes.forEach(function (n, i) { if (chapters[i]) chapters[i].node = n; }); measureChapters(); spyChapters(window.pageYOffset || 0); return; }
    list._sig = sig; list.textContent = ""; chapters = []; chapterActive = -1;
    nodes.forEach(function (n, i) {
      var li = el("li", "ch-item" + (n.getAttribute("data-level") === "2" ? " sub" : ""));
      var b = el("button", ""); b.type = "button"; b.appendChild(el("i", "")); b.appendChild(el("span", "", n.getAttribute("data-chapter")));
      b.addEventListener("click", function () { jumpTo(i); }); li.appendChild(b); list.appendChild(li);
      chapters.push({ node: n, item: li, top: 0 });
    });
    aside.hidden = chapters.length < 2;
    measureChapters(); spyChapters(window.pageYOffset || 0);
  }
  // 窄屏的章节芯片行可以横向滚动；高亮的那个不在视野里时把它滚出来
  function revealChip(li) {
    var ol = $("chapterList"); if (ol.scrollWidth <= ol.clientWidth + 1) return;
    var l = li.offsetLeft, r = l + li.offsetWidth, to = null;
    if (l < ol.scrollLeft) to = l - 8; else if (r > ol.scrollLeft + ol.clientWidth) to = r - ol.clientWidth + 8;
    if (to !== null) ol.scrollTo({ left: Math.max(0, to), behavior: reduce ? "auto" : "smooth" });
  }
  function measureChapters() { chapters.forEach(function (c) { c.top = docTop(c.node); }); }
  function jumpTo(i) {
    var c = chapters[i]; if (!c) return; measureChapters();
    var y = Math.max(0, c.top - stickH - 14); jumping = Date.now(); setChapterActive(i);
    window.scrollTo({ top: y, behavior: reduce ? "auto" : "smooth" });
    fx(c.node, [{ boxShadow: "0 0 0 3px var(--blue-200)", offset: 0 }, { boxShadow: "0 0 0 0 transparent" }], { duration: 1400, delay: 350, easing: EASE });
  }
  function setChapterActive(i) {
    if (chapterActive === i) return; chapterActive = i;
    chapters.forEach(function (c, k) { c.item.classList.toggle("on", k === i); });
    if (chapters[i]) revealChip(chapters[i].item);
  }
  function spyChapters(sy) {
    if (!chapters.length || Date.now() - jumping < 700) return;
    var line = sy + stickH + 40, idx = 0;
    for (var i = 0; i < chapters.length; i++) if (chapters[i].top <= line) idx = i;
    if (sy > 0 && sy + window.innerHeight >= document.documentElement.scrollHeight - 4) idx = chapters.length - 1;
    setChapterActive(idx);
  }

  /* =================== 概览：数字块 + 创作者卡片 =================== */
  var TILE_DEFS = [["creators", "订阅创作者", "user"], ["checks", "近 24 小时检查", "search"], ["next", "下次检查", "clock"], ["week", "近 7 天推送", "cal"], ["errors", "近 24 小时报错", "alert"], ["total", "总推送", "sum"]];
  var tileRefs = {};
  function buildTiles() { var box = $("tiles"); box.textContent = ""; TILE_DEFS.forEach(function (d, i) { var t = later(el("div", "tile enter"), 180 + i * 55); var l = el("span", "lbl"); l.appendChild(iconEl(d[2], "ic")); l.appendChild(el("span", "", d[1])); var v = el("span", "val sk", "0000"); v.setAttribute("data-v", "0"); var n = el("span", "note", NBSP); t.appendChild(l); t.appendChild(v); t.appendChild(n); box.appendChild(t); tileRefs[d[0]] = { val: v, note: n }; }); }
  function renderHero() {
    var st = data.stats, ser = st.series, pl = data.plugin, hero = $("heroNum");
    if (hero.classList.contains("sk")) { hero.classList.remove("sk"); fx(hero, [{ opacity: 0, transform: "translateY(10px)", offset: 0 }], { duration: 1000, easing: EASE }); }
    setNum(hero, ser.pushes.periods.day, "full");
    Object.keys(tileRefs).forEach(function (k, i) { var v = tileRefs[k].val; if (v.classList.contains("sk")) { v.classList.remove("sk"); fx(v, [{ opacity: 0, transform: "translateY(6px)", offset: 0 }], { duration: 800, delay: i * 45, easing: EASE, fill: "backwards" }); } });
    var hourly = ser.pushes.hourly, peak = Math.max.apply(null, hourly), peakAt = hourly.lastIndexOf(peak);
    setText($("heroMeta"), peak > 0 ? ("每小时峰值 " + full(peak) + " 篇 · " + (peakAt === 23 ? "最近 1 小时" : "约 " + (23 - peakAt) + " 小时前")) : ("最近 24 小时还没有新帖 · 检查了 " + full(ser.checks.periods.day) + " 次"));
    drawSpark(hourly.some(function (v) { return v > 0; }) ? hourly : ser.checks.hourly);
    var bad = 0; data.creators.forEach(function (c) { var od = (c.stats && c.stats.outcomes_day) || {}; bad += (od.not_found || 0) + (od.blocked || 0) + (od.error || 0); });
    setNum(tileRefs.creators.val, data.creators.length, "compact"); setText(tileRefs.creators.note, data.sessions.length + " 个会话");
    setNum(tileRefs.checks.val, ser.checks.periods.day, "compact"); setText(tileRefs.checks.note, bad ? ("其中 " + bad + " 次没成功") : "全部成功");
    var nv = tileRefs.next.val; nv.removeAttribute("data-v");
    if (pl.polling) { nv.removeAttribute("data-until"); nv.textContent = "检查中"; } else if (pl.next_poll_at) { nv.setAttribute("data-until", String(pl.next_poll_at)); nv.textContent = left(pl.next_poll_at); } else { nv.textContent = "—"; }
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
    $("sparkLine").setAttribute("d", d); $("sparkArea").setAttribute("d", d + " L" + W + " " + H + " L0 " + H + " Z");
    var last = pts[pts.length - 1], dot = $("sparkDot"); dot.style.left = (last[0] / W * 100).toFixed(2) + "%"; dot.style.top = (last[1] / H * 100).toFixed(2) + "%";
  }
  function drawSpark(vals) {
    var from = sparkVals; sparkVals = vals.slice(); var svg = $("spark");
    if (!from || reduce) { paintSpark(vals); if (!svg.classList.contains("drawn")) { svg.classList.add("drawn"); $("sparkDot").classList.add("on"); } return; }
    var id = ++sparkRun, t0 = performance.now();
    function step(t) { if (id !== sparkRun) return; var k = Math.min(1, Math.max(0, (t - t0) / 900)), e = 1 - Math.pow(1 - k, 3); paintSpark(vals.map(function (v, i) { return from[i] + (v - from[i]) * e; })); if (k < 1) requestAnimationFrame(step); }
    requestAnimationFrame(step);
  }
  function setPill(node, p) {
    var sig = p.cls + "|" + p.icon + "|" + p.text; if (node._sig === sig) return;
    var changed = !!node._sig; node._sig = sig; node.className = p.cls; node.textContent = "";
    node.appendChild(iconEl(p.icon)); node.appendChild(el("span", "", p.text));
    if (changed) fx(node, [{ transform: "scale(.9)", offset: 0 }], { duration: 650, easing: "cubic-bezier(.34,1.56,.64,1)" });
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
  function setAvatar(av, name, url) {
    if (av._url === url) return; av._url = url; av.textContent = ""; av.classList.remove("has-img");
    if (url) { var i = img(url); i.addEventListener("error", function () { av.classList.remove("has-img"); av.textContent = (name || "?").slice(0, 2); }); av.classList.add("has-img"); av.appendChild(i); }
    else { av.textContent = (name || "?").slice(0, 2); }
  }
  function adultHidden(adult) { return adult && !(data && data.plugin.send_adult_cover); }
  function buildCard(c, index) {
    var base = firstRender ? 60 + index * 120 : 0;
    var card = later(el("article", "acct card enter"), base); card.id = "ch-creator-" + c.creator; card.setAttribute("data-chapter", c.name || c.creator); card.setAttribute("data-level", "2");
    var head = later(el("header", "acct-head rv enter"), base + 90); var av = el("div", "avatar"); var title = el("div", "acct-title"); var h3 = el("h3", ""); var sub = el("span", "acct-sub"); title.appendChild(h3); title.appendChild(sub);
    var pill = el("span", "pill"); var pvb = el("button", "btn sm ghost"); pvb.type = "button"; pvb.appendChild(iconEl("eye")); pvb.appendChild(el("span", "", "预览样式")); pvb.addEventListener("click", function () { previewFrom(c.creator); });
    head.appendChild(av); head.appendChild(title); head.appendChild(pill); head.appendChild(pvb); card.appendChild(head);
    var body = el("div", "acct-body"); var col = later(el("div", "acct-col rv enter"), base + 160);
    var ph = el("div", "mix-head"); ph.appendChild(el("span", "", "推送篇数")); var phs = el("small", ""); ph.appendChild(phs); col.appendChild(ph);
    var periods = el("div", "periods four"); var pRefs = {}; PERIODS.forEach(function (p) { var cell = el("div", "period"); var b = counter("b", ""); cell.appendChild(b); cell.appendChild(el("span", "", p[1])); periods.appendChild(cell); pRefs[p[0]] = b; }); col.appendChild(periods);
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
    var post = el("div", "post"); var thumb = el("div", "thumb"); var pm = el("div", "post-main"); var trow = el("div", "title-row"); var pa = el("b", ""); trow.appendChild(pa); var pcopy = copyBtn(function () { return pa._url; }); trow.appendChild(pcopy); var ps = el("span", ""); pm.appendChild(trow); pm.appendChild(ps);
    var side = el("div", "post-side"); var feePill = el("span", "pill"); var likePill = el("span", "pill p-muted"); side.appendChild(feePill); side.appendChild(likePill);
    post.appendChild(thumb); post.appendChild(pm); post.appendChild(side); postBlock.appendChild(post); card.appendChild(postBlock);
    return { el: card, base: base, fresh: true, phs: phs, av: av, h3: h3, sub: sub, pill: pill, pRefs: pRefs, mhs: mhs, seg: seg, segRefs: segRefs, lgRefs: lgRefs, chs: chs, bars: bars, barRefs: barRefs, pts: pts, thumb: thumb, pa: pa, pcopy: pcopy, ps: ps, feePill: feePill, likePill: likePill };
  }
  function updateThumb(node, latest) {
    var key = !latest || !latest.cover_url ? "none" : adultHidden(latest.adult) ? "hidden:" + latest.id : latest.cover_url;
    if (node._key === key) return; node._key = key; node.textContent = ""; node.className = "thumb";
    if (key === "none") { node.classList.add("hidden"); node.textContent = "无封面"; return; }
    if (key.indexOf("hidden:") === 0) { node.classList.add("hidden"); node.textContent = "R-18"; return; }
    var i = img(latest.cover_url); i.addEventListener("error", function () { node.textContent = ""; node.classList.add("hidden"); node.textContent = "封面加载失败"; }); node.appendChild(i);
  }
  function updateCard(ref, c) {
    var st = c.stats || {}, name = c.name || c.creator;
    if (ref.h3.textContent !== name) ref.h3.textContent = name;
    if (ref.el.getAttribute("data-chapter") !== name) ref.el.setAttribute("data-chapter", name);
    setAvatar(ref.av, name, st.icon_url || "");
    var subBits = [c.creator]; if (st.last_check_at) subBits.push("最近检查 " + ago(st.last_check_at * 1000)); if (st.avg_latency_ms != null) subBits.push("平均 " + st.avg_latency_ms + " ms"); subBits.push("推到 " + c.sessions.map(sessionLabel).join("、"));
    ref.sub.textContent = subBits.join(" · "); ref.sub.title = st.last_error || "";
    setPill(ref.pill, creatorPill(st));
    var w = ref.fresh ? ref.base + 200 : 0, pu = st.pushes || {};
    var vals = { p_hour: pu.hour, p_day: pu.day, p_week: pu.week, p_total: pu.total };
    setText(ref.phs, st.last_push_at ? ("最近一次 " + ago(st.last_push_at * 1000)) : "还没有推送过");
    PERIODS.forEach(function (p, i) { setNum(ref.pRefs[p[0]], vals[p[0]] || 0, "compact", w + i * 50); });
    var od = st.outcomes_day || {}, sum = 0; OUT.forEach(function (o) { sum += od[o[0]] || 0; });
    setText(ref.mhs, sum ? ("共 " + full(sum) + " 次") : "暂无检查");
    OUT.forEach(function (o) { var v = od[o[0]] || 0; ref.segRefs[o[0]].style.flexGrow = String(sum ? v : 0); ref.segRefs[o[0]].style.display = v ? "block" : "none"; setNum(ref.lgRefs[o[0]], v, "full", w + 120); });
    if (ref.fresh) fx(ref.seg, [{ clipPath: "inset(0 100% 0 0 round 999px)" }, { clipPath: "inset(0 0% 0 0 round 999px)" }], { duration: 1300, delay: ref.base + 320, easing: EASE, fill: "backwards" });
    var hc = st.hourly_checks || [], hp = st.hourly_pushes || []; ref.el._hc = hc; ref.el._hp = hp;
    var peak = Math.max.apply(null, hc.concat([0])), max = Math.max(1, peak), pushedHours = hp.filter(function (v) { return v > 0; }).length;
    setText(ref.chs, pushedHours ? ("有 " + pushedHours + " 个小时推送了新帖") : ("峰值 " + full(peak) + " 次"));
    ref.barRefs.forEach(function (b, i) { var v = hc[i] || 0, pv = hp[i] || 0; b.wrap.className = "bar" + (pv > 0 || i === 23 ? " now" : "") + (v === 0 ? " zero" : ""); b.wrap.setAttribute("aria-label", hourLabel(i) + "：检查 " + v + " 次，推送 " + pv + " 篇"); b.fill.style.height = v === 0 ? "2px" : (Math.max(4, Math.round(v / max * 100)) + "%"); if (ref.fresh) fx(b.fill, [{ height: "0px", offset: 0 }], { duration: 950, delay: ref.base + 340 + i * 22, easing: EASE, fill: "backwards" }); });
    var latest = st.latest;
    setText(ref.pts, st.post_count != null ? ("列表里最近 " + st.post_count + " 篇") : "");
    updateThumb(ref.thumb, latest);
    if (latest) {
      ref.pa.textContent = latest.title || "（无标题）"; ref.pa.title = ref.pa.textContent; ref.pa._url = latest.url || ("https://" + c.creator + ".fanbox.cc"); ref.pcopy.hidden = false;
      ref.ps.textContent = "发布于 " + (isoAgo(latest.published) || "—") + (latest.published ? " · " + cardDate(latest.published) : "");
      setPill(ref.feePill, latest.fee > 0 ? { cls: "pill p-blue", icon: "lock", text: latest.fee + " 日元" + (latest.adult ? " · R-18" : "") } : { cls: "pill p-good", icon: "check", text: "免费" + (latest.adult ? " · R-18" : "") });
      ref.likePill.hidden = false; ref.likePill.textContent = ""; ref.likePill.appendChild(iconEl("heart")); ref.likePill.appendChild(el("span", "", full(latest.like_count || 0)));
    } else {
      ref.pa.textContent = "还没有检查过"; ref.pa._url = ""; ref.pcopy.hidden = true; ref.ps.textContent = "下一次检查后显示"; setPill(ref.feePill, { cls: "pill p-muted", icon: "dash", text: "—" }); ref.likePill.hidden = true;
    }
    ref.fresh = false;
  }
  function renderCreators() {
    var box = $("creators"); var ghost = box.querySelector(":scope > .ghost"); if (ghost) ghost.remove();
    var pl = data.plugin;
    setText($("creatorHint"), "推送起点：" + pl.floor_text + (pl.max_post_age_hours ? " · 不推 " + pl.max_post_age_hours + " 小时前的帖子" : ""));
    if (!data.creators.length) {
      Object.keys(cards).forEach(function (k) { drop(cards[k].el); delete cards[k]; });
      if (!box.querySelector(":scope > .empty")) { var e = el("div", "card empty enter"); e.appendChild(el("b", "", "还没有订阅")); e.appendChild(document.createElement("br")); e.appendChild(el("span", "", "到「订阅」里添加，或在 QQ 里发 /fanbox关注 <创作者ID>")); e.appendChild(document.createElement("br")); var go = el("button", "btn sm primary", "去添加订阅"); go.type = "button"; go.style.marginTop = "12px"; go.addEventListener("click", function () { showTab("subs"); }); e.appendChild(go); box.appendChild(e); }
      return;
    }
    var emptyNode = box.querySelector(":scope > .empty"); if (emptyNode) emptyNode.remove();
    var existing = Object.keys(cards).map(function (k) { return cards[k].el; }), seen = {};
    flip(existing, function () { data.creators.forEach(function (c, i) { var ref = cards[c.creator]; if (!ref) { ref = buildCard(c, i); cards[c.creator] = ref; } place(box, ref.el, i); updateCard(ref, c); seen[c.creator] = 1; }); });
    Object.keys(cards).forEach(function (k) { if (!seen[k]) { drop(cards[k].el); delete cards[k]; } });
  }

  /* =================== 推送记录：FANBOX 卡片 / 列表 =================== */
  function dayKey(ms) { var d = new Date(ms); return d.getFullYear() + "-" + (d.getMonth() + 1) + "-" + d.getDate(); }
  function dayLabel(ms) {
    var d = new Date(ms), t = new Date(); var today = new Date(t.getFullYear(), t.getMonth(), t.getDate()).getTime();
    var that = new Date(d.getFullYear(), d.getMonth(), d.getDate()).getTime(), diff = Math.round((today - that) / 86400000);
    if (diff === 0) return "今天"; if (diff === 1) return "昨天"; if (diff === 2) return "前天";
    return (d.getFullYear() !== t.getFullYear() ? d.getFullYear() + "年" : "") + (d.getMonth() + 1) + "月" + d.getDate() + "日";
  }
  function fbCard(p, delay) {
    /* 和插件生成的卡片图同一套样式：封面、头像、名字、日期、档位、标题、摘要、点赞 */
    var card = later(el("article", "fbcard enter"), delay || 0);
    var cover = el("div", "fb-cover");
    if (p.cover_url && !adultHidden(p.adult)) { var ci = img(p.cover_url); ci.addEventListener("error", function () { cover.textContent = ""; cover.classList.add("ph"); cover.appendChild(el("span", "", "封面加载失败")); }); cover.appendChild(ci); }
    else { cover.classList.add("ph"); cover.appendChild(el("span", "", p.cover_url ? "R-18 · 封面已隐藏" : (p.fee === undefined ? "旧记录没有封面信息" : "FANBOX"))); }
    var status = el("span", "fb-status " + (p.ok ? "ok" : "fail")); status.appendChild(iconEl(p.ok ? "check" : "alert")); status.appendChild(el("span", "", (p.test ? (p.ok ? "测试推送到 " : "测试推送失败 · ") : (p.ok ? "已推送到 " : "推送失败 · ")) + sessionLabel(p.umo) + " · " + styleLabel(p.style)));
    cover.appendChild(status);
    card.appendChild(cover);
    var body = el("div", "fb-body");
    var head = el("div", "fb-head"); var av = el("span", "fb-av"); setAvatar(av, p.name || p.creator, p.icon_url || ""); var who = el("div", "fb-who"); who.appendChild(el("b", "", p.name || p.creator)); who.appendChild(el("span", "", cardDate(p.published) || ("推送于 " + stamp(p.at * 1000))));
    var badges = el("div", "fb-badges"); if (p.adult) badges.appendChild(el("span", "fb-badge adult", "R-18")); if (p.fee !== undefined) badges.appendChild(el("span", "fb-badge", p.fee > 0 ? p.fee + "日元" : "免费"));
    head.appendChild(av); head.appendChild(who); head.appendChild(badges); body.appendChild(head);
    body.appendChild(el("h4", "fb-title", p.title || "（无标题）"));
    if (p.excerpt) body.appendChild(el("p", "fb-excerpt", String(p.excerpt).replace(/\s+/g, " ")));
    var foot = el("div", "fb-foot");
    var meta = el("span", "fb-time"); meta.appendChild(iconEl("send")); var ma = el("span", ""); ma.setAttribute("data-ago", String(p.at * 1000)); ma.textContent = ago(p.at * 1000); meta.appendChild(ma); meta.title = "推送于 " + stamp(p.at * 1000);
    foot.appendChild(meta);
    var tail = el("span", "fb-tail"); if (p.url) tail.appendChild(copyBtn(function () { return p.url; }));
    if (p.like_count !== undefined) { var like = el("span", "fb-like"); like.appendChild(iconEl("heart")); like.appendChild(el("span", "", full(p.like_count || 0))); tail.appendChild(like); }
    foot.appendChild(tail); body.appendChild(foot);
    if (!p.ok && p.error) body.appendChild(el("code", "err-msg", p.error));
    card.appendChild(body);
    return card;
  }
  function renderRecords() {
    var st = data.stats, box = $("records"), pushes = st.pushes || [], now = Date.now();
    var day = pushes.filter(function (p) { return now - p.at * 1000 < 86400000; }).length;
    setText($("pushHint"), pushes.length ? ("近 24 小时 " + day + " 条 · 共保留最近 " + pushes.length + " 条 · 卡片样式和插件生成的卡片图一致") : "推送到 QQ 的帖子，按 FANBOX 网页的卡片样式展示");
    var sig = recordView + "|" + (data.plugin.send_adult_cover ? 1 : 0) + "|" + pushes.map(function (p) { return p.id; }).join(",") + "|" + Object.keys(groupNames).length;
    if (box._sig === sig) return;
    var first = box._sig === undefined; box._sig = sig; box.textContent = "";
    if (!pushes.length) {
      var d = el("div", "card mini-empty enter"); d.appendChild(iconEl("send", "err-ic o-push")); var t = el("div", ""); t.appendChild(el("b", "", "还没有推送记录")); t.appendChild(el("span", "", "有新帖推送后，会按 FANBOX 网页的卡片样式列在这里：封面、作者、档位、标题、摘要，以及推给了哪个会话、有没有送达")); d.appendChild(t); box.appendChild(d);
      return;
    }
    var groups = [], cur = null;
    pushes.forEach(function (p) { var k = dayKey(p.at * 1000); if (!cur || cur.key !== k) { cur = { key: k, label: dayLabel(p.at * 1000), items: [] }; groups.push(cur); } cur.items.push(p); });
    groups.forEach(function (g, gi) {
      var sec = el("section", "day-group"); sec.id = "ch-day-" + g.key; sec.setAttribute("data-chapter", g.label + "（" + g.items.length + "）");
      var h = el("div", "day-head"); h.appendChild(el("b", "", g.label)); h.appendChild(el("span", "hint", g.items.length + " 条")); sec.appendChild(h);
      if (recordView === "cards") {
        var grid = el("div", "fb-grid"); g.items.forEach(function (p, i) { grid.appendChild(fbCard(p, first ? Math.min(i, 8) * 45 + gi * 60 : 0)); }); sec.appendChild(grid);
      } else {
        var list = el("div", "card errs"); g.items.forEach(function (p) { var row = buildLogRow(0); updatePushRow(row, p); list.appendChild(row.el); }); sec.appendChild(list);
      }
      box.appendChild(sec);
    });
  }
  function buildLogRow(delay) {
    var r = later(el("article", "err enter"), delay); var ic = el("div", "err-ic"); ic.setAttribute("aria-hidden", "true");
    var main = el("div", "err-main"); var top = el("div", "err-top"); var kind = el("b", ""); var ep = el("span", "ep"); var desc = el("span", "dim"); top.appendChild(kind); top.appendChild(ep); top.appendChild(desc);
    var why = el("div", "err-why"); var msg = el("code", "err-msg"); var meta = el("div", "err-meta"); main.appendChild(top); main.appendChild(why); main.appendChild(msg); main.appendChild(meta);
    var side = el("div", "err-side"); var res = el("span", "pill"); var t = el("time", ""); var abs = el("small", ""); side.appendChild(res); side.appendChild(t); side.appendChild(abs);
    r.appendChild(ic); r.appendChild(main); r.appendChild(side);
    return { el: r, ic: ic, kind: kind, ep: ep, desc: desc, why: why, msg: msg, meta: meta, res: res, t: t, abs: abs };
  }
  function setIcon(node, cls, icon) { var sig = cls + "|" + icon; if (node._sig === sig) return; node._sig = sig; node.className = "err-ic " + cls; node.innerHTML = ICON[icon]; }
  function setTime(row, atSec) { var ms = atSec * 1000; row.t.setAttribute("data-ago", String(ms)); row.t.setAttribute("datetime", new Date(ms).toISOString()); row.t.textContent = ago(ms); row.abs.textContent = stamp(ms); }
  function updatePushRow(row, p) {
    setIcon(row.ic, p.ok ? "o-push" : "o-fail", p.ok ? "send" : "alert"); row.kind.textContent = (p.test ? "测试" : "") + (p.ok ? "已推送" : "推送失败");
    row.ep.textContent = ""; row.ep.appendChild(el("span", "ttl", p.title || "（无标题）")); if (p.url) row.ep.appendChild(copyBtn(function () { return p.url; }));
    row.desc.textContent = p.name || p.creator; row.why.textContent = "推送到 " + sessionLabel(p.umo) + " · " + styleLabel(p.style);
    row.msg.hidden = p.ok; if (!p.ok) { row.msg.className = "err-msg"; row.msg.textContent = p.error || "没有错误说明"; }
    row.meta.textContent = p.creator + " · 帖子 " + p.post_id;
    setPill(row.res, p.ok ? { cls: "pill p-good", icon: "check", text: "已送达" } : { cls: "pill p-bad", icon: "alert", text: "下次重试" }); setTime(row, p.at);
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
  function renderErrors() {
    var st = data.stats, now = Date.now(), items = (st.errors || []).slice(0, 30), box = $("errors");
    var eday = (st.errors || []).filter(function (e) { return now - e.at * 1000 < 86400000; }).length;
    setText($("errHint"), ((st.errors || []).length ? ("近 24 小时 " + eday + " 条 · ") : "") + "保留 30 天，最多显示 30 条");
    var ghost = box.querySelector(":scope > .err-ghost"); if (ghost) ghost.remove();
    var empty = box.querySelector(":scope > .mini-empty");
    if (!items.length) { if (!empty) { var d = el("div", "mini-empty"); d.appendChild(iconEl("check", "err-ic o-ok")); var t = el("div", ""); t.appendChild(el("b", "", "暂无报错记录")); t.appendChild(el("span", "", "被 FANBOX 拦截、获取失败、消息没发出去、卡片图渲染失败，都会在这里列出原因和插件的处理结果")); d.appendChild(t); box.appendChild(d); } }
    else if (empty) { empty.remove(); }
    var existing = Object.keys(errRows).map(function (k) { return errRows[k].el; }), seen = {};
    flip(existing, function () { items.forEach(function (it, i) { var row = errRows[it.id]; if (!row) { row = buildLogRow(firstRender ? 120 + Math.min(i, 8) * 50 : 0); errRows[it.id] = row; } place(box, row.el, i); updateErrRow(row, it); seen[it.id] = 1; }); });
    Object.keys(errRows).forEach(function (k) { if (!seen[k]) { drop(errRows[k].el); delete errRows[k]; } });
  }

  /* =================== 订阅：添加 + 按会话管理 =================== */
  function renderSessions() {
    var box = $("sessions");
    var sig = JSON.stringify(data.sessions) + "|" + JSON.stringify(groupNames) + "|" + data.creators.map(function (c) { return c.creator + ((c.stats || {}).icon_url || ""); }).join(",");
    if (box._sig === sig) return; box._sig = sig; box.textContent = "";
    if (!data.sessions.length) { var e = el("div", "card mini-empty"); e.appendChild(iconEl("users", "err-ic o-push")); var t = el("div", ""); t.appendChild(el("b", "", "还没有订阅")); t.appendChild(el("span", "", "用上面的表单添加；每个会话会在这里单独成一块，右侧章节栏可以直接跳过去")); e.appendChild(t); box.appendChild(e); return; }
    data.sessions.forEach(function (s) {
      var sec = el("section", "card sess-card"); sec.id = "ch-sess-" + s.umo.replace(/[^A-Za-z0-9_-]/g, "_"); sec.setAttribute("data-chapter", sessionLabel(s.umo));
      var h = el("div", "sess-card-head"); var hn = el("div", ""); hn.appendChild(el("h3", "", sessionLabel(s.umo))); hn.appendChild(el("span", "hint", sessionSub(s.umo) + " · 订阅了 " + s.subscriptions.length + " 位创作者")); h.appendChild(hn); sec.appendChild(h);
      s.subscriptions.forEach(function (r) {
        var row = el("div", "sess"); var name = el("div", "sess-name"); var top = el("div", "sess-who"); var av = el("span", "fb-av sm"); var ci = creatorInfo(r.creator); setAvatar(av, r.name, ci && ci.stats ? ci.stats.icon_url || "" : ""); top.appendChild(av); var nb = el("div", ""); nb.appendChild(el("b", "", r.name)); nb.appendChild(el("span", "", r.creator)); top.appendChild(nb); name.appendChild(top);
        var meta = el("div", "sess-meta"); meta.appendChild(el("span", "", "订阅于 " + (r.subscribed_at ? new Date(r.subscribed_at).toLocaleString("zh-CN", { hour12: false }) : "—"))); meta.appendChild(el("small", "", "推送起点 " + (r.floor_at ? new Date(r.floor_at).toLocaleString("zh-CN", { hour12: false }) : "—") + " · 已推送 " + r.pushed_count + " 篇"));
        var act = el("div", "sess-act"); var pv = el("button", "btn sm ghost"); pv.type = "button"; pv.appendChild(iconEl("eye")); pv.appendChild(el("span", "", "预览样式")); pv.addEventListener("click", function () { previewFrom(r.creator); });
        var rm = el("button", "btn sm ghost danger"); rm.type = "button"; rm.appendChild(iconEl("trash")); var rml = el("span", "", "取消订阅"); rm.appendChild(rml);
        rm.addEventListener("click", function () {
          if (!rm._armed) { rm._armed = true; rml.textContent = "再点一次确认"; clearTimeout(rm._t); rm._t = setTimeout(function () { rm._armed = false; rml.textContent = "取消订阅"; }, 3000); return; }
          clearTimeout(rm._t); rm._armed = false; rm.disabled = true; rml.textContent = "正在取消…";
          api("POST", "subscriptions/remove", { umo: s.umo, creator: r.creator }).then(function () { toast("已取消订阅 " + r.name + "（" + sessionLabel(s.umo) + "）", true); load(); }).catch(function (e) { rm.disabled = false; rml.textContent = "取消订阅"; toast("取消失败：" + errMsg(e)); });
        });
        act.appendChild(pv); act.appendChild(rm); row.appendChild(name); row.appendChild(meta); row.appendChild(act); sec.appendChild(row);
      });
      box.appendChild(sec);
    });
  }
  function fillSessionSelect() { fillSessionsInto($("addSession"), $("addQQ")); fillSessionsInto($("pvSession"), $("pvQQ"), "请选择要测试推送到的会话"); }
  function fillSessionsInto(sel, qq, placeholder) {
    var cur = sel.value; sel.textContent = ""; var seen = {};
    // 测试推送会真的发消息，默认不选任何会话，避免误发到群里
    if (placeholder) { var ph = el("option", "", placeholder); ph.value = ""; sel.appendChild(ph); }
    platforms.forEach(function (p) { if (!p.groups.length) return; var og = document.createElement("optgroup"); og.label = "QQ 群（" + p.id + "）"; p.groups.forEach(function (gr) { var umo = p.id + ":GroupMessage:" + gr.group_id; var o = el("option", "", (gr.group_name || "群 " + gr.group_id) + "（" + gr.group_id + "）"); o.value = umo; og.appendChild(o); seen[umo] = 1; }); sel.appendChild(og); });
    var known = (data ? data.sessions : []).filter(function (s) { return !seen[s.umo]; });
    if (known.length) { var og2 = document.createElement("optgroup"); og2.label = "已有订阅的会话"; known.forEach(function (s) { var o = el("option", "", sessionLabel(s.umo)); o.value = s.umo; og2.appendChild(o); }); sel.appendChild(og2); }
    var pids = platforms.map(function (p) { return p.id; }); if (!pids.length && data) data.sessions.forEach(function (s) { var p = parseUmo(s.umo); if (p && pids.indexOf(p.platform) < 0) pids.push(p.platform); });
    if (pids.length) { var og3 = document.createElement("optgroup"); og3.label = "私聊"; pids.forEach(function (pid) { var o = el("option", "", "私聊（填 QQ 号）· " + pid); o.value = "__friend:" + pid; og3.appendChild(o); }); sel.appendChild(og3); }
    if (sel.options.length === (placeholder ? 1 : 0)) { var o = el("option", "", "没有可用的会话（QQ 端未连接）"); o.value = ""; sel.appendChild(o); }
    if (cur && [].some.call(sel.options, function (o) { return o.value === cur; })) sel.value = cur;
    qq.hidden = sel.value.indexOf("__friend:") !== 0;
  }
  function sessionPayload(sel, qq, payload) {
    var sv = sel.value; if (!sv) { toast("没有可推送的会话"); return null; }
    if (sv.indexOf("__friend:") === 0) { var q = qq.value.trim(); if (!/^\d{5,12}$/.test(q)) { toast("QQ 号格式不对"); return null; } payload.platform = sv.slice(9); payload.type = "FriendMessage"; payload.target = q; payload._label = "私聊 " + q; }
    else { payload.umo = sv; payload._label = sessionLabel(sv); }
    return payload;
  }
  function loadSessions() {
    return api("GET", "sessions").then(function (res) {
      platforms = (res && res.platforms) || []; groupNames = {};
      platforms.forEach(function (p) { p.groups.forEach(function (gr) { if (gr.group_name) groupNames[p.id + ":" + gr.group_id] = gr.group_name; }); });
      fillSessionSelect(); if (data) { renderCreators(); renderRecords(); renderErrors(); renderSessions(); rebuildChapters(); }
    }).catch(function () { fillSessionSelect(); });
  }

  /* =================== 设置（按 schema 生成） =================== */
  function countDirty() { if (!draft) return 0; var n = 0; Object.keys(draft).forEach(function (g) { Object.keys(draft[g]).forEach(function (k) { if (JSON.stringify(draft[g][k]) !== JSON.stringify(savedValues[g][k])) n++; }); }); return n; }
  function diffPatch() { var patch = {}; if (!draft) return patch; Object.keys(draft).forEach(function (g) { Object.keys(draft[g]).forEach(function (k) { if (JSON.stringify(draft[g][k]) !== JSON.stringify(savedValues[g][k])) { (patch[g] = patch[g] || {})[k] = draft[g][k]; } }); }); return patch; }
  function refreshDirty() {
    var n = countDirty(); $("dirtyCount").textContent = String(n); $("savebar").classList.toggle("show", n > 0);
    document.body.classList.toggle("has-savebar", n > 0); // 给保存条留出位置，别挡住预览面板底部
    Object.keys(controls).forEach(function (id) { var c = controls[id]; c.row.classList.toggle("changed", JSON.stringify(draft[c.g][c.k]) !== JSON.stringify(savedValues[c.g][c.k])); });
    updateStartRows();
  }
  function setDraft(g, k, v) { draft[g][k] = v; refreshDirty(); if (g === "style") updateStyleRows(); if (g === "start") updateStartRows(); if (STYLE_GROUPS.indexOf(g) >= 0) schedulePreview(450); }
  // 显示/隐藏一块设置：隐藏时淡出并收起高度，出现时展开并淡入；首次渲染不做动画
  function setShown(el, show, animate) {
    if (!el) return false;
    var visible = !el.hidden && !el._leaving;
    if (visible === show) return false;
    if (el._anim) { el._anim.cancel(); el._anim = null; el.style.overflow = ""; }
    if (!animate || reduce || typeof el.animate !== "function") { el.hidden = !show; el._leaving = false; return true; }
    var collapsed = { height: "0px", paddingTop: "0px", paddingBottom: "0px", marginTop: "0px", marginBottom: "0px" };
    if (show) {
      el.hidden = false; el._leaving = false;
      var cs = getComputedStyle(el);
      var open = { opacity: 1, transform: "none", height: el.offsetHeight + "px", paddingTop: cs.paddingTop, paddingBottom: cs.paddingBottom, marginTop: cs.marginTop, marginBottom: cs.marginBottom };
      el.style.overflow = "hidden";
      el._anim = el.animate([Object.assign({ opacity: 0, transform: "translateY(14px) scale(.98)" }, collapsed), open], { duration: 520, easing: EASE });
      el._anim.onfinish = function () { el._anim = null; el.style.overflow = ""; measureSoon(); };
    } else {
      var cs2 = getComputedStyle(el);
      var from = { opacity: 1, transform: "none", height: el.offsetHeight + "px", paddingTop: cs2.paddingTop, paddingBottom: cs2.paddingBottom, marginTop: cs2.marginTop, marginBottom: cs2.marginBottom };
      el._leaving = true; el.style.overflow = "hidden";
      el._anim = el.animate([from, Object.assign({ opacity: 0, transform: "translateY(-10px) scale(.98)" }, collapsed)], { duration: 400, easing: EASE });
      el._anim.onfinish = function () { el.hidden = true; el._leaving = false; el._anim = null; el.style.overflow = ""; rebuildChapters(); measureSoon(); };
    }
    return true;
  }
  var styleRowsReady = false;
  // 只显示当前推送样式用得到的设置：卡片图 → 卡片图配文、卡片图外观；文字模板 → 推送模板、附带封面图
  function updateStyleRows() {
    if (!draft.style || !controls["style.push_style"]) return;
    var animate = styleRowsReady, card = draft.style.push_style === "card", mode = draft.style.card_text;
    var tpl = draft.style.message_template || (data && data.template ? data.template["default"] : "") || "";
    var ct = controls["style.card_text"];
    if (ct) { setShown(ct.row, card, animate); if (ct.extra) ct.extra.textContent = mode === "merge" ? "一条消息：按配文模板的顺序，卡片图上下都可以放文字" : mode === "separate" ? "按卡片图切开：上方文字、卡片图、下方文字各发一条" : "不发文字，只发卡片图"; }
    var sc = controls["style.send_cover"]; if (sc) setShown(sc.row, !card, animate);
    var changed = false;
    changed = setShown($("ch-template"), !card, animate) || changed;
    changed = setShown($("ch-card-text"), card && mode !== "none", animate) || changed;
    changed = setShown($("ch-card"), card || tpl.indexOf("{card_image}") >= 0, animate) || changed;  // 文字模板里用了卡片图时也要能调外观
    styleRowsReady = true;
    if (changed) { rebuildChapters(); measureSoon(); }
  }
  function updateStartRows() {
    var anim = styleRowsReady;  // 第一次（刚建好设置表单时）不做动画
    updateStyleRows();
    var c = controls["start.start_time"]; if (!c) return; setShown(c.row, draft.start.start_from === "custom", anim);
    var ex = controls["start.start_from"]; if (ex && ex.extra) ex.extra.textContent = draft.start.start_from === "deploy" && data ? ("部署时间：" + data.plugin.deployed_text) : draft.start.start_from === "subscribe" ? "每个订阅各自从订阅那一刻开始" : "按下面填写的时间";
  }
  function buildControl(g, k, item) {
    var row = el("div", "set-row"); var lab = el("div", "set-label"); var b = el("b", ""); b.appendChild(el("span", "", item.description || k)); b.appendChild(el("i", "dirty")); lab.appendChild(b);
    var hint = el("p", ""); if (item.hint) hint.textContent = item.hint; hint.appendChild(document.createTextNode(item.hint ? " " : "")); hint.appendChild(el("code", "", g + "." + k)); lab.appendChild(hint);
    var ctl = el("div", "set-ctl"); var ref = { row: row, g: g, k: k, item: item };
    if (item.type === "bool") {
      var sw = el("button", "switch"); sw.type = "button"; sw.setAttribute("role", "switch"); sw.setAttribute("aria-label", item.description || k);
      sw.addEventListener("click", function () { setDraft(g, k, !draft[g][k]); ref.set(draft[g][k]); }); ref.set = function (v) { sw.setAttribute("aria-checked", v ? "true" : "false"); }; ctl.appendChild(sw);
    } else if (item.type === "int") {
      var nf = el("div", "num-field"); var minus = el("button", "", "−"); minus.type = "button"; var inp = document.createElement("input"); inp.type = "number"; inp.inputMode = "numeric"; var plus = el("button", "", "+"); plus.type = "button"; var rg = RANGES[k] || [null, null];
      if (rg[0] != null) inp.min = rg[0]; if (rg[1] != null) inp.max = rg[1];
      var commit = function (v) { v = parseInt(v, 10); if (isNaN(v)) v = savedValues[g][k]; if (rg[0] != null) v = Math.max(rg[0], v); if (rg[1] != null) v = Math.min(rg[1], v); setDraft(g, k, v); ref.set(v); };
      minus.addEventListener("click", function () { commit((draft[g][k] || 0) - 1); }); plus.addEventListener("click", function () { commit((draft[g][k] || 0) + 1); });
      inp.addEventListener("change", function () { commit(inp.value); }); inp.addEventListener("input", function () { var v = parseInt(inp.value, 10); if (!isNaN(v)) { draft[g][k] = v; refreshDirty(); if (STYLE_GROUPS.indexOf(g) >= 0) schedulePreview(700); } });
      nf.appendChild(minus); nf.appendChild(inp); nf.appendChild(plus); if (UNITS[k]) nf.appendChild(el("span", "unit", UNITS[k]));
      ref.set = function (v) { if (document.activeElement !== inp) inp.value = String(v); }; ctl.appendChild(nf);
    } else if (item.options && item.options.length) {
      var seg = el("div", "seg"); seg.setAttribute("role", "group"); var btns = {};
      item.options.forEach(function (opt) { var bt = el("button", "", (OPTION_LABELS[k] && OPTION_LABELS[k][opt]) || opt); bt.type = "button"; bt.title = opt; bt.addEventListener("click", function () { setDraft(g, k, opt); ref.set(opt); }); seg.appendChild(bt); btns[opt] = bt; });
      ref.set = function (v) { Object.keys(btns).forEach(function (o) { btns[o].setAttribute("aria-pressed", o === v ? "true" : "false"); }); }; ctl.appendChild(seg);
      ref.extra = el("div", "set-extra"); lab.appendChild(ref.extra);
    } else if (item.type === "text") {
      row.classList.add("wide"); ref.set = buildTemplateEditor(ctl, g, k);
    } else {
      var ti = document.createElement("input"); ti.className = "input" + (MONO[k] ? " mono" : ""); ti.type = "text"; ti.spellcheck = false; ti.placeholder = k === "start_time" ? "例如 2026-11-15 08:00" : k === "proxy" ? "例如 http://127.0.0.1:7890" : k === "time_format" ? "%Y-%m-%d %H:%M" : "留空使用默认值";
      ti.addEventListener("input", function () { draft[g][k] = ti.value; refreshDirty(); if (STYLE_GROUPS.indexOf(g) >= 0) schedulePreview(800); });
      ref.set = function (v) { if (document.activeElement !== ti) ti.value = v == null ? "" : String(v); }; ctl.appendChild(ti);
    }
    row.appendChild(lab); row.appendChild(ctl); controls[g + "." + k] = ref; return row;
  }
  function insertAtCursor(ta, text) { var s = ta.selectionStart, e = ta.selectionEnd, v = ta.value; ta.value = v.slice(0, s) + text + v.slice(e); ta.selectionStart = ta.selectionEnd = s + text.length; ta.focus(); ta.dispatchEvent(new Event("input")); }
  function buildTemplateEditor(ctl, g, k) {
    var tplData = data.template, isCard = k === "card_template", def = isCard ? tplData.card_default : tplData["default"], wrap = el("div", "tpl-one" + (isCard ? " card-tpl" : ""));
    var ta = el("textarea", "textarea"); ta.spellcheck = false; ta.rows = isCard ? 6 : 9; ta.setAttribute("aria-label", isCard ? "卡片图配文模板" : "推送模板");
    // 卡片图配文模板：{card_image} 是卡片图本身，必须有且只能有一个（删掉会立即恢复，多插的只留第一个）
    var prev = "", lockNote = null, lockTimer = 0;
    function cardCount(v) { return v.split(CARD_EL).length - 1; }
    function keepFirstCard(v) { var i = v.indexOf(CARD_EL) + CARD_EL.length; return v.slice(0, i) + v.slice(i).split(CARD_EL).join(""); }
    function showLock(msg) { if (!lockNote) return; lockNote.textContent = msg; lockNote.hidden = false; clearTimeout(lockTimer); lockTimer = setTimeout(function () { lockNote.hidden = true; }, 3200); }
    ta.addEventListener("input", function () {
      if (isCard) {
        var n = cardCount(ta.value);
        if (n === 0) { var pos = ta.selectionStart; ta.value = prev; ta.selectionStart = ta.selectionEnd = Math.min(pos, prev.length); showLock("{card_image} 是卡片图本身，不能删除；想换位置，把光标放到目标行，再点「把卡片图移到光标处」"); }
        else if (n > 1) { var p2 = ta.selectionStart; ta.value = keepFirstCard(ta.value); ta.selectionStart = ta.selectionEnd = Math.min(p2, ta.value.length); showLock("卡片图只能有一个，多出来的 {card_image} 已去掉"); }
        prev = ta.value;
      }
      draft[g][k] = ta.value === def ? "" : ta.value; refreshDirty(); schedulePreview(600);
      if (k === "message_template") updateStyleRows();  // 模板里加上或去掉 {card_image} 时，卡片图外观那组跟着出现或收起
    });
    wrap.appendChild(ta);
    if (isCard) { lockNote = el("div", "tpl-lock"); lockNote.hidden = true; lockNote.setAttribute("role", "status"); wrap.appendChild(lockNote); }
    var tools = el("div", "tpl-tools"); tools.appendChild(el("span", "hint", isCard ? "{card_image} 上面的文字在卡片图上方，下面的文字在卡片图下方；清空或恢复默认，都使用默认配文" : "清空或恢复默认，都使用默认模板；推送样式选「卡片图」时改用「卡片图配文模板」"));
    if (isCard) {
      var move = el("button", "btn sm", "把卡片图移到光标处"); move.type = "button";
      move.addEventListener("click", function () {
        var v = ta.value, pos = ta.selectionStart, i = v.indexOf(CARD_EL); if (i < 0) return;
        var start = i, end = i + CARD_EL.length, ls = v.lastIndexOf("\n", i - 1) + 1, le = v.indexOf("\n", end); if (le < 0) le = v.length;
        if (!v.slice(ls, i).trim() && !v.slice(end, le).trim()) { start = ls; end = le < v.length ? le + 1 : le; if (end === v.length && start > 0) start -= 1; } // 卡片图独占一行时连这一行一起移走
        if (pos > start) pos = pos >= end ? pos - (end - start) : start;
        var rest = v.slice(0, start) + v.slice(end), before = rest.slice(0, pos), after = rest.slice(pos);
        var ins = (before && !/\n$/.test(before) ? "\n" : "") + CARD_EL + (after && !/^\n/.test(after) ? "\n" : "");
        ta.value = before + ins + after; ta.focus(); ta.selectionStart = ta.selectionEnd = before.length + ins.length; ta.dispatchEvent(new Event("input"));
      });
      tools.appendChild(move);
    }
    var reset = el("button", "btn sm", isCard ? "恢复默认配文" : "恢复默认模板"); reset.type = "button";
    reset.addEventListener("click", function () { ta.value = def; prev = def; draft[g][k] = ""; refreshDirty(); schedulePreview(200); }); tools.appendChild(reset); wrap.appendChild(tools);
    var vars = el("div", "vars"); vars.appendChild(el("h4", "", "文字变量（" + Object.keys(tplData.text_variables).length + " 个，点一下插入到光标处）"));
    var chips = el("div", "chips"); Object.keys(tplData.text_variables).forEach(function (name) { var c = el("button", "chip", "{" + name + "}"); c.type = "button"; c.addEventListener("click", function () { insertAtCursor(ta, "{" + name + "}"); }); bindTip(c, function () { return ["{" + name + "}", tplData.text_variables[name]]; }); chips.appendChild(c); }); vars.appendChild(chips);
    if (isCard) { var cardRow = el("div", "card-el"); cardRow.appendChild(el("code", "", CARD_EL)); cardRow.appendChild(el("span", "", "卡片图元素：切换到卡片图样式时默认就有，不能删除，只能有一个；放在哪一行，卡片图就出现在哪儿（其他图片变量在这里会被忽略）")); vars.appendChild(cardRow); }
    if (!isCard) { vars.appendChild(el("h4", "", "图片变量（写在哪儿，图片就出现在哪儿）"));
    var ichips = el("div", "chips"); Object.keys(tplData.image_variables).forEach(function (name) { var c = el("button", "chip img", "{" + name + "}"); c.type = "button"; c.addEventListener("click", function () { insertAtCursor(ta, "{" + name + "}"); }); bindTip(c, function () { return ["{" + name + "}", tplData.image_variables[name]]; }); ichips.appendChild(c); }); vars.appendChild(ichips); }
    var rules = el("ul", "rules"); [["{{ 和 }}", " 表示花括号本身"], ["", "一行里的变量全为空、这一行又没有其他文字时，整行自动删掉"], ["?", " 开头的行：只要行里有一个变量为空，整行就删掉"], ["", "不认识的 {xxx} 原样显示"]].forEach(function (r) { var li = el("li", ""); if (r[0]) li.appendChild(el("code", "", r[0])); li.appendChild(document.createTextNode(r[1])); rules.appendChild(li); }); vars.appendChild(rules);
    wrap.appendChild(vars); ctl.appendChild(wrap);
    return function (v) { if (document.activeElement !== ta) { ta.value = v ? v : def; prev = ta.value; } };
  }
  function groupCard(id, title, hint, icon, rows, delay) {
    var card = later(el("section", "card set-group rv enter"), delay); card.id = id; card.setAttribute("data-chapter", title);
    var head = el("div", "set-head"); head.appendChild(iconEl(icon, "ic")); var ht = el("div", ""); ht.appendChild(el("h3", "", title)); if (hint) ht.appendChild(el("p", "", hint)); head.appendChild(ht); card.appendChild(head);
    rows.forEach(function (r) { card.appendChild(r); }); return card;
  }
  var PAGE_HINTS = { basic: "轮询频率和网络。", card: "卡片图的外观。推送样式为卡片图，或推送模板里用到 {card_image} 时显示。" };
  function buildSettings() {
    var schema = data.settings.schema; controls = {};
    var sf = $("styleForms"), gf = $("settingsForms"); sf.textContent = ""; gf.textContent = "";
    var items = schema.style.items, d = firstRender ? 80 : 0;
    var styleRows = ["push_style", "card_text", "send_cover", "send_adult_cover", "creator_cover_fallback"].filter(function (k) { return items[k]; }).map(function (k) { return buildControl("style", k, items[k]); });
    sf.appendChild(groupCard("ch-style", "推送样式", "先选推送样式，下面只显示这种样式用得到的设置，另一种样式的设置会自动收起。改动后预览会自动更新。", "layers", styleRows, d));
    if (items.message_template) sf.appendChild(groupCard("ch-template", "推送模板", "点下面的变量插入到光标处；用到 {card_image} 时，下面会出现卡片图外观的设置。", "text", [buildControl("style", "message_template", items.message_template)], d + 60));
    if (items.card_template) sf.appendChild(groupCard("ch-card-text", "卡片图配文", "推送样式为「卡片图」时的消息模板。{card_image} 就是卡片图本身，默认就有、不能删除；它上面的文字在卡片图上方，下面的（比如链接）在卡片图下方。合成一条还是分开发，在上面的「卡片图配文」里选。", "text", [buildControl("style", "card_template", items.card_template)], d + 90));
    ["content", "card"].forEach(function (g, i) { var body = schema[g]; if (!body) return; sf.appendChild(groupCard("ch-" + g, body.description || g, PAGE_HINTS[g] || body.hint || "", GROUP_ICON[g], Object.keys(body.items).map(function (k) { return buildControl(g, k, body.items[k]); }), d + 120 + i * 60)); });
    SETTINGS_GROUPS.forEach(function (g, i) { var body = schema[g]; if (!body) return; gf.appendChild(groupCard("ch-" + g, body.description || g, PAGE_HINTS[g] || body.hint || "", GROUP_ICON[g], Object.keys(body.items).map(function (k) { return buildControl(g, k, body.items[k]); }), d + i * 60)); });
    settingsBuilt = true;
  }
  function renderSettings() {
    var set = data.settings;
    if (settingsBuilt && countDirty() > 0) return; // 正在编辑时不覆盖
    var changed = !savedValues || JSON.stringify(savedValues) !== JSON.stringify(set.values);
    savedValues = clone(set.values); draft = clone(set.values);
    if (!settingsBuilt) { buildSettings(); changed = true; }
    if (changed) Object.keys(controls).forEach(function (id) { var c = controls[id]; c.set(draft[c.g][c.k]); });
    refreshDirty();
  }
  function saveSettings() {
    var btn = $("saveBtn"), patch = diffPatch(), n = countDirty(); if (!n) return;
    busy(btn, true, "保存中");
    api("POST", "settings/save", { values: patch }).then(function (res) {
      savedValues = clone(draft); refreshDirty();
      toast("已保存 " + n + " 项设置，立即生效" + (res && res.warnings && res.warnings.length ? "（" + res.warnings.join("；") + "）" : ""), true);
      load();
    }).catch(function (e) { toast("没有保存：" + errMsg(e)); }).then(function () { busy(btn, false); });
  }
  function discardSettings() { draft = clone(savedValues); Object.keys(controls).forEach(function (id) { var c = controls[id]; c.set(draft[c.g][c.k]); }); refreshDirty(); updateStartRows(); schedulePreview(200); toast("已撤销未保存的修改", true); }

  /* =================== 实时预览（推送样式 / 推送模板） =================== */
  var pv = { seq: 0, timer: 0, ran: false };
  function pvUrl() { return $("pvUrl").value.trim(); }
  function looksLikeRef(s) { return /fanbox\.cc/i.test(s) || /^@?[A-Za-z0-9][A-Za-z0-9_-]{0,63}$/.test(s); }
  function setPvState(kind, text) { var cls = kind === "ok" ? "pill p-good" : kind === "busy" ? "pill p-blue" : kind === "err" ? "pill p-bad" : "pill p-muted"; var n = $("pvState"); n.className = cls; n.textContent = ""; if (kind === "busy") n.appendChild(el("span", "spin sm")); n.appendChild(el("span", "", text)); }
  function schedulePreview(ms) { if (currentTab !== "style" && !pv.ran) return; clearTimeout(pv.timer); pv.timer = setTimeout(runPreview, ms || 0); }
  function fillPvQuick() {
    var box = $("pvQuick"); var list = (data ? data.creators : []).map(function (c) { return [c.creator, c.name]; });
    if (!list.some(function (c) { return c[0] === "official"; })) list.push(["official", "pixivFANBOX 官方"]);
    var sig = JSON.stringify(list); if (box._sig === sig) return; box._sig = sig; box.textContent = "";
    box.appendChild(el("span", "pv-quick-label", "快速选择"));
    list.forEach(function (c) { var b = el("button", "chip", c[1]); b.type = "button"; b.title = c[0] + " 的最新一篇"; b.addEventListener("click", function () { $("pvUrl").value = c[0]; runPreview(); }); box.appendChild(b); });
  }
  function onStyleShown() { fillPvQuick(); if (!pv.ran && data) { if (!pvUrl()) $("pvUrl").value = storeGet("fanbox-preview-url") || (data.creators.length ? data.creators[0].creator : "official"); runPreview(); } }
  function previewFrom(cid) { $("pvUrl").value = cid; pv.ran = true; showTab("style"); runPreview(); }
  function runPreview() {
    clearTimeout(pv.timer);
    var url = pvUrl(); if (!url) { setPvState("idle", "待命"); return; }
    if (!looksLikeRef(url)) { setPvState("err", "链接格式不对"); return; }
    if (!bridge || !data) return;
    pv.ran = true; storeSet("fanbox-preview-url", url);
    var seq = ++pv.seq, payload = { url: url, values: diffPatch() };
    setPvState("busy", "生成中"); $("pvGo").disabled = true;
    api("POST", "preview", payload).then(function (res) {
      if (seq !== pv.seq) return; // 已经有更新的预览请求
      var body = $("pvBody"); body.textContent = "";
      var post = res.post || {}, ph = $("pvPost"); ph.textContent = "";
      var line = el("div", "pv-post-line"); line.appendChild(el("b", "", post.creator_name || res.creator)); line.appendChild(el("span", "", (res.source === "post" ? "指定帖子" : "最新一篇") + " · 《" + (post.title || "") + "》")); if (post.url) line.appendChild(copyBtn(function () { return post.url; })); ph.appendChild(line);
      var msgs = res.messages || [res.pieces];
      msgs.forEach(function (m, i) {
        var onlyImg = m.length === 1 && m[0].type === "image", b = el("div", "bubble" + (onlyImg ? " img" : " mixed"));
        m.forEach(function (p) {
          if (p.type === "text") { var tx = p.text.replace(/^\n+|\n+$/g, ""); if (tx) b.appendChild(el("div", "b-text", tx)); }
          else { var im = document.createElement("img"); im.alt = "预览图片"; im.src = p.src; b.appendChild(im); }
        });
        body.appendChild(b); fx(b, [{ opacity: 0, transform: "translateY(6px)", offset: 0 }], { duration: 420, delay: i * 60, easing: EASE, fill: "backwards" });
      });
      var all = res.pieces || [], imgs = all.filter(function (p) { return p.type === "image"; }), dirty = countDirty();
      var styleName = res.style === "card" ? styleLabel(res.card_text && res.card_text !== "none" ? "card_" + res.card_text : "card") : "文字模板";
      body.appendChild(el("div", "preview-meta", styleName + " · " + msgs.length + " 条消息" + (imgs.length ? "（" + imgs.length + " 张图，共 " + Math.round(imgs.reduce(function (s, p) { return s + p.bytes; }, 0) / 1024) + " KB）" : "") + " · 取帖 " + (res.fetch_ms || 0) + " ms · 生成 " + res.ms + " ms" + (dirty ? " · 含 " + dirty + " 项未保存的修改" : "")));
      setPvState("ok", "已按当前样式更新"); measureSoon();
    }).catch(function (e) {
      if (seq !== pv.seq) return;
      setPvState("err", "预览失败"); $("pvPost").textContent = ""; var body = $("pvBody"); body.textContent = ""; body.appendChild(el("div", "preview-empty", errMsg(e)));
    }).then(function () { if (seq === pv.seq) $("pvGo").disabled = false; });
  }

  /* =================== 主流程 =================== */
  function renderFoot() { var pl = data.plugin; $("foot").textContent = "astrbot_plugin_fanbox " + (data.version || "") + " · 部署于 " + pl.deployed_text + " · 生成于 " + new Date(data.generated_at).toLocaleString("zh-CN", { hour12: false }) + "（本机时间）"; }
  function render() {
    $("brandSub").textContent = "astrbot_plugin_fanbox · " + (data.version || "") + " · " + (data.plugin.push_style === "card" ? "卡片图" : "文字模板");
    renderHero(); renderCreators(); renderRecords(); renderErrors(); renderSessions(); renderSettings(); renderFoot(); fillSessionSelect(); fillPvQuick();
    firstRender = false; tick(); rebuildChapters(); measureSoon();
  }
  function tick() {
    var now = Date.now();
    document.querySelectorAll("[data-until]").forEach(function (n) { var u = Number(n.getAttribute("data-until")); n.textContent = u > now ? left(u) : "即将检查"; });
    document.querySelectorAll("[data-ago]").forEach(function (n) { var v = Number(n.getAttribute("data-ago")); if (!v) return; if (n.id === "liveText") { var s = Math.round((now - v) / 1000); n.textContent = s < 5 ? "实时 · 刚刚更新" : ("实时 · " + s + " 秒前更新"); } else n.textContent = ago(v); });
  }
  function showLoadError(msg) {
    if (data) { toast("刷新失败（" + msg + "），30 秒后重试"); return; }
    var box = $("creators"); var ghost = box.querySelector(":scope > .ghost"); if (ghost) ghost.remove();
    var card = box.querySelector(":scope > .load-error"), txt;
    if (!card) { card = el("div", "card load-error enter"); card.appendChild(iconEl("alert", "err-ic o-fail")); var t = el("div", ""); t.appendChild(el("b", "", "数据加载失败")); txt = el("span", "le-msg"); t.appendChild(txt); var retry = el("button", "btn sm", "重试"); retry.type = "button"; retry.addEventListener("click", function () { load(); loadSessions(); }); t.appendChild(retry); card.appendChild(t); box.appendChild(card); }
    card.querySelector(".le-msg").textContent = msg + "。30 秒后会自动重试。";
  }
  function clearLoadError() { var c = document.querySelector("#creators > .load-error"); if (c) c.remove(); }
  var loading = false;
  function load() {
    if (loading) return Promise.resolve(); loading = true;
    return api("GET", "overview").then(function (j) { data = j; clearLoadError(); render(); setLive(true); }).catch(function (e) { setLive(false); showLoadError(errMsg(e)); }).then(function () { loading = false; });
  }
  function wire() {
    wireTabs();
    $("refreshBtn").addEventListener("click", function () { load(); loadSessions(); });
    $("saveBtn").addEventListener("click", saveSettings); $("discardBtn").addEventListener("click", discardSettings);
    $("addSession").addEventListener("change", function () { $("addQQ").hidden = this.value.indexOf("__friend:") !== 0; });
    $("addForm").addEventListener("submit", function (ev) {
      ev.preventDefault(); var btn = $("addSubmit"), creator = $("addCreator").value.trim(), sv = $("addSession").value, payload = { creator: creator };
      if (!creator) { toast("填一下创作者 ID 或主页链接"); return; } if (!sv) { toast("没有可推送的会话"); return; }
      if (sv.indexOf("__friend:") === 0) { var qq = $("addQQ").value.trim(); if (!/^\d{5,12}$/.test(qq)) { toast("QQ 号格式不对"); return; } payload.platform = sv.slice(9); payload.type = "FriendMessage"; payload.target = qq; } else { payload.umo = sv; }
      busy(btn, true, "订阅中");
      api("POST", "subscriptions/add", payload).then(function (r) { toast("已订阅 " + r.name + " · 推送起点 " + r.floor + (r.pending ? " · 下次检查推送 " + r.will_push + " 篇" : ""), true); $("addCreator").value = ""; load(); }).catch(function (e) { toast("订阅失败：" + errMsg(e)); }).then(function () { busy(btn, false); });
    });
    var check = $("checkBtn");
    check.addEventListener("click", function () { busy(check, true, "检查中"); api("POST", "check").then(function (r) { toast("检查完成，推送了 " + r.sent + " 篇新帖", true); load(); }).catch(function (e) { toast("检查失败：" + errMsg(e)); }).then(function () { busy(check, false); }); });
    $("recordView").addEventListener("click", function (ev) { var b = ev.target.closest("button[data-view]"); if (!b) return; recordView = b.getAttribute("data-view"); storeSet("fanbox-record-view", recordView); [].forEach.call(this.querySelectorAll("button"), function (x) { x.setAttribute("aria-pressed", x === b ? "true" : "false"); }); if (data) { renderRecords(); rebuildChapters(); measureSoon(); } });
    $("pvGo").addEventListener("click", runPreview);
    $("pvSession").addEventListener("change", function () { $("pvQQ").hidden = this.value.indexOf("__friend:") !== 0; });
    $("pvFriend").addEventListener("click", function () {
      var sel = $("pvSession"), opt = [].filter.call(sel.options, function (o) { return o.value.indexOf("__friend:") === 0; })[0];
      if (!opt) { toast("QQ 端还没连上，暂时不能选私聊"); return; }
      sel.value = opt.value; $("pvQQ").hidden = false; $("pvQQ").focus();
    });
    var send = $("pvSend");
    function disarmSend() { send._armed = false; send.textContent = "发送"; send.classList.remove("primary"); $("pvSendNote").hidden = true; }
    send.addEventListener("click", function () {
      var url = pvUrl(); if (!url || !looksLikeRef(url)) { toast("先在上面填一个 FANBOX 帖子链接或创作者 ID"); return; }
      var payload = sessionPayload($("pvSession"), $("pvQQ"), { url: url, values: diffPatch() }); if (!payload) return;
      var label = payload._label; delete payload._label;
      var note = $("pvSendNote");
      if (!send._armed) { send._armed = true; send.textContent = "确认发送"; send.classList.add("primary"); setText(note, "将发到「" + label + "」，6 秒内再点一次「确认发送」"); note.hidden = false; clearTimeout(send._t); send._t = setTimeout(disarmSend, 6000); return; }
      clearTimeout(send._t); disarmSend(); busy(send, true, "发送中");
      api("POST", "preview/send", payload).then(function () { toast("已测试推送到「" + label + "」，推送记录里可以看到这张卡片", true); load(); })
        .catch(function (e) { toast("测试推送失败：" + errMsg(e)); load(); })
        .then(function () { busy(send, false); send.textContent = "发送"; });
    });
    $("pvUrl").addEventListener("keydown", function (ev) { if (ev.key === "Enter") { ev.preventDefault(); runPreview(); } });
    $("pvUrl").addEventListener("input", function () { var v = pvUrl(); clearTimeout(pv.timer); if (v && looksLikeRef(v)) pv.timer = setTimeout(runPreview, 900); });
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", function () { hideTip(); moveIndicator(false); if (data) rebuildChapters(); measureSoon(); });
    if (window.ResizeObserver) new ResizeObserver(function () { measureSoon(); }).observe($("main"));
    document.addEventListener("visibilitychange", function () { if (!document.hidden) load(); });
    window.addEventListener("beforeunload", function (ev) { if (draft && countDirty() > 0) { ev.preventDefault(); ev.returnValue = ""; } });
  }

  document.querySelectorAll(".enter").forEach(function (n) { settle(n); });
  if (storeGet("fanbox-record-view") === "list") { recordView = "list"; [].forEach.call($("recordView").querySelectorAll("button"), function (x) { x.setAttribute("aria-pressed", x.getAttribute("data-view") === "list" ? "true" : "false"); }); }
  buildTiles(); wire();
  var initialTab = location.hash.replace(/^#/, ""); if (TAB_NAMES.indexOf(initialTab) < 0) initialTab = storeGet("fanbox-panel-tab") || "overview";
  showTab(initialTab, { initial: true }); measure();
  function waitForBridge(timeoutMs) { return new Promise(function (resolve) { var t0 = Date.now(); (function poll() { if (window.AstrBotPluginPage) return resolve(window.AstrBotPluginPage); if (Date.now() - t0 > timeoutMs) return resolve(null); setTimeout(poll, 50); })(); }); }
  function withTimeout(promise, ms) { return Promise.race([promise, new Promise(function (r) { setTimeout(r, ms); })]); }
  waitForBridge(8000).then(function (b) {
    bridge = b;
    if (!bridge) { setLive(false, "未连接到 AstrBot"); showLoadError("没有找到 AstrBot 的插件页接口（window.AstrBotPluginPage）。请从 AstrBot 管理面板的插件页打开，或刷新一下"); return null; }
    return withTimeout(bridge.ready(), 3000).then(function () { return true; });
  }).then(function (ok) {
    if (!ok) return;
    load().then(function () { if (currentTab === "style") onStyleShown(); });
    loadSessions();
    setInterval(load, REFRESH_MS); setInterval(tick, 1000);
  });
})();
