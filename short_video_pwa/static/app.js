// ─── Utilities ───────────────────────────────────────────────────────────────

async function api(path, method = 'GET', body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(path, opts);
  const data = await res.json();
  if (!res.ok) throw new Error(data.message || '请求失败');
  return data;
}

function getChecked(containerId) {
  return Array.from(document.querySelectorAll(`#${containerId} input[type=checkbox]`))
    .filter(i => i.checked)
    .map(i => i.value);
}

function setLoading(btn, loading) {
  btn.disabled = loading;
  btn.classList.toggle('loading', loading);
}

function exportTxt(outputId, filename) {
  const text = document.getElementById(outputId).textContent.trim();
  if (!text || text.startsWith('请填写')) return alert('没有可导出的内容');
  const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = filename; a.click();
  URL.revokeObjectURL(url);
}

// ─── Tab switching ────────────────────────────────────────────────────────────

document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById(btn.dataset.tab).classList.add('active');
  });
});

// ─── Tab 0: 爆款文案生成器 ───────────────────────────────────────────────────

function collectScriptData() {
  return {
    business: document.getElementById('business').value.trim(),
    industry: document.getElementById('industry').value.trim(),
    audience: document.getElementById('audience').value.trim(),
    core_selling_points: document.getElementById('core_selling_points').value.trim(),
    acquisition_method: document.getElementById('acquisition_method').value.trim(),
    benchmarks: document.getElementById('benchmarks').value.trim(),
    benchmark_notes: document.getElementById('benchmark_notes').value.trim(),
    style: document.getElementById('style').value,
    platforms: getChecked('scriptPlatforms'),
  };
}

async function generateScript() {
  const out = document.getElementById('output');
  const btn = document.getElementById('generateBtn');
  const data = collectScriptData();
  if (!data.platforms.length) return alert('请选择平台');
  out.textContent = '生成中，请稍候…';
  setLoading(btn, true);
  try {
    const res = await api('/api/generate', 'POST', data);
    out.textContent = res.result;
  } catch (e) {
    out.textContent = '错误：' + e.message;
  } finally {
    setLoading(btn, false);
  }
}

document.getElementById('generateBtn').addEventListener('click', generateScript);
document.getElementById('exportBtn').addEventListener('click', () => exportTxt('output', '爆款脚本.txt'));

// ─── Tab 1: 带货视频生成器 ───────────────────────────────────────────────────

let productImageFile = null;

function setupImageUpload(areaId, inputId, hintId, previewId) {
  const area = document.getElementById(areaId);
  const input = document.getElementById(inputId);
  const hint = document.getElementById(hintId);
  const preview = document.getElementById(previewId);

  function handleFile(file) {
    if (!file) return;
    if (!file.type.startsWith('image/')) return alert('请上传图片文件');
    if (file.size > 10 * 1024 * 1024) return alert('图片文件不能超过 10MB');
    productImageFile = file;
    const reader = new FileReader();
    reader.onload = e => {
      preview.src = e.target.result;
      preview.classList.remove('hidden');
      hint.classList.add('hidden');
    };
    reader.readAsDataURL(file);
  }

  input.addEventListener('change', () => handleFile(input.files[0]));
  area.addEventListener('dragover', e => { e.preventDefault(); area.classList.add('drag-over'); });
  area.addEventListener('dragleave', () => area.classList.remove('drag-over'));
  area.addEventListener('drop', e => {
    e.preventDefault(); area.classList.remove('drag-over');
    handleFile(e.dataTransfer.files[0]);
  });
}

setupImageUpload('productUploadArea', 'productImage', 'productUploadHint', 'productImagePreview');

async function analyzeProduct() {
  const out = document.getElementById('productOutput');
  const btn = document.getElementById('analyzeProductBtn');
  const topic = document.getElementById('productDescription').value.trim();
  if (!topic && !productImageFile) return alert('请上传商品图片或填写商品描述');

  out.textContent = '正在分析商品并生成带货方案，请稍候…';
  setLoading(btn, true);

  try {
    const platforms = getChecked('productPlatforms');
    let res;

    if (productImageFile) {
      // Multipart form upload with image
      const fd = new FormData();
      fd.append('image', productImageFile);
      fd.append('category', document.getElementById('productCategory').value);
      fd.append('description', document.getElementById('productDescription').value.trim());
      fd.append('target_audience', document.getElementById('productAudience').value.trim());
      fd.append('price_range', document.getElementById('productPrice').value.trim());
      fd.append('digital_human_desc', document.getElementById('productDigitalHuman').value.trim());
      fd.append('style', document.getElementById('productStyle').value);
      fd.append('platforms', platforms.join(','));
      const r = await fetch('/api/analyze-product', { method: 'POST', body: fd });
      res = await r.json();
      if (!r.ok) throw new Error(res.message || '请求失败');
    } else {
      res = await api('/api/analyze-product', 'POST', {
        category: document.getElementById('productCategory').value,
        description: document.getElementById('productDescription').value.trim(),
        target_audience: document.getElementById('productAudience').value.trim(),
        price_range: document.getElementById('productPrice').value.trim(),
        digital_human_desc: document.getElementById('productDigitalHuman').value.trim(),
        style: document.getElementById('productStyle').value,
        platforms,
      });
    }
    out.textContent = res.result;
  } catch (e) {
    out.textContent = '错误：' + e.message;
  } finally {
    setLoading(btn, false);
  }
}

