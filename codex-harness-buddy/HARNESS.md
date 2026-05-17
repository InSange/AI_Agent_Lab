# Codex Harness Buddy - Project Harness

이 문서는 `codex-harness-buddy` 프로젝트의 하네스 제어 문서다. 새 Codex 세션은 루트 `AGENTS.md`를 먼저 읽고, 그다음 이 문서를 기준으로 작업을 이어간다.

## 1. 프로젝트 개요

### 프로젝트 이름

```text
codex-harness-buddy
```

### 한 줄 목표

```text
Codex IDE에서 호출 가능한 한국어 터미널 하네스 버디를 만든다.
```

### 사용자 시나리오

```text
사용자가 Codex IDE 또는 터미널에서 버디를 호출하면, 버디가 현재 프로젝트의 목표, 승인 규칙, 검증 명령, 다음 행동을 한국어로 안내한다.
```

### 현재 단계

```text
초기 세팅
```

## 2. 사용 모델

### Hugging Face 모델 ID

```text
현재 미사용
```

초기 버전은 Hugging Face 모델 없이 표준 Python CLI로 만든다. 이후 감정 분석, 로그 요약, 캐릭터 반응 생성 등이 필요해지면 Hugging Face 모델 도입을 검토한다.

### 태스크 유형

```text
현재 미사용
```

### 모델 라이선스

```text
현재 미사용
```

### 실행 요구사항

```text
Python: TBD
CPU/GPU: CPU
VRAM: 필요 없음
주요 패키지: 초기 버전은 표준 라이브러리 우선
대략적인 모델 크기: 해당 없음
```

### 모델 다운로드 정책

- 초기 버전에서는 모델 다운로드를 하지 않는다.
- Hugging Face 모델을 도입하려면 모델 ID, 용량, 라이선스, 저장 위치, 목적을 사용자에게 보고하고 승인받는다.
- 모델 캐시, 가중치, 데이터셋은 Git에 포함하지 않는다.

### nudge 모델 기반 분류 도입 기준

Hugging Face 모델 기반 `nudge` 분류기는 다음 기준을 먼저 만족해야 도입을 검토한다.

- 한국어 짧은 명령형 입력을 처리할 수 있다.
- `fast`, `careful`, `review`, `check`, `status`, `unknown` 의도를 구분할 수 있다.
- CPU에서 짧은 문장 1개를 실행 가능한 속도로 처리할 수 있다.
- 모델 ID, 태스크 유형, 라이선스, 다운로드 용량을 문서에 기록할 수 있다.
- `transformers`, `torch` 등 추가 의존성 필요 여부와 설치 영향을 보고할 수 있다.
- confidence 또는 score가 낮으면 명령을 추천하지 않고 확인 요청으로 처리한다.
- 모델 캐시, 가중치, 데이터셋은 저장소에 포함하지 않는다.
- 도입 전 규칙 기반 분류와 동일한 입력 샘플로 비교하는 smoke test 계획을 세운다.

모델 후보를 검토하더라도 다운로드, 의존성 설치, 코드 연결은 별도 승인 후 진행한다.

### nudge 평가 샘플

모델 후보나 규칙 변경을 평가할 때는 최소한 다음 입력과 기대 의도를 비교한다.

```text
빨리 해줘 -> fast
대충 빨리 가자 -> fast
조심해서 해줘 -> careful
좀 불안한데 -> careful
검증해줘 -> check
테스트 돌려 -> check
상태 보여줘 -> status
지금 상태 어때 -> status
마무리해도 돼? -> review
이거 믿어도 돼? -> review
```

모델 기반 분류 후보는 다음 애매한 입력을 `careful`, `review`, `unknown` 중 어떻게 다루는지도 비교한다.

```text
뭔가 이상한데? -> careful 후보
이거 가능해? -> unknown 후보
뭐 하지? -> unknown 후보
```

현재 규칙 기반 분류기는 `unknown`을 반환하지 않는다. `unknown`은 모델 기반 분류를 도입할 때 confidence가 낮은 입력을 안전하게 처리하기 위한 후보 정책으로 둔다.

평가 샘플은 다음 별도 하네스로 실행한다.

```powershell
python tools/harness_buddy.py evaluate-nudge
```

현재 `evaluate-nudge`는 내부에서 `scripts/evaluate_nudge.py`를 실행하며, 전체 `scripts/check.py` 파이프라인에는 포함하지 않는다.

## 3. 입력/출력 계약

### 입력

초기 CLI는 다음 정보를 읽는다.

```text
프로젝트 루트의 HARNESS.md
루트 AGENTS.md: 이후 단계에서 사용
선택적 상태 파일 buddy_state.json
```

명령행 인자는 추후 확정한다.

예상 예:

