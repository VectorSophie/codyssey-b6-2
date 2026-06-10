"""AI 기반 Git 커밋/PR 자동 생성기."""
import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / '.env')

import convention as conv
from ai_client import AIClient
from git_collector import GitCollector
from prompt_builder import build_commit_prompt, build_pr_prompt
from validator import validate_commit, validate_pr

DEFAULT_MODEL = 'anthropic/claude-3.5-haiku'
DEFAULT_TEMPERATURE = 0.3
DEFAULT_MAX_TOKENS = 1024


def _make_client(args: argparse.Namespace) -> AIClient:
    return AIClient(
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )


def cmd_commit(args: argparse.Namespace, convention: dict) -> None:
    collector = GitCollector()

    if not collector.count_changed_files():
        print('[INFO] 변경 사항이 없습니다. 커밋 메시지를 생성하지 않고 종료합니다.')
        sys.exit(0)

    max_files = args.safe_max_files or convention.get('safe_max_files', 10)
    max_lines = args.safe_max_lines or convention.get('safe_max_lines', 200)

    status = collector.get_status()
    diff = collector.get_diff(safe_mode=args.safe_mode,
                              safe_max_files=max_files, safe_max_lines=max_lines)
    file_count = collector.count_changed_files()
    diff_lines = len(diff.splitlines())

    print(f'[INFO] Git status 수집 완료: {file_count}개 파일 변경 감지')
    print(f'[INFO] Git diff 수집 완료: {diff_lines}줄')
    if args.safe_mode:
        print(f'[INFO] 안전 모드: 파일 최대 {max_files}개 / 줄 최대 {max_lines}줄')
    print('[INFO] AI API 요청 중...')

    client = _make_client(args)
    prompt = build_commit_prompt(status, diff, convention)
    result = client.generate(prompt)
    commit_msg = validate_commit(result)

    print('[DONE] 커밋 메시지 생성 완료\n')
    print('--- Commit Message ---')
    print(commit_msg)
    print('----------------------')
    print(f'\n[INFO] 모델: {args.model}  |  호출 횟수: 1')


def cmd_pr(args: argparse.Namespace, convention: dict) -> None:
    collector = GitCollector()

    if not collector.count_changed_files():
        print('[INFO] 변경 사항이 없습니다. PR 초안을 생성하지 않고 종료합니다.')
        sys.exit(0)

    max_files = args.safe_max_files or convention.get('safe_max_files', 10)
    max_lines = args.safe_max_lines or convention.get('safe_max_lines', 200)

    branch = collector.get_current_branch()
    diff = collector.get_diff(safe_mode=args.safe_mode, for_pr=True,
                              safe_max_files=max_files, safe_max_lines=max_lines)
    status = collector.get_status()
    diff_lines = len(diff.splitlines())

    print(f'[INFO] 현재 브랜치: {branch}')
    print(f'[INFO] Git diff 수집 완료: {diff_lines}줄')
    if args.safe_mode:
        print(f'[INFO] 안전 모드: 파일 최대 {max_files}개 / 줄 최대 {max_lines}줄')
    print('[INFO] AI API 요청 중...')

    client = _make_client(args)
    prompt = build_pr_prompt(status, diff, branch, convention)
    result = client.generate(prompt)
    title, body = validate_pr(result)

    print('[DONE] PR 초안 생성 완료\n')
    print('--- PR Title ---')
    print(title)
    print('--- PR Body ---')
    print(body)
    print('---------------')
    print(f'\n[INFO] 모델: {args.model}  |  호출 횟수: 1')


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog='main.py',
        description='AI 기반 Git 커밋/PR 자동 생성기 (OpenRouter)',
    )
    parser.add_argument('--model', '-m', default=DEFAULT_MODEL,
                        help=f'AI 모델 ID (기본값: {DEFAULT_MODEL})')
    parser.add_argument('--temperature', '-t', type=float, default=DEFAULT_TEMPERATURE,
                        help=f'생성 온도 0.0~1.0 (기본값: {DEFAULT_TEMPERATURE})')
    parser.add_argument('--max-tokens', type=int, default=DEFAULT_MAX_TOKENS,
                        dest='max_tokens',
                        help=f'최대 출력 토큰 수 (기본값: {DEFAULT_MAX_TOKENS})')
    parser.add_argument('--safe-mode', '-s', action='store_true',
                        help='민감 정보 마스킹 + diff 크기 제한')
    parser.add_argument('--safe-max-files', type=int, default=None,
                        dest='safe_max_files',
                        help='안전 모드 파일 수 제한 (기본값: 컨벤션 설정 또는 10)')
    parser.add_argument('--safe-max-lines', type=int, default=None,
                        dest='safe_max_lines',
                        help='안전 모드 줄 수 제한 (기본값: 컨벤션 설정 또는 200)')
    parser.add_argument('--convention', '-c', default=None, metavar='FILE',
                        help='컨벤션 설정 파일 경로 (기본값: .ai-gitgen.yml)')

    sub = parser.add_subparsers(dest='command', metavar='command')
    sub.add_parser('commit', help='커밋 메시지 자동 생성')
    sub.add_parser('pr', help='PR 제목/본문 초안 자동 생성')

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    convention = conv.load(args.convention)

    if args.command == 'commit':
        cmd_commit(args, convention)
    elif args.command == 'pr':
        cmd_pr(args, convention)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
