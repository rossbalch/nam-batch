# File: data.py
# Created Date: Saturday February 5th 2022
# Author: Steven Atkinson (steven@atkinson.mn)

import abc
from collections import namedtuple
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Sequence, Tuple, Union

import numpy as np
import torch
import wavio
from scipy.interpolate import interp1d
from torch.utils.data import Dataset as _Dataset
from tqdm import tqdm

_REQUIRED_SAMPWIDTH = 3
REQUIRED_RATE = 48_000
_REQUIRED_CHANNELS = 1  # Mono


class Split(Enum):
    TRAIN = "train"
    VALIDATION = "validation"


@dataclass
class WavInfo:
    sampwidth: int
    rate: int


class AudioShapeMismatchError(ValueError):
    """
    Exception where the shape (number of samples, number of channels) of two audio files
    don't match but were supposed to.
    """

    def __init__(self, shape_expected, shape_actual, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._shape_expected = shape_expected
        self._shape_actual = shape_actual

    @property
    def shape_expected(self):
        return self._shape_expected

    @property
    def shape_actual(self):
        return self._shape_actual


def wav_to_np(
    filename: Union[str, Path],
    rate: Optional[int] = REQUIRED_RATE,
    require_match: Optional[Union[str, Path]] = None,
    required_shape: Optional[Tuple[int]] = None,
    required_wavinfo: Optional[WavInfo] = None,
    preroll: Optional[int] = None,
    info: bool = False,
) -> Union[np.ndarray, Tuple[np.ndarray, WavInfo]]:
    """
    :param preroll: Drop this many samples off the front
    """
    x_wav = wavio.read(str(filename))
    assert x_wav.data.shape[1] == _REQUIRED_CHANNELS, "Mono"
    assert x_wav.sampwidth == _REQUIRED_SAMPWIDTH, "24-bit"
    if rate is not None and x_wav.rate != rate:
        raise RuntimeError(
            f"Explicitly expected sample rate of {rate}, but found {x_wav.rate} in "
            f"file {filename}!"
        )

    if require_match is not None:
        assert required_shape is None
        assert required_wavinfo is None
        y_wav = wavio.read(str(require_match))
        required_shape = y_wav.data.shape
        required_wavinfo = WavInfo(y_wav.sampwidth, y_wav.rate)
    if required_wavinfo is not None:
        if x_wav.rate != required_wavinfo.rate:
            raise ValueError(
                f"Mismatched rates {x_wav.rate} versus {required_wavinfo.rate}"
            )
    arr_premono = x_wav.data[preroll:] / (2.0 ** (8 * x_wav.sampwidth - 1))
    if required_shape is not None:
        if arr_premono.shape != required_shape:
            raise AudioShapeMismatchError(
                arr_premono.shape,
                required_shape,
                f"Mismatched shapes. Expected {required_shape}, but this is "
                f"{arr_premono.shape}!",
            )
        # sampwidth fine--we're just casting to 32-bit float anyways
    arr = arr_premono[:, 0]
    return arr if not info else (arr, WavInfo(x_wav.sampwidth, x_wav.rate))


def wav_to_tensor(
    *args, info: bool = False, **kwargs
) -> Union[torch.Tensor, Tuple[torch.Tensor, WavInfo]]:
    out = wav_to_np(*args, info=info, **kwargs)
    if info:
        arr, info = out
        return torch.Tensor(arr), info
    else:
        arr = out
        return torch.Tensor(arr)


def tensor_to_wav(x: torch.Tensor, *args, **kwargs):
    np_to_wav(x.detach().cpu().numpy(), *args, **kwargs)


def np_to_wav(
    x: np.ndarray,
    filename: Union[str, Path],
    rate: int = 48_000,
    sampwidth: int = 3,
    scale="none",
):
    wavio.write(
        str(filename),
        (np.clip(x, -1.0, 1.0) * (2 ** (8 * sampwidth - 1))).astype(np.int32),
        rate,
        scale=scale,
        sampwidth=sampwidth,
    )


class AbstractDataset(_Dataset, abc.ABC):
    @abc.abstractmethod
    def __getitem__(
        self, idx: int
    ) -> Union[
        Tuple[torch.Tensor, torch.Tensor],
        Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    ]:
        """
        :return:
            Case 1: Input (N1,), Output (N2,)
            Case 2: Parameters (D,), Input (N1,), Output (N2,)
        """
        pass


class _DelayInterpolationMethod(Enum):
    """
    :param LINEAR: Linear interpolation
    :param CUBIC: Cubic spline interpolation
    """

    # Note: these match scipy.interpolate.interp1d kwarg "kind"
    LINEAR = "linear"
    CUBIC = "cubic"


def _interpolate_delay(
    x: torch.Tensor, delay: float, method: _DelayInterpolationMethod
) -> np.ndarray:
    """
    NOTE: This breaks the gradient tape!
    """
    if delay == 0.0:
        return x
    t_in = np.arange(len(x))
    n_out = len(x) - int(np.ceil(np.abs(delay)))
    if delay > 0:
        t_out = np.arange(n_out) + delay
    elif delay < 0:
        t_out = np.arange(len(x) - n_out, len(x)) - np.abs(delay)

    return torch.Tensor(
        interp1d(t_in, x.detach().cpu().numpy(), kind=method.value)(t_out)
    )


class XYError(ValueError):
    """
    Exceptions related to invalid x and y provided for data sets
    """

    pass


class StartStopError(ValueError):
    """
    Exceptions related to invalid start and stop arguments
    """

    pass


class StartError(StartStopError):
    pass


class StopError(StartStopError):
    pass
