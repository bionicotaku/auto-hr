import re
import shutil
import uuid
from dataclasses import dataclass
from pathlib import Path

from app.core.config import Settings
from app.core.exceptions import DomainValidationError
from app.repositories.candidate_repository import (
    CandidateCreateData,
    CandidateDocumentCreateData,
    CandidateProfileCreateData,
    CandidateRepository,
    CandidateRubricResultCreateData,
    CandidateTagCreateData,
)
from app.services.candidate_analysis_service import CandidateAnalysisBundle


@dataclass(frozen=True)
class PersistedCandidateResult:
    candidate_id: str
    job_id: str


class CandidatePersistWorkflow:
    def __init__(
        self,
        *,
        settings: Settings,
        candidate_repository: CandidateRepository,
    ) -> None:
        self.settings = settings
        self.candidate_repository = candidate_repository

    def run(self, session, bundle: CandidateAnalysisBundle) -> PersistedCandidateResult:
        candidate_id = str(uuid.uuid4())
        final_dir = self.settings.upload_dir_path / "candidates" / candidate_id
        temp_root = self._temp_root(bundle.prepared_input.temp_request_id)
        standardized = bundle.standardized_candidate

        try:
            final_documents = self._promote_documents(
                candidate_id=candidate_id,
                documents=bundle.prepared_input.documents,
                final_dir=final_dir,
                candidate_name=standardized.identity.full_name,
            )
        except Exception as exc:
            self._remove_dir(final_dir)
            self._remove_dir(temp_root)
            raise DomainValidationError("Failed to persist candidate import.") from exc

        try:
            candidate_data, profile_data, rubric_result_data, tag_data = self._build_repository_payloads(
                candidate_id=candidate_id,
                bundle=bundle,
                final_documents=final_documents,
            )
            self.candidate_repository.create_candidate_graph(
                session,
                candidate_data=candidate_data,
                profile_data=profile_data,
                document_data=final_documents,
                rubric_result_data=rubric_result_data,
                tag_data=tag_data,
            )
            session.commit()
        except Exception as exc:
            session.rollback()
            self._remove_dir(final_dir)
            self._remove_dir(temp_root)
            raise DomainValidationError("Failed to persist candidate import.") from exc

        self._remove_dir(temp_root)
        return PersistedCandidateResult(
            candidate_id=candidate_id,
            job_id=bundle.prepared_input.job_id,
        )

    def _build_repository_payloads(
        self,
        *,
        candidate_id: str,
        bundle: CandidateAnalysisBundle,
        final_documents: list[CandidateDocumentCreateData],
    ) -> tuple[
        CandidateCreateData,
        CandidateProfileCreateData,
        list[CandidateRubricResultCreateData],
        list[CandidateTagCreateData],
    ]:
        standardized = bundle.standardized_candidate
        supervisor = bundle.supervisor_summary
        full_name = standardized.identity.full_name or "未知候选人"

        candidate_data = CandidateCreateData(
            candidate_id=candidate_id,
            job_id=bundle.prepared_input.job_id,
            full_name=full_name,
            current_title=standardized.identity.current_title,
            current_company=standardized.identity.current_company,
            location_text=standardized.identity.location_text,
            email=standardized.identity.email,
            phone=standardized.identity.phone,
            linkedin_url=standardized.identity.linkedin_url,
            professional_summary_raw=standardized.profile_summary.professional_summary_raw,
            professional_summary_normalized=standardized.profile_summary.professional_summary_normalized,
            years_of_total_experience=standardized.profile_summary.years_of_total_experience,
            years_of_relevant_experience=standardized.profile_summary.years_of_relevant_experience,
            seniority_level=standardized.profile_summary.seniority_level,
            raw_text_input=bundle.prepared_input.raw_text_input,
            hard_requirement_overall=supervisor.hard_requirement_overall,
            overall_score_percent=supervisor.overall_score_percent,
            ai_summary=supervisor.ai_summary,
            evidence_points_json=supervisor.evidence_points,
            recommendation=supervisor.recommendation,
        )
        profile_data = CandidateProfileCreateData(
            work_experiences_json=[item.model_dump(mode="json") for item in standardized.work_experiences],
            educations_json=[item.model_dump(mode="json") for item in standardized.educations],
            skills_json=standardized.skills.model_dump(mode="json"),
            employment_preferences_json=standardized.employment_preferences.model_dump(mode="json"),
            application_answers_json=[
                item.model_dump(mode="json") for item in standardized.application_answers
            ],
            additional_information_json=standardized.additional_information.model_dump(mode="json"),
        )
        rubric_result_data = [
            CandidateRubricResultCreateData(
                job_rubric_item_id=item.job_rubric_item_id,
                criterion_type=item.criterion_type,
                score_0_to_5=item.score_0_to_5,
                hard_requirement_decision=None,
                reason_text=item.reason_text,
                evidence_points_json=item.evidence_points,
                uncertainty_note=item.uncertainty_note,
            )
            for item in bundle.rubric_score_items.weighted_results
        ] + [
            CandidateRubricResultCreateData(
                job_rubric_item_id=item.job_rubric_item_id,
                criterion_type=item.criterion_type,
                score_0_to_5=None,
                hard_requirement_decision=item.hard_requirement_decision,
                reason_text=item.reason_text,
                evidence_points_json=item.evidence_points,
                uncertainty_note=item.uncertainty_note,
            )
            for item in bundle.rubric_score_items.hard_requirement_results
        ]
        tag_data = [
            CandidateTagCreateData(tag_name=tag_name, tag_source="ai")
            for tag_name in self._build_ai_tags(supervisor.tags, supervisor.hard_requirement_overall)
        ]
        return candidate_data, profile_data, rubric_result_data, tag_data

    def _promote_documents(
        self,
        *,
        candidate_id: str,
        documents,
        final_dir: Path,
        candidate_name: str | None,
    ) -> list[CandidateDocumentCreateData]:
        final_dir.mkdir(parents=True, exist_ok=True)
        promoted_documents: list[CandidateDocumentCreateData] = []
        safe_candidate_name = self._sanitize_candidate_filename(candidate_name)

        for index, document in enumerate(documents, start=1):
            source_path = Path(document.storage_path)
            destination_filename = f"{safe_candidate_name}-{index}.pdf"
            destination_path = final_dir / destination_filename
            shutil.move(source_path.as_posix(), destination_path.as_posix())
            promoted_documents.append(
                CandidateDocumentCreateData(
                    document_type="resume" if index == 1 else "other",
                    filename=destination_filename,
                    storage_path=str(destination_path),
                    mime_type=document.mime_type,
                    page_count=document.page_count,
                    upload_order=document.upload_order,
                )
            )

        return promoted_documents

    def _temp_root(self, request_id: str) -> Path:
        return self.settings.temp_upload_dir_path / "candidate-imports" / request_id

    def _remove_dir(self, path: Path) -> None:
        shutil.rmtree(path, ignore_errors=True)

    def _dedupe_tags(self, tags: list[str]) -> list[str]:
        seen: set[str] = set()
        deduped: list[str] = []
        for raw_tag in tags:
            tag = raw_tag.strip()
            if not tag or tag in seen:
                continue
            seen.add(tag)
            deduped.append(tag)
        return deduped

    def _build_ai_tags(self, supervisor_tags: list[str], hard_requirement_overall: str) -> list[str]:
        default_tags: list[str] = []
        if hard_requirement_overall == "has_fail":
            default_tags.append("硬性要求未通过")
        elif hard_requirement_overall == "has_borderline":
            default_tags.append("需要复核")
        return self._dedupe_tags([*supervisor_tags, *default_tags])

    def _sanitize_candidate_filename(self, candidate_name: str | None) -> str:
        raw_name = (candidate_name or "").strip() or "candidate"
        normalized = raw_name.replace("_", "-")
        normalized = re.sub(r"[^\w\u4e00-\u9fff-]+", "-", normalized, flags=re.UNICODE)
        normalized = re.sub(r"-{2,}", "-", normalized).strip("-")
        return normalized or "candidate"
