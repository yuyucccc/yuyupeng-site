(function () {
  var body = document.body;
  var mark = document.getElementById('mark');
  var dot = document.getElementById('dot');

  // capture hooks: ?gallery jumps straight to the constellation, ?eager loads
  // every picture up front, so a screenshot is valid evidence.
  var q = location.search;
  if (/[?&]eager/.test(q)) {
    document.querySelectorAll('img[loading="lazy"]').forEach(function (im) { im.loading = 'eager'; });
  }
  var wantGallery = /[?&]gallery/.test(q);

  var opened = false;
  function open() {
    if (opened) return;
    opened = true;
    body.classList.remove('front');
    body.classList.add('gallery');
    startField();
  }
  if (mark) mark.addEventListener('click', open);

  // ── the constellation drifts ─────────────────────────────────────────
  // Each picture wanders on two slow sines per axis, at periods that do not
  // divide into each other, so the path never visibly repeats. It ignores the
  // pointer entirely: the drift is the whole motion, and it looks the same
  // whether or not anyone is moving a mouse.
  //
  // Computed here rather than in CSS keyframes because the pictures have to
  // be kept off each other, which needs all ten positions in one place.
  var DRIFT  = 0.055;   // of the window's short side, at full depth
  var EDGE   = 0.06;    // white margin all round, as a share of the short side
  var GAP    = 1.03;    // how close two footprints may come, 1 = exactly touching

  var still = window.matchMedia('(prefers-reduced-motion: reduce)');
  var phone = window.matchMedia('(max-width: 56rem)');

  var nodes = [].map.call(document.querySelectorAll('.node'), function (el, i) {
    // deterministic per project, so the composition is the same on every visit
    var r = function (k) { return (Math.sin((i + 1) * 12.9898 + k * 78.233) * 43758.5453) % 1; };
    var a = function (k) { return Math.abs(r(k)); };
    return {
      el: el,
      d: el.querySelector('.node__d'),
      group: el.getAttribute('data-group') || 'professional',
      on: true,
      hw: 0, hh: 0, ox: 0, oy: 0,
      x: parseFloat(el.style.getPropertyValue('--x')),
      y: parseFloat(el.style.getPropertyValue('--y')),
      dz: parseFloat(el.style.getPropertyValue('--dz')) || 1,
      ax: 0.7 + a(1) * 0.8, ay: 0.7 + a(2) * 0.8,
      // periods in seconds: two per axis, deliberately not multiples
      t1: 17 + a(3) * 9, t2: 26 + a(4) * 13,
      t3: 21 + a(5) * 8, t4: 31 + a(6) * 11,
      p1: a(7) * 6.283, p2: a(8) * 6.283,
      p3: a(9) * 6.283, p4: a(10) * 6.283
    };
  });

  var running = false;

  // asymptotic limit: linear while there is room, flattening onto lo/hi
  function soft(v, lo, hi) {
    if (v >= 0) { hi = Math.max(hi, 1); return hi * Math.tanh(v / hi); }
    lo = Math.min(lo, -1); return lo * Math.tanh(v / lo);
  }

  // The travel a picture may make from where it was authored, given that its
  // whole footprint has to stay inside [lo, hi]. The anchor is pulled into that
  // band first: soft() needs room on both sides of it, and a picture authored
  // past the margin — a tall one hung near the top — would otherwise be handed
  // a one-sided range, quietly lose its limit, and hang off the edge.
  function anchored(want, home, lo, hi) {
    if (hi < lo) { var mid = (lo + hi) / 2; lo = hi = mid; }
    var a = Math.min(Math.max(home, lo), hi);
    return (a - home) + soft(want - a, lo - a, hi - a);
  }

  // A caption is allowed to run wider than the picture it sits under, so the
  // element's own box under-reports the footprint and two projects can collide
  // while their boxes say they are clear. Measure the union of the picture and
  // its lines instead, and remember how far that union's centre sits from the
  // element's. offset* is used rather than getBoundingClientRect because the
  // entrance transition is still scaling the node when this first runs.
  function measure() {
    nodes.forEach(function (n) {
      var l = 0, t = 0, r = n.el.offsetWidth, b = n.el.offsetHeight;
      [].forEach.call(n.el.querySelectorAll('img,.node__t,.node__m'), function (c) {
        if (!c.offsetWidth) return;
        l = Math.min(l, c.offsetLeft);
        t = Math.min(t, c.offsetTop);
        r = Math.max(r, c.offsetLeft + c.offsetWidth);
        b = Math.max(b, c.offsetTop + c.offsetHeight);
      });
      n.hw = (r - l) / 2; n.hh = (b - t) / 2;
      n.ox = (l + r) / 2 - n.el.offsetWidth / 2;
      n.oy = (t + b) / 2 - n.el.offsetHeight / 2;
    });
  }
  window.addEventListener('resize', function () { if (running) measure(); }, { passive: true });
  window.addEventListener('load', function () { if (running) measure(); });

  // The name, the two filters and the address are fixed, so the separation
  // pass has to know about them or a picture will drift straight over the one
  // line that says which half of the work you are looking at. Re-read every
  // few frames: the mark is still shrinking, and the filters still fading in,
  // for most of a second after the gallery opens.
  // The filters are given the whole left column rather than the box their
  // letters happen to fill — she asked for pictures to stay out of that region,
  // and a picture stopping a few pixels short of the words still reads as
  // crowding them.
  var FURNITURE = [
    { q: '.wordmark',   px: 18, py: 18 },
    { q: '.side',       px: 38, py: 52, column: true },
    { q: '.corner--br', px: 18, py: 18 },
    { q: '.mark',       px: 12, py: 12 }
  ];
  var furn = [];
  function measureFurniture() {
    furn.length = 0;
    for (var k = 0; k < FURNITURE.length; k++) {
      var f = FURNITURE[k], el = document.querySelector(f.q);
      if (!el) continue;
      var r = el.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      var l = r.left - f.px, rt = r.right + f.px;
      if (f.column) l = Math.min(l, 0);       // out to the window's edge
      furn.push({ cx: (l + rt) / 2, cy: r.top + r.height / 2,
                  hw: (rt - l) / 2, hh: r.height / 2 + f.py });
    }
  }

  var X = [], Y = [], tick = 0;

  function frame(now) {
    if (!running) return;
    var w = window.innerWidth, h = window.innerHeight;
    var S = Math.min(w, h), t = now / 1000, i, n;
    var edge = Math.max(40, S * EDGE);

    // 1 — where each picture wants to be, wider for the small ones
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      X[i] = n.x * w / 100 + n.ox
           + DRIFT * S * n.ax * n.dz * (Math.sin(6.283 * t / n.t1 + n.p1) * 0.66 +
                                        Math.sin(6.283 * t / n.t2 + n.p2) * 0.34);
      Y[i] = n.y * h / 100 + n.oy
           + DRIFT * S * n.ay * n.dz * (Math.sin(6.283 * t / n.t3 + n.p3) * 0.66 +
                                        Math.sin(6.283 * t / n.t4 + n.p4) * 0.34);
    }

    // 2 — and where it may actually go. With this much travel two pictures
    //     will meet, and a caption vanishing behind a neighbour's photograph
    //     is the one collision that costs you a project. Boxes are separated
    //     along whichever axis they overlap least, which is the shortest way
    //     out, so they slide past each other instead of shoving. Only what is
    //     on screen takes part: a filtered-out picture must not hold a space.
    if ((tick++ % 8) === 0) measureFurniture();
    var act = [];
    for (i = 0; i < nodes.length; i++) if (nodes[i].on) act.push(i);

    // The wall is relaxed together with the rest, not applied afterwards: a
    // tall picture hung near the top cannot move up, so if separation is
    // resolved first and the margin imposed second, the margin simply pushes
    // it back into its neighbour and the overlap never clears. Inside the loop
    // the next pass sees the true position and separates along the other axis.
    for (var pass = 0; pass < 8; pass++) {
      for (var a = 0; a < act.length; a++) {
        i = act[a];
        for (var b = a + 1; b < act.length; b++) {
          var j = act[b];
          var sw = (nodes[i].hw + nodes[j].hw) * GAP;
          var sh = (nodes[i].hh + nodes[j].hh) * GAP;
          var ox = sw - Math.abs(X[j] - X[i]);
          var oy = sh - Math.abs(Y[j] - Y[i]);
          if (ox <= 0 || oy <= 0) continue;
          if (ox / sw < oy / sh) {
            var sx = (X[j] >= X[i] ? 1 : -1) * ox * 0.5;
            X[i] -= sx; X[j] += sx;
          } else {
            var sy = (Y[j] >= Y[i] ? 1 : -1) * oy * 0.5;
            Y[i] -= sy; Y[j] += sy;
          }
        }
        // the furniture does not move, so the picture takes the whole push
        for (var f = 0; f < furn.length; f++) {
          var F = furn[f];
          var fw = nodes[i].hw + F.hw, fh = nodes[i].hh + F.hh;
          var fx = fw - Math.abs(F.cx - X[i]), fy = fh - Math.abs(F.cy - Y[i]);
          if (fx <= 0 || fy <= 0) continue;
          if (fx / fw < fy / fh) X[i] += (X[i] >= F.cx ? 1 : -1) * fx;
          else                   Y[i] += (Y[i] >= F.cy ? 1 : -1) * fy;
        }

        var hx = nodes[i].x * w / 100 + nodes[i].ox;
        var hy = nodes[i].y * h / 100 + nodes[i].oy;
        X[i] = hx + anchored(X[i], hx, edge + nodes[i].hw, w - edge - nodes[i].hw);
        Y[i] = hy + anchored(Y[i], hy, edge + nodes[i].hh, h - edge - nodes[i].hh);
      }
    }

    // 3 — draw. Anything filtered out was never relaxed, so it is still held
    //     to the wall here, ready for when it comes back.
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      var ux = n.x * w / 100 + n.ox, uy = n.y * h / 100 + n.oy;
      var dx = n.on ? X[i] - ux
                    : anchored(X[i], ux, edge + n.hw, w - edge - n.hw);
      var dy = n.on ? Y[i] - uy
                    : anchored(Y[i], uy, edge + n.hh, h - edge - n.hh);

      n.d.style.transform = 'translate3d(' + dx.toFixed(2) + 'px,' + dy.toFixed(2) + 'px,0)';
    }
    requestAnimationFrame(frame);
  }

  function startField() {
    if (running || still.matches || phone.matches || !nodes.length) return;
    running = true;
    measure();
    measureFurniture();
    requestAnimationFrame(frame);
  }

  // ── the three filters ────────────────────────────────────────────────
  // One of three, never a pair of toggles: all, or one half. "all" starts lit,
  // so the page opens on everything and there is always one line to come back to.
  var showing = 'all';
  var filters = [].slice.call(document.querySelectorAll('.side__b'));

  function applyFilter() {
    nodes.forEach(function (n) {
      n.on = showing === 'all' || n.group === showing;
      n.el.classList.toggle('node--off', !n.on);
    });
    filters.forEach(function (b) {
      var lit = b.getAttribute('data-show') === showing;
      b.classList.toggle('is-on', lit);
      b.setAttribute('aria-pressed', lit ? 'true' : 'false');
    });
  }

  filters.forEach(function (b) {
    b.addEventListener('click', function () {
      showing = b.getAttribute('data-show');
      applyFilter();
    });
  });
  applyFilter();

  if (wantGallery && mark) {
    body.classList.remove('front'); body.classList.add('gallery'); startField();
  }


  // ── opening a project ────────────────────────────────────────────────
  // The picture grows out of the page while everything else clears, and only
  // then does the project load. The drift is stopped first, so the frame loop
  // is not writing a transform underneath the one that is growing.
  document.querySelectorAll('.node').forEach(function (n) {
    n.addEventListener('click', function (ev) {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      var href = n.getAttribute('href');
      if (still.matches) return;            // no animation, follow the link
      ev.preventDefault();
      running = false;
      // Grow it as far as the window allows and no further, then slide it only
      // as far as it must to stay wholly on screen. A picture that has drifted
      // near an edge would otherwise grow straight off it, and a photograph
      // cropped by the window is the one thing she asked me never to do.
      var im = n.querySelector('img');
      if (im) {
        var r = im.getBoundingClientRect();
        var vw = window.innerWidth, vh = window.innerHeight, M = 24;
        var z = Math.max(1.15, Math.min(1.75, (vh - M * 2) / r.height,
                                              (vw - M * 2) / r.width));
        var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        var hw = r.width * z / 2, hh = r.height * z / 2, tx = 0, ty = 0;
        if (cx - hw < M) tx = M - (cx - hw);
        else if (cx + hw > vw - M) tx = vw - M - (cx + hw);
        if (cy - hh < M) ty = M - (cy - hh);
        else if (cy + hh > vh - M) ty = vh - M - (cy + hh);
        n.style.setProperty('--zoom', z.toFixed(3));
        n.style.setProperty('--tx', tx.toFixed(1) + 'px');
        n.style.setProperty('--ty', ty.toFixed(1) + 'px');
      }
      body.classList.add('zooming');
      n.classList.add('zoom');
      setTimeout(function () { location.href = href; }, 560);
    });
  });

  document.querySelectorAll('.js-mail').forEach(function (a) {
    var addr = a.dataset.u + '@' + a.dataset.d;
    a.href = 'mailto:' + addr;
    var t = a.querySelector('.js-mail-txt');
    if (t) t.textContent = addr;
  });

  // ── the pointer ──────────────────────────────────────────────────────
  // A black dot in place of the arrow. The lag that makes it feel attached to
  // your hand is a CSS transition on the transform, not a loop here, so it
  // costs nothing while the constellation is already animating.
  if (dot && window.matchMedia('(pointer: fine)').matches) {
    document.documentElement.classList.add('hasdot');
    var seen = false;
    window.addEventListener('pointermove', function (ev) {
      if (ev.pointerType && ev.pointerType !== 'mouse') return;
      dot.style.transform = 'translate3d(' + ev.clientX + 'px,' + ev.clientY + 'px,0)';
      if (!seen) { seen = true; dot.classList.add('on'); }
    }, { passive: true });

    // swell over anything that can be clicked
    document.addEventListener('pointerover', function (ev) {
      if (ev.target.closest && ev.target.closest('.node,.mark,a,button')) dot.classList.add('big');
    });
    document.addEventListener('pointerout', function (ev) {
      if (ev.target.closest && ev.target.closest('.node,.mark,a,button')) dot.classList.remove('big');
    });

    // the arrow is gone, so the dot must not be: put it back when the pointer
    // leaves the window or the tab, or there is nothing on screen at all
    document.addEventListener('pointerleave', function () { dot.classList.remove('on'); });
    window.addEventListener('blur', function () { dot.classList.remove('on'); });
  }
})();
