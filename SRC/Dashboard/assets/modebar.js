(function () {
  function styleBtn(btn) {
    btn.style.setProperty('background',     'none',    'important');
    btn.style.setProperty('border',         'none',    'important');
    btn.style.setProperty('padding',        '6px 8px', 'important');
    btn.style.setProperty('cursor',         'pointer', 'important');
    btn.style.setProperty('border-radius',  '6px',     'important');
    btn.style.setProperty('flex-shrink',    '0',       'important');
    btn.style.setProperty('display',        'inline-flex', 'important');
    btn.style.setProperty('align-items',    'center',  'important');
    btn.style.setProperty('justify-content','center',  'important');
  }

  function attachHamburger(modebar) {
    if (modebar.dataset.hb) return;
    modebar.dataset.hb = '1';

    modebar.querySelectorAll('.modebar-group').forEach(function (g) {
      g.style.setProperty('display', 'none', 'important');
    });

    var btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'modebar-hamburger';
    btn.title = 'Opções do gráfico';
    btn.setAttribute('aria-label', 'Opções do gráfico');
    // a seta é desenhada por CSS via ::before, não precisa de conteúdo aqui
    styleBtn(btn);

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      modebar.querySelectorAll('.modebar-group').forEach(function (g) {
        if (isOpen) g.style.removeProperty('display');
        else g.style.setProperty('display', 'none', 'important');
      });
    });

    modebar.insertBefore(btn, modebar.firstChild);

    document.addEventListener('click', function (e) {
      if (!modebar.contains(e.target) && modebar.classList.contains('mb-open')) {
        modebar.classList.remove('mb-open');
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
