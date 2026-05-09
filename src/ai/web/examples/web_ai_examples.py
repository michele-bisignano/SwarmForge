#!/usr/bin/env python3
"""
Example usage of web AI automation in the SwarmForge main program.
This script demonstrates how to use ChatGPT and Gemini models in a host workflow.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ai.text.web.providers.chatgpt.chatgpt_web_model import ChatGPTWebModel
from src.ai.text.web.providers.gemini.gemini_web_model import GeminiWebModel

def basic_usage_example():
    """Basic example of using web AI models."""
    print("🔧 BASIC USAGE EXAMPLE")
    print("-" * 40)

    chatgpt = ChatGPTWebModel(headless=True)

    prompt = "Explain what artificial intelligence is in 3 points."
    response, context = chatgpt.generate_text(prompt)

    print(f"Prompt: {prompt}")
    print(f"Response: {response[:200]}...")
    print(f"Conversation ID: {context.get('conversation_id')}")

    chatgpt.reset_context()

def gemini_google_example():
    """Example using Gemini with Google-based navigation."""
    print("\n🔍 GEMINI WITH GOOGLE NAVIGATION EXAMPLE")
    print("-" * 40)

    gemini = GeminiWebModel(headless=True, start_from_google=True)

    prompt = "What are the benefits of automation?"
    response, context = gemini.generate_text(prompt)

    print(f"Prompt: {prompt}")
    print(f"Response: {response[:200]}...")
    print(f"Last interaction state: {context.get('last_interaction')}")

    gemini.reset_context()

def saved_conversations_example():
    """Example accessing saved conversation logs."""
    print("\n💾 SAVED CONVERSATIONS EXAMPLE")
    print("-" * 40)

    model = ChatGPTWebModel()

    conversations = model.list_conversations()
    print(f"Total conversations: {len(conversations)}")

    if conversations:
        conv = model.load_conversation(conversations[0])
        if conv:
            print(f"Conversation {conv.conversation_id}:")
            print(f"  Provider: {conv.provider}")
            print(f"  Messages: {len(conv.messages)}")
            print(f"  Processing time: {conv.metadata.processing_time_ms}ms")

    stats = model.get_conversation_stats()
    print(f"Statistics: {stats}")

def orchestrator_integration_example():
    """Example of how web models can be integrated into an orchestrator."""
    print("\n🎯 ORCHESTRATOR INTEGRATION EXAMPLE")
    print("-" * 40)

    print("To integrate with a SwarmForge orchestrator:")
    print("1. Import the web models")
    print("2. Register them with the orchestrator agent registry")
    print("3. Dispatch tasks through the orchestrator")
    print("4. Conversation logs are saved automatically to JSON")

    print("\nExample (conceptual):")
    print("  orchestrator.register_agent(ChatGPTWebModel())")
    print("  orchestrator.register_agent(GeminiWebModel())")
    print("  result = await orchestrator.run('Write integration documentation')")

def main():
    """Main demonstration entry point."""
    print("🤖 SWARMFORGE - WEB AI AUTOMATION EXAMPLES")
    print("=" * 50)

    basic_usage_example()
    gemini_google_example()
    saved_conversations_example()
    orchestrator_integration_example()

    print("\n" + "=" * 50)
    print("✅ Examples completed!")
    print("📁 Conversation logs saved in: data/conversations/")
    print("📖 Full documentation: Docs/architecture/web-automation-architecture.md")

if __name__ == "__main__":
    main()