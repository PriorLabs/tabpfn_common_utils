import numpy as np
import torch


class RegressionPredictResult:
    def __init__(self, res: {}):
        # res:
        # {
        #   criterion <class 'tabpfn.model.bar_distribution.FullSupportBarDistribution'>
        #   mean <class 'numpy.ndarray'>
        #   median <class 'numpy.ndarray'>
        #   mode <class 'numpy.ndarray'>
        #   logits <class 'numpy.ndarray'>
        #   buckets <class 'numpy.ndarray'>
        #   quantile_0.10 <class 'numpy.ndarray'>
        #   quantile_0.20 <class 'numpy.ndarray'>
        #   quantile_0.30 <class 'numpy.ndarray'>
        #   quantile_0.40 <class 'numpy.ndarray'>
        #   quantile_0.50 <class 'numpy.ndarray'>
        #   quantile_0.60 <class 'numpy.ndarray'>
        #   quantile_0.70 <class 'numpy.ndarray'>
        #   quantile_0.80 <class 'numpy.ndarray'>
        #   quantile_0.90 <class 'numpy.ndarray'>
        # }

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
    def serialize(res: "RegressionPredictResult") -> {str: list}:
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
            **{k: serialize_fn(v) for k, v in res.quantiles.items()}
        }

    @staticmethod
    def deserialize(
            serialized: {str: list},
            output_val_type: [np.ndarray, torch.Tensor]
    ) -> {str, np.ndarray | torch.Tensor}:
        if output_val_type == torch.Tensor:
            deserialize_fn = torch.tensor
        else:
            deserialize_fn = np.array

        return {
            "mean": deserialize_fn(serialized["mean"]),
            "median": deserialize_fn(serialized["median"]),
            "mode": deserialize_fn(serialized["mode"]),
            **{
                k: deserialize_fn(v)
                for k, v in serialized.items() if k.startswith("quantile_")
            }
        }
