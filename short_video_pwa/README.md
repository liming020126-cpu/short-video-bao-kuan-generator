# 短视频爆款生成器 (PWA)

## 本地运行
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# 填写 OPENAI_API_KEY
python app.py
```
打开 `http://localhost:8000`

## 生产部署（Render）
- 将本项目推送到 GitHub/GitLab
- Render 使用 `render.yaml` 自动部署
- 在 Render 中配置环境变量：
  - `OPENAI_API_KEY`
  - `OPENAI_MODEL` (默认 gpt-4o-mini)
  - `OPENAI_API_BASE` (默认 https://api.openai.com/v1)

## 功能
- 登录/注册（服务器数据库）
- 输入业务信息
- 选择风格与平台
- 输出按平台拆分的爆款内容
- 支持 PWA 安装

## 注意
- API 可用性受地区和网络限制影响。
