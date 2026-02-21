# 슬라이드 03: RAG 도구 URL 설정

## 슬라이드 내용 (한 장)

**Dify 앱에서 도구 설정**
• Dify Web UI → 앱 선택 → 워크플로우 편집
• 도구 노드 추가: "HTTP 요청" 또는 "사용자 정의 도구"
• 도구 이름: "지식검색", "문서조회" 등

**RAG Backend URL 입력**
• **DrillQuiz**: `http://rag-backend-drillquiz.rag:8000/query`
• **CoinTutor**: `http://rag-backend.rag:8000/query`
• 포트 8000 (또는 저장소 설정값)
• `/query` 엔드포인트: 텍스트 입력 받아 관련 문서 반환

**요청·응답 형식**
• **요청**: `POST /query`, body: `{"question": "..."}`
• **응답**: JSON with matched documents, scores, metadata

**검증**
• Dify 테스트 채팅 → 메시지 전송
• 도구가 정상 호출되는지 로그 확인
• 관련 문서가 반환되면 성공

---

## 발표 노트

이제 Dify 앱에서 RAG 도구를 연결합니다. Dify Web UI에서 앱을 선택하고 워크플로우를 편집합니다. 여기서 도구 노드를 추가하는데, HTTP 요청 도구나 사용자 정의 도구를 선택합니다. 도구의 이름은 "지식검색", "문서조회" 같이 명확하게 짓습니다.

RAG Backend URL을 입력하는 게 핵심입니다. DrillQuiz 앱이면 rag-backend-drillquiz.rag:8000/query를, CoinTutor 앱이면 rag-backend.rag:8000/query를 입력합니다. 여기서 중요한 건 K8s 클러스터 내부 Service DNS를 쓴다는 것입니다. rag는 네임스페이스 이름이고, 클러스터 내부에서는 service-name.namespace:port 형식으로 호출합니다.

/query 엔드포인트는 POST 요청을 받습니다. 요청 body는 {"question": "..."} 형식으로 사용자의 질문을 보내면, RAG Backend가 관련 문서들을 찾아서 JSON으로 반환합니다. 반환되는 데이터는 문서 내용, 유사도 점수, 메타데이터(출처 등)를 포함합니다.

설정이 끝나면 Dify 테스트 채팅에서 확인합니다. 메시지를 보내서 도구가 정상 호출되는지, 관련 문서가 제대로 반환되는지 봅니다. 로그에서 요청과 응답을 확인하면, 문제가 있으면 URL이 잘못됐는지, 백엔드가 다운됐는지 등을 파악할 수 있습니다. 도구가 제대로 작동하고 관련 문서가 나오면 섹션 완료입니다.