document.getElementById('analyzeProductBtn').addEventListener('click', analyzeProduct);
document.getElementById('exportProductBtn').addEventListener('click', () => exportTxt('productOutput', '带货视频方案.txt'));

// ─── Tab 2: 口播脚本生成器 ───────────────────────────────────────────────────

async function analyzeCompetitor() {
  const out = document.getElementById('voiceoverOutput');
  const btn = document.getElementById('analyzeCompetitorBtn');
  const topic = document.getElementById('voiceoverVideoTopic').value.trim();
  if (!topic) return alert('请填写对标视频的主题 / 选题方向');

  out.textContent = '正在分析对标视频并生成口播方案，请稍候…';
  setLoading(btn, true);

  try {
    const res = await api('/api/analyze-competitor', 'POST', {
      video_url: document.getElementById('voiceoverVideoUrl').value.trim(),
      video_topic: document.getElementById('voiceoverVideoTopic').value.trim(),
      video_description: document.getElementById('voiceoverVideoDesc').value.trim(),
      own_business: document.getElementById('voiceoverOwnBusiness').value.trim(),
      own_audience: document.getElementById('voiceoverOwnAudience').value.trim(),
      digital_human_desc: document.getElementById('voiceoverDigitalHuman').value.trim(),
      style: document.getElementById('voiceoverStyle').value,
      platforms: getChecked('voiceoverPlatforms'),
    });
    out.textContent = res.result;
  } catch (e) {
    out.textContent = '错误：' + e.message;
  } finally {
    setLoading(btn, false);
  }
}

document.getElementById('analyzeCompetitorBtn').addEventListener('click', analyzeCompetitor);
document.getElementById('exportVoiceoverBtn').addEventListener('click', () => exportTxt('voiceoverOutput', '口播视频方案.txt'));

// ─── Tab 3: 多平台一键发布 ───────────────────────────────────────────────────

async function generatePublishContent() {
  const out = document.getElementById('publishOutput');
  const btn = document.getElementById('generatePublishBtn');
  const title = document.getElementById('publishVideoTitle').value.trim();
  const desc = document.getElementById('publishVideoDesc').value.trim();
  if (!title || !desc) return alert('请填写视频标题和内容摘要');

  out.textContent = '正在为各平台生成发布方案，请稍候…';
  setLoading(btn, true);

  try {
    const res = await api('/api/generate-publish-content', 'POST', {
      video_title: title,
      video_description: desc,
      video_category: document.getElementById('publishVideoCategory').value,
      core_selling_points: document.getElementById('publishSellingPoints').value.trim(),
      target_audience: document.getElementById('publishAudience').value.trim(),
      account_style: document.getElementById('publishAccountStyle').value.trim(),
      platforms: getChecked('publishPlatforms'),
    });
    out.textContent = res.result;
  } catch (e) {
    out.textContent = '错误：' + e.message;
  } finally {
    setLoading(btn, false);
  }
}

document.getElementById('generatePublishBtn').addEventListener('click', generatePublishContent);
document.getElementById('exportPublishBtn').addEventListener('click', () => exportTxt('publishOutput', '多平台发布方案.txt'));

// ─── Checkbox chip styling fallback (for browsers without :has() support) ────

function syncChipStyles() {
  document.querySelectorAll('.chips input[type=checkbox]').forEach(cb => {
    const label = cb.closest('label');
    if (label) label.classList.toggle('checked', cb.checked);
  });
}

document.querySelectorAll('.chips input[type=checkbox]').forEach(cb => {
  cb.addEventListener('change', syncChipStyles);
});

syncChipStyles();

// ─── Service Worker ───────────────────────────────────────────────────────────

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
