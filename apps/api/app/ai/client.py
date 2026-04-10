import json
import logging
from typing import Any

from openai import APIConnectionError, APIStatusError, APITimeoutError, BadRequestError, OpenAI

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class OpenAIResponsesClient:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.client = OpenAI(
            api_key=self.settings.openai_api_key or None,
            timeout=self.settings.openai_timeout_seconds,
        )

    def generate_structured_output(
        self,
        *,
        prompt: str,
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        logger.info(
            "LLM request started: schema=%s model=%s mode=prompt",
            schema_name,
            self.settings.openai_model,
        )
        try:
            response = self.client.responses.create(
                model=self.settings.openai_model,
                reasoning={"effort": self.settings.openai_reasoning},
                input=[
                    {
                        "role": "user",
                        "content": [{"type": "input_text", "text": prompt}],
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
        except BadRequestError as exc:
            logger.error(
                "LLM request failed: schema=%s model=%s error=%s",
                schema_name,
                self.settings.openai_model,
                self._extract_openai_error_message(exc),
            )
            raise ValueError(self._extract_openai_error_message(exc)) from exc
        except APITimeoutError as exc:
            logger.error(
                "LLM request timed out: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("AI 请求超时，请稍后重试。") from exc
        except APIConnectionError as exc:
            logger.error(
                "LLM request connection failed: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("AI 服务连接失败，请稍后重试。") from exc
        except APIStatusError as exc:
            logger.error(
                "LLM request failed with API status error: schema=%s model=%s error=%s",
                schema_name,
                self.settings.openai_model,
                self._extract_openai_error_message(exc),
            )
            raise ValueError(self._extract_openai_error_message(exc)) from exc

        output_text = response.output_text
        if not output_text:
            logger.error(
                "LLM request returned empty output_text: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("Responses API returned empty output_text.")

        logger.info(
            "LLM response received: schema=%s model=%s output_text=%s",
            schema_name,
            self.settings.openai_model,
            output_text,
        )
        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            logger.error(
                "LLM response was non-object JSON: schema=%s model=%s output_text=%s",
                schema_name,
                self.settings.openai_model,
                output_text,
            )
            raise ValueError("Responses API returned non-object JSON.")
        return parsed

    def generate_structured_output_from_inputs(
        self,
        *,
        inputs: list[dict[str, Any]],
        schema_name: str,
        schema: dict[str, Any],
    ) -> dict[str, Any]:
        logger.info(
            "LLM request started: schema=%s model=%s mode=inputs input_items=%s",
            schema_name,
            self.settings.openai_model,
            len(inputs),
        )
        try:
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
        except BadRequestError as exc:
            logger.error(
                "LLM request failed: schema=%s model=%s error=%s",
                schema_name,
                self.settings.openai_model,
                self._extract_openai_error_message(exc),
            )
            raise ValueError(self._extract_openai_error_message(exc)) from exc
        except APITimeoutError as exc:
            logger.error(
                "LLM request timed out: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("AI 请求超时，请稍后重试。") from exc
        except APIConnectionError as exc:
            logger.error(
                "LLM request connection failed: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("AI 服务连接失败，请稍后重试。") from exc
        except APIStatusError as exc:
            logger.error(
                "LLM request failed with API status error: schema=%s model=%s error=%s",
                schema_name,
                self.settings.openai_model,
                self._extract_openai_error_message(exc),
            )
            raise ValueError(self._extract_openai_error_message(exc)) from exc

        output_text = response.output_text
        if not output_text:
            logger.error(
                "LLM request returned empty output_text: schema=%s model=%s",
                schema_name,
                self.settings.openai_model,
            )
            raise ValueError("Responses API returned empty output_text.")

        logger.info(
            "LLM response received: schema=%s model=%s output_text=%s",
            schema_name,
            self.settings.openai_model,
            output_text,
        )
        parsed = json.loads(output_text)
        if not isinstance(parsed, dict):
            logger.error(
                "LLM response was non-object JSON: schema=%s model=%s output_text=%s",
                schema_name,
                self.settings.openai_model,
                output_text,
            )
            raise ValueError("Responses API returned non-object JSON.")
        return parsed

    def _to_openai_json_schema(self, schema: dict[str, Any]) -> dict[str, Any]:
        def normalize(node: Any) -> Any:
            if isinstance(node, dict):
                normalized = {
                    key: normalize(value)
                    for key, value in node.items()
                    if key != "default"
                }
                if normalized.get("type") == "object":
                    properties = normalized.get("properties", {})
                    if isinstance(properties, dict) and properties:
                        normalized["required"] = list(properties.keys())
                    normalized.setdefault("additionalProperties", False)
                return normalized
            if isinstance(node, list):
                return [normalize(item) for item in node]
            return node

        return normalize(schema)

    def _extract_openai_error_message(self, exc: BadRequestError) -> str:
        response = getattr(exc, "response", None)
        if response is not None:
            try:
                payload = response.json()
            except Exception:
                payload = None
            if isinstance(payload, dict):
                error = payload.get("error")
                if isinstance(error, dict):
                    message = error.get("message")
                    if isinstance(message, str) and message.strip():
                        return message
        return str(exc)
