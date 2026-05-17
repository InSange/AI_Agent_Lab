# Codex Harness Buddy

Codex Harness Buddy는 Codex IDE에서 호출해 사용할 수 있는 한국어 터미널 컴패니언 실험 프로젝트다.

목표는 Claude Code의 Buddy 같은 상주형 펫을 그대로 복제하는 것이 아니라, Codex 작업 흐름에 맞춰 `AGENTS.md`와 `HARNESS.md`를 읽고 프로젝트의 목표, 승인 규칙, 검증 명령을 친근하게 안내하는 로컬 하네스 버디를 만드는 것이다.

## 초기 목표

- 프로젝트의 `HARNESS.md`를 읽어 현재 목표를 요약한다.
- 변경 전 승인 체크리스트를 출력한다.
- 스모크 테스트 명령을 안내한다.
- 마지막 검증 상태를 로컬 상태 파일에 저장한다.
- 모든 메시지는 기본적으로 한국어로 출력한다.

## 현재 상태

```text
단계: 초기 세팅
구현 코드: 최소 CLI와 smoke test 구현됨
의존성: 표준 라이브러리만 사용
```

## 실행 형태

프로젝트 폴더에서는 다음 명령으로 CLI를 실행한다.

```powershell
python tools/harness_buddy.py
```

명령 설명은 다음 도움말에서 확인한다.

```powershell
python tools/harness_buddy.py help
```

도움말은 프로젝트 폴더 기준 명령과 루트 폴더 기준 명령을 나눠 보여주고, 보통 먼저 실행할 check 명령도 위치별로 안내한다.

루트 작업 폴더에서는 다음 명령으로 전체 최소 검증을 실행한다.

```powershell
python codex-harness-buddy\scripts\check.py
```

`check.py`는 CLI, smoke test, UI smoke test, character UI smoke test를 실행한 뒤 무엇을 확인했는지 짧은 검증 요약을 출력한다.
요약에는 선택 검증 명령과 캐릭터 UI 수동 확인 명령도 프로젝트 폴더 기준과 루트 폴더 기준으로 나눠 표시된다.
성공 출력의 `수동 확인` 섹션은 `[레이아웃]`, `[상호작용]`, `[Preview]` 그룹으로 나뉜다. 각 그룹은 캐릭터 UI에서 Review 후 Nudge 입력창이 보이는지, Check 실행 중 얼굴과 라벨이 `검증 중`으로 바뀌는지, 예시 입력과 항상 위 토글이 동작하는지, `Waiting`/`Needs Review` 프리뷰의 얼굴, 라벨, 반응 문구가 바뀌고 `Refresh`로 실제 상태에 돌아오는지 확인하도록 안내한다.

Buddy CLI에서도 검증 파이프라인을 실행할 수 있다.

```powershell
python tools/harness_buddy.py check
```

`check` 명령은 마지막 검증 결과, 검증 시각, 실패 시 요약을 `buddy_state.json`에 저장한다. 이 파일은 로컬 실행 상태이므로 Git에 포함하지 않는다.
테스트나 별도 도구에서는 `--state-path`로 상태 파일을 분리할 수 있다.

마지막 검증 상태는 다음 명령으로 확인한다.

```powershell
python tools/harness_buddy.py status
```

캐릭터 UI가 읽을 상태 스냅샷은 다음 명령으로 JSON 출력한다.

```powershell
python tools/harness_buddy.py state-json
```

캐릭터 상태 라벨 매핑은 다음 별도 하네스로 확인한다.

```powershell
python scripts/character_state_test.py
```

최소 캐릭터 창은 다음 명령으로 실행한다.

```powershell
python tools/buddy_character.py
```

