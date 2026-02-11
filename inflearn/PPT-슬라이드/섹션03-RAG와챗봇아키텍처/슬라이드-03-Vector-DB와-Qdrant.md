# 슬라이드 03: Vector DB와 Qdrant

## 슬라이드 내용 (한 장)

**Vector DB**  
• **벡터(임베딩)** 저장 + “이 벡터와 유사한 벡터” **빠른 검색**  
• 일반 RDB의 키 검색이 아니라 **유사도 검색**(ANN)에 최적화

**Qdrant**  
• 오픈소스 벡터 DB. tz-chatbot에서는 **K8s에 Helm** 설치, `rag` NS  
• **컬렉션(collection)**: 토픽별 구분 (예: rag_docs_cointutor, rag_docs_drillquiz)  
• 벡터 차원·거리 메트릭(코사인 등)은 컬렉션 생성 시 지정  
• RAG Backend·Ingestion이 Qdrant API로 upsert·search

**tz-chatbot에서**  
• Ingestion: MinIO → 청킹·임베딩 → Qdrant 컬렉션에 upsert  
• RAG Backend: 질의 임베딩 → Qdrant search → 상위 k개 청크 → Dify에 전달  
• 토픽별 컬렉션으로 CoinTutor/DrillQuiz 검색 분리 (섹션 07)

---

## 발표 노트

Vector DB는 벡터, 즉 임베딩을 저장하고 “이 벡터와 유사한 벡터들을 빠르게 찾는” 데 특화된 DB입니다. 일반 RDB처럼 키나 인덱스로 정확히 매칭하는 게 아니라, 유사도 검색, 대략 최근접 이웃 검색 ANN에 최적화되어 있습니다.

tz-chatbot에서는 Qdrant를 씁니다. 오픈소스 벡터 DB이고, K8s에 Helm으로 설치하며 rag 네임스페이스에 올라갑니다. 데이터는 컬렉션 단위로 나뉘고, 토픽별로 rag_docs_cointutor, rag_docs_drillquiz처럼 컬렉션을 따로 둡니다. 컬렉션 생성 시 벡터 차원이랑 거리 메트릭, 예를 들어 코사인 유사도를 지정합니다. RAG Backend와 Ingestion 스크립트가 Qdrant API로 데이터를 넣고, 검색할 때는 search를 호출합니다.

tz-chatbot에서의 역할을 정리하면, Ingestion 단계에서는 MinIO에서 문서를 읽어서 청킹·임베딩한 뒤 Qdrant 컬렉션에 upsert합니다. RAG Backend는 사용자 질의를 임베딩해서 Qdrant에서 search하고, 상위 k개 청크를 가져와서 Dify에 전달합니다. 토픽별로 컬렉션을 나눠서 CoinTutor와 DrillQuiz 검색이 서로 섞이지 않도록 하고, 이 토픽 분리 전략은 섹션 7에서 자세히 다룹니다.
