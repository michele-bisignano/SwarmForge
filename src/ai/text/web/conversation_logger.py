import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Message:
    """Represents a single message in a conversation."""
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

@dataclass
class ConversationMetadata:
    """Metadata for a conversation session."""
    browser_profile: str
    start_from_google: bool
    processing_time_ms: int
    total_tokens: int
    headless: bool
    provider: str
    model: str

@dataclass
class Conversation:
    """Complete conversation data structure."""
    conversation_id: str
    timestamp: str
    provider: str
    model: str
    messages: List[Message]
    metadata: ConversationMetadata

class ConversationLogger:
    """
    Handles JSON serialization and persistence of AI conversations.
    Integrates seamlessly with the SwarmForge web automation framework.
    """

    def __init__(self, base_dir: str = "data/conversations"):
        """
        Initialize the conversation logger.

        Args:
            base_dir: Base directory for storing conversation files
        """
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def log_interaction(
        self,
        provider: str,
        model: str,
        user_prompt: str,
        ai_response: str,
        browser_profile: str,
        start_from_google: bool,
        processing_time_ms: int,
        headless: bool,
        conversation_id: Optional[str] = None
    ) -> str:
        """
        Log a single interaction (user prompt + AI response).

        Args:
            provider: AI provider name (e.g., "chatgpt", "gemini")
            model: Specific model name (e.g., "gpt-4", "gemini-pro")
            user_prompt: User's input prompt
            ai_response: AI's response text
            browser_profile: Path to temporary browser profile
            start_from_google: Whether navigation started from Google search
            processing_time_ms: Total processing time in milliseconds
            headless: Whether browser ran in headless mode
            conversation_id: Optional existing conversation ID for multi-turn

        Returns:
            str: The conversation ID used
        """
        # Generate new conversation ID if not provided
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        # Try to load an existing conversation for multi-turn support
        existing_conversation = self.load_conversation(conversation_id) if conversation_id else None

        # Create timestamp for the new user message
        timestamp = datetime.now().isoformat()

        # Build new messages
        new_messages = [
            Message(role="user", content=user_prompt, timestamp=timestamp),
            Message(
                role="assistant",
                content=ai_response,
                timestamp=datetime.now().isoformat(),  # Slight delay for response
            ),
        ]

        if existing_conversation:
            messages = existing_conversation.messages + new_messages
            conversation_timestamp = existing_conversation.timestamp
        else:
            messages = new_messages
            conversation_timestamp = timestamp

        # Estimate token count (rough approximation)
        total_tokens = self._estimate_tokens("".join([msg.content for msg in messages]))

        # Create metadata
        metadata = ConversationMetadata(
            browser_profile=browser_profile,
            start_from_google=start_from_google,
            processing_time_ms=processing_time_ms,
            total_tokens=total_tokens,
            headless=headless,
            provider=provider,
            model=model,
        )

        # Create or update conversation object
        conversation = Conversation(
            conversation_id=conversation_id,
            timestamp=conversation_timestamp,
            provider=provider,
            model=model,
            messages=messages,
            metadata=metadata,
        )

        # Save to file
        self._save_conversation(conversation)

        return conversation_id

    def _save_conversation(self, conversation: Conversation) -> None:
        """
        Save conversation to JSON file.

        Args:
            conversation: Conversation object to save
        """
        filename = f"{conversation.conversation_id}.json"
        filepath = self.base_dir / filename

        # Convert to dictionary
        conversation_dict = asdict(conversation)

        # Save with pretty formatting
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_dict, f, indent=2, ensure_ascii=False)

    def load_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """
        Load a conversation from JSON file.

        Args:
            conversation_id: ID of the conversation to load

        Returns:
            Conversation object or None if not found
        """
        filepath = self.base_dir / f"{conversation_id}.json"

        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Convert back to Conversation object
            messages = [Message(**msg) for msg in data['messages']]
            metadata = ConversationMetadata(**data['metadata'])

            return Conversation(
                conversation_id=data['conversation_id'],
                timestamp=data['timestamp'],
                provider=data['provider'],
                model=data['model'],
                messages=messages,
                metadata=metadata
            )
        except Exception:
            return None

    def list_conversations(self, provider: Optional[str] = None) -> List[str]:
        """
        List all conversation IDs, optionally filtered by provider.

        Args:
            provider: Optional provider filter

        Returns:
            List of conversation IDs
        """
        conversations = []

        for filepath in self.base_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if provider is None or data.get('provider') == provider:
                    conversations.append(data['conversation_id'])
            except Exception:
                continue

        return sorted(conversations)

    def get_conversation_stats(self) -> Dict[str, Any]:
        """
        Get statistics about logged conversations.

        Returns:
            Dictionary with conversation statistics
        """
        conversations = []
        providers = {}
        total_tokens = 0
        total_processing_time = 0

        for filepath in self.base_dir.glob("*.json"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                conversations.append(data)
                provider = data.get('provider', 'unknown')
                providers[provider] = providers.get(provider, 0) + 1
                total_tokens += data.get('metadata', {}).get('total_tokens', 0)
                total_processing_time += data.get('metadata', {}).get('processing_time_ms', 0)
            except Exception:
                continue

        return {
            "total_conversations": len(conversations),
            "providers": providers,
            "total_tokens": total_tokens,
            "average_processing_time_ms": total_processing_time / max(len(conversations), 1),
            "storage_path": str(self.base_dir)
        }

    def _estimate_tokens(self, text: str) -> int:
        """
        Rough token estimation (approximation).

        Args:
            text: Text to estimate tokens for

        Returns:
            Estimated token count
        """
        # Simple approximation: ~4 characters per token for English text
        return len(text) // 4

    def export_conversations(self, output_file: str, provider: Optional[str] = None) -> None:
        """
        Export conversations to a single JSON file.

        Args:
            output_file: Path to output file
            provider: Optional provider filter
        """
        conversations = []

        for conv_id in self.list_conversations(provider):
            conv = self.load_conversation(conv_id)
            if conv:
                conversations.append(asdict(conv))

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)