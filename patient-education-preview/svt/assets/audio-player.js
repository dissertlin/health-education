(() => {
  'use strict';
  const player = new Audio();
  player.preload = 'metadata';
  let current = null;
  let requestId = 0;
  function paint(group, state, status) {
    if (!group) return;
    const button = group.querySelector('.audio-main');
    button.querySelector('.label').textContent = state === 'playing' ? '暫停' : state === 'paused' ? '繼續' : button.dataset.idleLabel;
    button.querySelector('.round').textContent = state === 'playing' ? '⏸' : state === 'paused' ? '▶' : '🔊';
    button.setAttribute('aria-pressed', String(state === 'playing'));
    group.querySelector('.audio-status').textContent = status;
  }
  async function start(group, restart) {
    const id = ++requestId;
    if (current && current !== group) paint(current, 'idle', '已停止播放');
    const changed = current !== group;
    current = group;
    if (changed) player.src = group.dataset.src;
    if (restart || player.ended) player.currentTime = 0;
    paint(group, 'playing', '正在載入語音');
    try { await player.play(); }
    catch (error) {
      if (id === requestId && error.name !== 'AbortError') paint(group, 'idle', '語音無法播放，請再試一次');
    }
  }
  document.addEventListener('click', event => {
    const button = event.target.closest('button[data-action]');
    if (!button) return;
    const group = button.closest('.audio-wrap');
    if (!group) return;
    if (button.dataset.action === 'repeat') { start(group, true); return; }
    if (current === group && !player.paused) {
      ++requestId; player.pause(); paint(group, 'paused', '已暫停');
    } else start(group, false);
  });
  player.addEventListener('playing', () => paint(current, 'playing', '正在播放國語語音'));
  player.addEventListener('waiting', () => { if (current) current.querySelector('.audio-status').textContent = '正在載入語音'; });
  player.addEventListener('ended', () => paint(current, 'idle', '播放完畢'));
  player.addEventListener('error', () => paint(current, 'idle', '語音檔載入失敗，請確認完整資料夾已解壓縮或網路連線正常'));
  window.addEventListener('pagehide', () => { ++requestId; player.pause(); });
})();