```powershell
python tools/harness_buddy.py
python tools/harness_buddy.py help
python tools/harness_buddy.py fast
python tools/harness_buddy.py careful
python tools/harness_buddy.py review
python tools/harness_buddy.py check
python tools/harness_buddy.py status
python tools/harness_buddy.py state-json
python tools/harness_buddy.py prompt fast
python tools/harness_buddy.py prompt careful
python tools/harness_buddy.py prompt review
python tools/harness_buddy.py check --state-path tmp\smoke_buddy_state.json
python tools/harness_buddy.py nudge "빨리 좀 해"
```

`help` 명령은 프로젝트 폴더 기준 명령과 루트 폴더 기준 명령을 나눠 안내하고, 보통 먼저 실행할 check 명령도 위치별로 표시한다.

`state-json` 명령은 캐릭터 UI가 읽을 수 있는 상태 스냅샷을 JSON으로 출력한다.

### 출력

터미널에 한국어 상태 요약을 출력한다.

예상 예:

```text
Codex Harness Buddy
프로젝트: codex-harness-buddy
현재 단계: 초기 세팅
다음 행동: 최소 CLI 하네스 설계
검증 명령: python scripts/smoke_test.py
```

Buddy 모드는 다음 운영 의도를 표현한다.

```text
fast: 빠른 응답 우선, 복잡한 판단의 검토 깊이는 줄어들 수 있음
careful: 정확성과 승인 규칙 우선, 더 느릴 수 있지만 위험과 검증을 더 분명히 확인함
review: 완료 전 점검 우선, 마지막 검증 상태를 읽어 누락과 남은 이슈 확인에 집중함
```

현재 Buddy 모드는 Codex 모델의 실제 추론 속도나 reasoning effort를 직접 변경하지 않는다. 로컬 CLI가 다음 작업 지시와 검증 기준을 어떤 톤으로 정리할지 결정하는 하네스 모드다.

`prompt` 명령은 Codex 채팅 세션에 붙여넣을 수 있는 Buddy 지시문을 출력한다. 이 지시문은 실제 세션에서 `fast`, `careful`, `review` 작업 태도를 유도하기 위한 것이다.

`check` 명령은 `scripts/check.py`를 실행하고 결과를 Buddy 출력으로 요약한다.
마지막 검증 결과, 검증 시각, 실패 시 요약은 로컬 상태 파일 `buddy_state.json`에 저장한다. 이 파일은 `.gitignore`에 포함되어 Git에 들어가지 않는다.
`--state-path`를 지정하면 테스트나 별도 도구가 실제 사용자 상태 파일을 건드리지 않고 분리된 상태 파일을 사용할 수 있다.

`status` 명령은 `buddy_state.json`을 읽어 마지막 검증 상태를 보여준다.
`review` 모드도 `buddy_state.json`을 읽어 성공/실패 상태에 따라 다음 행동을 다르게 안내한다. 실패 상태에서는 재현, 핵심 로그 확인, 최소 수정, 재검증 순서로 안내한다.
마지막 검증 시각이 30분보다 오래됐으면 `status`와 `review`는 오래된 검증 상태로 보고 다시 `check`를 권장한다.

Buddy는 루트 `AGENTS.md`의 승인 규칙을 우선한다.

```text
승인 필요: 파일/폴더 변경, 의존성/가상환경 변경, 모델/데이터 다운로드, Git 작업, 토큰/환경 변수 변경
```

`nudge` 명령은 짧은 자연어 입력을 키워드 규칙 기반으로 `fast`, `careful`, `review`, `check`, `status` 의도 중 하나에 매핑하고 다음 명령을 안내한다. `review` 계열 의도는 상태 파일을 함께 확인해 최신/오래됨/실패 상태에 따라 추천을 조정한다.
현재 `nudge`는 Hugging Face 모델이나 AI 자연어 처리 모델을 사용하지 않고, 추천 명령을 실제로 실행하지 않는다. 출력에는 `분류 방식: 키워드 규칙`, `모델 사용: 없음`, `실행 여부: 추천만 함`을 표시한다.
내부 분류 결과는 `NudgeClassification`으로 표현하며, 현재 구현은 `classify_nudge_with_rules()`를 통해 생성한다. 이후 모델 기반 분류를 도입하더라도 출력 계약은 이 결과 객체를 통해 유지한다.
초기 규칙은 `빨리`, `대충`, `조심`, `불안`, `마무리`, `믿어도`, `테스트`, `되는지`, `상태`, `어때` 같은 표현을 다룬다.

### 실패 응답

```text
HARNESS.md를 찾지 못하면 현재 폴더와 상위 폴더에서 찾았는지 설명하고, 생성 또는 경로 지정이 필요하다고 안내한다.
상태 파일을 읽지 못하면 경고만 출력하고 기본 상태로 계속한다.
검증 명령이 정의되지 않았으면 HARNESS.md 업데이트를 요청한다.
```

## 4. 최소 실행 하네스

### 최소 성공 기준

```text
python tools/harness_buddy.py 실행 시 프로젝트 이름, 현재 단계, 다음 행동, 검증 명령 안내가 한국어로 출력된다.
```

