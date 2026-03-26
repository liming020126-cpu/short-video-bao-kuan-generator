#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from dotenv import load_dotenv

from engine import call_openai_responses, call_openai_with_image
from prompts import (
    SYSTEM_PROMPT, build_user_prompt,
    PRODUCT_VIDEO_SYSTEM_PROMPT, build_product_video_prompt,
    VOICEOVER_SYSTEM_PROMPT, build_voiceover_prompt,
    PUBLISH_SYSTEM_PROMPT, build_publish_prompt,
)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder="static", template_folder="templates")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/manifest.json")
def manifest():
    return send_from_directory(app.static_folder, "manifest.json")


@app.route("/sw.js")
def sw():
    return send_from_directory(app.static_folder, "sw.js")


@app.route("/health")
def health():
    return {"ok": True}


@app.route("/api/register", methods=["POST"])
def api_register():
    return jsonify({"ok": False, "message": "已关闭登录功能"}), 404


@app.route("/api/login", methods=["POST"])
def api_login():
    return jsonify({"ok": False, "message": "已关闭登录功能"}), 404


@app.route("/api/logout", methods=["POST"])
def api_logout():
    return jsonify({"ok": True})


@app.route("/api/me", methods=["GET"])
def api_me():
    return jsonify({"ok": True, "username": "guest"})


@app.route("/api/generate", methods=["POST"])
def api_generate():
    data = request.get_json(force=True)
    # Build prompt
    user_prompt = build_user_prompt(data)
    try:
        result = call_openai_responses(SYSTEM_PROMPT, user_prompt)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


@app.route("/api/analyze-product", methods=["POST"])
def api_analyze_product():
    """Module 1: analyze a product image and generate a complete promotional video plan."""
    image_bytes = None
    mime_type = "image/jpeg"

    if request.content_type and "multipart/form-data" in request.content_type:
        # File upload path
        file = request.files.get("image")
        if file:
            mime_type = file.content_type or "image/jpeg"
            if mime_type not in ALLOWED_IMAGE_TYPES:
                return jsonify({"ok": False, "message": "不支持的图片格式，请上传 JPG/PNG/WEBP"}), 400
            image_bytes = file.read()
            if len(image_bytes) > MAX_IMAGE_BYTES:
                return jsonify({"ok": False, "message": "图片文件过大，请上传 10MB 以内的图片"}), 400
        data = request.form.to_dict(flat=True)
        # platforms is submitted as comma-separated string from FormData
        platforms_raw = data.get("platforms", "")
        data["platforms"] = [p.strip() for p in platforms_raw.split(",") if p.strip()]
    else:
        data = request.get_json(force=True)

    user_prompt = build_product_video_prompt(data, has_image=image_bytes is not None)
    try:
        if image_bytes:
            result = call_openai_with_image(PRODUCT_VIDEO_SYSTEM_PROMPT, user_prompt, image_bytes, mime_type)
        else:
            result = call_openai_responses(PRODUCT_VIDEO_SYSTEM_PROMPT, user_prompt)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


@app.route("/api/analyze-competitor", methods=["POST"])
def api_analyze_competitor():
    """Module 2: analyze a competitor video and generate an original voice-over script."""
    data = request.get_json(force=True)
    user_prompt = build_voiceover_prompt(data)
    try:
        result = call_openai_responses(VOICEOVER_SYSTEM_PROMPT, user_prompt)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


@app.route("/api/generate-publish-content", methods=["POST"])
def api_generate_publish_content():
    """Module 3: generate platform-specific publishing content for a finished video."""
    data = request.get_json(force=True)
    user_prompt = build_publish_prompt(data)
    try:
        result = call_openai_responses(PUBLISH_SYSTEM_PROMPT, user_prompt)
        return jsonify({"ok": True, "result": result})
    except Exception as e:
        return jsonify({"ok": False, "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
