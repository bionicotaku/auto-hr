import asyncio
import inspect

from app.ai.client import OpenAIResponsesClient
from app.core.exceptions import DomainValidationError
from app.schemas.ai.job_definition import JobFinalizeScoringResponseSchema
from app.workflows.job_definition.finalize_rubric_items import (
    JobDefinitionFinalizeRubricItemsWorkflow,
)
from app.workflows.job_definition.finalize_title_summary import (
    JobDefinitionFinalizeTitleSummaryWorkflow,
)


class JobDefinitionFinalizeWorkflow:
    def __init__(
        self,
        client: OpenAIResponsesClient | None = None,
        *,
        title_summary_workflow: JobDefinitionFinalizeTitleSummaryWorkflow | None = None,
        rubric_items_workflow: JobDefinitionFinalizeRubricItemsWorkflow | None = None,
    ) -> None:
        if title_summary_workflow is None or rubric_items_workflow is None:
            if client is None:
                raise ValueError(
                    "JobDefinitionFinalizeWorkflow requires a client when default sub-workflows are used."
                )

        self.title_summary_workflow = title_summary_workflow or JobDefinitionFinalizeTitleSummaryWorkflow(
            client
        )
        self.rubric_items_workflow = rubric_items_workflow or JobDefinitionFinalizeRubricItemsWorkflow(
            client,
            concurrency_limit=6,
            max_retries=1,
        )

    async def run(
        self,
        *,
        description_text: str,
        responsibilities: list[str],
        skills: list[str],
        rubric_items: list[dict],
        progress_callback=None,
    ) -> JobFinalizeScoringResponseSchema:
        async def run_title_summary():
            result = await asyncio.to_thread(
                self.title_summary_workflow.run,
                description_text=description_text,
                responsibilities=responsibilities,
                skills=skills,
                rubric_items=rubric_items,
            )
            if progress_callback is not None:
                callback_result = progress_callback("title_summary", result)
                if inspect.isawaitable(callback_result):
                    await callback_result
            return result

        rubric_items_task = self.rubric_items_workflow.run(
            description_text=description_text,
            responsibilities=responsibilities,
            skills=skills,
            rubric_items=rubric_items,
            progress_callback=lambda result: progress_callback("rubric_item", result)
            if progress_callback is not None
            else None,
        )

        title_summary, rubric_item_enrichment = await asyncio.gather(
            run_title_summary(),
            rubric_items_task,
        )

        seen_sort_orders = {item.sort_order for item in rubric_item_enrichment}
        expected_sort_orders = {int(item["sort_order"]) for item in rubric_items}
        if seen_sort_orders != expected_sort_orders or len(rubric_item_enrichment) != len(rubric_items):
            raise DomainValidationError("Finalize rubric enrichment did not match the requested rubric items.")

        return JobFinalizeScoringResponseSchema(
            title=title_summary.title,
            summary=title_summary.summary,
            rubric_items=rubric_item_enrichment,
        )
