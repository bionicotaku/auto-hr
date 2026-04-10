import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from openai import OpenAI

from app.core.config import get_settings


class OpenAIResponsesClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(api_key=self.settings.openai_api_key or None)

    def generate_structured_output(
        self,
        *,
        prompt: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        # Prompt rendering is standardized through LangChain templates,
        # while the actual generation uses the OpenAI Responses API.
        message = ChatPromptTemplate.from_messages([("human", "{prompt}")]).invoke(
            {"prompt": prompt}
        )
        rendered_prompt = message.messages[0].content

        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning},
            input=[
                {
                    "role": "user",
                    "content": [{"type": "input_text", "text": rendered_prompt}],
                }
            ],
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": self._to_openai_json_schema(schema),
                    "strict": True,
                }
            },
        )

        output_text = response.output_text
        if not output_text:
            raise ValueError("Responses API returned empty output_text.")

        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            raise ValueError("Responses API returned non-object JSON.")
        return parsed

    def generate_structured_output_from_inputs(
        self,
        *,
        inputs: list[dict[str, Any]],
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        response = self.client.responses.create(
            model=self.settings.openai_model,
            reasoning={"effort": self.settings.openai_reasoning},
            input=inputs,
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "schema": self._to_openai_json_schema(schema),
                    "strict": True,
                }
            },
        )

        output_text = response.output_text
        if not output_text:
            raise ValueError("Responses API returned empty output_text.")

        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            raise ValueError("Responses API returned non-object JSON.")
        return parsed

    def _to_openai_json_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        def normalize(node: Any) -> Any:
            if isinstance(node, dict):
                normalized = {key: normalize(value) for key, value in node.items()}
                if normalized.get("type") == "object":
                    normalized.setdefault("additionalProperties", False)
                return normalized
            if isinstance(node, list):
                return [normalize(item) for item in node]
            return node

        return normalize(schema)
