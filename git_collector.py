import re
import subprocess

# Default safe-mode limits (overridable via CLI or convention)
DEFAULT_MAX_FILES = 10
DEFAULT_MAX_LINES = 200

_SENSITIVE: list[tuple[str, str]] = [
    # OpenRouter / OpenAI keys
    (r'sk-or-[A-Za-z0-9\-_]{20,}', '[MASKED_OR_KEY]'),
    (r'sk-[A-Za-z0-9\-_]{20,}', '[MASKED_API_KEY]'),
    # Anthropic keys
    (r'sk-ant-[A-Za-z0-9\-_]{20,}', '[MASKED_ANT_KEY]'),
    # AWS keys
    (r'AKIA[0-9A-Z]{16}', '[MASKED_AWS_KEY]'),
    # JWT tokens
    (r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.?[A-Za-z0-9\-_.+/=]*', '[MASKED_JWT]'),
    # PEM private keys
    (r'-----BEGIN [A-Z ]+ KEY-----[\s\S]+?-----END [A-Z ]+ KEY-----',
     '[MASKED_PEM_KEY]'),
    # Generic secret assignments
    (r'(?i)(api[_-]?key|secret[_-]?key|access[_-]?token|password|passwd)\s*[=:]\s*[\'"]?[A-Za-z0-9\-_/+]{8,}[\'"]?',
     r'\1=[MASKED]'),
    # Email addresses
    (r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', '[MASKED_EMAIL]'),
    # Credit card numbers
    (r'\b[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}[- ]?[0-9]{4}\b', '[MASKED_CC]'),
]


class GitCollector:
    def _run(self, cmd: list[str]) -> str:
        r = subprocess.run(cmd, capture_output=True, text=True,
                           encoding='utf-8', errors='replace')
        return r.stdout

    def get_status(self) -> str:
        return self._run(['git', 'status'])

    def count_changed_files(self) -> int:
        out = self._run(['git', 'status', '--porcelain'])
        return len([l for l in out.splitlines() if l.strip()])

    def get_diff(self, safe_mode: bool = False, for_pr: bool = False,
                 safe_max_files: int = DEFAULT_MAX_FILES,
                 safe_max_lines: int = DEFAULT_MAX_LINES) -> str:
        diff = ''
        if for_pr:
            diff = self._branch_diff()
        if not diff:
            staged = self._run(['git', 'diff', '--cached'])
            unstaged = self._run(['git', 'diff'])
            diff = (staged + unstaged).strip()
        if not diff:
            diff = self._run(['git', 'diff', 'HEAD~1']).strip()

        if safe_mode:
            diff, stats = self._apply_safe(diff, safe_max_files, safe_max_lines)
            if stats['masked']:
                print(f'[SAFE] 민감 패턴 {stats["masked"]}건 마스킹됨')
            if stats['files_trimmed']:
                print(f'[SAFE] 파일 {stats["files_trimmed"]}개 생략됨 (최대 {safe_max_files}개)')
            if stats['lines_trimmed']:
                print(f'[SAFE] {stats["lines_trimmed"]}줄 생략됨 (최대 {safe_max_lines}줄)')

        return diff

    def get_current_branch(self) -> str:
        branch = self._run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch or 'main'

    def _branch_diff(self) -> str:
        for base in ['main', 'master', 'origin/main', 'origin/master']:
            r = subprocess.run(['git', 'merge-base', 'HEAD', base],
                               capture_output=True, text=True)
            if r.returncode == 0:
                sha = r.stdout.strip()
                diff = self._run(['git', 'diff', f'{sha}..HEAD'])
                if diff:
                    return diff
        return ''

    def _apply_safe(self, diff: str, max_files: int,
                    max_lines: int) -> tuple[str, dict]:
        stats = {'masked': 0, 'files_trimmed': 0, 'lines_trimmed': 0}

        for pattern, repl in _SENSITIVE:
            new, n = re.subn(pattern, repl, diff, flags=re.DOTALL)
            diff = new
            stats['masked'] += n

        lines = diff.splitlines()
        total_files = sum(1 for l in lines if l.startswith('diff --git'))
        filtered, file_count = [], 0
        for line in lines:
            if line.startswith('diff --git'):
                file_count += 1
                if file_count > max_files:
                    stats['files_trimmed'] = total_files - max_files
                    filtered.append(
                        f'\n[SAFE] 나머지 {stats["files_trimmed"]}개 파일 생략됨')
                    break
            filtered.append(line)

        result = '\n'.join(filtered)
        result_lines = result.splitlines()
        if len(result_lines) > max_lines:
            stats['lines_trimmed'] = len(result_lines) - max_lines
            result = '\n'.join(result_lines[:max_lines])
            result += f'\n\n[SAFE] {stats["lines_trimmed"]}줄 생략됨'

        return result, stats
