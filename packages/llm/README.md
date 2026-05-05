# LLM Package

NVIDIA build is the default month-one model provider. The current API adapter lives in `services/api/app/nvidia.py` and uses the OpenAI-compatible chat completions endpoint.

All future LLM calls should write to `llm_usage` and connect to `agent_actions`.
