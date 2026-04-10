import asyncio

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.candidate_supervisor import build_candidate_supervisor_prompt
from app.core.exceptions import DomainValidationError
from app.schemas.ai.candidate_rubric_result import CandidateRubricScoreItemsResult
from app.schemas.ai.candidate_standardization import CandidateStandardizationSchema
from app.schemas.ai.candidate_supervisor import CandidateSupervisorSchema


class CandidateSummarizeWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    async def run(
        self,
        *,
        job_title: str,
        job_summary: str,
        standardized_candidate: CandidateStandardizationSchema,
        rubric_score_items: CandidateRubricScoreItemsResult,
        hard_requirement_overall: str,
        overall_score_5: float,
        overall_score_percent: float,
    ) -> CandidateSupervisorSchema:
        prompt = build_candidate_supervisor_prompt(
            job_title=job_title,
            job_summary=job_summary,
            standardized_candidate=standardized_candidate.model_dump(mode="json"),
            rubric_results=rubric_score_items.model_dump(mode="json"),
            hard_requirement_overall=hard_requirement_overall,
            overall_score_5=overall_score_5,
            overall_score_percent=overall_score_percent,
        )
        payload = await asyncio.to_thread(
            self.client.generate_structured_output,
            prompt=prompt,
            schema_name="candidate_supervisor_schema",
            schema=CandidateSupervisorSchema.model_json_schema(),
        )
        result = CandidateSupervisorSchema.model_validate(payload)

        if result.hard_requirement_overall != hard_requirement_overall:
            raise DomainValidationError("Supervisor hard requirement summary did not match computed value.")
        if abs(result.overall_score_5 - overall_score_5) > 0.001:
            raise DomainValidationError("Supervisor overall_score_5 did not match computed value.")
        if abs(result.overall_score_percent - overall_score_percent) > 0.01:
            raise DomainValidationError("Supervisor overall_score_percent did not match computed value.")

        if hard_requirement_overall in {"has_fail", "has_borderline"} and result.recommendation == "advance":
            raise DomainValidationError("Supervisor recommendation cannot advance a candidate with failed or borderline hard requirements.")

        return result
