import typing
from functools import wraps

import pandas as pd
import numpy as np
from sklearn.datasets import load_breast_cancer, load_digits, load_iris, load_diabetes
from sklearn.model_selection import train_test_split


def serialize_to_csv_formatted_bytes(
    data: typing.Union[pd.DataFrame, pd.Series, np.ndarray],
) -> bytes:
    if type(data) not in [pd.DataFrame, pd.Series, np.ndarray]:
        raise TypeError(f"({type(data)}) is not supported for serialization")

    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)

    # data is now of type pd.DataFrame
    csv_bytes = data.to_csv(index=False).encode("utf-8")

    return csv_bytes


FileName = str
FileContent = bytes
FileUpload = typing.Tuple[FileName, FileContent]


def to_httpx_post_file_format(file_uploads: typing.List[FileUpload]) -> typing.Dict:
    ret = {}
    for file_category, filename, content in file_uploads:
        ret[file_category] = (filename, content)

    return ret


def to_oauth_request_form(username: str, password: str) -> {}:
    return {"grant_type": "password", "username": username, "password": password}


# implement singleton by decorator
def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    cls.delete_instance = lambda self: instances.pop(cls, None)

    return get_instance


def get_example_dataset(
    dataset_name: typing.Literal["iris", "breast_cancer", "digits", "diabetes"],
) -> typing.Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    load_dataset_fn = {
        "iris": load_iris,
        "breast_cancer": load_breast_cancer,
        "digits": load_digits,
        "diabetes": load_diabetes,
    }
    x_train, y_train = load_dataset_fn[dataset_name](return_X_y=True, as_frame=True)

    # shuffle and get 10 examples
    # shuffle is needed because we will might get examples with only 1 class
    indices = np.random.permutation(len(x_train))[:10]
    x_train = x_train.iloc[indices]
    y_train = y_train.iloc[indices]

    x_train, x_test, y_train, y_test = train_test_split(
        x_train, y_train, test_size=0.33, random_state=42
    )

    return x_train, x_test, y_train, y_test


def get_dataset_with_specific_size(
    num_examples: int = 10_000, num_columns: int = 100
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    x_train = np.random.RandomState(42).rand(num_examples, num_columns)
    y_train = np.random.RandomState(42).randint(0, 2, size=num_examples)

    return x_train, x_train, y_train, y_train


def assert_y_pred_proba_is_valid(x_test, y_pred_proba):
    if isinstance(y_pred_proba, list):
        y_pred_proba = np.array(y_pred_proba)

    proba_shape = y_pred_proba.shape
    assert proba_shape[0] == len(x_test)
    assert proba_shape[1] >= 2
    assert np.allclose(y_pred_proba.sum(axis=1), np.ones(proba_shape[0]))
