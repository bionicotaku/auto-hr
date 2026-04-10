from app.core.exceptions import DomainValidationError
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    is_effective_candidate_name,
)


def validate_candidate_for_persistence(candidate: CandidateStandardizationSchema) -> None:
    if not candidate.is_candidate_like:
        raise DomainValidationError(
            candidate.invalid_reason or "无法识别为有效候选人资料。"
        )
    if not is_effective_candidate_name(candidate.identity.full_name):
        raise DomainValidationError("无法识别候选人姓名。")
