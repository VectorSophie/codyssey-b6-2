import os
import sys

from openai import (
    OpenAI,
    AuthenticationError,
    APIConnectionError,
    RateLimitError,
    APIStatusError,
)

OPENROUTER_BASE = 'https://openrouter.ai/api/v1'


class AIClient:
    def __init__(self, model: str, temperature: float, max_tokens: int):
        api_key = os.environ.get('OPENROUTER_API_KEY')
        if not api_key:
            print('[ERROR] OPENROUTER_API_KEY 환경변수가 설정되지 않았습니다.')
            print('## 예) .env 파일에  OPENROUTER_API_KEY="YOUR_KEY"  추가')
            sys.exit(1)

        self.client = OpenAI(base_url=OPENROUTER_BASE, api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{'role': 'user', 'content': prompt}],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
            return resp.choices[0].message.content or ''
        except AuthenticationError:
            print('[ERROR] API 인증 실패: OPENROUTER_API_KEY를 확인하세요.')
            sys.exit(1)
        except APIConnectionError as e:
            print(f'[ERROR] 네트워크 연결 오류: {e}')
            sys.exit(1)
        except RateLimitError:
            print('[ERROR] API 요청 한도 초과. 잠시 후 다시 시도하세요.')
            sys.exit(1)
        except APIStatusError as e:
            print(f'[ERROR] API 오류 ({e.status_code}): {e.message}')
            sys.exit(1)
        except Exception as e:
            print(f'[ERROR] API 호출 실패: {e}')
            sys.exit(1)
