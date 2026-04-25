(function () {
  function attachHamburger(modebar) {
    if (modebar.dataset.hb) return;
    modebar.dataset.hb = '1';

    modebar.querySelectorAll('.modebar-group').forEach(function (g) {
      g.style.display = 'none';
    });

    var btn = document.createElement('button');
    btn.className = 'modebar-hamburger';
    btn.title = 'Opções do gráfico';
    btn.textContent = '▾';  // seta para baixo = fechado

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      btn.textContent = isOpen ? '▴' : '▾';
      modebar.querySelectorAll('.modebar-group').forEach(function (g) {
        g.style.display = isOpen ? '' : 'none';
      });
    });

    modebar.insertBefore(btn, modebar.firstChild);

    document.addEventListener('click', function (e) {
      if (!modebar.contains(e.target) && modebar.classList.contains('mb-open')) {
        modebar.classList.remove('mb-open');
        btn.textContent = '▾';
        modebar.querySelectorAll('.modebar-group').forEach(function (g) {
          g.style.display = 'none';
        });
      }
    });
  }

  var observer = new MutationObserver(function () {
    document.querySelectorAll('.modebar').forEach(function (mb) {
      if (!mb.dataset.hb) attachHamburger(mb);
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });
}());
