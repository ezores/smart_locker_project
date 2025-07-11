import os
import sys

import pytest

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_import_app():
    """Test that the main app can be imported"""
    try:
        from app import app

        assert app is not None
        print("App import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import app: {e}")


def test_import_models():
    """Test that models can be imported"""
    try:
        from models import init_models

        assert init_models is not None
        print("Models import successful")
    except ImportError as e:
        pytest.fail(f"Failed to import models: {e}")


def test_basic_math():
    """Basic test to ensure pytest is working"""
    assert 2 + 2 == 4
    assert 3 * 3 == 9
    print("Basic math test passed")


def test_string_operations():
    """Test string operations"""
    test_string = "Smart Locker"
    assert len(test_string) == 12
    assert "Smart" in test_string
    assert "Locker" in test_string
    print("String operations test passed")


if __name__ == "__main__":
    # Run tests if executed directly
    test_import_app()
    test_import_models()
    test_basic_math()
    test_string_operations()
    print("All basic tests passed!")
