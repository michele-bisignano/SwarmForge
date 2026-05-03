#!/usr/bin/env python3
"""
Setup script for configuring the SwarmForge browser profile.
Allows manual login to AI sites before automation begins.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ai.text.web.providers.chatgpt.chatgpt_web_model import ChatGPTWebModel
from src.ai.text.web.providers.gemini.gemini_web_model import GeminiWebModel

def setup_chatgpt():
    """Set up the browser profile for ChatGPT."""
    print("\n🤖 CHATGPT SETUP")
    print("-" * 30)
    print("This setup lets you log in to ChatGPT manually.")
    print("The browser profile will be saved and reused automatically.")
    print()

    model = ChatGPTWebModel(persistent_profile=True)
    model.setup_browser_profile()

def setup_gemini():
    """Set up the browser profile for Gemini."""
    print("\n🌟 GEMINI SETUP")
    print("-" * 30)
    print("This setup lets you log in to Gemini manually.")
    print("The browser profile will be saved and reused automatically.")
    print()

    model = GeminiWebModel(persistent_profile=True)
    model.setup_browser_profile()

def setup_all():
    """Complete setup for all supported AI services."""
    print("\n🚀 FULL SETUP - ALL SERVICES")
    print("-" * 40)
    print("This setup walks you through login for all supported AI services.")
    print("Procedure:")
    print("1. First ChatGPT - go to chatgpt.com and log in")
    print("2. Then Gemini - go to gemini.google.com and log in")
    print("3. Close the browser when finished")
    print()

    print("STEP 1: ChatGPT setup")
    chatgpt = ChatGPTWebModel(persistent_profile=True)
    chatgpt.setup_browser_profile()

    print("\nSTEP 2: Gemini setup")
    gemini = GeminiWebModel(persistent_profile=True)
    gemini.setup_browser_profile()

def clear_profiles():
    """Delete all saved browser profiles."""
    print("\n🗑️  CLEAR PROFILES")
    print("-" * 30)
    print("This will delete all saved browser profiles.")
    print("You will need to log in again to AI services.")

    confirm = input("Are you sure? Type 'YES' to confirm: ")
    if confirm.upper() == 'YES':
        model = ChatGPTWebModel()
        model.clear_browser_profile()
        print("✅ Profiles deleted!")
    else:
        print("❌ Operation cancelled.")

def check_profiles():
    """Check the browser profile status."""
    print("\n📊 PROFILE STATUS")
    print("-" * 30)

    import os
    profile_dir = os.path.expanduser("~/.swarmforge_browser_profile")

    if os.path.exists(profile_dir):
        print(f"✅ Profile found: {profile_dir}")

        files = os.listdir(profile_dir)
        cookies = [f for f in files if 'cookie' in f.lower()]
        logins = [f for f in files if 'login' in f.lower() or 'auth' in f.lower()]

        print(f"📁 Total files: {len(files)}")
        if cookies:
            print(f"🍪 Cookie files: {len(cookies)}")
        if logins:
            print(f"🔐 Auth files: {len(logins)}")

        print("\n🧪 Quick browser test...")
        try:
            model = ChatGPTWebModel(persistent_profile=True, headless=True)
            profile_path = model.get_browser_profile_path()
            model.reset_context()
            print(f"✅ Browser test OK - Profile: {profile_path}")
        except Exception as e:
            print(f"❌ Browser error: {e}")

    else:
        print("❌ No profile found.")
        print("Run setup before using automation.")

def main():
    """Main menu."""
    print("🔧 SWARMFORGE - BROWSER PROFILE SETUP")
    print("=" * 50)
    print("This tool configures the browser profile to maintain")
    print("AI service login sessions (ChatGPT, Gemini).")
    print()

    while True:
        print("\nCHOOSE AN OPTION:")
        print("1. 🔐 ChatGPT setup")
        print("2. 🌟 Gemini setup")
        print("3. 🚀 Full setup (All services)")
        print("4. 📊 Check profiles")
        print("5. 🗑️  Clear profiles")
        print("6. ❌ Exit")

        try:
            choice = input("\nChoice (1-6): ").strip()

            if choice == '1':
                setup_chatgpt()
            elif choice == '2':
                setup_gemini()
            elif choice == '3':
                setup_all()
            elif choice == '4':
                check_profiles()
            elif choice == '5':
                clear_profiles()
            elif choice == '6':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Try again.")

        except KeyboardInterrupt:
            print("\n\n👋 Setup interrupted by user.")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please retry or verify configuration.")

if __name__ == "__main__":
    main()