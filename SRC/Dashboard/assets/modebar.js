(function () {
  var ARROW_DOWN =
    '<svg width="10" height="6" viewBox="0 0 10 6" xmlns="http://www.w3.org/2000/svg"' +
    ' style="display:block;pointer-events:none">' +
    '<path d="M0,0 L10,0 L5,6 Z" fill="#555"/>' +
    '</svg>';

  var ARROW_UP =
    '<svg width="10" height="6" viewBox="0 0 10 6" xmlns="http://www.w3.org/2000/svg"' +
    ' style="display:block;pointer-events:none">' +
    '<path d="M0,6 L10,6 L5,0 Z" fill="#FF6B00"/>' +
    '</svg>';

  function styleBtn(btn) {
    btn.style.setProperty('background',     'none',    'important');
    btn.style.setProperty('border',         'none',    'important');
    btn.style.setProperty('padding',        '4px 8px', 'important');
    btn.style.setProperty('cursor',         'pointer', 'important');
    btn.style.setProperty('border-radius',  '6px',     'important');
    btn.style.setProperty('flex-shrink',    '0',       'important');
    btn.style.setProperty('display',        'flex',    'important');
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
    btn.className = 'modebar-hamburger';
    btn.title = 'Opções do gráfico';
    btn.innerHTML = ARROW_DOWN;
    styleBtn(btn);

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      btn.innerHTML = isOpen ? ARROW_UP : ARROW_DOWN;
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
        btn.innerHTML = ARROW_DOWN;
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
