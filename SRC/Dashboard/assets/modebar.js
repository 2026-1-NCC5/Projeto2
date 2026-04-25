(function () {
  function attachHamburger(modebar) {
    if (modebar.dataset.hb) return;
    modebar.dataset.hb = '1';

    // Esconde todos os grupos inicialmente
    modebar.querySelectorAll('.modebar-group').forEach(function (g) {
      g.style.display = 'none';
    });

    // Cria o botão hambúrguer
    var btn = document.createElement('button');
    btn.className = 'modebar-hamburger';
    btn.title = 'Opções do gráfico';
    btn.innerHTML =
      '<svg viewBox="0 0 20 20" width="15" height="15" fill="currentColor">' +
      '<rect y="3"  width="20" height="2.5" rx="1.2"/>' +
      '<rect y="9"  width="20" height="2.5" rx="1.2"/>' +
      '<rect y="15" width="20" height="2.5" rx="1.2"/>' +
      '</svg>';

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isOpen = modebar.classList.toggle('mb-open');
      modebar.querySelectorAll('.modebar-group').forEach(function (g) {
        g.style.display = isOpen ? '' : 'none';
      });
    });

    modebar.insertBefore(btn, modebar.firstChild);

    // Fecha ao clicar fora
    document.addEventListener('click', function (e) {
      if (!modebar.contains(e.target) && modebar.classList.contains('mb-open')) {
        modebar.classList.remove('mb-open');
        modebar.querySelectorAll('.modebar-group').forEach(function (g) {
          g.style.display = 'none';
        });
      }
    });
  }

  // Observa o DOM para capturar modebars criadas/recriadas pelo Plotly
  var observer = new MutationObserver(function () {
    document.querySelectorAll('.modebar').forEach(function (mb) {
      if (!mb.dataset.hb) attachHamburger(mb);
    });
  });

  observer.observe(document.body, { childList: true, subtree: true });
}());
