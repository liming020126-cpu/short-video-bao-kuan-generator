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

async function checkLogin() {
  try {
    const data = await api('/api/me');
    document.getElementById('authPanel').style.display = 'none';
    document.getElementById('appPanel').style.display = 'grid';
    document.getElementById('userArea').style.display = 'flex';
    document.getElementById('userName').textContent = data.username;
  } catch (e) {
    document.getElementById('authPanel').style.display = 'block';
    document.getElementById('appPanel').style.display = 'none';
    document.getElementById('userArea').style.display = 'none';
  }
}

async function login() {
  const username = document.getElementById('authUser').value.trim();
  const password = document.getElementById('authPass').value.trim();
  if (!username || !password) return alert('请输入用户名和密码');
  await api('/api/login', 'POST', { username, password });
  await checkLogin();
}

async function register() {
  const username = document.getElementById('authUser').value.trim();
  const password = document.getElementById('authPass').value.trim();
  if (!username || !password) return alert('请输入用户名和密码');
  await api('/api/register', 'POST', { username, password });
  alert('注册成功，请登录');
}

async function logout() {
  await api('/api/logout', 'POST');
  await checkLogin();
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
window.addEventListener('load', checkLogin);

document.getElementById('loginBtn').addEventListener('click', login);
document.getElementById('registerBtn').addEventListener('click', register);
document.getElementById('logoutBtn').addEventListener('click', logout);
document.getElementById('generateBtn').addEventListener('click', generate);
document.getElementById('exportBtn').addEventListener('click', exportTxt);

// Register service worker
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
