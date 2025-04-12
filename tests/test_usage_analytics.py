import unittest
from usage_analytics import get_calling_class


class TestGetCallingClass(unittest.TestCase):
    def test_standalone_function(self):
        """Test that standalone functions return 'StandaloneFunction'"""
        result = get_calling_class()
        self.assertEqual(result, "TestGetCallingClass")

    def test_direct_class_call(self):
        """Test direct class method call returns the correct class name"""

        class DirectCaller:
            def call_method(self):
                return get_calling_class()

        caller = DirectCaller()
        result = caller.call_method()
        self.assertEqual(result, "DirectCaller")

    def test_nested_class_call(self):
        """Test nested class method calls return the outermost caller"""

        class InnerCaller:
            def call_method(self):
                return get_calling_class()

        class OuterCaller:
            def __init__(self):
                self.inner = InnerCaller()

            def call_method(self):
                return self.inner.call_method()

        caller = OuterCaller()
        result = caller.call_method()
        self.assertEqual(result, "OuterCaller")

    def test_deeply_nested_call(self):
        """Test deeply nested class method calls return the outermost caller"""

        class Level3:
            def call_method(self):
                return get_calling_class()

        class Level2:
            def __init__(self):
                self.level3 = Level3()

            def call_method(self):
                return self.level3.call_method()

        class Level1:
            def __init__(self):
                self.level2 = Level2()

            def call_method(self):
                return self.level2.call_method()

        caller = Level1()
        result = caller.call_method()
        self.assertEqual(result, "Level1")

    def test_with_parameter(self):
        """Test that the recursive parameter works correctly"""

        class InnerCaller:
            def call_method(self):
                # With recursive=False, should return InnerCaller
                return get_calling_class(recursive=False)

        class OuterCaller:
            def __init__(self):
                self.inner = InnerCaller()

            def call_method(self):
                return self.inner.call_method()

        caller = OuterCaller()
        result = caller.call_method()
        self.assertEqual(result, "InnerCaller")


if __name__ == "__main__":
    unittest.main()
