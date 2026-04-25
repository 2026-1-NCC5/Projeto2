(function () {
  function applyArrow(arrow, open) {
    arrow.style.setProperty('display',         'block',    'important');
    arrow.style.setProperty('width',           '0',        'important');
    arrow.style.setProperty('height',          '0',        'important');
    arrow.style.setProperty('border-left',     '5px solid transparent', 'important');
    arrow.style.setProperty('border-right',    '5px solid transparent', 'important');
    arrow.style.setProperty('border-top',
      '6px solid ' + (open ? '#FF6B00' : '#5C534B'), 'important');
    arrow.style.setProperty('pointer-events',  'none',     'important');
    arrow.style.setProperty('transition',
      'transform .25s ease, border-top-color .2s', 'important');
    arrow.style.setProperty('transform',
      open ? 'rotate(180deg)' : 'none', 'important');
  }

  function styleBtn(btn) {
    btn.style.setProperty('background',     'none',         'important');
    btn.style.setProperty('border',         'none',         'important');
    btn.style.setProperty('padding',        '7px 9px',      'important');
    btn.style.setProperty('margin',         '0 2px',        'important');
    btn.style.setProperty('cursor',         'pointer',      'important');
    btn.style.setProperty('border-radius',  '6px',          'important');
    btn.style.setProperty('flex-shrink',    '0',            'important');
    btn.style.setProperty('display',        'inline-flex',  'important');
    btn.style.setProperty('align-items',    'center',       'important');
    btn.style.setProperty('justify-content','center',       'important');
    btn.style.setProperty('transition',     'background .15s', 'important');
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
    styleBtn(btn);

    var arrow = document.createElement('span');
    arrow.className = 'mb-arrow';
    applyArrow(arrow, false);
    btn.appendChild(arrow);

    btn.addEventListener('mouseenter', function () {
      btn.style.setProperty('background', 'rgba(255,107,0,.08)', 'important');
    });
    btn.addEventListener('mouseleave', function () {
      btn.style.setProperty('background', 'none', 'important');
    });

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      applyArrow(arrow, isOpen);
      modebar.querySelectorAll('.modebar-group').forEach(function (g) {
        if (isOpen) g.style.removeProperty('display');
        else g.style.setProperty('display', 'none', 'important');
      });
    });

    modebar.insertBefore(btn, modebar.firstChild);

    document.addEventListener('click', function (e) {
      if (!modebar.contains(e.target) && modebar.classList.contains('mb-open')) {
        modebar.classList.remove('mb-open');
        applyArrow(arrow, false);
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
