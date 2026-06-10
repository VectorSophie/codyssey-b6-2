from pathlib import Path

try:
    import yaml as _yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

DEFAULTS: dict = {
    'commit_language': 'ko',
    'commit_prefix': True,
    'pr_language': 'ko',
    'pr_sections': ['Why', 'What', 'How to Test'],
    'safe_max_files': 10,
    'safe_max_lines': 200,
}


def load(path: str | None = None) -> dict:
    """Load .ai-gitgen.yml convention; fall back to DEFAULTS."""
    config_path = Path(path) if path else Path('.ai-gitgen.yml')

    if config_path.exists():
        if not _HAS_YAML:
            print('[WARN] pyyaml 미설치 — 컨벤션 파일 무시. pip install pyyaml')
            return DEFAULTS.copy()
        with open(config_path, encoding='utf-8') as f:
            data = _yaml.safe_load(f) or {}
        merged = {**DEFAULTS, **data.get('convention', {})}
        print(f'[INFO] 컨벤션 로드: {config_path}')
        return merged

    if path:
        print(f'[WARN] 컨벤션 파일 없음: {path}  →  기본값 사용')
    return DEFAULTS.copy()