상태별 Buddy 반응 문구는 고정 규칙 기반이다. 현재는 Hugging Face 모델이나 자연어 생성 모델을 사용하지 않는다.
`Preview` 버튼은 상태별 얼굴, 라벨, 반응 문구를 화면에서만 미리 보여준다. 실제 `buddy_state.json`은 수정하지 않으며, `Refresh`를 누르면 실제 상태로 돌아온다. UI에는 `표시만 바뀜 · Refresh로 복귀` 안내를 함께 표시한다.
캐릭터 창 버튼은 `검증`, `명령`, `Nudge`, `예시 입력`, `Preview 확인` 영역으로 나눠 표시한다.
캐릭터 창의 `Check` 버튼은 백그라운드에서 검증을 실행한 뒤 상태를 다시 읽는다. 실행 중에는 얼굴과 라벨이 `검증 중` 상태로 잠깐 바뀌고, 중복 클릭과 동시 갱신을 막기 위해 조작 버튼이 잠시 비활성화된다.
Check 실행 결과는 상태 메시지와 별도의 문구로 표시한다.
`Refresh` 버튼은 `state-json`을 다시 읽어 얼굴, 상태 라벨, 메시지, 마지막 갱신 시각을 갱신한다.
`항상 위` 토글을 켜면 캐릭터 창이 다른 창 위에 머물고, 끄면 일반 창처럼 동작한다.
`Status`, `Review`, `Fast`, `Careful`, `Nudge` 버튼은 캐릭터 창에서 바로 Buddy CLI 명령을 실행하고 결과 문구를 갱신한다.
결과 문구는 버튼별로 핵심 줄을 최대 2줄까지 표시한다. `Status`는 마지막 검증과 검증 상태, `Review`는 다음 행동과 마지막 검증, `Fast`와 `Careful`은 Buddy 지시문, `Nudge`는 다음 명령과 감지된 의도를 우선 보여준다.
`Nudge` 버튼은 입력 직후 키워드 규칙으로 캐릭터 얼굴과 라벨을 잠깐 바꾼다. `빨리` 계열은 `빠르게`, `조심` 계열은 `신중하게`, `검증` 계열은 `검증 준비`로 표시한다. 이 반응은 UI 피드백이며 Hugging Face 모델을 사용하지 않는다.
결과 문구 영역은 고정 높이를 사용해 긴 결과가 Nudge 입력 영역을 밀어내지 않게 한다.
`예시 입력` 영역의 Nudge 예시 버튼은 입력창에 예시 문장만 채우며 자동 실행하지 않는다. 실제 해석은 사용자가 `Nudge` 버튼을 눌렀을 때 실행한다.

초기 캐릭터 창은 이미지나 애니메이션 없이 ASCII 얼굴, 상태 라벨, 상태 메시지, 마지막 갱신 시각, 핵심 조작 버튼만 표시한다.

마지막 검증 시각이 30분보다 오래됐으면 `status`와 `review`가 다시 `check`를 권장한다.

## Buddy 모드

공식 Codex `/pet`은 에이전트 상태 표시 레이어로 두고, Harness Buddy는 하네스 문서를 읽는 행동 엔진으로 키운다.

```powershell
python tools/harness_buddy.py fast
python tools/harness_buddy.py careful
python tools/harness_buddy.py review
```

- `fast`: 다음 행동과 검증 명령만 짧게 출력한다.
- `careful`: 현재 단계, 승인 안내, 검증 명령을 출력한다.
- `review`: 마지막 검증 상태를 읽어 완료 전 점검 방향을 안내한다. 실패 상태에서는 재현, 핵심 로그 확인, 최소 수정, 재검증 절차를 보여준다.

현재 Buddy 모드는 Codex 모델의 실제 추론 속도나 reasoning effort를 직접 바꾸지 않는다. 대신 다음 작업 지시를 빠르게, 조심스럽게, 또는 검토 중심으로 정리하는 로컬 하네스 출력 모드다.

Buddy는 루트 `AGENTS.md`의 승인 규칙을 우선한다. 특히 파일/폴더 변경, 의존성/가상환경 변경, 모델/데이터 다운로드, Git 작업, 토큰/환경 변수 변경은 먼저 승인받아야 한다.

## 프롬프트 생성

다음 명령은 Codex 채팅 세션에 붙여넣을 수 있는 Buddy 지시문을 출력한다.

```powershell
python tools/harness_buddy.py prompt fast
python tools/harness_buddy.py prompt careful
python tools/harness_buddy.py prompt review
```

이 기능은 Buddy를 먼저 만들기 위한 단계다. `/pet` 확장, 별도 UI, Hugging Face 모델 기반 의도 분류는 이후 단계에서 검토한다.

## 자연어 nudge

