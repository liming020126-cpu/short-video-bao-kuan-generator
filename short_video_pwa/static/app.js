async function api(path, method = 'GET', body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || '请求失败');
  return data;
}

function getPlatforms() {
  return Array.from(document.querySelectorAll('.chips input[type=checkbox]'))
    .filter(i => i.checked)
    .map(i => i.value);
}

function collectData() {
  return {
    business: document.getElementById('business').value.trim(),
    industry: document.getElementById('industry').value.trim(),
    audience: document.getElementById('audience').value.trim(),
    core_selling_points: document.getElementById('core_selling_points').value.trim(),
    acquisition_method: document.getElementById('acquisition_method').value.trim(),
    benchmarks: document.getElementById('benchmarks').value.trim(),
    benchmark_notes: document.getElementById('benchmark_notes').value.trim(),
    style: document.getElementById('style').value,
    platforms: getPlatforms(),
  };
}

async function generate() {
  const out = document.getElementById('output');
  const data = collectData();
  if (!data.platforms.length) return alert('请选择平台');
  out.textContent = '生成中...';
  try {
    const res = await api('/api/generate', 'POST', data);
    out.textContent = res.result;
  } catch (e) {
    out.textContent = '错误：' + e.message;
  }
}

function exportTxt() {
  const text = document.getElementById('output').textContent.trim();
  if (!text) return alert('没有内容');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = '爆款脚本.txt';
  a.click();
  URL.revokeObjectURL(url);
}

// Events
window.addEventListener('load', () => {
  document.getElementById('appPanel').style.display = 'grid';
});
document.getElementById('generateBtn').addEventListener('click', generate);
document.getElementById('exportBtn').addEventListener('click', exportTxt);

// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
