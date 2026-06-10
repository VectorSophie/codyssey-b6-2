_COMMIT_TMPL = """\
Git 변경 사항을 분석하여 커밋 메시지를 생성하세요.

규칙:
- 제목: 50자 이내 권장(최대 72자), 명령형, 마침표 없음
- conventional commit 형식: feat/fix/docs/refactor/test/chore/style
- 본문: 변경된 파일(모듈) 1~3개 언급, 핵심 변경 사항 1~2개를 불릿으로 요약
- 커밋 메시지만 출력하고 다른 설명은 쓰지 않음

출력 형식:
<type>: <한 줄 설명>

- <변경 사항 1>
- <변경 사항 2>

--- GIT STATUS ---
{status}

--- GIT DIFF ---
{diff}
"""

_PR_TMPL = """\
Git 변경 사항을 분석하여 Pull Request 제목과 본문 초안을 생성하세요.

규칙:
- PR 제목: 최대 80자, 변경 내용을 명확하게 표현
- PR 본문: 아래 정확한 섹션 구조 필수 (각 섹션 최소 불릿 1개)
- 한국어로 작성
- 다른 설명 없이 지정된 형식만 출력

출력 형식 (이 형식을 정확히 따를 것):
TITLE: <PR 제목>

## Why
- <변경 배경>

## What
- <핵심 변경 사항>

## How to Test
- <테스트 방법>

--- 현재 브랜치 ---
{branch}

--- GIT STATUS ---
{status}

--- GIT DIFF ---
{diff}
"""


def build_commit_prompt(status: str, diff: str) -> str:
    return _COMMIT_TMPL.format(status=status, diff=diff)


def build_pr_prompt(status: str, diff: str, branch: str) -> str:
    return _PR_TMPL.format(status=status, diff=diff, branch=branch)
