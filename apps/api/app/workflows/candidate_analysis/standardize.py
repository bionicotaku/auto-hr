import base64
from pathlib import Path

from pydantic import ValidationError

from app.ai.client import OpenAIResponsesClient
from app.ai.prompts.candidate_standardization import build_candidate_standardization_prompt
from app.schemas.ai.candidate_standardization import (
    CandidateStandardizationSchema,
    PreparedCandidateImportInput,
)


class CandidateStandardizeWorkflow:
    def __init__(self, client: OpenAIResponsesClient) -> None:
        self.client = client

    def run(self, prepared_input: PreparedCandidateImportInput) -> CandidateStandardizationSchema:
        prompt = build_candidate_standardization_prompt(
            job_title=prepared_input.job_title,
            job_summary=prepared_input.job_summary,
            raw_text_input=prepared_input.raw_text_input,
        )
        inputs = [
            {
                "role": "user",
                "content": [{"type": "input_text", "text": prompt}],
            }
        ]

        file_inputs = [
            {
                "type": "input_file",
                "filename": document.filename,
                "file_data": self._encode_file_data(document.storage_path),
            }
            for document in prepared_input.documents
        ]
        if file_inputs:
            inputs[0]["content"].extend(file_inputs)

        payload = self.client.generate_structured_output_from_inputs(
            inputs=inputs,
            schema_name="candidate_standardization_schema",
            schema=CandidateStandardizationSchema.model_json_schema(),
        )

        try:
            return CandidateStandardizationSchema.model_validate(payload)
        except ValidationError as exc:
            raise ValueError("LLM returned invalid candidate standardization schema.") from exc

    def _encode_file_data(self, storage_path: str) -> str:
        path = Path(storage_path)
        try:
            file_bytes = path.read_bytes()
        except OSError as exc:
            raise ValueError(f"Failed to read candidate document: {path.name}") from exc
        encoded = base64.b64encode(file_bytes).decode("ascii")
        return f"data:application/pdf;base64,{encoded}"
