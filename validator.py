import re

COMMIT_SOFT = 50
COMMIT_HARD = 72
PR_TITLE_MAX = 80
REQUIRED_SECTIONS = ['## Why', '## What', '## How to Test']


def validate_commit(text: str) -> str:
    lines = text.strip().splitlines()
    if not lines:
        return text

    title = lines[0].strip()
    if len(title) > COMMIT_HARD:
        print(f'[WARN] 커밋 제목 {len(title)}자 → {COMMIT_HARD}자로 자릅니다.')
        title = title[:COMMIT_HARD]
    elif len(title) > COMMIT_SOFT:
        print(f'[WARN] 커밋 제목이 {len(title)}자입니다. 50자 이내 권장.')

    return '\n'.join([title] + lines[1:])


def validate_pr(text: str) -> tuple[str, str]:
    text = text.strip()

    # Extract TITLE: line
    m = re.search(r'^TITLE:\s*(.+)$', text, re.MULTILINE)
    if m:
        title = m.group(1).strip()
        body = text[m.end():].strip()
    else:
        # Fallback: first line as title
        parts = text.split('\n', 1)
        title = parts[0].strip()
        body = parts[1].strip() if len(parts) > 1 else ''

    if len(title) > PR_TITLE_MAX:
        print(f'[WARN] PR 제목 {len(title)}자 → {PR_TITLE_MAX}자로 자릅니다.')
        title = title[:PR_TITLE_MAX]

    missing = [s for s in REQUIRED_SECTIONS if s not in body]
    if missing:
        print(f'[WARN] PR 본문 필수 섹션 누락: {", ".join(missing)}')

    return title, body