### 최소 실행 명령

```powershell
python tools/harness_buddy.py
```

### 기대 결과

```text
터미널에 Codex Harness Buddy 제목과 프로젝트 상태 요약이 표시된다.
오류 없이 종료 코드 0으로 종료된다.
```

## 5. 검증 명령

### 스모크 테스트

```powershell
python scripts/smoke_test.py
```

현재 구현된 최소 smoke test는 CLI 실행, 종료 코드 0, 필수 한국어 출력 줄을 확인한다.
또한 없는 `HARNESS.md` 경로, 필수 항목 누락, `fast`/`careful`/`review` Buddy 모드, `prompt` 명령, `check` 명령, `status` 명령의 핵심 출력을 확인한다.
`check` 명령 후 `buddy_state.json`의 `last_check.status`, `last_check.command`, `last_check.mode`, `last_check.checked_at`도 확인한다.
강제 실패 경로에서는 `last_check.summary`와 `status`의 실패 요약 출력도 확인한다.
smoke test는 `--state-path`로 테스트 전용 상태 파일을 사용해 실제 `buddy_state.json`을 오염시키지 않는다.
대표 `nudge` 입력이 의도한 명령으로 분류되는지, `review` 계열 입력이 상태 파일의 최신/오래됨/실패 상태를 반영하는지도 확인한다.

### 전체 검증 파이프라인

```powershell
python scripts/check.py
```

현재 전체 검증은 CLI 기본 실행, smoke test, UI smoke test, character UI smoke test를 실행한다.
성공 시 `검증 요약` 섹션에서 각 단계가 무엇을 확인했는지 짧게 출력한다.
`선택 검증` 섹션에는 nudge 평가, 캐릭터 UI 수동 확인, 기존 UI 수동 확인 명령을 프로젝트 폴더 기준과 루트 폴더 기준으로 나눠 표시한다.
`수동 확인` 섹션은 `[레이아웃]`, `[상호작용]`, `[Preview]` 그룹으로 나눠 출력한다. 각 그룹에는 Review 후 Nudge 입력창 표시, 예시 입력 버튼 의미, Check 실행 중 얼굴과 라벨의 `검증 중` 변경 확인, 예시 입력 후 Nudge 결과 표시, `항상 위` 체크/해제 시 창 z축 동작 확인, `Waiting`/`Needs Review` 프리뷰의 얼굴, 라벨, 반응 문구 변경 확인, Preview 확인 후 `Refresh`로 실제 상태 복귀, Preview 안내 문구 확인 항목을 배치한다.
`evaluate-nudge`는 아직 전체 검증에 포함하지 않고 별도 실행 대상으로 안내한다.

### 캐릭터 상태 하네스

```powershell
python scripts/character_state_test.py
```

현재 캐릭터 상태 하네스는 `state-json`의 `buddy.state` 값을 캐릭터 UI에서 표시할 한국어 라벨로 매핑한다.
`ready`, `stale`, `waiting`, `needs_review` 상태를 확인한다.

### 최소 캐릭터 UI

```powershell
python tools/buddy_character.py
```

초기 캐릭터 UI는 `state-json`을 읽어 ASCII 얼굴, 상태 라벨, 상태 메시지, 마지막 갱신 시각을 작은 `tkinter` 창에 표시한다.
상태별 Buddy 반응 문구는 고정 규칙 기반으로 표시한다. 현재는 Hugging Face 모델이나 자연어 생성 모델을 사용하지 않는다.
`Preview` 버튼은 상태별 얼굴, 라벨, 반응 문구를 화면에서만 미리 보여준다. 실제 `buddy_state.json`은 수정하지 않으며, `Refresh`를 누르면 실제 상태로 돌아온다. UI에는 `표시만 바뀜 · Refresh로 복귀` 안내를 함께 표시한다.
캐릭터 창 버튼은 `검증`, `명령`, `Nudge`, `예시 입력`, `Preview 확인` 영역으로 나눠 표시한다.
`Check` 버튼은 백그라운드 스레드에서 `harness_buddy.py check`를 실행한 뒤 상태를 다시 읽어 표시를 갱신한다. 실행 중에는 얼굴 `(o_o)`, 라벨 `검증 중`, 반응 문구 `검증을 돌리고 있어요.`를 표시하고, 중복 클릭과 동시 갱신을 막기 위해 조작 버튼을 비활성화한다.
Check 실행 결과는 상태 메시지와 별도의 문구로 표시한다.
`Refresh` 버튼은 `state-json`을 다시 읽어 표시와 마지막 갱신 시각을 갱신한다.
`항상 위` 토글은 `tkinter`의 `-topmost` 속성을 켜고 끈다. 기본값은 꺼짐이다.
`Status`, `Review`, `Fast`, `Careful`, `Nudge` 버튼은 캐릭터 창에서 바로 Buddy CLI 명령을 실행하고 결과 문구를 갱신한다.
결과 문구는 버튼별로 핵심 줄을 최대 2줄까지 표시한다. `Status`는 마지막 검증과 검증 상태, `Review`는 다음 행동과 마지막 검증, `Fast`와 `Careful`은 Buddy 지시문, `Nudge`는 다음 명령과 감지된 의도를 우선 보여준다.
`Nudge` 버튼은 입력 직후 UI 전용 키워드 규칙으로 캐릭터 얼굴과 라벨을 잠깐 바꾼다. `빨리`/`대충` 계열은 `빠르게`, `조심`/`불안` 계열은 `신중하게`, `검증`/`테스트`/`되는지` 계열은 `검증 준비`로 표시한다. 이 반응은 화면 피드백이며 Hugging Face 모델이나 자연어 생성 모델을 사용하지 않는다.
결과 문구 영역은 고정 높이를 사용해 긴 결과가 Nudge 입력 영역을 밀어내지 않게 한다.
`예시 입력` 영역의 Nudge 예시 버튼은 입력창에 예시 문장만 채우며 자동 실행하지 않는다. 실제 해석은 사용자가 `Nudge` 버튼을 눌렀을 때 실행한다.
아직 이미지/sprite, 애니메이션은 구현하지 않는다.

