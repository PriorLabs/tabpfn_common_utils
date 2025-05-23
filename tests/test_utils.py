import unittest
from io import BytesIO

import numpy as np
import pandas as pd

from tabpfn_common_utils.utils import (
    serialize_to_csv_formatted_bytes,
    assert_y_pred_proba_is_valid,
)


class TestDataSerialization(unittest.TestCase):
    def test_serialize_numpy_array_to_csv_formatted_bytes(self):
        test_data = np.array([[1, 2, 3], [4, 5, 6]])
        test_pd_data = pd.DataFrame(test_data, columns=["0", "1", "2"])
        csv_bytes = serialize_to_csv_formatted_bytes(test_data)
        data_recovered = pd.read_csv(BytesIO(csv_bytes), delimiter=",")
        pd.testing.assert_frame_equal(test_pd_data, data_recovered)

    def test_serialize_pandas_dataframe_to_csv_formatted_bytes(self):
        test_data = pd.DataFrame([[1, 2, 3], [4, 5, 6]], columns=["a", "b", "c"])
        csv_bytes = serialize_to_csv_formatted_bytes(test_data)
        data_recovered = pd.read_csv(BytesIO(csv_bytes), delimiter=",")
        pd.testing.assert_frame_equal(test_data, data_recovered)


class TestAssertYPredProbaIsValid(unittest.TestCase):
    x_test = pd.DataFrame([[1, 2, 3], [4, 5, 6]])

    def test_valid_y_pred_proba_assert_true(self):
        y_pred = np.array([[0.1, 0.2, 0.7], [0.3, 0.4, 0.3]])
        assert_y_pred_proba_is_valid(self.x_test, y_pred)

    def test_invalid_shape_assert_false(self):
        y_pred = np.array([1, 2, 3])
        with self.assertRaises(AssertionError):
            assert_y_pred_proba_is_valid(self.x_test, y_pred)

    def test_invalid_value_assert_false(self):
        y_pred = np.array([[0.1, 0.2, 0.6], [0.3, 0.4, 0.3]])
        with self.assertRaises(AssertionError):
            assert_y_pred_proba_is_valid(self.x_test, y_pred)
