def build_commit_prompt(status: str, diff: str, convention: dict) -> str:
    lang = '한국어' if convention.get('commit_language', 'ko') == 'ko' else 'English'
    prefix_rule = (
        '- conventional commit 형식 사용: feat/fix/docs/refactor/test/chore/style'
        if convention.get('commit_prefix', True)
        else '- prefix 없이 자유 형식 허용'
    )

    return f"""\
Git 변경 사항을 분석하여 커밋 메시지를 생성하세요.
언어: {lang}

규칙:
- 제목: 50자 이내 권장(최대 72자), 명령형, 마침표 없음
{prefix_rule}
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


def build_pr_prompt(status: str, diff: str, branch: str, convention: dict) -> str:
    lang = '한국어' if convention.get('pr_language', 'ko') == 'ko' else 'English'
    sections: list[str] = convention.get('pr_sections', ['Why', 'What', 'How to Test'])
    section_names = ', '.join(sections)
    section_template = '\n\n'.join(f'## {s}\n- <내용>' for s in sections)

    return f"""\
Git 변경 사항을 분석하여 Pull Request 제목과 본문 초안을 생성하세요.
언어: {lang}

규칙:
- PR 제목: 최대 80자, 변경 내용을 명확하게 표현
- PR 본문: 다음 섹션 필수 포함 ({section_names}), 각 섹션 최소 불릿 1개
- 다른 설명 없이 지정된 형식만 출력

출력 형식:
TITLE: <PR 제목>

{section_template}

--- 현재 브랜치 ---
{branch}

--- GIT STATUS ---
{status}

--- GIT DIFF ---
{diff}
"""
