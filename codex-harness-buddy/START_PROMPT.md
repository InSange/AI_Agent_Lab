# 새 Codex 세션 시작 프롬프트

아래 프롬프트를 새 Codex 채팅 세션에 붙여넣으면 이 프로젝트를 이어서 진행할 수 있다.

```text
이 작업 폴더는 Hugging Face 기반 프로젝트와 Codex용 도구를 만드는 루트입니다.

먼저 루트의 AGENTS.md를 읽고 전체 작업 규칙을 따라주세요.
그다음 codex-harness-buddy/HARNESS.md와 codex-harness-buddy/README.md를 읽고 현재 프로젝트 상태를 파악해주세요.

중요 규칙:
- 모든 대화와 보고는 한국어로 해주세요.
- 파일 생성, 수정, 삭제, 폴더 구조 변경, 의존성 설치, 커밋/푸쉬는 반드시 먼저 작업 계획을 보고하고 제 승인을 받은 뒤 진행해주세요.
- 이 프로젝트는 Karpathy식 하네스 엔지니어링을 따릅니다.
- 먼저 작은 CLI 하네스부터 만들고, smoke test로 검증해주세요.
- 개인 로컬 경로, 사용자명, 토큰, .env 내용은 공개 가능한 문서나 코드에 넣지 마세요.

현재 목표:
Codex IDE에서 호출 가능한 한국어 터미널 컴패니언인 Codex Harness Buddy의 첫 CLI 버전을 설계하고 구현하는 것입니다.

원하는 첫 구현 목표:
- python tools/harness_buddy.py 실행 시 프로젝트 이름, 현재 단계, 다음 행동, 검증 명령을 한국어로 출력
- python scripts/smoke_test.py로 최소 실행 검증
- 초기 버전은 Hugging Face 모델 없이 표준 라이브러리만 사용

먼저 파일을 읽고, 어떤 파일을 어떻게 바꿀지 계획을 보고해주세요. 제가 approve라고 답하면 구현을 진행해주세요.
```
