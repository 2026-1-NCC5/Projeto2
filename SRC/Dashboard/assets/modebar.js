(function () {
  function styleBtn(btn, open) {
    btn.style.setProperty('color',       open ? '#FF6B00' : '#555', 'important');
    btn.style.setProperty('background',  'none',                    'important');
    btn.style.setProperty('border',      'none',                    'important');
    btn.style.setProperty('font-size',   '14px',                    'important');
    btn.style.setProperty('line-height', '1',                       'important');
    btn.style.setProperty('padding',     '3px 8px',                 'important');
    btn.style.setProperty('cursor',      'pointer',                 'important');
    btn.style.setProperty('border-radius','6px',                    'important');
    btn.style.setProperty('flex-shrink', '0',                       'important');
  }

  function attachHamburger(modebar) {
    if (modebar.dataset.hb) return;
    modebar.dataset.hb = '1';

    modebar.querySelectorAll('.modebar-group').forEach(function (g) {
      g.style.setProperty('display', 'none', 'important');
    });

    var btn = document.createElement('button');
    btn.className = 'modebar-hamburger';
    btn.title = 'Opções do gráfico';
    btn.textContent = '▾';
    styleBtn(btn, false);

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      btn.textContent = isOpen ? '▴' : '▾';
      styleBtn(btn, isOpen);
      modebar.querySelectorAll('.modebar-group').forEach(function (g) {
        if (isOpen) {
          g.style.removeProperty('display');
        } else {
          g.style.setProperty('display', 'none', 'important');
        }
      });
    });

    modebar.insertBefore(btn, modebar.firstChild);

    document.addEventListener('click', function (e) {
      if (!modebar.contains(e.target) && modebar.classList.contains('mb-open')) {
        modebar.classList.remove('mb-open');
        btn.textContent = '▾';
        styleBtn(btn, false);
        modebar.querySelectorAll('.modebar-group').forEach(function (g) {
          g.style.setProperty('display', 'none', 'important');
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
