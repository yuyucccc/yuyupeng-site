(function () {
  var body = document.body;
  var mark = document.getElementById('mark');
  var grain = document.getElementById('grain');

  // Film grain, drawn once into a canvas and tiled. Cheaper than an SVG filter
  // and it looks like emulsion rather than like noise.
  (function makeGrain() {
    var n = 150, c = document.createElement('canvas');
    c.width = c.height = n;
    var g = c.getContext('2d'), d = g.createImageData(n, n), p = d.data;
    for (var i = 0; i < p.length; i += 4) {
      var v = 200 + Math.random() * 55;
      p[i] = p[i + 1] = p[i + 2] = v;
      p[i + 3] = 255;
    }
    g.putImageData(d, 0, 0);
    grain.style.backgroundImage = 'url(' + c.toDataURL() + ')';
    grain.style.backgroundSize = n + 'px ' + n + 'px';
  })();

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
    var quick = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (quick) {
      body.classList.remove('front'); body.classList.add('gallery');
      startField(); return;
    }
    body.classList.add('filming');
    setTimeout(function () {
      body.classList.remove('front');
      body.classList.add('gallery');
      startField();
    }, 420);
    setTimeout(function () { body.classList.remove('filming'); }, 1050);
  }
  mark.addEventListener('click', open);

  // ── the constellation moves ──────────────────────────────────────────
  // Two motions, composed on one element per project:
  //
  //   drift   two slow sines per axis at periods that do not divide into each
  //           other, so the path never visibly repeats
  //   follow  the whole field lags after the pointer. tosen.es, the reference,
  //           has no idle motion at all — everything you see there is the
  //           cursor dragging the cluster around — so this is the half that
  //           carries the range, and the drift only keeps it alive when the
  //           page is left alone.
  //
  // Both are computed here rather than in CSS keyframes, because the threads
  // have to end exactly where the pictures are, and reading that back out of
  // layout every frame would force ten reflows.
  var DRIFT  = 0.055;   // of the window's short side, at full depth
  var FOLLOW = 0.115;   // of the window, at full depth
  var LAG    = 0.055;   // how slowly the field catches up with the pointer
  var EDGE   = 12;      // px of window margin a picture may never cross
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
      line: null,
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

  var lines = document.querySelectorAll('.threads line');
  nodes.forEach(function (n, i) { n.line = lines[i] || null; });

  var pxT = 0, pyT = 0, px = 0, py = 0, running = false;

  // asymptotic limit: linear while there is room, flattening onto lo/hi
  function soft(v, lo, hi) {
    if (v >= 0) { hi = Math.max(hi, 1); return hi * Math.tanh(v / hi); }
    lo = Math.min(lo, -1); return lo * Math.tanh(v / lo);
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

  window.addEventListener('pointermove', function (ev) {
    var w = window.innerWidth, h = window.innerHeight;
    pxT = (ev.clientX / w - 0.5) * 2;    // -1 .. 1
    pyT = (ev.clientY / h - 0.5) * 2;
  }, { passive: true });

  var X = [], Y = [];

  function frame(now) {
    if (!running) return;
    var w = window.innerWidth, h = window.innerHeight;
    var S = Math.min(w, h), t = now / 1000, i, n;

    px += (pxT - px) * LAG;
    py += (pyT - py) * LAG;

    // 1 — where each picture wants to be: its own drift, plus the field's lag
    //     after the pointer, deeper for the small ones
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      X[i] = n.x * w / 100 + n.ox
           + DRIFT * S * n.ax * n.dz * (Math.sin(6.283 * t / n.t1 + n.p1) * 0.66 +
                                        Math.sin(6.283 * t / n.t2 + n.p2) * 0.34)
           + px * FOLLOW * w * n.dz;
      Y[i] = n.y * h / 100 + n.oy
           + DRIFT * S * n.ay * n.dz * (Math.sin(6.283 * t / n.t3 + n.p3) * 0.66 +
                                        Math.sin(6.283 * t / n.t4 + n.p4) * 0.34)
           + py * FOLLOW * h * n.dz;
    }

    // 2 — and where it may actually go. With this much travel two pictures
    //     will meet, and a caption vanishing behind a neighbour's photograph
    //     is the one collision that costs you a project. Boxes are separated
    //     along whichever axis they overlap least, which is the shortest way
    //     out, so they slide past each other instead of shoving.
    for (var pass = 0; pass < 3; pass++) {
      for (i = 0; i < nodes.length; i++) {
        for (var j = i + 1; j < nodes.length; j++) {
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
      }
    }

    // 3 — the window's edge, eased rather than clipped, then draw
    for (i = 0; i < nodes.length; i++) {
      n = nodes[i];
      var ux = n.x * w / 100 + n.ox, uy = n.y * h / 100 + n.oy;
      var dx = soft(X[i] - ux, EDGE + n.hw - ux, w - EDGE - n.hw - ux);
      var dy = soft(Y[i] - uy, EDGE + n.hh - uy, h - EDGE - n.hh - uy);

      n.d.style.transform = 'translate3d(' + dx.toFixed(2) + 'px,' + dy.toFixed(2) + 'px,0)';
      if (n.line) {
        // the thread stays straight and stays drawn; only its far end travels
        n.line.setAttribute('x2', (n.x + dx / w * 100).toFixed(3));
        n.line.setAttribute('y2', (n.y + dy / h * 100).toFixed(3));
      }
    }
    requestAnimationFrame(frame);
  }

  function startField() {
    if (running || still.matches || phone.matches || !nodes.length) return;
    running = true;
    measure();
    requestAnimationFrame(frame);
  }

  if (wantGallery) {
    body.classList.remove('front'); body.classList.add('gallery'); startField();
  }


  // Click swells the picture before the project opens, so the tap is felt.
  document.querySelectorAll('.node').forEach(function (n) {
    n.addEventListener('click', function (ev) {
      if (ev.metaKey || ev.ctrlKey || ev.shiftKey || ev.button !== 0) return;
      if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
      ev.preventDefault();
      n.classList.add('pop');
      setTimeout(function () { location.href = n.getAttribute('href'); }, 270);
    });
  });

  document.querySelectorAll('.js-mail').forEach(function (a) {
    var addr = a.dataset.u + '@' + a.dataset.d;
    a.href = 'mailto:' + addr;
    var t = a.querySelector('.js-mail-txt');
    if (t) t.textContent = addr;
  });
})();
