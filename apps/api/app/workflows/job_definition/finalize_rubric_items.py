import asyncio
import inspect
from typing import Any

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.job_definition import build_job_finalize_rubric_item_prompt
from app.core.exceptions import DomainValidationError
from app.schemas.ai.job_definition import JobFinalizeRubricItemEnrichmentSchema


class JobDefinitionFinalizeRubricItemsWorkflow:
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

    async def run(
        self,
        *,
        description_text: str,
        responsibilities: list[str],
        skills: list[str],
        rubric_items: list[dict[str, Any]],
        progress_callback=None,
    ) -> list[JobFinalizeRubricItemEnrichmentSchema]:
        semaphore = asyncio.Semaphore(self.concurrency_limit)
        rubric_overview = [self._serialize_rubric_overview_item(item) for item in rubric_items]
        tasks = [
            self._generate_single_item(
                semaphore=semaphore,
                description_text=description_text,
                responsibilities=responsibilities,
                skills=skills,
                rubric_overview=rubric_overview,
                rubric_item=self._serialize_rubric_item(item),
                progress_callback=progress_callback,
            )
            for item in rubric_items
        ]
        results = await asyncio.gather(*tasks)

        seen_sort_orders = {item.sort_order for item in results}
        expected_sort_orders = {int(item["sort_order"]) for item in rubric_items}
        if seen_sort_orders != expected_sort_orders or len(results) != len(rubric_items):
            raise DomainValidationError("Finalize rubric enrichment did not match the requested rubric items.")

        return results

    async def _generate_single_item(
        self,
        *,
        semaphore: asyncio.Semaphore,
        description_text: str,
        responsibilities: list[str],
        skills: list[str],
        rubric_overview: list[dict[str, Any]],
        rubric_item: dict[str, Any],
        progress_callback,
    ) -> JobFinalizeRubricItemEnrichmentSchema:
        async with semaphore:
            last_error: Exception | None = None
            for _attempt in range(self.max_retries + 1):
                try:
                    prompt = build_job_finalize_rubric_item_prompt(
                        description_text=description_text,
                        responsibilities=responsibilities,
                        skills=skills,
                        rubric_overview=rubric_overview,
                        rubric_item=rubric_item,
                    )
                    payload = await asyncio.to_thread(
                        self.client.generate_structured_output,
                        prompt=prompt,
                        schema_name="job_finalize_rubric_item_enrichment_schema",
                        schema=JobFinalizeRubricItemEnrichmentSchema.model_json_schema(),
                    )
                    result = JobFinalizeRubricItemEnrichmentSchema.model_validate(payload)
                    if progress_callback is not None:
                        callback_result = progress_callback(result)
                        if inspect.isawaitable(callback_result):
                            await callback_result
                    return result
                except Exception as exc:
                    last_error = exc

            raise DomainValidationError(
                f"Finalize rubric enrichment failed for item {rubric_item['sort_order']} after retry."
            ) from last_error

    def _serialize_rubric_overview_item(self, rubric_item: dict[str, Any]) -> dict[str, Any]:
        return {
            "sort_order": int(rubric_item["sort_order"]),
            "name": rubric_item["name"],
            "criterion_type": rubric_item["criterion_type"],
            "weight_input": rubric_item["weight_input"],
        }

    def _serialize_rubric_item(self, rubric_item: dict[str, Any]) -> dict[str, Any]:
        return {
            "sort_order": int(rubric_item["sort_order"]),
            "name": rubric_item["name"],
            "description": rubric_item["description"],
            "criterion_type": rubric_item["criterion_type"],
            "weight_input": rubric_item["weight_input"],
        }
