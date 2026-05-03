from abc import abstractmethod
from typing import Any, Iterator
import time
import os
import tempfile
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from .conversation_logger import ConversationLogger

from ..text_model import AbstractTextModel

class AbstractWebTextModel(AbstractTextModel):
    """
    LEVEL 2: Abstract class for web automation-based models (RPA).
    Manages Playwright lifecycle and browser state abstraction.
    """

    def __init__(self, headless: bool = True, start_from_google: bool = False, persistent_profile: bool = True, **kwargs):
        super().__init__(**kwargs)
        self._headless = headless
        self._start_from_google = start_from_google
        self._persistent_profile = persistent_profile
        self._playwright = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None
        self._page: Page | None = None
        self._logger = ConversationLogger()
        self._current_conversation_id: str | None = None

    def __del__(self):
        """Safety destructor: prevents orphaned browser processes."""
        self.reset_context()

    # --- ABSTRACT CONFIGURATION METHODS ---

    @abstractmethod
    def get_target_url(self) -> str: ...

    @abstractmethod
    def get_input_selector(self) -> str: ...

    @abstractmethod
    def get_output_selector(self) -> str: ...

    def _wait_for_generation_complete(self) -> None:
        """
        Template method to wait for AI generation to complete.
        Child implementations should override this for UI-specific checks.
        Base fallback: fixed short wait.
        """
        if self._page:
            self._page.wait_for_timeout(5000)

    # --- CORE RPA ENGINE ---

    def _ensure_browser_running(self):
        """Start the browser instance using the current Chrome profile."""
        if not self._playwright:
            import os
            import tempfile
            
            # 1. Prevent stale Chrome processes on macOS.
            # Terminate background Chrome instances that can lock the profile.
            try:
                os.system("pkill -9 'Google Chrome'")
            except Exception:
                pass
                
            self._playwright = sync_playwright().start()
            
            # Use a dedicated profile directory to avoid conflicts with the main Chrome profile.
            # This makes automation stable and preserves login state when enabled.
            if self._persistent_profile:
                # Use persistent profile to keep login sessions across runs
                profile_dir = os.path.expanduser("~/.swarmforge_browser_profile")
                os.makedirs(profile_dir, exist_ok=True)
                print(f"[*] Using persistent profile: {profile_dir}")
                print("    💡 Login sessions will be preserved between executions")
            else:
                # Use temporary profile for non-persistent sessions
                profile_dir = tempfile.mkdtemp(prefix="playwright_chrome_")
                print(f"[*] Using temporary profile: {profile_dir}")

            self._temp_profile_dir = profile_dir  # Store for logging

            # 2. Robust configuration:
            # Use launch_persistent_context with the chosen profile directory
            self._context = self._playwright.chromium.launch_persistent_context(
                user_data_dir=profile_dir,
                headless=self._headless,
                channel="chrome",
                no_viewport=True,  # Let Chrome decide the optimal viewport size
                args=[
                    "--disable-blink-features=AutomationControlled",  # Hide automation from websites (anti-bot)
                    "--disable-infobars",  # Remove the 'Chrome is controlled by automated software' bar
                    "--disable-extensions",  # Disable extensions that may interfere
                    "--disable-plugins",  # Disable plugins
                    "--no-first-run",  # Skip first-run setup
                    "--disable-default-apps",  # Disable default apps
                    "--disable-sync",  # Disable sync
                    "--disable-translate",  # Disable automatic translation
                    "--hide-scrollbars",  # Hide scrollbars
                    "--metrics-recording-only",  # Only record metrics
                    "--mute-audio",  # Mute audio
                    "--no-sandbox",  # Disable sandbox for compatibility
                    "--disable-dev-shm-usage",  # Avoid shared memory issues
                ]
            )
            
            # Select an existing page or open a new one.
            if len(self._context.pages) > 0:
                self._page = self._context.pages[0]
            else:
                self._page = self._context.new_page()

            # Initial navigation
            if self._start_from_google:
                self._navigate_from_google()
            else:
                self._page.goto(self.get_target_url())

    def _navigate_from_google(self):
        """Navigate to the target site starting from a Google search."""
        # Go to Google
        self._page.goto("https://www.google.com")
        
        # Wait for the search field to become available
        self._page.wait_for_selector("textarea[name='q']", state="visible", timeout=10000)

        # Search for the AI service name
        search_term = self._get_google_search_term()
        self._page.fill("textarea[name='q']", search_term)
        self._page.press("textarea[name='q']", "Enter")

        # Wait for search results to load
        self._page.wait_for_load_state("networkidle", timeout=10000)

        # Click the first result, usually the official service page
        first_result = self._page.query_selector("h3")
        if first_result:
            first_result.click()
        else:
            # Fallback: navigate directly to the target URL
            self._page.goto(self.get_target_url())
    
    def _get_google_search_term(self) -> str:
        """Return the Google search term for the configured provider."""
        provider = self.get_provider()
        if "chatgpt" in provider.lower():
            return "ChatGPT OpenAI"
        elif "gemini" in provider.lower():
            return "Gemini Google AI"
        else:
            return "AI Chat"
    def generate_text(
        self, 
        prompt: str, 
        images: list[Any] | None = None, 
        ai_context: dict[str, Any] | None = None, 
        **kwargs: Any
    ) -> tuple[str, dict[str, Any]]:
        
        # Start timing
        start_time = time.time()
        
        self._ensure_browser_running()
        
        try:
            # FIX 1: Snapshot the initial DOM state to manage multi-turn conversation responses
            initial_count = len(self._page.query_selector_all(self.get_output_selector()))

            # Fill and submit the prompt
            self._page.wait_for_selector(self.get_input_selector(), state="visible")
            self._page.fill(self.get_input_selector(), prompt)
            self._page.press(self.get_input_selector(), "Enter")
            
            # FIX 2: Wait for a new response node to be created in the DOM
            js_condition = f"() => document.querySelectorAll(\"{self.get_output_selector()}\").length > {initial_count}"
            self._page.wait_for_function(js_condition, timeout=60000)
            
            # FIX 3: Wait for the text streaming process to complete
            self._wait_for_generation_complete()

            # Extract final text from the latest response node
            elements = self._page.query_selector_all(self.get_output_selector())
            response_text = elements[-1].inner_text().strip() if elements else ""

            # Calculate processing time
            processing_time_ms = int((time.time() - start_time) * 1000)

            # Log the conversation and preserve multi-turn history
            conversation_id = self._logger.log_interaction(
                provider=self.get_provider(),
                model=self.get_api_id(),
                user_prompt=prompt,
                ai_response=response_text,
                browser_profile=getattr(self, '_temp_profile_dir', 'unknown'),
                start_from_google=self._start_from_google,
                processing_time_ms=processing_time_ms,
                headless=self._headless,
                conversation_id=self._current_conversation_id,
            )

            # Store conversation ID for multi-turn conversations
            self._current_conversation_id = conversation_id

        except Exception as e:
            response_text = f"[Web Automation Error]: {str(e)}"

        ctx = ai_context or {}
        ctx["last_interaction"] = "success"
        ctx["conversation_id"] = self._current_conversation_id
        
        return response_text, ctx

    def reset_context(self) -> None:
        """Safe forced shutdown and full cleanup."""
        try:
            # Close the Playwright context and browser
            if self._context: self._context.close()
            if self._playwright: self._playwright.stop()
        except Exception:
            pass  # Ignore errors if the process is already terminated

        # Reset conversation ID for new sessions
        self._current_conversation_id = None

        # Clear internal state
        self._playwright, self._browser, self._context, self._page = None, None, None, None

    # --- BROWSER PROFILE MANAGEMENT METHODS ---

    def setup_browser_profile(self):
        """
        Prepare the browser profile with manual login.
        Useful for initial session setup.
        """
        print("🔐 BROWSER PROFILE SETUP")
        print("This method opens the browser so you can perform manual login.")
        print("Log in to the services you want to automate (Google, ChatGPT, Gemini, etc.)")
        print("Press ENTER when finished...")
        
        # Force visible mode for setup
        original_headless = self._headless
        self._headless = False
        
        try:
            self._ensure_browser_running()
            print(f"✅ Browser opened. Profile: {self._temp_profile_dir}")
            print("ℹ️  Perform the required logins, then close the browser.")

            # Wait for user input
            input("\nPress ENTER when you have completed the login...")
            
        finally:
            self.reset_context()
            self._headless = original_headless  # Restore original headless setting

    def clear_browser_profile(self):
        """Delete the persistent browser profile (useful for a full reset)."""
        import shutil

        profile_dir = os.path.expanduser("~/.swarmforge_browser_profile")
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
            print(f"🗑️  Browser profile deleted: {profile_dir}")
        else:
            print("ℹ️  No persistent profile found.")

    def get_browser_profile_path(self) -> str:
        """Return the path of the current browser profile."""
        return self._temp_profile_dir if hasattr(self, '_temp_profile_dir') else "not initialized"

    def get_conversation_logger(self) -> ConversationLogger:
        """Return the conversation logger instance."""
        return self._logger

    def get_current_conversation_id(self) -> str | None:
        """Return the current conversation ID."""
        return self._current_conversation_id

    def load_conversation(self, conversation_id: str):
        """Load a saved conversation."""
        return self._logger.load_conversation(conversation_id)

    def list_conversations(self, provider: str | None = None) -> list[str]:
        """List all conversations, optionally filtered by provider."""
        return self._logger.list_conversations(provider)

    def get_conversation_stats(self) -> dict[str, Any]:
        """Return statistics for saved conversations."""
        return self._logger.get_conversation_stats()

    # Dummy implementations for the abstract contract
    def supports_streaming(self) -> bool: return False
    def supports_vision(self) -> bool: return False
    def count_tokens(self, prompt: str, images: list[Any] | None = None) -> int: return len(prompt.split())
    def stream_text(self, prompt: str, **kwargs) -> Iterator[str]: raise NotImplementedError()