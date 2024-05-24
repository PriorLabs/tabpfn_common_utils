from typing import Union

import numpy as np
import torch


class RegressionPredictResult:
    def __init__(self, res: {}):
        self.mean = res["mean"]
        self.median = res["median"]
        self.mode = res["mode"]
        self.quantiles = {k: v for k, v in res.items() if k.startswith("quantile_")}

        # assume values are either all numpy arrays or all torch tensors
        if isinstance(self.mean, torch.Tensor):
            self._val_type = torch.Tensor
        elif isinstance(self.mean, np.ndarray):
            self._val_type = np.ndarray
        elif isinstance(self.mean, list):
            self._val_type = list
        else:
            raise ValueError(f"Invalid type for mean: {type(self.mean)}")

        # assert all values are of the same type
        for val in [self.mean, self.median, self.mode, *self.quantiles.values()]:
            assert isinstance(val, self._val_type)

    @property
    def val_type(self):
        return self._val_type

    @staticmethod
    def to_basic_representation(res: "RegressionPredictResult") -> dict[str, list]:
        if res.val_type == list:
            return res

        if res.val_type == torch.Tensor:
            serialize_fn = torch.Tensor.tolist
        else:
            serialize_fn = np.ndarray.tolist

        return {
            "mean": serialize_fn(res.mean),
            "median": serialize_fn(res.median),
            "mode": serialize_fn(res.mode),
            **{k: serialize_fn(v) for k, v in res.quantiles.items()},
        }

    @staticmethod
    def from_basic_representation(
        basic_repr: dict[str, list],
        output_val_type: Union[np.ndarray, torch.Tensor]
    ) -> dict[str, Union[np.ndarray, torch.Tensor]]:

        if output_val_type == torch.Tensor:
            deserialize_fn = torch.tensor
        else:
            deserialize_fn = np.array

        return {
            "mean": deserialize_fn(basic_repr["mean"]),
            "median": deserialize_fn(basic_repr["median"]),
            "mode": deserialize_fn(basic_repr["mode"]),
            **{
                k: deserialize_fn(v)
                for k, v in basic_repr.items()
                if k.startswith("quantile_")
            },
        }
