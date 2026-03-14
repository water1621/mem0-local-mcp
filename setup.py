#!/usr/bin/env python3
"""Setup script for Mem0 Local MCP Server."""
import os
import sys
from pathlib import Path


def main():
    """Run setup."""
    print("🧠 Mem0 Local MCP Server Setup")
    print("=" * 40)
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    # Step 1: Check Python version
    print("\n📋 Checking Python version...")
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Step 2: Install dependencies
    print("\n📦 Installing dependencies...")
    os.system(f'"{sys.executable}" -m pip install -r requirements.txt')
    
    # Step 3: Create config file if not exists
    config_file = script_dir / "config.yaml"
    config_example = script_dir / "config.example.yaml"
    
    if not config_file.exists():
        if config_example.exists():
            print("\n📝 Creating config.yaml from template...")
            import shutil
            shutil.copy(config_example, config_file)
            print(f"✅ Created: {config_file}")
            print("\n⚠️  Please edit config.yaml and add your API keys!")
        else:
            print("\n⚠️  config.example.yaml not found, please create config.yaml manually")
    else:
        print(f"\n✅ Config file exists: {config_file}")
    
    # Step 4: Create data directory
    data_dir = script_dir / "data"
    if not data_dir.exists():
        print("\n📁 Creating data directory...")
        data_dir.mkdir()
        print(f"✅ Created: {data_dir}")
    
    # Step 5: Print next steps
    print("\n" + "=" * 40)
    print("✅ Setup complete!")
    print("\n📌 Next steps:")
    print(f"   1. Edit config.yaml: {'notepad' if sys.platform == 'win32' else 'nano'} {config_file}")
    print("   2. Add your LLM API key and Embedding API key")
    print("   3. Run: python server.py")
    print("\n📚 Documentation: README.md")


if __name__ == "__main__":
    main()