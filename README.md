# b6-2 — AI 기반 Git 커밋/PR 자동 생성기

Git 변경 사항(`git status`, `git diff`)을 AI API에 전달하여 커밋 메시지와 PR 초안을 자동 생성하는 Python CLI 도구.

## 개발 환경

| 항목 | 내용 |
|---|---|
| Python | 3.10 이상 |
| AI API | OpenRouter (OpenAI 호환) |
| 기본 모델 | `anthropic/claude-3.5-haiku` |

---

## 설치 및 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경변수 설정

프로젝트 루트에 `.env` 파일을 생성하고 API Key를 추가한다.

```bash
# .env
OPENROUTER_API_KEY="sk-or-v1-YOUR_KEY_HERE"
```

OpenRouter 계정 및 API Key 발급: https://openrouter.ai/keys

### 3. Git 변경 사항 준비

```bash
# 분석할 변경 사항을 스테이징
git add <파일명>   # 또는 git add .
```

---

## 명령 사용 예시

### 커밋 메시지 자동 생성

```bash
python main.py commit
```

### PR 제목/본문 초안 자동 생성

```bash
python main.py pr
```

### 옵션

| 옵션 | 기본값 | 설명 |
|---|---|---|
| `--model`, `-m` | `anthropic/claude-3.5-haiku` | AI 모델 ID |
| `--temperature`, `-t` | `0.3` | 생성 온도 (0.0~1.0) |
| `--max-tokens` | `1024` | 최대 출력 토큰 수 |
| `--safe-mode`, `-s` | 비활성화 | 민감 정보 마스킹 + diff 크기 제한 |

```bash
# 모델 변경 예시
python main.py --model openai/gpt-4o-mini commit

# 안전 모드 활성화
python main.py --safe-mode pr

# 파라미터 조합
python main.py --temperature 0.5 --max-tokens 2048 commit
```

---

## 출력 예시

### 커밋 메시지 생성 결과

```
[INFO] Git status 수집 완료: 3개 파일 변경 감지
[INFO] Git diff 수집 완료: 128줄
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료

--- Commit Message ---
feat: Git 변경 사항 기반 커밋 메시지 자동 생성 기능 추가

- git diff 결과를 수집해 AI 입력 컨텍스트로 전달하도록 구현
- 커밋 메시지 템플릿(feat/fix 등) 생성 규칙 적용
- API Key 미설정 시 안내 메시지 및 에러 처리 개선
----------------------

[INFO] 모델: anthropic/claude-3.5-haiku  |  호출 횟수: 1
```

### PR 초안 생성 결과

```
[INFO] 현재 브랜치: feature/commit-pr-generator
[INFO] Git diff 수집 완료: 429줄
[INFO] AI API 요청 중...
[DONE] PR 초안 생성 완료

--- PR Title ---
feat: 커밋/PR 자동 생성 기능 추가
--- PR Body ---
## Why
- 팀 협업 시 커밋 메시지와 PR 설명 작성에 시간이 소요되어 자동 생성 도구가 필요했습니다.

## What
- git status, git diff 결과를 수집해 AI 입력 컨텍스트로 전달하는 로직 추가
- 커밋/PR 자동 생성 CLI 구현 (python main.py commit / pr)

## How to Test
- 환경변수 설정: OPENROUTER_API_KEY를 .env에 추가
- python main.py commit 실행 후 커밋 메시지 확인
- python main.py pr 실행 후 PR 본문 구조 확인
---------------

[INFO] 모델: anthropic/claude-3.5-haiku  |  호출 횟수: 1
```

### API Key 미설정 시

```
[ERROR] OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.
## 예) .env 파일에  OPENROUTER_API_KEY="YOUR_KEY"  추가
```

### 변경 사항 없는 경우

```
[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.
```

---

## 파일 구조

```
codyssey-b6-2/
├── main.py           # CLI 진입점 (commit / pr 서브커맨드)
├── git_collector.py  # git status/diff 수집 및 안전 모드 처리
├── ai_client.py      # OpenRouter API 호출 및 예외 처리
├── prompt_builder.py # 커밋/PR 프롬프트 템플릿
├── validator.py      # 출력 길이/형식 검증 및 후처리
├── requirements.txt
├── .gitignore        # .env 포함 (API Key git 제외)
└── README.md
```

---

## 주의사항 및 운영 관점

### 민감 정보 보호

`git diff`에 API Key, 비밀번호, 이메일 등 민감 정보가 포함될 수 있다.  
`--safe-mode` 옵션 사용 시 아래 보호 정책이 적용된다.

| 정책 | 기준 |
|---|---|
| 마스킹 패턴 | `sk-...` 형태 API Key, AWS Key, 이메일 주소, `password=` 형태 |
| 파일 수 제한 | diff 최대 10개 파일 |
| 줄 수 제한 | diff 최대 200줄 |

```bash
python main.py --safe-mode commit
```

### API 비용 및 요청 횟수

- `commit`, `pr` 명령 각각 **API 1회** 호출
- 기본 모델 `anthropic/claude-3.5-haiku`: OpenRouter 기준 저비용 모델
- 1회 실행 예상 비용: 약 $0.001 미만 (diff 크기에 따라 다름)
- 비용 절감: `--max-tokens 512` 옵션으로 출력 토큰 제한 가능

### 생성 결과 검토 필수

AI가 생성한 커밋/PR 텍스트는 초안이며, **반드시 사용자가 검토 후 적용**해야 한다.  
생성된 결과는 터미널에만 출력되며, git commit 또는 PR 작성은 사용자가 직접 수행한다.
