import subprocess
import sys

def install_requirements():
    print("=" * 50)
    print("SteganoSuite - Installation")
    print("=" * 50)
    
    packages = [
        "pillow",
        "pycryptodome"
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✅ {package} installed successfully!")
        except Exception as e:
            print(f"❌ Failed to install {package}: {e}")
            print(f"   Try: pip install {package}")
    
    print("\n" + "=" * 50)
    print("✅ INSTALLATION COMPLETE!")
    print("\nRun: python main.py")
    print("=" * 50)

if __name__ == "__main__":
    install_requirements()