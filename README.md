# AI Agent Lab

Hugging Face 모델과 AI 에이전트 도구를 실험하고, 작은 하네스부터 검증 가능한 형태로 쌓아가는 작업 저장소입니다.

이 저장소는 여러 하위 프로젝트를 담는 루트입니다. 각 프로젝트는 가능한 한 자체 `README.md`와 `HARNESS.md`를 두고, 실행 방법과 검증 방법을 분리해 기록합니다.

## 작업 원칙

- 먼저 작은 CLI, 스크립트, smoke test 같은 최소 하네스를 만든다.
- 파일 구조와 의존성은 프로젝트 목적에 필요한 만큼만 추가한다.
- Hugging Face 모델을 쓰는 경우 모델 ID, 라이선스, 입력/출력 형식, 실행 요구사항을 문서화한다.
- 토큰, `.env`, 개인 로컬 경로, 모델 캐시, 대형 데이터는 저장소에 포함하지 않는다.
- 각 작업은 검증 명령 또는 수동 확인 방법을 남긴다.

## 프로젝트 목록

| 프로젝트 | 설명 | 상태 |
| --- | --- | --- |
| `codex-harness-buddy` | Codex IDE에서 호출할 수 있는 한국어 터미널/캐릭터 하네스 버디 | 초기 프로토타입 |

## 현재 프로젝트

### codex-harness-buddy

Codex 작업 흐름에 맞춰 프로젝트 하네스를 읽고 다음 행동, 검증 명령, 상태를 한국어로 안내하는 로컬 도구입니다.

주요 실행 명령:

```powershell
python codex-harness-buddy\tools\harness_buddy.py
python codex-harness-buddy\scripts\check.py
python codex-harness-buddy\tools\buddy_character.py
```

자세한 내용은 [`codex-harness-buddy/README.md`](codex-harness-buddy/README.md)와 [`codex-harness-buddy/HARNESS.md`](codex-harness-buddy/HARNESS.md)를 확인합니다.

## 저장소 구조

```text
AI_Agent_Lab/
  README.md
  AGENTS.md
  PROJECT_HARNESS_TEMPLATE.md
  codex-harness-buddy/
    README.md
    HARNESS.md
    tools/
    scripts/
```

## 브랜치 운영

- `main`: 루트 README, 공통 규칙, 안정된 프로젝트 스냅샷
- `project/<project-name>`: 개별 하위 프로젝트 개발 브랜치

## 검증

현재 전체 검증은 다음 명령을 우선 사용합니다.

```powershell
python codex-harness-buddy\scripts\check.py
```
