import os, sys
# Add project root (parent of tests/) to Python path so "import analysis" works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
