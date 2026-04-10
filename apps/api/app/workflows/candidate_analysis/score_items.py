import asyncio
from dataclasses import dataclass
from typing import Any

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.candidate_rubric_scoring import (
    build_hard_requirement_scoring_prompt,
    build_weighted_rubric_scoring_prompt,
)
from app.core.exceptions import DomainValidationError
from app.schemas.ai.candidate_rubric_result import (
    CandidateRubricScoreItemsResult,
    HardRequirementRubricResultSchema,
    WeightedRubricResultSchema,
)
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateImportInput,
)


@dataclass(frozen=True)
class PreparedRubricScoringInput:
    prepared_input: PreparedCandidateImportInput
    standardized_candidate: CandidateStandardizationSchema
    rubric_items: list[dict[str, Any]]


class CandidateScoreItemsWorkflow:
    def __init__(
        self,
        client: OpenAIResponsesClient,
        *,
        concurrency_limit: int = 6,
        max_retries: int = 1,
    ) -> None:
        self.client = client
        self.concurrency_limit = concurrency_limit
        self.max_retries = max_retries

    async def run(self, scoring_input: PreparedRubricScoringInput) -> CandidateRubricScoreItemsResult:
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        tasks = [
            self._score_single_item(
                semaphore=semaphore,
                job_title=scoring_input.prepared_input.job_title,
                job_summary=scoring_input.prepared_input.job_summary,
                standardized_candidate=scoring_input.standardized_candidate,
                rubric_item=rubric_item,
            )
            for rubric_item in scoring_input.rubric_items
        ]
        results = await asyncio.gather(*tasks)

        weighted_results = [
            result for result in results if isinstance(result, WeightedRubricResultSchema)
        ]
        hard_requirement_results = [
            result for result in results if isinstance(result, HardRequirementRubricResultSchema)
        ]

        seen_ids = {result.job_rubric_item_id for result in results}
        expected_ids = {str(item["id"]) for item in scoring_input.rubric_items}
        if seen_ids != expected_ids or len(results) != len(scoring_input.rubric_items):
            raise DomainValidationError("Rubric scoring results did not match the requested rubric items.")

        return CandidateRubricScoreItemsResult(
            weighted_results=weighted_results,
            hard_requirement_results=hard_requirement_results,
        )

    async def _score_single_item(
        self,
        *,
        semaphore: asyncio.Semaphore,
        job_title: str,
        job_summary: str,
        standardized_candidate: CandidateStandardizationSchema,
        rubric_item: dict[str, Any],
    ) -> WeightedRubricResultSchema | HardRequirementRubricResultSchema:
        async with semaphore:
            last_error: Exception | None = None
            serialized_candidate = standardized_candidate.model_dump(mode="json")
            serialized_rubric_item = self._serialize_rubric_item(rubric_item)

            for _attempt in range(self.max_retries + 1):
                try:
                    if rubric_item["criterion_type"] == "weighted":
                        prompt = build_weighted_rubric_scoring_prompt(
                            job_title=job_title,
                            job_summary=job_summary,
                            rubric_item=serialized_rubric_item,
                            standardized_candidate=serialized_candidate,
                        )
                        payload = await asyncio.to_thread(
                            self.client.generate_structured_output,
                            prompt=prompt,
                            schema_name="weighted_rubric_result_schema",
                            schema=WeightedRubricResultSchema.model_json_schema(),
                        )
                        return WeightedRubricResultSchema.model_validate(payload)

                    prompt = build_hard_requirement_scoring_prompt(
                        job_title=job_title,
                        job_summary=job_summary,
                        rubric_item=serialized_rubric_item,
                        standardized_candidate=serialized_candidate,
                    )
                    payload = await asyncio.to_thread(
                        self.client.generate_structured_output,
                        prompt=prompt,
                        schema_name="hard_requirement_rubric_result_schema",
                        schema=HardRequirementRubricResultSchema.model_json_schema(),
                    )
                    return HardRequirementRubricResultSchema.model_validate(payload)
                except Exception as exc:
                    last_error = exc

            rubric_item_id = str(rubric_item["id"])
            raise DomainValidationError(
                f"Rubric scoring failed for item {rubric_item_id} after retry."
            ) from last_error

    def _serialize_rubric_item(self, rubric_item: dict[str, Any]) -> dict[str, Any]:
        return {
            "id": str(rubric_item["id"]),
            "sort_order": rubric_item["sort_order"],
            "name": rubric_item["name"],
            "description": rubric_item["description"],
            "criterion_type": rubric_item["criterion_type"],
            "weight_input": rubric_item["weight_input"],
            "weight_normalized": rubric_item["weight_normalized"],
            "scoring_standard_items": rubric_item["scoring_standard_items"],
            "agent_prompt_text": rubric_item["agent_prompt_text"],
            "evidence_guidance_text": rubric_item["evidence_guidance_text"],
        }
