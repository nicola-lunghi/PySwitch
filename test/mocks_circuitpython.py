import sys
from unittest.mock import MagicMock

# Mock the 'board' module
sys.modules['board'] = MagicMock()
