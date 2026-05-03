# Web Automation Architecture — AI Chat Interface Automation

**Feature:** Web Automation for AI Chat Interfaces
**Phase:** 1 — *Browser-Based AI Integration*
**Status:** Implemented — **Production Ready**
**Date:** May 3, 2026
**Authors:** [Michele Bisignano], [Alessandro Campani]

---

## 1. Overview & Vision

The Web Automation Architecture provides a robust, browser-based interface for interacting with external AI chat services (ChatGPT, Gemini) through automated web scraping and interaction. This system enables seamless integration of third-party AI services while maintaining full control over the interaction flow, data persistence, and error handling.

**Key Objectives:**
- Automate browser navigation and user interactions with AI chat interfaces
- Provide reliable prompt submission and response extraction
- Enable both direct URL navigation and Google search-based discovery
- Implement comprehensive logging and data persistence in JSON format
- Ensure compatibility with the main SwarmForge orchestrator framework

---

## 2. Architecture Components

### 2.1 Core Classes Hierarchy

```
─── Abstract Base Classes ──────────────────────────────

AbstractWebTextModel (ABC)
  │   Core browser automation engine using Playwright
  │   Manages browser lifecycle, navigation, and DOM interaction
  │   Provides template methods for service-specific implementations
  │
  ├── ChatGPTWebModel          (Concrete implementation for OpenAI ChatGPT)
  │     └─ Target: https://chatgpt.com/
  │     └─ Input Selector: #prompt-textarea
  │     └─ Output Selector: div[data-message-author-role='assistant'] .markdown
  │
  └── GeminiWebModel           (Concrete implementation for Google Gemini)
      └─ Target: https://gemini.google.com/app
      └─ Input Selector: textarea, [contenteditable='true'], [role='textbox']
      └─ Output Selector: .message-content, [data-message-author='model']

─── Data Persistence Layer ────────────────────────────

ConversationLogger
  │   Handles JSON serialization of all interactions
  │   Maintains conversation history and metadata
  │   Provides query capabilities for logged conversations
  │
  └── JSON Structure:
      {
        "conversation_id": "uuid4",
        "timestamp": "ISO8601",
        "provider": "chatgpt|gemini",
        "model": "gpt-4|gemini-pro",
        "messages": [
          {
            "role": "user|assistant",
            "content": "text",
            "timestamp": "ISO8601"
          }
        ],
        "metadata": {
          "browser_profile": "temp_dir_path",
          "start_from_google": true|false,
          "total_tokens": 150,
          "processing_time_ms": 2500
        }
      }
```

### 2.2 Browser Automation Engine

The `AbstractWebTextModel` class serves as the core automation engine:

**Key Features:**
- **Persistent Browser Profiles:** Maintains login sessions across executions using dedicated profile directory (~/.swarmforge_browser_profile)
- **Dual Navigation Modes:** Direct URL access or Google search-based discovery
- **DOM Interaction:** Automated form filling, button clicking, and content extraction
- **Error Handling:** Comprehensive timeout management and fallback strategies
- **Resource Management:** Automatic browser cleanup and process termination

**Browser Profile Management:**
```python
# Persistent profile (recommended to preserve login)
model = ChatGPTWebModel(persistent_profile=True)  # Default: True

# Temporary profile (non-persistent sessions)
model = ChatGPTWebModel(persistent_profile=False)

# Initial profile setup with manual login
model.setup_browser_profile()  # Opens the browser for manual login

# Reset the profile when needed
model.clear_browser_profile()
```

**Browser Configuration:**
```python
# Chrome launch arguments for automation
args = [
    "--disable-blink-features=AutomationControlled",  # Anti-detection
    "--disable-infobars",                            # Clean interface
    "--disable-extensions",                          # Performance
    "--no-first-run",                               # Skip setup
    "--disable-sync",                               # Privacy
    "--headless",                                   # Optional background mode
]
```

---

## 3. Implementation Steps

### Step 1: Environment Setup

