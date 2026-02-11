# 슬라이드 04: Dify의 역할과 도구 연동

## 슬라이드 내용 (한 장)

**Dify**  
• **LLM 오케스트레이션** 플랫폼: 대화 흐름·프롬프트·**도구(Tool)** 호출 조합  
• 웹 UI로 앱(워크플로우) 생성·배포, API Key 발급  
• tz-chatbot: K8s에 Helm, `dify` NS

**역할**  
• 챗봇 앱: 사용자 메시지 수신 → LLM 답변 (필요 시 도구 호출)  
• **RAG 도구 연동**: “지식 검색” 도구의 URL을 **RAG Backend** 주소로 설정  
• 사용자 ID: chat-gateway에서 `{system_id}_{user_id}` 형태로 Dify에 전달

**도구(Tool) URL (K8s 내부)**  
• CoinTutor: `http://rag-backend.rag.svc.cluster.local:8000/query`  
• DrillQuiz: `http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query`  
• Dify 워크플로우에서 도구 노드에 위 URL 설정 (섹션 09 실습)

---

## 발표 노트

Dify는 LLM 오케스트레이션 플랫폼입니다. 대화 흐름이랑 프롬프트, 그리고 도구 호출을 조합해서 챗봇이나 에이전트를 만드는 도구예요. 웹 UI에서 앱, 즉 워크플로우를 만들고 배포하고, API Key를 발급합니다. tz-chatbot에서는 Dify를 K8s에 Helm으로 설치하고 dify 네임스페이스에 둡니다.

Dify의 역할은 두 가지로 보시면 됩니다. 첫째, 챗봇 앱으로서 사용자 메시지를 받아서 LLM이 답변을 만들고, 필요하면 도구를 호출합니다. 둘째, RAG 도구 연동입니다. 워크플로우에 “지식 검색” 같은 도구를 추가하고, 그 도구의 URL을 우리가 만든 RAG Backend 주소로 넣습니다. 그러면 Dify가 그 URL로 요청을 보내고, RAG Backend가 Qdrant에서 검색한 결과를 돌려주면 Dify가 그걸 LLM 컨텍스트에 넣어서 답을 만드는 구조입니다. 사용자 구분은 chat-gateway에서 system_id와 user_id를 합쳐서, 예를 들어 drillquiz_12345 같은 형태로 Dify에 넘깁니다.

도구 URL은 K8s 클러스터 안에서만 쓰이기 때문에, 외부 도메인이 아니라 서비스 DNS를 씁니다. CoinTutor용 RAG Backend는 http://rag-backend.rag.svc.cluster.local:8000/query, DrillQuiz용은 http://rag-backend-drillquiz.rag.svc.cluster.local:8000/query 이런 식으로 설정합니다. Dify 워크플로우 편집 화면에서 도구 노드를 추가하고 이 URL을 넣는 작업은 섹션 9 실습에서 하게 됩니다.
