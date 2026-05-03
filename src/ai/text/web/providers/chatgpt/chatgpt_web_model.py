from typing import Any
from ...web_text_model import AbstractWebTextModel

class ChatGPTWebModel(AbstractWebTextModel):
    """
    LEVEL 3: Concrete implementation for ChatGPT via web automation.
    """

    def get_provider(self) -> str: return "openai_web"
    def get_api_id(self) -> str: return "chatgpt-web-ui"
    def is_available(self) -> bool: return True
    def supports_refining(self) -> bool: return True
    def get_context_window(self) -> int: return 32000
    def get_model_limits(self) -> dict[str, Any]:
        return {"rpm": 10, "rpd": 100, "max_output_tokens": 4096}

    # --- DEFINIZIONE SELETTORI DOM ---

    def get_target_url(self) -> str:
        return "https://chatgpt.com/"

    def get_input_selector(self) -> str:
        return "#prompt-textarea"

    def get_output_selector(self) -> str:
        return "div[data-message-author-role='assistant'] .markdown"

    # --- OVERRIDE COMPORTAMENTO SPECIFICO DEL SITO ---

    def _wait_for_generation_complete(self) -> None:
        """
        ChatGPT-specific logic: wait for the 'result-streaming' indicator
        to disappear from the DOM after the response finishes streaming.
        """
        try:
            # Diamo al motore 1 secondo per iniettare l'elemento streaming
            self._page.wait_for_timeout(1000)
            
            # Attendiamo che l'elemento indicatore di streaming venga nascosto/rimosso
            streaming_selector = "div.result-streaming"
            self._page.wait_for_selector(streaming_selector, state="hidden", timeout=120000)
        except Exception:
            # Fallback sistemistico se l'UI di OpenAI viene modificata
            self._page.wait_for_timeout(5000)