**Prerequisites:**
- Python 3.10+
- Playwright with Chromium browser
- Required packages: `playwright`, `pydantic`, `typing`

**Installation:**
```bash
# Install Playwright browsers
playwright install chromium

# Verify installation
python -c "import playwright; print('✓ Playwright ready')"
```

### Step 2: Browser Profile Setup

**Initial Login Setup (One-time):**
```bash
# Run setup to configure the profile with login
python -c "
from src.ai.text.web.providers.chatgpt.chatgpt_web_model import ChatGPTWebModel
model = ChatGPTWebModel()
model.setup_browser_profile()
"
```

**What happens during setup:**
1. Opens a dedicated browser profile at `~/.swarmforge_browser_profile`
2. Allows manual login to Google, ChatGPT, Gemini, etc.
3. Saves cookies and session data for future automated use
4. Sessions persist across program restarts

### Step 3: Model Initialization

**With Persistent Profile (Recommended):**
```python
from src.ai.text.web.providers.chatgpt.chatgpt_web_model import ChatGPTWebModel

# Uses persistent profile (maintains login sessions)
model = ChatGPTWebModel(headless=True, persistent_profile=True)
```

**With Temporary Profile:**
```python
# Uses temporary profile (fresh session each time)
model = ChatGPTWebModel(headless=True, persistent_profile=False)
```

### Step 3: Prompt Submission & Response

**Single Interaction:**
```python
prompt = "Explain quantum computing in simple terms"
response, context = model.generate_text(prompt)

print(f"Response: {response}")
print(f"Context: {context}")
```

**Multi-turn Conversation:**
```python
# First message
response1, context = model.generate_text("What is AI?")

# Follow-up (maintains conversation context)
response2, context = model.generate_text("Can you give a practical example?", ai_context=context)
```

### Step 4: Data Persistence

**Automatic JSON Logging:**
```python
# All interactions are automatically logged to JSON
# Files saved in: data/conversations/{conversation_id}.json

logger = ConversationLogger()
logger.save_conversation(conversation_data)
```

**JSON Output Structure:**
```json
{
  "conversation_id": "550e8400-e29b-41d4-a716-446655440000",
  "timestamp": "2026-05-03T15:30:00Z",
  "provider": "chatgpt",
  "model": "gpt-4",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?",
      "timestamp": "2026-05-03T15:30:00Z"
    },
    {
      "role": "assistant",
      "content": "I'm doing well, thank you for asking! How can I help you today?",
      "timestamp": "2026-05-03T15:30:02Z"
    }
  ],
  "metadata": {
    "browser_profile": "/tmp/playwright_chrome_abc123",
    "start_from_google": false,
    "processing_time_ms": 2150,
    "total_tokens": 45
  }
}
```

### Step 5: Resource Cleanup

**Proper Browser Termination:**
```python
# Always call reset_context() to clean up resources
model.reset_context()
```

---

## 4. Integration with SwarmForge Orchestrator

### 4.1 Agent Interface Compliance

The web automation models implement the standard `AbstractTextModel` interface:

```python
class ChatGPTWebModel(AbstractWebTextModel, AbstractTextModel):
    # Implements all required methods:
    # - generate_text()
    # - supports_streaming() -> False
    # - supports_vision() -> False
    # - count_tokens()
    # - get_context_window() -> 32000
    # - get_model_limits() -> dict
```

### 4.2 Orchestrator Integration

**Adding to Agent Registry:**
```python
from src.orchestrator.orchestrator import SwarmOrchestrator

orchestrator = SwarmOrchestrator()

# Register web-based AI agents
orchestrator.register_agent(ChatGPTWebModel())
orchestrator.register_agent(GeminiWebModel())

# Use in task decomposition
task = TaskRequest(description="Generate code documentation")
result = await orchestrator.process_task(task)
```

### 4.3 Data Pipeline Integration

