(() => {
  const player = new Audio();
  player.preload = 'metadata';
  let current = null;

  function paint(group, state, statusText) {
    const button = group.querySelector('.audio-main');
    const label = button.querySelector('.label');
    const icon = button.querySelector('.round');
    const idle = button.dataset.idleLabel || '按這裡聽本段';
    if (state === 'playing') { icon.textContent = '⏸'; label.textContent = '暫停'; }
    else if (state === 'paused') { icon.textContent = '▶'; label.textContent = '繼續'; }
    else { icon.textContent = '🔊'; label.textContent = idle; }
    button.setAttribute('aria-pressed', state === 'playing' ? 'true' : 'false');
    group.querySelector('.audio-status').textContent = statusText;
  }

  function fromStart(group) {
    if (current && current !== group) paint(current, 'idle', '已停止播放');
    player.pause();
    player.src = group.dataset.src;
    player.currentTime = 0;
    current = group;
    paint(group, 'playing', '正在載入國語語音');
    player.play().catch(() => { paint(group, 'idle', '語音無法播放，請重新按一次'); current = null; });
  }

  function toggle(group) {
    if (current !== group || !player.src || player.ended) return fromStart(group);
    if (player.paused) {
      player.play().catch(() => { paint(group, 'idle', '語音無法播放，請重新按一次'); current = null; });
      paint(group, 'playing', '繼續播放');
    } else {
      player.pause();
      paint(group, 'paused', '已暫停');
    }
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('[data-action]');
    if (!button) return;
    const group = button.closest('.audio-wrap');
    if (button.dataset.action === 'toggle') toggle(group);
    if (button.dataset.action === 'repeat') fromStart(group);
  });
  player.addEventListener('playing', () => { if (current) paint(current, 'playing', '正在播放國語語音'); });
  player.addEventListener('waiting', () => { if (current) current.querySelector('.audio-status').textContent = '正在載入語音'; });
  player.addEventListener('ended', () => { if (current) paint(current, 'idle', '播放完畢'); current = null; });
  player.addEventListener('error', () => { if (current) paint(current, 'idle', '語音檔載入失敗，請檢查網路'); current = null; });
  window.addEventListener('beforeunload', () => player.pause());
})();