터미널에서 짧은 자연어를 입력하면 Buddy가 키워드 규칙으로 의도를 분류하고 다음 명령을 안내한다. `review` 계열 요청은 상태 파일을 함께 확인해 최신/오래됨/실패 상태에 맞춰 추천한다.
현재 `nudge`는 Hugging Face 모델이나 AI 자연어 처리 모델을 사용하지 않으며, 추천 명령을 실제로 실행하지 않는다.

```powershell
python tools/harness_buddy.py nudge "빨리 좀 해"
python tools/harness_buddy.py nudge "대충 빨리 가자"
python tools/harness_buddy.py nudge "조심해서 해"
python tools/harness_buddy.py nudge "좀 불안한데"
python tools/harness_buddy.py nudge "끝났어?"
python tools/harness_buddy.py nudge "마무리해도 돼?"
python tools/harness_buddy.py nudge "검증해줘"
python tools/harness_buddy.py nudge "테스트 돌려"
python tools/harness_buddy.py nudge "상태 보여줘"
```

초기 버전은 Hugging Face 모델 없이 키워드 규칙으로만 분류한다. 출력에는 `분류 방식: 키워드 규칙`, `모델 사용: 없음`, `실행 여부: 추천만 함`을 표시한다.
모델 기반 의도 분류는 아직 미구현이며, 도입 기준과 평가 샘플은 `HARNESS.md`에 기록한다.

nudge 분류 평가 하네스는 다음 명령으로 별도 실행한다.

```powershell
python tools/harness_buddy.py evaluate-nudge
```

현재 이 평가는 전체 `check.py` 파이프라인에는 포함하지 않는다.

## 플로팅 Buddy UI 계획

다음 UI 단계는 `tkinter` 기반의 작은 플로팅 데스크톱 창으로 시작한다.

초기 UI 목표:

```text
Codex Harness Buddy의 CLI 기능을 호출하는 작은 플로팅 데스크톱 UI를 만든다.
```

초기 구성:

- 창 제목: `Codex Harness Buddy`
- 상태 영역: 마지막 검증 상태 표시
- 상태 버튼: `Check`, `Status`, `Review Status`
- 프롬프트 버튼: `Fast`, `Careful`, `Review Prompt`
- 입력칸: nudge 자연어 입력
- 복사 버튼: `Copy Output`, `Copy Prompt`
- 출력 영역: Buddy CLI 응답 표시

초기 UI는 다음 CLI 명령을 호출한다.

```powershell
python tools/harness_buddy.py check
python tools/harness_buddy.py status
python tools/harness_buddy.py review
python tools/harness_buddy.py prompt fast
python tools/harness_buddy.py prompt careful
python tools/harness_buddy.py prompt review
python tools/harness_buddy.py nudge "<입력>"
```

첫 UI 프로토타입에서는 캐릭터 애니메이션, 이미지/sprite, Hugging Face 모델, 공식 Codex `/pet` 수정, Codex 채팅 자동 삽입은 하지 않는다.

최소 UI는 다음 명령으로 실행한다.

```powershell
python tools/buddy_ui.py
```

버튼을 누르면 실행 상태 영역에 `실행 중`, `완료`, `실패`가 표시되고, Buddy 상태 영역에는 `준비됨`, `점검 필요`, `검토 중` 같은 의미 상태가 표시된다.
출력 영역에는 어떤 버튼이 어떤 CLI 명령을 실행했는지와 당시 Buddy 상태가 로그로 남는다. Nudge 입력도 별도 구분선과 함께 Buddy CLI의 의도 해석 결과를 표시한다.
`Copy Output` 버튼은 현재 출력 영역의 내용을 클립보드에 복사한다.
`Copy Prompt` 버튼은 마지막 `prompt` 명령 결과만 클립보드에 복사한다. 현재는 `Fast`, `Careful`, `Review Prompt` 버튼으로 생성한 지시문이 대상이다.
`Check`, `Status`, `Review Status`, `Nudge`를 실행하면 이전 프롬프트 복사 대상과 클립보드의 프롬프트 내용은 비워진다.

UI smoke test는 다음 명령으로 실행한다.

```powershell
python scripts/ui_smoke_test.py
```

## 다음 단계

1. UI 수동 확인 후 버튼 배치와 문구를 다듬는다.
2. Hugging Face 모델 기반 의도 분류는 UI 전후로 별도 승인 후 검토한다.

파일 생성, 코드 작성, 의존성 추가는 사용자 승인 후 진행한다.