**Conversation Data Flow:**
```
User Prompt → Web Automation → AI Response → JSON Logger → Database
                                      ↓
                            SwarmOrchestrator Context
```

---

## 5. Error Handling & Reliability

### 5.1 Timeout Management

**Configurable Timeouts:**
- **Page Load:** 10 seconds for initial navigation
- **Element Wait:** 30 seconds for DOM elements
- **Response Wait:** 60 seconds for AI generation
- **Generation Complete:** 120 seconds for streaming completion

### 5.2 Fallback Strategies

**Navigation Fallbacks:**
1. Direct URL access (primary)
2. Google search + click first result (fallback)
3. Manual URL input (emergency)

**Selector Fallbacks:**
1. Primary CSS selectors
2. Alternative attribute-based selectors
3. Generic element type selectors

### 5.3 Recovery Mechanisms

**Automatic Recovery:**
- Browser crash detection and restart
- Network timeout with retry logic
- DOM change adaptation
- Profile corruption handling

---

## 6. Security & Privacy Considerations

### 6.1 Data Isolation

**Browser Profile Management:**
- Temporary profiles for each session
- No persistent data storage
- Automatic cleanup on termination
- No access to user Chrome data

### 6.2 Network Security

**Traffic Considerations:**
- Direct HTTPS connections to AI services
- No proxy or MITM interception
- Standard SSL/TLS encryption
- No sensitive data logging

### 6.3 API Compliance

**Service Terms:**
- Respects rate limits of target services
- Implements proper user agent strings
- Avoids automation detection measures
- Maintains session integrity

---

## 7. Performance & Scalability

### 7.1 Resource Usage

**Memory Management:**
- Browser processes isolated per conversation
- Automatic cleanup prevents memory leaks
- Configurable headless mode for background operation

**Concurrent Sessions:**
- Multiple browser instances supported
- Independent session management
- No shared state between conversations

### 7.2 Optimization Strategies

**Performance Tuning:**
- Selective element waiting (vs full page loads)
- Efficient DOM queries with specific selectors
- Background processing for long-running tasks
- Connection pooling for repeated interactions

---

## 8. Testing & Validation

### 8.1 Unit Testing

**Test Coverage:**
```python
# Test browser initialization
def test_browser_launch():
    model = ChatGPTWebModel(headless=True)
    assert model._page is not None
    model.reset_context()

# Test prompt/response cycle
def test_conversation_flow():
    model = ChatGPTWebModel(headless=True)
    response, context = model.generate_text("Test prompt")
    assert len(response) > 0
    assert "conversation_id" in context
    model.reset_context()
```

### 8.2 Integration Testing

**End-to-End Validation:**
- Full conversation workflows
- Multi-turn dialogue handling
- Error recovery scenarios
- Data persistence verification

---

## 9. Future Enhancements

### 9.1 Planned Features

**Advanced Capabilities:**
- Multi-modal input support (images, files)
- Streaming response handling
- Custom prompt templates
- Conversation branching and versioning

**Platform Extensions:**
- Additional AI services (Claude, Grok, etc.)
- Mobile browser automation
- Cross-platform compatibility

### 9.2 Scalability Improvements

**Distributed Processing:**
- Load balancing across multiple browser instances
- Queue management for high-volume requests
- Resource pooling and optimization

---

## 10. Conclusion

The Web Automation Architecture provides a solid foundation for integrating external AI chat services into the SwarmForge ecosystem. By implementing robust browser automation, comprehensive error handling, and seamless data persistence, this system enables reliable AI interactions while maintaining full compatibility with the orchestrator framework.

**Key Achievements:**
- ✅ Successful browser automation for ChatGPT and Gemini
- ✅ Dual navigation modes (direct + Google search)
- ✅ Comprehensive JSON logging and data persistence
- ✅ Full integration with SwarmForge orchestrator
- ✅ Production-ready error handling and recovery

This implementation establishes SwarmForge as a versatile platform capable of leveraging multiple AI services through automated web interfaces, opening doors for extensive integration possibilities.