캐릭터 UI smoke test는 다음 명령으로 실행한다.

```powershell
python scripts/character_ui_smoke_test.py
```

이 하네스는 전체 `scripts/check.py` 파이프라인에도 포함한다.

### UI 하네스 계획

다음 UI 단계는 `tkinter` 기반의 작은 플로팅 데스크톱 창으로 시작한다.

```text
목표: Codex Harness Buddy의 CLI 기능을 호출하는 작은 플로팅 데스크톱 UI를 만든다.
기술: Python 표준 라이브러리 tkinter
의존성: 추가 없음
```

초기 UI 구성은 다음을 목표로 한다.

```text
창 제목: Codex Harness Buddy
상태 영역: 마지막 검증 상태 표시
상태 버튼: Check, Status, Review Status
프롬프트 버튼: Fast, Careful, Review Prompt
입력칸: nudge 자연어 입력
복사 버튼: Copy Output, Copy Prompt
출력 영역: Buddy CLI 응답 표시
```

초기 UI가 호출할 CLI 명령은 다음과 같다.

```powershell
python tools/harness_buddy.py check
python tools/harness_buddy.py status
python tools/harness_buddy.py review
python tools/harness_buddy.py prompt fast
python tools/harness_buddy.py prompt careful
python tools/harness_buddy.py prompt review
python tools/harness_buddy.py nudge "<입력>"
```

최소 UI 실행 명령은 다음과 같다.

```powershell
python tools/buddy_ui.py
```

첫 UI 프로토타입에서는 다음을 하지 않는다.

```text
캐릭터 애니메이션
이미지/sprite 생성
Hugging Face 모델 사용
공식 Codex /pet 직접 수정
Electron/Tauri/PySide 같은 추가 의존성
Codex 채팅 자동 삽입
```

### 단위 테스트

```powershell
python scripts/ui_smoke_test.py
```

현재 UI smoke test는 `tkinter` import, `tools/buddy_ui.py` import, 버튼 명령 계약, 버튼 그룹 계약, CLI 명령 생성 함수, 버튼 실행 상태 문구, Buddy 의미 상태 문구, 출력 헤더 계약, 출력 복사 버튼 계약, 프롬프트 복사 버튼 계약, 프롬프트 캐시 유지/비움 규칙, 프롬프트 없음 시 클립보드 비움 계약, Review 상태/프롬프트 분리 계약을 확인한다.

### 타입/정적 검사

```text
현재 미사용
```

### 포맷 검사

```text
현재 미사용
```

## 6. 실패 재현 절차

버그가 발견되면 다음 순서를 따른다.

1. 버그를 재현하는 명령을 기록한다.
2. 실패 로그의 핵심 줄을 기록한다.
3. 가능하면 `scripts/smoke_test.py` 또는 테스트로 재현한다.
4. 최소 코드만 수정한다.
5. 같은 명령이 통과하는지 확인한다.

### 재현 입력

```text
TBD
```

### 실패 명령

```text
TBD
```

### 기대 동작

```text
TBD
```

### 실제 동작

```text
TBD
```

## 7. 변경 승인 규칙

이 프로젝트 안에서 다음 작업은 사용자 승인 후 진행한다.

- 파일 생성, 수정, 삭제, 이동
- 폴더 구조 변경
- 의존성 추가, 제거, 버전 변경
- 모델 다운로드 또는 캐시 위치 변경
- 데이터셋 다운로드
- 환경 변수, 토큰, 인증 설정 변경
- Git 커밋, 푸쉬, 브랜치 변경
- 테스트 스냅샷 갱신
- 대규모 리팩터링 또는 포맷팅

승인 요청에는 다음을 포함한다.

1. 변경할 파일과 폴더
2. 변경 이유
3. 예상 영향 범위
4. 검증 방법

