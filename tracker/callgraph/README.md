# Call Graph 산출물 설명 (callgraph.png / module_callgraph.png / callgraph.dot)

이 폴더(또는 아티팩트)에 포함된 3개 파일은 `ai-law-suit-tracker` 프로젝트(첨부 ZIP 기준)의 **caller → callee(호출자→피호출자)** 구조를 정적 분석으로 추출해 시각화한 결과입니다.

> ⚠️ 주의: 본 그래프는 **정적 분석(AST 기반)** 이므로, `eval`, 런타임 동적 import, 리플렉션, 프레임워크가 내부적으로 수행하는 호출(예: requests 내부 호출)은 100% 반영되지 않을 수 있습니다.  
> 다만 프로젝트 내부 함수/모듈 간 호출 관계 파악에는 충분히 유용합니다.

---

## 1) callgraph.png (함수/메서드 단위 Call Graph)

### 목적
- 프로젝트 내부의 **함수/메서드 수준**에서 “누가 누구를 호출하는지”를 한눈에 보기 위한 그래프입니다.
- 디버깅/리팩터링/테스트 설계 시 “핵심 경로(엔트리포인트 → 처리 흐름)”를 파악하는 데 유용합니다.

### 노드(점) 표기 규칙
- **내부 정의 함수/메서드**: `module:function` 또는 `module:Class.method` 형태  
  예) `src.run:main`, `src.github_issue:find_or_create_issue`
- **외부 호출(라이브러리/표준 라이브러리 등)**: `ext:...` 형태로 표시될 수 있음  
  예) `ext:requests.get`, `ext:os.environ.get`

### 엣지(화살표) 의미
- `A -> B` 는 **A가 B를 호출한다**는 의미입니다.

### 가독성 정책(중요)
- PNG는 너무 복잡해지는 것을 막기 위해, 외부 호출(`ext:`)은 **“자주 호출되는 것”만 일부 포함**될 수 있습니다.
- 내부 함수 노드는 가능한 한 유지되도록 구성했습니다.

---

## 2) module_callgraph.png (모듈 단위 의존(Call) Graph)

### 목적
- 함수 단위가 아니라, **모듈(파일) 단위**로 “어떤 모듈이 어떤 모듈의 기능을 호출/의존하는지”를 요약해서 보여줍니다.
- 아키텍처 관점에서 “핵심 모듈”, “허브 모듈”, “순환 의존 가능성” 등을 파악할 때 유용합니다.

### 노드(점) 의미
- 각 노드는 **Python 모듈(대체로 .py 파일 단위)** 입니다.  
  예) `src.run`, `src.courtlistener`, `src.github_issue`

### 엣지(화살표) 의미
- `ModuleA -> ModuleB` 는 **ModuleA에 정의된 함수들이 ModuleB에 정의된 함수(혹은 B 모듈 네임스페이스)를 호출**하는 경향이 있음을 의미합니다.
- 외부 모듈(`ext:`)은 보통 이 그래프에서는 제외됩니다(내부 구조 요약 목적).

---

## 3) callgraph.dot (전체 Call Graph 원본 / Graphviz DOT)

### 목적
- `callgraph.png`는 “보기 좋게 축약”된 결과이지만,
- `callgraph.dot`는 가능한 한 많이 담은 **원본 call graph 데이터(텍스트)** 입니다.
- 더 정교한 시각화(Graphviz), 필터링, 서브그래프 생성, CI 연동에 적합합니다.

### 포맷
- Graphviz DOT 포맷(`digraph`)입니다.
- 노드 스타일:
  - 내부 함수: 보통 `shape=box`
  - 외부 호출: `style=dashed` 등으로 표시될 수 있음(분석 스크립트 규칙에 따름)

### 사용 예시(로컬에서 렌더링)
> Graphviz 설치가 필요합니다.

```bash
# PNG로 렌더링
dot -Tpng callgraph.dot -o callgraph_from_dot.png

# SVG로 렌더링(확대/검색 편리)
dot -Tsvg callgraph.dot -o callgraph.svg
