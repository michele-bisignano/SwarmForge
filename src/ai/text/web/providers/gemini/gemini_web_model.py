from typing import Any
from ...web_text_model import AbstractWebTextModel

class GeminiWebModel(AbstractWebTextModel):
    """
    LEVEL 3: Concrete implementation for Gemini via web automation.
    """

    def get_provider(self) -> str: return "google_web"
    def get_api_id(self) -> str: return "gemini-web-ui"
    def is_available(self) -> bool: return True
    def supports_refining(self) -> bool: return True
    def get_context_window(self) -> int: return 32000
    def get_model_limits(self) -> dict[str, Any]:
        return {"rpm": 10, "rpd": 100, "max_output_tokens": 4096}

    # --- DEFINIZIONE SELETTORI DOM ---

    def get_target_url(self) -> str:
        return "https://gemini.google.com/app"

    def get_input_selector(self) -> str:
        # Selettori possibili per Gemini
        return "textarea, [contenteditable='true'], [role='textbox']"

    def get_output_selector(self) -> str:
        # Selettori per le risposte di Gemini
        return ".message-content, [data-message-author='model'], .response-content"

    # --- OVERRIDE COMPORTAMENTO SPECIFICO DEL SITO ---

    def _wait_for_generation_complete(self) -> None:
        """
        Gemini-specific logic: wait for the generation indicator
        (spinner or loading class) to disappear from the DOM.
        """
        try:
            # Diamo al motore 1 secondo per iniziare la generazione
            self._page.wait_for_timeout(1000)

            # Attendiamo che eventuali elementi di loading spariscano
            # Gemini spesso usa classi come 'generating' o spinner
            loading_selectors = [
                "div.generating",
                "div.loading",
                ".spinner",
                "[aria-label*='Generating']"
            ]

            for selector in loading_selectors:
                try:
                    self._page.wait_for_selector(selector, state="hidden", timeout=5000)
                    break  # Se ne trova uno, esce dal loop
                except:
                    continue

            # Fallback: attendi un po' di tempo
            self._page.wait_for_timeout(3000)

        except Exception:
            # Fallback sistemistico se l'UI di Google viene modificata
            self._page.wait_for_timeout(5000)