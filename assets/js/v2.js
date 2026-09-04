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
  if (/[?&]gallery/.test(q)) {
    body.classList.remove('front'); body.classList.add('gallery');
  }

  var opened = false;
  function open() {
    if (opened) return;
    opened = true;
    var quick = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (quick) { body.classList.remove('front'); body.classList.add('gallery'); return; }
    body.classList.add('filming');
    setTimeout(function () {
      body.classList.remove('front');
      body.classList.add('gallery');
    }, 420);
    setTimeout(function () { body.classList.remove('filming'); }, 1050);
  }
  mark.addEventListener('click', open);

  // Threads are drawn in a 0..100 box stretched over the viewport, so the ends
  // sit on the same percentages the nodes use. No resize maths needed.

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
