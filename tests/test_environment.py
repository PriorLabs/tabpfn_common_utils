import unittest

from tabpfn_common_utils.environment import Environment


class TestEnvironment(unittest.TestCase):

    def tearDown(self):
        Environment.reset()

    def test_create_duplicate_instance_should_return_existing_instance(self):
        Environment.init(mode="dev")
        Environment.add_property(a=1, b=2)

        Environment.init(mode="dev")
        Environment.add_property(c=3, d=4)

        self.assertEqual(Environment.get_property(), {"mode": "dev", "a": 1, "b": 2, "c": 3, "d": 4})

    def test_create_different_instances_should_raise_error(self):
        Environment.init(mode="dev")

        with self.assertRaises(RuntimeError):
            Environment.init(mode="test")

    def test_delete_instance_should_delete_existing_instance(self):
        Environment.init(mode="dev")
        Environment.add_property(a=1, b=2)

        Environment.reset()
        with self.assertRaises(RuntimeError):
            Environment.get_property()

    def test_delete_instance_when_no_existing_instance_does_not_raise_error(self):
        Environment.reset()

    def test_add_properties_should_add_properties_to_existing_instance(self):
        Environment.init(mode="dev")
        Environment.add_property(a=1, b=2)

        self.assertEqual(Environment.get_property(), {"mode": "dev", "a": 1, "b": 2})

    def test_add_properties_to_deleted_instance_should_raise_error(self):
        Environment.init(mode="dev")
        Environment.add_property(a=1, b=2)
        Environment.reset()

        with self.assertRaises(RuntimeError):
            Environment.add_property(c=3, d=4)
