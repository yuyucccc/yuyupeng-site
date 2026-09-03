document.querySelectorAll('.js-mail').forEach(function(a){
  var addr = a.dataset.u + '@' + a.dataset.d;
  a.href = 'mailto:' + addr;
  var t = a.querySelector('.js-mail-txt');
  if (t) t.textContent = addr;
});

var rise = [].slice.call(document.querySelectorAll('.rise'));
function reveal(el){ el.classList.add('in'); }
function revealAll(){ rise.forEach(reveal); }

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches || !('IntersectionObserver' in window)) {
  revealAll();
} else {
  var io = new IntersectionObserver(function(entries){
    entries.forEach(function(en, i){
      if (!en.isIntersecting) return;
      var el = en.target;
      setTimeout(function(){ reveal(el); }, Math.min(i, 5) * 55);
      io.unobserve(el);
    });
  }, { rootMargin: '0px 0px -8% 0px', threshold: 0.05 });

  rise.forEach(function(el){
    // Anything already at or above the fold — including content the reader
    // jumped past with an anchor or a restored scroll position — is shown at
    // once. An observer alone never fires for those and would strand them.
    if (el.getBoundingClientRect().top < window.innerHeight) { reveal(el); return; }
    io.observe(el);
  });

  // Last resort: nothing on this site may stay invisible.
  setTimeout(revealAll, 4000);
}

// Lazy-loading has failed on this layout before (absolutely positioned plates
// inside a ratio-sized canvas). If an image is on screen and still has not
// decoded, stop waiting for the browser and fetch it.
// Capture-only hooks: ?probe reports the document height in the title so a
// screenshot script can size itself, and ?y scrolls to an offset so a tall page
// can be captured in segments at a normal viewport (where lazy-loading behaves).
(function(){
  var q = new URLSearchParams(location.search);
  if (q.has('y')) addEventListener('load', function(){
    setTimeout(function(){ window.scrollTo(0, parseInt(q.get('y'), 10) || 0); }, 400);
  });
  // ?onepage makes the whole document one PDF page, so --print-to-pdf yields a
  // valid full-page capture without relying on scroll or an over-tall window.
  if (q.has('onepage')) addEventListener('load', function(){
    setTimeout(function(){
      var w = document.documentElement.scrollWidth;
      var h = document.documentElement.scrollHeight;
      var s = document.createElement('style');
      s.textContent = '@page{size:' + w + 'px ' + h + 'px;margin:0}'
                    + 'html,body{width:' + w + 'px}';
      document.head.appendChild(s);
    }, 700);
  });
  if (q.has('probe')) addEventListener('load', function(){
    setTimeout(function(){
      document.title = 'H=' + document.documentElement.scrollHeight
                     + ' V=' + window.innerHeight;
    }, 900);
  });
})();

// ?eager=1 loads every picture up front. Used only for full-page capture, so
// screenshots are valid evidence rather than a half-decoded page.
if (location.search.indexOf('eager') > -1) {
  document.querySelectorAll('img[loading="lazy"]').forEach(function(im){ im.loading = 'eager'; });
}
function rescueImages(){
  document.querySelectorAll('img[loading="lazy"]').forEach(function(im){
    if (im.complete && im.naturalWidth > 0) return;
    var r = im.getBoundingClientRect();
    if (r.bottom > -600 && r.top < window.innerHeight + 600) im.loading = 'eager';
  });
}
addEventListener('scroll', rescueImages, { passive: true });
addEventListener('resize', rescueImages, { passive: true });
setTimeout(rescueImages, 1200);
setTimeout(rescueImages, 3500);
