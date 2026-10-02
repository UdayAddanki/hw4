import os
import json
from datetime import datetime, timezone
from pathlib import Path

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

try:
    from .models import ChatDependencies, ChatReply
    from .tools import check_stock, get_product_info, search_products
except ImportError:
    from models import ChatDependencies, ChatReply
    from tools import check_stock, get_product_info, search_products

PROMPT_PATH = Path(__file__).parent / "prompts" / "prompt.md"
SYSTEM_PROMPT = PROMPT_PATH.read_text(encoding="utf-8")
DEFAULT_MODEL = "gpt-5.6-luna"
AUDIT_PATH = Path(__file__).resolve().parents[1] / "output" / "audit_trail.json"


def _short(value: object, limit: int = 500) -> str:
    text = value if isinstance(value, str) else json.dumps(value, default=str, separators=(",", ":"))
    return text if len(text) <= limit else text[:limit - 1] + "…"


def _audit(tool_name: str, args: object, result: object, stopped_reason: str | None = None) -> None:
    """Append one compact, non-sensitive activity record to the audit trail."""
    AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        records = json.loads(AUDIT_PATH.read_text(encoding="utf-8")) if AUDIT_PATH.exists() else []
        if not isinstance(records, list):
            records = []
    except (OSError, json.JSONDecodeError):
        records = []
    record = {"time": datetime.now(timezone.utc).isoformat(), "tool_name": tool_name, "args": _short(args), "result": _short(result)}
    if stopped_reason is not None:
        record["stopped_reason"] = stopped_reason
    records.append(record)
    AUDIT_PATH.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")


def _audited_search_products(query: str):
    try:
        result = search_products(query)
        _audit("search_products", {"query": query}, result)
        return result
    except Exception as error:
        _audit("search_products", {"query": query}, str(error))
        raise


def _audited_get_product_info(product_query: str):
    try:
        result = get_product_info(product_query)
        _audit("get_product_info", {"product_query": product_query}, result)
        return result
    except Exception as error:
        _audit("get_product_info", {"product_query": product_query}, str(error))
        raise


def _audited_check_stock(product_query: str, size: str | None = None):
    try:
        result = check_stock(product_query, size)
        _audit("check_stock", {"product_query": product_query, "size": size}, result)
        return result
    except Exception as error:
        _audit("check_stock", {"product_query": product_query, "size": size}, str(error))
        raise


def build_agent() -> Agent:
    api_key = os.getenv("PORTKEY_API_KEY")
    if not api_key:
        raise RuntimeError("PORTKEY_API_KEY is not configured.")
    provider = OpenAIProvider(base_url="https://api.portkey.ai/v1", api_key=api_key)
    model = OpenAIChatModel(os.getenv("PORTKEY_MODEL", DEFAULT_MODEL), provider=provider)
    agent = Agent(model, output_type=ChatReply, deps_type=ChatDependencies, system_prompt=SYSTEM_PROMPT, retries=1)
    agent.tool_plain(_audited_search_products)
    agent.tool_plain(_audited_get_product_info)
    agent.tool_plain(_audited_check_stock)
    return agent


async def run_chat(message: str, dependencies: ChatDependencies) -> ChatReply:
    agent = build_agent()
    context = []
    if dependencies.customer_name or dependencies.customer_email:
        context.append(f"Logged-in customer: {dependencies.customer_name or 'Unknown'} ({dependencies.customer_email or 'email unavailable'}).")
    if dependencies.page_product_id:
        context.append(f"The customer is viewing product {dependencies.page_product_id} ({dependencies.page_product_name or 'name unavailable'}). Interpret 'this product' using this context.")
    prompt = message + ("\n\nContext for this request:\n" + "\n".join(context) if context else "")
    try:
        result = await agent.run(prompt, deps=dependencies)
        _audit("agent_run", {"message": message}, result.output, "completed")
        return result.output
    except Exception as error:
        _audit("agent_run", {"message": message}, str(error), f"failed: {type(error).__name__}")
        raise