## 8. 작업 원칙

- 먼저 목표와 성공 기준을 적는다.
- 전체 플러그인보다 작은 CLI 하네스를 먼저 만든다.
- 버그는 재현 후 수정한다.
- 요청과 직접 관련 없는 코드는 바꾸지 않는다.
- 새 추상화는 중복이나 복잡도를 실제로 줄일 때만 만든다.
- 검증하지 못한 부분은 완료 보고에 반드시 적는다.

### 세션 운영 규칙

- 시작 시 루트 `AGENTS.md`를 먼저 확인한다.
- 프로젝트 상태 파악은 `HARNESS.md`의 현재 단계, 입력/출력 계약, 검증 명령, 최신 작업 로그를 우선한다.
- 필요한 경우에만 `README.md`와 관련 스크립트를 추가로 읽는다.
- 작업은 Plan → Execute 순서로 진행한다.
- Plan 단계에서는 바꿀 파일, 이유, 영향 범위, 검증 방법을 짧게 보고하고 승인받는다.
- Execute 단계에서는 승인된 범위 안에서 최소 변경만 수행한다.
- 한 번의 작업에서는 가능한 한 3개 이하의 파일만 수정한다. 하네스 계약과 문서 동시 갱신처럼 필요한 경우에는 변경 이유를 보고한다.
- 작업 전후로 `python scripts/check.py` 또는 루트 기준 `python codex-harness-buddy\scripts\check.py`를 우선 검증 명령으로 사용한다.
- 캐릭터 UI 동작은 자동 smoke test 후 사용자 환경에서 수동 확인 방법을 함께 안내한다.
- Git 커밋은 사용자가 명시적으로 요청하거나 승인한 경우에만 수행한다.
- 커밋 전 `git log --oneline -n 5`로 최신 번호를 확인한다.
- 커밋 메시지는 `#[번호] Phase X: 작업내용 요약 (한글)` 형식을 사용한다.
- 커밋에는 `buddy_state.json`, `tmp/`, `__pycache__/`, `.env`, 모델 캐시, 빌드 산출물을 포함하지 않는다.

## 9. 공개 저장소 체크리스트

공개 전 다음을 확인한다.

- 개인 사용자명이 들어간 로컬 경로를 제거하거나 일반화했다.
- `C:\Users\...` 같은 절대 경로를 `<PROJECT_ROOT>`, `<LOCAL_VENV_PATH>`, `<HF_CACHE_DIR>` 같은 플레이스홀더로 바꿨다.
- `.env`, API 키, 토큰, 개인 키, 인증 정보가 포함되지 않았다.
- 모델 캐시, 가중치, 대형 데이터셋, 임시 출력물이 포함되지 않았다.
- README, HARNESS, 예시 코드가 특정 개인 PC에만 맞춰져 있지 않다.

## 10. 금지 사항

- 사용자 승인 없는 파일/폴더 변경
- 사용자 승인 없는 의존성 설치
- 사용자 승인 없는 대형 모델 또는 데이터 다운로드
- `.env`, 토큰, 개인 키, 인증 정보 커밋
- 검증 없이 "완료"라고 보고
- 관련 없는 코드 정리, 포맷팅, 리팩터링
- 실패 로그나 테스트 실패를 숨기기

## 11. 완료 기준

초기 구현 작업은 다음 조건을 만족해야 완료로 본다.

- `python tools/harness_buddy.py`가 성공한다.
- `python scripts/smoke_test.py`가 성공한다.
- CLI 출력이 한국어로 표시된다.
- 입력/출력 계약이 문서와 실제 동작에서 일치한다.
- 변경된 파일과 실행한 검증이 보고된다.

## 12. 작업 로그

작업 로그는 최신 항목을 위에 추가한다.

