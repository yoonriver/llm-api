## LangGraph 개념 정리

### LangGraph란?

LangGraph는 LLM 애플리케이션의 작업 흐름을 그래프 형태로 구성하는 도구다.

단순히 LLM을 한 번 호출하는 것이 아니라, 질문 분류, 검색, 답변 생성, 검증, 재시도 같은 여러 단계를 상태 기반 workflow로 연결할 수 있다.

예:

```text
사용자 질문
  ↓
질문 유형 분류
  ↓
답변 생성
  ↓
답변 검증
  ↓
최종 응답
```

LangGraph로 표현하면:

```text
START
  ↓
classify_question
  ↓
generate_answer
  ↓
validate_answer
  ↓
END
```

---

### LangChain과 LangGraph 차이

```text
LangChain:
  Prompt, Model, Parser 같은 LLM 호출 구성 요소를 조합하는 데 사용한다.

LangGraph:
  State, Node, Edge 기반으로 LLM 애플리케이션 workflow를 구성하는 데 사용한다.
```

쉽게 말하면:

```text
LangChain:
  "LLM을 어떻게 호출할까?"

LangGraph:
  "LLM 호출 전후의 작업 흐름을 어떻게 관리할까?"
```

---

### State

State는 그래프 전체를 흐르는 공유 데이터다.

쉽게 말하면:

```text
State = 작업 과정에서 계속 들고 다니는 가방
```

예:

```python
class AgentState(TypedDict):
    message: str
    question_type: str
    answer: str
    validated: bool
    trace: list[str]
```

각 필드 의미:

```text
message:
  사용자의 질문

question_type:
  질문 분류 결과

answer:
  생성된 답변

validated:
  답변 검증 결과

trace:
  어떤 노드들이 실행됐는지 기록
```

---

### Node

Node는 실제 작업을 수행하는 함수다.

예:

```text
classify_question:
  질문 유형을 분류하는 노드

generate_answer:
  답변을 생성하는 노드

validate_answer:
  답변을 검증하는 노드
```

Node는 State를 입력으로 받고, 변경할 값만 dict로 반환한다.

예:

```python
def classify_question(state: AgentState) -> dict:
    message = state["message"]

    if "AWS" in message:
        question_type = "aws"
    else:
        question_type = "general"

    return {
        "question_type": question_type
    }
```

---

### Edge

Edge는 노드와 노드를 연결하는 선이다.

예:

```python
graph.add_edge("classify_question", "generate_answer")
```

뜻:

```text
classify_question이 끝나면 generate_answer를 실행한다.
```

---

### START / END

```text
START:
  그래프 시작점

END:
  그래프 종료점
```

예:

```python
graph.add_edge(START, "classify_question")
graph.add_edge("validate_answer", END)
```

---

### Conditional Edge

Conditional Edge는 조건에 따라 다음 노드를 다르게 선택하는 연결이다.

예:

```text
classify_question
  ├─ aws → generate_aws_answer
  ├─ llm_framework → generate_llm_answer
  └─ general → generate_general_answer
```

7일차 기본에서는 단순 edge를 사용하고, 다음 단계에서 조건 분기를 추가한다.

---

### Graph

Graph는 State, Node, Edge를 합친 workflow 전체다.

```text
Graph = State + Nodes + Edges
```

예:

```python
graph = StateGraph(AgentState)
```

---

### Compile

Compile은 정의한 graph를 실행 가능한 객체로 변환하는 단계다.

```python
agent_graph = graph.compile()
```

---

### Invoke

Invoke는 graph를 실제로 실행하는 것이다.

동기 실행:

```python
result = agent_graph.invoke(initial_state)
```

비동기 실행:

```python
result = await agent_graph.ainvoke(initial_state)
```

FastAPI에서는 async endpoint를 사용하므로 `ainvoke()`를 사용한다.

---

### 회사 파이프라인과 비교

MWAA DAG는 PDF 파싱, OCR, Drawing Parser, promote, DB indexing 같은 데이터 파이프라인 workflow를 관리한다.

LangGraph는 질문 분류, 답변 생성, 답변 검증 같은 LLM 애플리케이션 workflow를 관리한다.

```text
MWAA DAG:
  데이터 처리 파이프라인 workflow

LangGraph:
  LLM 애플리케이션 workflow
```

---

### 핵심 요약

```text
LangGraph는 LLM 애플리케이션의 복잡한 작업 흐름을 State, Node, Edge로 표현하는 workflow 도구다.

State는 들고 다니는 데이터다.
Node는 작업 함수다.
Edge는 다음 작업으로 가는 연결선이다.

LangChain은 LLM 호출 부품 조립에 가깝고,
LangGraph는 LLM 작업 흐름 관리에 가깝다.
```