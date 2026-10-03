import json
import os

import requests


class AIProviderError(Exception):
	pass


class AIRateLimitError(AIProviderError):
	pass


class LLMClient:
	def __init__(self):
		self.api_key = os.getenv("LLM_API_KEY")
		self.base_url = os.getenv(
			"LLM_API_BASE_URL",
			"https://api.openai.com/v1",
		).rstrip("/")
		self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")

	def generate_structured(self, system_prompt, user_data):
		if not self.api_key:
			raise AIProviderError("LLM_API_KEY is not configured.")

		try:
			response = requests.post(
				f"{self.base_url}/chat/completions",
				headers={
					"Authorization": f"Bearer {self.api_key}",
					"Content-Type": "application/json",
				},
				json={
					"model": self.model,
					"messages": [
						{"role": "system", "content": system_prompt},
						{
							"role": "user",
							"content": json.dumps(user_data, ensure_ascii=True),
						},
					],
					"response_format": {"type": "json_object"},
					"temperature": 0,
				},
				timeout=20,
			)
		except requests.Timeout as exc:
			raise TimeoutError("LLM request timed out.") from exc
		except requests.RequestException as exc:
			raise AIProviderError("LLM request failed.") from exc

		if response.status_code == 429:
			raise AIRateLimitError("LLM rate limit reached.")
		if response.status_code != 200:
			raise AIProviderError("LLM returned an unexpected response.")

		try:
			content = response.json()["choices"][0]["message"]["content"]
			return json.loads(content)
		except (KeyError, IndexError, TypeError, ValueError) as exc:
			raise AIProviderError("LLM returned invalid JSON output.") from exc