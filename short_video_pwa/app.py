#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, send_from_directory, render_template
from dotenv import load_dotenv

from engine import call_openai_responses
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder="static", template_folder="templates")


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


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
