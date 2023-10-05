import typing
from functools import wraps

import pandas as pd
import numpy as np
import torch
from sklearn.datasets import load_breast_cancer, load_digits, load_iris
from sklearn.model_selection import train_test_split


def serialize_to_csv_formatted_bytes(data: typing.Union[pd.DataFrame, np.ndarray, torch.Tensor]) -> bytes:
    if type(data) not in [pd.DataFrame, np.ndarray, torch.Tensor]:
        raise TypeError(f"({type(data)}) is not supported for serialization")

    if isinstance(data, torch.Tensor):
        data = data.numpy()

    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)

    # data is now of type pd.DataFrame
    csv_bytes = data.to_csv(index=False).encode('utf-8')

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
    return {
        "grant_type": "password",
        "username": username,
        "password": password
    }


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


def get_example_dataset(dataset_name: typing.Literal["iris", "breast_cancer", "digits"]) \
        -> typing.Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    load_dataset_fn = {
        "iris": load_iris,
        "breast_cancer": load_breast_cancer,
        "digits": load_digits,
    }
    x_train, y_train = load_dataset_fn[dataset_name](return_X_y=True)
    x_train, x_test, y_train, y_test = train_test_split(x_train, y_train, test_size=0.33, random_state=42)

    return x_train, x_test, y_train, y_test
