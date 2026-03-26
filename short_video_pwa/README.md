# 短视频智能体 — PWA 应用目录

本目录包含 Flask PWA 应用的全部源码。详细的使用说明请查阅根目录的 [README.md](../README.md)。

## 本地运行

```bash
# 在 short_video_pwa 目录下执行
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env，填写 OPENAI_API_KEY
python app.py
```

打开 `http://localhost:8000`

## 生产部署（Render）

项目根目录的 `render.yaml` 已配置好部署参数，推送到 GitHub 后在 Render 中连接仓库即可自动部署。
需要在 Render 后台配置以下环境变量：

- `OPENAI_API_KEY`（必填）
- `OPENAI_MODEL`（默认 `gpt-4o-mini`）
- `OPENAI_VISION_MODEL`（默认 `gpt-4o`，用于商品图片分析）
- `OPENAI_API_BASE`（默认 `https://api.openai.com/v1`）

## 目录结构

```
short_video_pwa/
├── app.py          # Flask 路由（4 个 API 端点 + 静态文件服务）
├── engine.py       # OpenAI API 调用封装（文本 + 视觉）
├── prompts.py      # 四个模块的系统提示词与用户提示词构建器
├── db.py           # SQLite 用户/会话工具（当前未启用登录）
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html  # 四标签页 PWA 主界面
└── static/
    ├── app.js      # 前端逻辑（标签切换、图片上传、API 调用）
    ├── app.css     # 深色主题样式
    ├── manifest.json
    └── sw.js       # Service Worker（PWA 离线缓存）
```

## API 端点

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/generate` | 模块一：爆款文案生成 |
| `POST` | `/api/analyze-product` | 模块二：带货视频方案生成（支持图片上传） |
| `POST` | `/api/analyze-competitor` | 模块三：口播脚本改写 |
| `POST` | `/api/generate-publish-content` | 模块四：多平台发布文案生成 |
| `GET`  | `/health` | 健康检查 |

