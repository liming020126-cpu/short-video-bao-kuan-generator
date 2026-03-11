#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import time
import secrets
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "app.db")


def _ensure_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            salt TEXT NOT NULL,
            pwd_hash TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
        """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            token TEXT PRIMARY KEY,
            user_id INTEGER NOT NULL,
            expires_at INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )
    conn.commit()
    conn.close()


def _get_conn():
    _ensure_db()
    return sqlite3.connect(DB_PATH)


def hash_password(password: str, salt: str | None = None):
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return salt, dk.hex()


def create_user(username: str, password: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=?", (username,))
    if cur.fetchone():
        conn.close()
        return False, "用户名已存在"
    salt, pwd_hash = hash_password(password)
    cur.execute(
        "INSERT INTO users (username, salt, pwd_hash, created_at) VALUES (?, ?, ?, ?)",
        (username, salt, pwd_hash, int(time.time())),
    )
    conn.commit()
    conn.close()
    return True, "注册成功"


def verify_user(username: str, password: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, salt, pwd_hash FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return False, "用户不存在", None
    user_id, salt, pwd_hash = row
    _, new_hash = hash_password(password, salt)
    if secrets.compare_digest(new_hash, pwd_hash):
        return True, "登录成功", user_id
    return False, "密码错误", None


def create_session(user_id: int, days: int = 7):
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + days * 24 * 3600
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO sessions (token, user_id, expires_at) VALUES (?, ?, ?)", (token, user_id, expires_at))
    conn.commit()
    conn.close()
    return token, expires_at


def delete_session(token: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM sessions WHERE token=?", (token,))
    conn.commit()
    conn.close()


def get_user_by_session(token: str):
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute("SELECT user_id, expires_at FROM sessions WHERE token=?", (token,))
    row = cur.fetchone()
    if not row:
        conn.close()
        return None
    user_id, expires_at = row
    if int(time.time()) > expires_at:
        cur.execute("DELETE FROM sessions WHERE token=?", (token,))
        conn.commit()
        conn.close()
        return None
    cur.execute("SELECT username FROM users WHERE id=?", (user_id,))
    u = cur.fetchone()
    conn.close()
    if not u:
        return None
    return {"id": user_id, "username": u[0]}
