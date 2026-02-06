import os
from utils.currency_converter import CurrencyConverter
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv


class CurrencyConverterTool:
    def __init__(self):
        load_dotenv()
        self.api_key = os.environ.get("EXCHANGE_RATE_API_KEY")
        self.currency_service = (
            CurrencyConverter(self.api_key)
            if self.api_key
            else None
        )
        self.currency_converter_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        """Setup all tools for the currency converter tool"""
        if not self.currency_service or not self.currency_service.is_enabled():
            # Skip registering the tool when the API key is missing so the agent keeps running
            print(
                "Currency conversion tool disabled: missing EXCHANGE_RATE_API_KEY"
            )
            return []

        @tool
        def convert_currency(
            amount: float,
            from_currency: str,
            to_currency: str
        ):
            """Convert amount from one currency to another"""
            try:
                converted = self.currency_service.convert(
                    amount,
                    from_currency,
                    to_currency
                )
            except Exception as exc:  # pragma: no cover - relies on external API
                return f"Currency conversion failed: {exc}"

            if converted is None:
                return (
                    f"Currency conversion unavailable for "
                    f"{from_currency} -> {to_currency}"
                )
            return converted

        return [convert_currency]
