#!/usr/bin/env python3
"""
RAG 배치 평가: 기대 질문 세트(YAML)로 RAG Backend /query 를 호출하고,
품질 로그와 동일한 형식의 JSON 라인을 stdout 또는 파일로 출력합니다.

사용법:
  export RAG_BACKEND_URL=http://localhost:8000   # 또는 K8s 포트포워드 주소
  python batch_eval_rag.py [expected_questions.yaml] [--output eval_logs.jsonl]

의존성: pip install requests pyyaml
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

try:
    import requests
    import yaml
except ImportError as e:
    print("pip install requests pyyaml 필요", file=sys.stderr)
    raise SystemExit(1) from e


def load_questions(path: str) -> List[dict]:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return data.get("questions") or []


def call_query(base_url: str, question: str, top_k: int = 5, collection: Optional[str] = None) -> dict:
    url = (base_url.rstrip("/") + "/query").strip()
    payload = {"question": question, "top_k": top_k}
    if collection:
        payload["collection"] = collection
    resp = requests.post(url, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="RAG 배치 평가: 기대 질문으로 /query 호출 후 로그 생성")
    parser.add_argument(
        "questions_file",
        nargs="?",
        default=os.path.join(os.path.dirname(__file__), "expected_questions.yaml"),
        help="YAML 기대 질문 파일 (기본: expected_questions.yaml)",
    )
    parser.add_argument("--output", "-o", default=None, help="출력 JSONL 파일 (미지정 시 stdout)")
    parser.add_argument("--url", default=None, help="RAG Backend base URL (기본: RAG_BACKEND_URL 환경변수)")
    parser.add_argument("--top-k", type=int, default=5, help="top_k 파라미터")
    parser.add_argument("--collection", default=None, help="Qdrant 컬렉션 (미지정 시 Backend 기본값)")
    args = parser.parse_args()

    base_url = args.url or os.environ.get("RAG_BACKEND_URL", "http://localhost:8000")
    questions_path = Path(args.questions_file)
    if not questions_path.exists():
        print(f"파일 없음: {questions_path}", file=sys.stderr)
        sys.exit(1)

    questions = load_questions(str(questions_path))
    if not questions:
        print("질문이 없습니다.", file=sys.stderr)
        sys.exit(0)

    out_file = open(args.output, "w", encoding="utf-8") if args.output else sys.stdout
    try:
        for q in questions:
            qid = q.get("id", "")
            question = (q.get("question") or "").strip()
            if not question:
                continue
            try:
                t0 = datetime.now(timezone.utc)
                data = call_query(base_url, question, top_k=args.top_k, collection=args.collection)
                t1 = datetime.now(timezone.utc)
                results = data.get("results") or []
                retrieved = [
                    {
                        "chunk_id": r.get("chunk_id", ""),
                        "score": r.get("score"),
                        "content": (r.get("text") or "")[:500],
                        "source_path": r.get("path") or r.get("source") or "",
                    }
                    for r in results
                ]
                latency_ms = int((t1 - t0).total_seconds() * 1000)
                log_row = {
                    "log_type": "rag_query",
                    "source": "batch_eval",
                    "eval_question_id": qid,
                    "ground_truth": q.get("ground_truth"),
                    "keywords": q.get("keywords"),
                    "timestamp": t1.isoformat().replace("+00:00", "Z"),
                    "question": question,
                    "retrieved": retrieved,
                    "top_k": args.top_k,
                    "collection": args.collection or "",
                    "latency_ms": latency_ms,
                }
                out_file.write(json.dumps(log_row, ensure_ascii=False) + "\n")
                out_file.flush()
            except Exception as e:
                print(f"질문 id={qid} 오류: {e}", file=sys.stderr)
    finally:
        if args.output and out_file is not sys.stdout:
            out_file.close()

    print(f"완료: {len(questions)}개 질문 처리", file=sys.stderr)


if __name__ == "__main__":
    main()
