"""self-check: 실제 uvicorn 서버를 띄우고 create -> list -> detail -> edit -> not_found -> delete 흐름을 검증한다.
실행: python3 test_app.py
"""
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

BASE = "http://127.0.0.1:8010"
DB_FILE = "test_run_database.db"


def request(method, path, data=None):
    body = urllib.parse.urlencode(data).encode() if data is not None else None
    req = urllib.request.Request(BASE + path, data=body, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return resp.status, resp.geturl(), resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.geturl(), e.read().decode()


def run():
    for f in (DB_FILE,):
        if os.path.exists(f):
            os.remove(f)

    env = dict(os.environ, DATABASE_URL=f"sqlite:///./{DB_FILE}")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8010"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(BASE + "/", timeout=0.5)
                break
            except Exception:
                time.sleep(0.2)
        else:
            raise RuntimeError("server did not start: " + proc.stdout.read().decode())

        status, _, body = request("GET", "/")
        assert status == 200 and "메모" in body

        status, _, body = request("GET", "/memos")
        assert status == 200 and "등록된 메모가 없습니다" in body

        status, url, _ = request("POST", "/memos", {"title": "오늘 배운 것", "content": "PRG 패턴"})
        assert status == 200  # urllib follows the 303 redirect automatically
        memo_id = url.rstrip("/").split("/")[-1]

        status, _, body = request("GET", f"/memos/{memo_id}")
        assert status == 200 and "오늘 배운 것" in body and "PRG 패턴" in body

        status, _, body = request("GET", "/memos")
        assert "오늘 배운 것" in body

        status, _, _ = request(
            "POST", f"/memos/{memo_id}/edit", {"title": "수정된 제목", "content": "수정된 내용"}
        )
        assert status == 200

        status, _, body = request("GET", f"/memos/{memo_id}")
        assert "수정된 제목" in body and "수정된 내용" in body

        status, _, body = request("GET", "/memos/999999")
        assert status == 404 and "찾을 수 없습니다" in body

        status, _, _ = request("POST", f"/memos/{memo_id}/delete")
        assert status == 200

        status, _, body = request("GET", "/memos")
        assert "등록된 메모가 없습니다" in body

        print("OK: all self-checks passed")
    finally:
        proc.terminate()
        proc.wait(timeout=5)
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)


if __name__ == "__main__":
    run()
