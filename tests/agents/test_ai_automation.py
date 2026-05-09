#!/usr/bin/env python3
"""
End-to-end test script for web automation with ChatGPT and Gemini.
Demonstrates browser startup, prompt submission, multi-turn flow, and JSON logging.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Import moved to main() function to avoid scope issues

def test_model(model_class, model_name, prompt, start_from_google=False, persistent_profile=True):
    """Run a single model test scenario."""
    print(f"\n{'='*50}")
    print(f"TEST {model_name.upper()}")
    print(f"{'='*50}")
    print(f"Start from Google: {start_from_google}")
    print(f"Persistent Profile: {persistent_profile}")
    print(f"Prompt: {prompt}")

    model = None
    try:
        model = model_class(headless=False, start_from_google=start_from_google, persistent_profile=persistent_profile)

        print("\n[*] Generating response...")
        response, context = model.generate_text(prompt)

        print(f"\n{model_name} response:")
        print(response)

        if response and "[Error]" not in response:
            follow_up = "Can you explain that in more detail?"
            print(f"\n[*] Multi-turn follow-up: {follow_up}")
            response2, context2 = model.generate_text(follow_up, ai_context=context)
            print(f"Follow-up response: {response2}")

        print(f"\n[*] Conversation saved with ID: {model.get_current_conversation_id()}")

        stats = model.get_conversation_stats()
        print(f"[*] Conversation statistics: {stats}")

        print(f"\n[*] {model_name} test completed successfully!")

    except Exception as e:
        print(f"[!] Error during {model_name} test: {e}")

    finally:
        if model:
            try:
                model.reset_context()
                print(f"[*] Closed browser for {model_name}.")
            except Exception:
                pass

def main():
    """Main entry point for the web automation test script."""
    from src.ai.text.web.providers.chatgpt.chatgpt_web_model import ChatGPTWebModel
    from src.ai.text.web.providers.gemini.gemini_web_model import GeminiWebModel
    
    print("🤖 WEB AI AUTOMATION TEST SCRIPT")
    print("This script demonstrates browser automation for ChatGPT and Gemini.")
    print("Before running these tests, ensure the persistent browser profile is set up:")
    print("  python setup_browser_profile.py")

    test_prompt = "Write a short poem about technology in English."

    test_model(ChatGPTWebModel, "ChatGPT (Direct)", test_prompt, start_from_google=False, persistent_profile=True)
    test_model(ChatGPTWebModel, "ChatGPT (From Google)", test_prompt, start_from_google=True, persistent_profile=True)
    test_model(GeminiWebModel, "Gemini (Direct)", test_prompt, start_from_google=False, persistent_profile=True)
    test_model(GeminiWebModel, "Gemini (From Google)", test_prompt, start_from_google=True, persistent_profile=True)

    print("\n" + "="*50)
    print("🎉 ALL TESTS COMPLETED!")
    print("You can now integrate these models into your application.")
    print("="*50)
    
    print("\n📊 SAVED CONVERSATIONS DEMO")
    print("-"*50)
    
    temp_model = ChatGPTWebModel()
    all_conversations = temp_model.list_conversations()
    print(f"📝 Total saved conversations: {len(all_conversations)}")
    
    if all_conversations:
        last_conv_id = all_conversations[-1]
        last_conv = temp_model.load_conversation(last_conv_id)
        
        if last_conv:
            print(f"📄 Last conversation (ID: {last_conv_id}):")
            print(f"   Provider: {last_conv.provider}")
            print(f"   Messages: {len(last_conv.messages)}")
            print(f"   Processing time: {last_conv.metadata.processing_time_ms}ms")
            print(f"   Total tokens: {last_conv.metadata.total_tokens}")
            
            if last_conv.messages:
                first_msg = last_conv.messages[0].content[:100]
                print(f"   First message: {first_msg}{'...' if len(last_conv.messages[0].content) > 100 else ''}")
    
    stats = temp_model.get_conversation_stats()
    print(f"\n📈 Overall statistics:")
    print(f"   Total conversations: {stats['total_conversations']}")
    print(f"   Total tokens: {stats['total_tokens']}")
    print(f"   Average processing time: {stats['average_processing_time_ms']:.1f}ms")
    print(f"   Storage path: {stats['storage_path']}")
    
    print("\n💡 Conversation logs are saved as JSON for future analysis!")

if __name__ == "__main__":
    main()