```text
2026-05-18
- 작업자: Codex
- 요청: Buddy 개발 브랜치 분리 후 재개 지점 기록
- 변경 파일: HARNESS.md
- 실행한 검증: python codex-harness-buddy\scripts\check.py, 개인 경로/토큰 문자열 검색, git status --short --branch
- 결과: 완료
- 남은 이슈: 없음

2026-05-18
- 작업자: Codex
- 요청: 프로젝트 운영 규칙을 HARNESS.md에 정리하고 Git 저장 준비
- 변경 파일: HARNESS.md
- 실행한 검증: python codex-harness-buddy\scripts\check.py, 개인 경로/토큰 문자열 검색, git log --oneline -n 5
- 결과: 완료
- 남은 이슈: 없음

2026-05-18
- 작업자: Codex
- 요청: Nudge 입력 직후 캐릭터 반응 상태 표시
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 사용자 환경의 실제 Nudge 반응 체감은 수동 확인 필요

2026-05-18
- 작업자: Codex
- 요청: check 수동 확인에 Check 실행 중 검증 중 상태 항목 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 Check 실행 중 표시 체감은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: Check 실행 중 캐릭터 검증 중 상태 표시
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 사용자 환경의 실제 Check 실행 중 표시 체감은 수동 확인 필요

2026-05-17
- 작업자: Codex
- 요청: check 수동 확인에 Waiting/Needs Review 프리뷰 확인 항목 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 Waiting/Needs Review 프리뷰 체감은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: check 수동 확인 체크리스트 그룹화
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 그룹화된 수동 확인 출력의 체감 가독성은 사용자 환경에서 확인

2026-05-17
- 작업자: Codex
- 요청: check 수동 확인에 Preview 안내 문구 항목 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: Preview 안내 문구 체감은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: Preview 안내 문구 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창 안내 문구 가독성은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: check 수동 확인에 Preview 복귀 항목 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 Preview 복귀 동작은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 버튼 그룹 라벨 정리
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창 그룹 라벨 가독성은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 상태 프리뷰 모드 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 프리뷰 버튼 배치와 Refresh 복귀 동작은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 상태별 반응 문구 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창 레이아웃과 문구 체감은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: check 수동 확인에 항상 위 z축 동작 항목 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창 z축 동작은 사용자 환경에서 수동 확인

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 항상 위 토글 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창 topmost 동작은 사용자 환경에서 수동 확인 필요

2026-05-17
- 작업자: Codex
- 요청: check 출력에 캐릭터 UI 수동 확인 체크리스트 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 사용자 환경에서 진행

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 레이아웃 안정화와 Nudge 예시 의미 보강
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창에서 Review 후 Nudge 입력 영역이 보이는지 수동 확인 필요

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI Nudge 예시 입력 버튼 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 결과 요약을 2줄로 확장
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 버튼별 결과 요약 규칙 분리
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-17
- 작업자: Codex
- 요청: 캐릭터 UI 결과 요약 강화
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-17
- 작업자: Codex
- 요청: check 출력에 캐릭터 UI 수동 확인 안내 추가
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-17
- 작업자: Codex
- 요청: character UI smoke test를 전체 검증 파이프라인에 포함
- 변경 파일: scripts/check.py, README.md, HARNESS.md
- 실행한 검증: python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 캐릭터 창 수동 확인은 필요 시 별도 실행

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI 핵심 버튼 복원
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창에서 버튼 배치와 결과 문구 가독성 수동 확인 필요

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI Check 결과 문구 표시
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py, python scripts/check.py, python codex-harness-buddy\scripts\check.py
- 결과: 완료
- 남은 이슈: 실제 창에서 결과 문구가 상태 메시지와 헷갈리지 않는지 확인 필요

2026-05-16
- 작업자: Codex
- 요청: Check 실행 중 Refresh 동시 실행 방지
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Check 중 Refresh 비활성화 수동 확인 필요

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI Check 비동기 실행
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 진행률/취소/로그 표시는 아직 미구현

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI Check 실행 상태 표시 강화
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: Check 실행 중 창이 잠깐 멈추는 동기 실행 한계는 남아 있음

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI Check 버튼 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Check 클릭 후 상태 갱신 수동 확인 필요

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI 마지막 갱신 시각 표시
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Refresh 시 시간이 바뀌는지 수동 확인 필요

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI 새로고침 버튼 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 check 후 Refresh 갱신 수동 확인 필요

2026-05-16
- 작업자: Codex
- 요청: 최소 캐릭터 표시 UI 추가
- 변경 파일: tools/buddy_character.py, scripts/character_ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창 수동 확인 필요, 이미지/애니메이션/상호작용은 이후 단계

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 상태 매핑 하네스 추가
- 변경 파일: scripts/character_state_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/character_state_test.py
- 결과: 진행 중
- 남은 이슈: 실제 캐릭터 표시 UI는 다음 단계

2026-05-16
- 작업자: Codex
- 요청: 캐릭터 UI용 Buddy 상태 JSON 스냅샷 명령 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 캐릭터 UI에서 state-json을 읽는 구현은 다음 단계

2026-05-16
- 작업자: Codex
- 요청: check 선택 검증 명령도 위치별로 안내
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: check 요약이 너무 길어졌는지 사용자 확인 필요

2026-05-16
- 작업자: Codex
- 요청: help의 기본 실행 추천을 위치별로 분리
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: help가 길어졌는지 사용자 확인 필요

2026-05-16
- 작업자: Codex
- 요청: help에 실행 위치별 명령 안내 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 루트/프로젝트 폴더 기준 안내가 너무 길지 않은지 확인 필요

2026-05-16
- 작업자: Codex
- 요청: Buddy CLI 도움말 명령 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: help 설명이 충분히 짧고 이해되는지 사용자 확인 필요

2026-05-16
- 작업자: Codex
- 요청: Buddy CLI에 nudge 평가 명령 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, scripts/check.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: evaluate-nudge는 아직 전체 check.py 자동 실행 대상이 아님

2026-05-16
- 작업자: Codex
- 요청: check 요약에 선택 검증 명령 표시
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 선택 검증 명령이 사용자에게 충분히 직관적인지 확인 필요

2026-05-16
- 작업자: Codex
- 요청: check 결과가 무엇을 검증했는지 요약 출력
- 변경 파일: scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 요약 문구가 실제 사용자에게 충분히 이해되는지 확인 필요

2026-05-16
- 작업자: Codex
- 요청: nudge 평가 스크립트에 분류기 메타데이터 출력 추가
- 변경 파일: scripts/evaluate_nudge.py, HARNESS.md
- 실행한 검증: python scripts/evaluate_nudge.py
- 결과: 진행 중
- 남은 이슈: 모델 기반 분류기 비교 출력은 아직 미구현

2026-05-16
- 작업자: Codex
- 요청: nudge 의도 분류 평가 스크립트 추가
- 변경 파일: scripts/evaluate_nudge.py, README.md, HARNESS.md
- 실행한 검증: python scripts/evaluate_nudge.py
- 결과: 진행 중
- 남은 이슈: evaluate_nudge.py는 아직 전체 check.py에 포함하지 않음

2026-05-16
- 작업자: Codex
- 요청: nudge 의도 분류 평가 샘플 문서화
- 변경 파일: README.md, HARNESS.md
- 실행한 검증: python scripts/check.py
- 결과: 진행 중
- 남은 이슈: unknown 정책은 모델 기반 분류 단계까지 문서 후보로 유지

2026-05-16
- 작업자: Codex
- 요청: Hugging Face nudge 의도 분류 도입 기준 문서화
- 변경 파일: README.md, HARNESS.md
- 실행한 검증: python scripts/check.py
- 결과: 진행 중
- 남은 이슈: 모델 후보 조사, 의존성 설치, 다운로드는 아직 미진행

2026-05-16
- 작업자: Codex
- 요청: nudge 분류기 인터페이스를 규칙 기반 결과 객체로 분리
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: Hugging Face 모델 기반 분류기는 아직 미구현

2026-05-15
- 작업자: Codex
- 요청: nudge가 규칙 기반이며 모델 미사용임을 출력과 문서에 명확화
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: Hugging Face 모델 기반 의도 분류는 별도 단계로 유지

2026-05-15
- 작업자: Codex
- 요청: UI 버튼을 상태/프롬프트 그룹으로 정리
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 그룹 라벨과 버튼 간격 수동 확인 필요

2026-05-15
- 작업자: Codex
- 요청: Review 상태 점검 버튼과 Review 프롬프트 버튼 분리
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 버튼 폭과 배치가 좁지 않은지 수동 확인 필요

2026-05-15
- 작업자: Codex
- 요청: 프롬프트 캐시 비움 시 클립보드도 정리
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Copy Prompt 없음 상태 후 붙여넣기 결과 수동 확인 필요

2026-05-15
- 작업자: Codex
- 요청: UI 프롬프트 캐시 유지/비움 규칙 명확화
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Check/Status/Nudge 후 Copy Prompt가 비워지는지 수동 확인 필요

2026-05-15
- 작업자: Codex
- 요청: UI에서 마지막 프롬프트만 복사하는 Copy Prompt 추가
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: Review 점검 명령과 prompt review 전용 흐름을 분리할지 검토 필요

2026-05-15
- 작업자: Codex
- 요청: UI 출력 클립보드 복사 버튼 추가
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창에서 Copy Output 후 붙여넣기 수동 확인 필요

2026-05-14
- 작업자: Codex
- 요청: UI에 Buddy 의미 상태 패널 추가
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창 수동 확인 후 의미 상태 문구가 중복처럼 느껴지는지 확인 필요

2026-05-14
- 작업자: Codex
- 요청: UI 버튼 실행 상태와 출력 로그 구분 강화
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실제 창 수동 확인 후 상태 라벨과 로그 문구 체감 확인 필요

2026-05-14
- 작업자: Codex
- 요청: tkinter 플로팅 Buddy UI 최소 구현
- 변경 파일: tools/buddy_ui.py, scripts/ui_smoke_test.py, scripts/check.py, README.md, HARNESS.md
- 실행한 검증: python scripts/ui_smoke_test.py, python scripts/check.py
- 결과: 진행 중
- 남은 이슈: 실제 창 수동 확인 후 버튼 배치와 문구 조정 필요

2026-05-14
- 작업자: Codex
- 요청: 플로팅 Buddy UI 하네스 설계 문서화
- 변경 파일: README.md, HARNESS.md
- 실행한 검증: python scripts/check.py
- 결과: 진행 중
- 남은 이슈: tkinter 플로팅 UI 최소 구현 여부 승인 필요

2026-05-14
- 작업자: Codex
- 요청: nudge 자연어 입력 표현 확장
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 플로팅 Buddy UI 프로토타입 검토

2026-05-13
- 작업자: Codex
- 요청: nudge가 buddy_state 상태까지 고려해 review/check 추천을 조정
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: nudge 입력 표현을 더 넓힐지, Hugging Face 의도 분류 도입 여부 검토

2026-05-13
- 작업자: Codex
- 요청: 자연어 nudge 명령을 규칙 기반으로 fast/careful/review/check/status에 매핑
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: nudge가 상태 파일까지 고려해 명령을 추천하도록 확장할지 검토

2026-05-13
- 작업자: Codex
- 요청: smoke test가 실제 buddy_state.json을 오염시키지 않도록 --state-path 상태 파일 격리 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 자연어 nudge 명령을 규칙 기반으로 모드에 매핑할지 검토

2026-05-13
- 작업자: Codex
- 요청: 마지막 검증 시각이 30분보다 오래됐는지 감지해 재검증 권장
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 자연어 nudge 명령을 규칙 기반으로 모드에 매핑할지 검토

2026-05-13
- 작업자: Codex
- 요청: 실패 상태 review 모드에 Karpathy식 하네스 절차 안내 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 오래된 검증 상태 감지와 재검증 권장 여부 검토

2026-05-13
- 작업자: Codex
- 요청: review 모드가 buddy_state.json의 마지막 검증 상태를 읽어 안내하도록 개선
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실패 상태에서 재현 명령과 최소 수정 순서를 더 구체적으로 안내할지 검토

2026-05-13
- 작업자: Codex
- 요청: check 실패 시 실패 요약을 buddy_state.json에 저장하고 status에 표시
- 변경 파일: tools/harness_buddy.py, scripts/check.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 실패 상태일 때 review 모드가 상태 파일을 읽어 안내하도록 개선 검토

2026-05-13
- 작업자: Codex
- 요청: buddy_state.json에 검증 시각 checked_at 저장 및 status 출력에 표시
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python tools/harness_buddy.py check, python tools/harness_buddy.py status
- 결과: 진행 중
- 남은 이슈: 상태 파일에 실패 요약을 넣을지 검토 필요

2026-05-13
- 작업자: Codex
- 요청: buddy_state.json의 마지막 검증 상태를 보여주는 status 명령 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 상태 파일에 검증 시각이나 실패 요약을 넣을지 검토 필요

2026-05-13
- 작업자: Codex
- 요청: check 실행 후 마지막 검증 상태를 buddy_state.json에 저장
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python tools/harness_buddy.py check
- 결과: 진행 중
- 남은 이슈: 상태 파일을 읽어 보여주는 명령은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Buddy CLI에서 check.py 검증 파이프라인 실행 기능 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: AGENTS.md 승인 규칙을 Buddy 출력과 프롬프트에 더 정확히 반영
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: check.py 결과 요약, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Codex 세션에 붙여넣을 Buddy 프롬프트 생성 기능 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: AGENTS.md 승인 규칙 정밀 반영, check.py 결과 요약, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Buddy 모드별 운영 의도와 트레이드오프 명시
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: AGENTS.md 승인 규칙 정밀 반영, check.py 결과 요약, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Codex Harness Buddy 행동 모드 fast/careful/review 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py
- 결과: 진행 중
- 남은 이슈: AGENTS.md 승인 규칙 정밀 반영, check.py 결과 요약, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Codex Harness Buddy 실패 응답 하네스 추가
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py
- 결과: 진행 중
- 남은 이슈: 승인 체크리스트 출력, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Codex Harness Buddy 첫 CLI와 로컬 검증 파이프라인 구현
- 변경 파일: tools/harness_buddy.py, scripts/smoke_test.py, scripts/check.py, README.md, HARNESS.md
- 실행한 검증: python scripts/smoke_test.py, python scripts/check.py
- 결과: 진행 중
- 남은 이슈: 승인 체크리스트 출력, 실패 응답, 상태 파일 저장은 이후 단계에서 구현

2026-05-13
- 작업자: Codex
- 요청: Codex용 Harness Buddy 초기 폴더 및 환경 세팅
- 변경 파일: README.md, HARNESS.md, START_PROMPT.md, .gitignore, requirements.txt
- 실행한 검증: UTF-8 읽기, 개인 경로 문자열 검색, 폴더 구조 확인
- 결과: 진행 중
- 남은 이슈: 실제 CLI 구현과 smoke test 작성 필요
```

## 13. 프로젝트별 메모

```text
Codex IDE 네이티브 상주 UI가 아니라, 먼저 Codex가 호출할 수 있는 로컬 CLI 버디로 시작한다.
공식 Codex `/pet`은 상태 표시 레이어로 두고, Harness Buddy는 프로젝트 하네스를 읽고 행동을 안내하는 CLI 엔진으로 발전시킨다.
향후 Codex skill/plugin 형태나 별도 UI로 확장할 수 있다.
현재 개발 브랜치: project/codex-harness-buddy
main 브랜치는 루트 README와 안정 스냅샷을 유지한다.
다음 작업 후보: Nudge 반응 수동 확인 항목 추가 또는 캐릭터 반응 지속/복귀 규칙 정리.
```
