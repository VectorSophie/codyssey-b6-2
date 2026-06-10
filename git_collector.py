import re
import subprocess

SAFE_MAX_FILES = 10
SAFE_MAX_LINES = 200

_SENSITIVE = [
    (r'sk-[A-Za-z0-9\-_]{20,}', '[MASKED_API_KEY]'),
    (r'AKIA[0-9A-Z]{16}', '[MASKED_AWS_KEY]'),
    (r'[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}', '[MASKED_EMAIL]'),
    (r'(?i)(password|passwd|secret|token)\s*[=:]\s*\S+', r'\1=[MASKED]'),
]


class GitCollector:
    def _run(self, cmd: list[str]) -> str:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        return r.stdout

    def get_status(self) -> str:
        return self._run(['git', 'status'])

    def count_changed_files(self) -> int:
        out = self._run(['git', 'status', '--porcelain'])
        return len([l for l in out.splitlines() if l.strip()])

    def get_diff(self, safe_mode: bool = False, for_pr: bool = False) -> str:
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
            diff = self._apply_safe(diff)
        return diff

    def get_current_branch(self) -> str:
        branch = self._run(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()
        return branch or 'main'

    def _branch_diff(self) -> str:
        for base in ['main', 'master', 'origin/main', 'origin/master']:
            r = subprocess.run(
                ['git', 'merge-base', 'HEAD', base],
                capture_output=True, text=True
            )
            if r.returncode == 0:
                sha = r.stdout.strip()
                diff = self._run(['git', 'diff', f'{sha}..HEAD'])
                if diff:
                    return diff
        return ''

    def _apply_safe(self, diff: str) -> str:
        for pattern, repl in _SENSITIVE:
            diff = re.sub(pattern, repl, diff)

        lines = diff.splitlines()
        total_files = sum(1 for l in lines if l.startswith('diff --git'))
        filtered, file_count = [], 0
        for line in lines:
            if line.startswith('diff --git'):
                file_count += 1
                if file_count > SAFE_MAX_FILES:
                    filtered.append(
                        f'\n[SAFE MODE] 나머지 {total_files - SAFE_MAX_FILES}개 파일 생략됨'
                    )
                    break
            filtered.append(line)

        result = '\n'.join(filtered)
        result_lines = result.splitlines()
        if len(result_lines) > SAFE_MAX_LINES:
            result = '\n'.join(result_lines[:SAFE_MAX_LINES])
            result += f'\n\n[SAFE MODE] diff {len(result_lines) - SAFE_MAX_LINES}줄 생략됨'
        return result
