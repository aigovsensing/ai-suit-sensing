import os
import sys

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import debug_log

def test_debug_log():
    print("Testing debug_log with DEBUG=1")
    os.environ["DEBUG"] = "1"
    debug_log("This should be visible")
    
    print("\nTesting debug_log with DEBUG=0")
    os.environ["DEBUG"] = "0"
    debug_log("This should NOT be visible")

def test_imports():
    print("\nTesting imports of modified files")
    try:
        from src import run
        from src import courtlistener
        print("✅ Imports successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")

if __name__ == "__main__":
    test_debug_log()
    test_imports()
