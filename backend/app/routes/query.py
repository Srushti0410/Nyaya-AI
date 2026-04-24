from fastapi import APIRouter, HTTPException
from app.models.schema import QueryRequest, RecommendationRequest, SummarizeRequest
from app.services.rag import filter_relevant_context, retrieve_context
from app.services.llm import generate_answer
from app.services.summarizer import summarize_case
from app.services.lawyer_service import detect_case_type, recommend_lawyers
from app.services.input_processor import enrich_query, extract_case_context

router = APIRouter()


def build_full_query(query: str, history: list[str] | None = None) -> str:
    """
    Combine the latest user situation with the current question so follow-up
    questions stay tied to the same case.
    """
    if history:
        last_user_message = history[-1]
        case_notes = enrich_query(query, history)
        return (
            f"User situation:\n{last_user_message}\n\n"
            f"User question:\n{query}\n\n"
            f"Case notes:\n{case_notes}"
        )
    return query


def get_case_lawyers(full_query: str, history: list[str] | None = None) -> tuple[str, list[dict]]:
    """
    Resolve the legal issue type from the combined query and return matching lawyers.
    """
    case_context = extract_case_context(full_query, history)
    issue_type = case_context.get("issue_type") or detect_case_type(full_query)
    lawyers = recommend_lawyers(full_query, issue_type) if issue_type else []
    return issue_type, lawyers

@router.post("/ask")
def ask(request: QueryRequest):
    try:
        full_query = build_full_query(request.query, request.history)
        issue_type, lawyers = get_case_lawyers(full_query, request.history)

        # Retrieve context using the combined situation + current question.
        context, sources = retrieve_context(full_query)
        context, sources, _ = filter_relevant_context(full_query, context, sources)

        answer = generate_answer(context, full_query, history=request.history)
        
        return {
            "answer": answer,
            "sources": sources,
            "issue_type": issue_type,
            "lawyers": lawyers,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to generate answer: {exc}") from exc


@router.post("/summarize/")
def summarize(request: SummarizeRequest):
    try:
        return summarize_case(request.query)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to summarize case: {exc}") from exc


@router.post("/recommend-lawyers")
def recommend(request: RecommendationRequest):
    try:
        lawyers = recommend_lawyers(request.query, request.issue_type)
        return lawyers
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to recommend lawyers: {exc}") from exc


@router.post("/pipeline")
def pipeline(request: QueryRequest):
    try:
        full_query = build_full_query(request.query, request.history)
        issue_type, lawyers = get_case_lawyers(full_query, request.history)

        context, sources = retrieve_context(full_query)
        context, sources, _ = filter_relevant_context(full_query, context, sources)

        answer = generate_answer(context, full_query, history=request.history)

        summary = summarize_case(full_query)
        summary_issue_type = summary.get("issue_type", "")
        summary_lawyers = recommend_lawyers(full_query, summary_issue_type) if summary_issue_type else []

        return {
            "answer": answer,
            "sources": sources,
            "summary": summary,
            "issue_type": issue_type,
            "lawyers": lawyers or summary_lawyers,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Pipeline failed: {exc}") from exc