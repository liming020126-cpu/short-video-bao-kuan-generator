#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from flask import Flask, request, jsonify, send_from_directory, make_response, render_template
from dotenv import load_dotenv

from db import create_user, verify_user, create_session, delete_session, get_user_by_session
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
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jsonify({"ok": False, "message": "用户名和密码不能为空"}), 400
    ok, msg = create_user(username, password)
    return jsonify({"ok": ok, "message": msg}), (200 if ok else 400)


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(force=True)
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    ok, msg, user_id = verify_user(username, password)
    if not ok:
        return jsonify({"ok": False, "message": msg}), 401

    token, expires_at = create_session(user_id)
    resp = make_response(jsonify({"ok": True, "message": "登录成功", "username": username}))
    resp.set_cookie("session", token, max_age=7 * 24 * 3600, httponly=True, samesite="Lax")
    return resp


@app.route("/api/logout", methods=["POST"])
def api_logout():
    token = request.cookies.get("session")
    if token:
        delete_session(token)
    resp = make_response(jsonify({"ok": True}))
    resp.set_cookie("session", "", expires=0)
    return resp


@app.route("/api/me", methods=["GET"])
def api_me():
    token = request.cookies.get("session")
    if not token:
        return jsonify({"ok": False}), 401
    user = get_user_by_session(token)
    if not user:
        return jsonify({"ok": False}), 401
    return jsonify({"ok": True, "username": user["username"]})


@app.route("/api/generate", methods=["POST"])
def api_generate():
    token = request.cookies.get("session")
    user = get_user_by_session(token) if token else None
    if not user:
        return jsonify({"ok": False, "message": "未登录"}), 401

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
