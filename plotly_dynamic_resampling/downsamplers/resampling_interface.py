"""AbstractSeriesDownsampler interface-class, subclassed by concrete downsamplers."""

__author__ = 'Jonas Van Der Donckt'

import re
from abc import ABC, abstractmethod
from typing import List

import pandas as pd


class AbstractSeriesDownsampler(ABC):
    def __init__(
            self,
            interleave_gaps: bool = True,
            dtype_regex_list: List[str] = None
    ) -> None:
        self.interleave_gaps = interleave_gaps
        self.dtype_regex_list = dtype_regex_list
        self.max_gap_q = 0.95
        super().__init__()

    @abstractmethod
    def _downsample(self, s: pd.Series, n_out: int) -> pd.Series:
        pass

    def _supports_dtype(self, s: pd.Series):
        # base case
        if self.dtype_regex_list is None:
            return

        for dtype_regex_str in self.dtype_regex_list:
            m = re.compile(dtype_regex_str).match(str(s.dtype))
            if m is not None:  # a match is found
                return
        raise ValueError(
            f"{s.dtype} doesn't match with any regex in {self.dtype_regex_list}"
        )

    def _interleave_gaps_none(self, s: pd.Series):
        # ------- add None where there are gaps / irregularly sampled data
        if isinstance(s.index, pd.DatetimeIndex):
            series_index_diff = s.index.to_series().diff().dt.total_seconds()
        else:
            series_index_diff = s.index.to_series().diff()

        # use a quantile based approach
        min_diff, max_gap_q_s = series_index_diff.quantile(q=[0, self.max_gap_q])

        # add None data-points in between the gaps
        if min_diff is not None and max_gap_q_s is not None:
            df_res_gap = s.loc[series_index_diff > max_gap_q_s].copy()
            if len(df_res_gap):
                df_res_gap.loc[:] = None
                if isinstance(s.index, pd.DatetimeIndex):
                    df_res_gap.index -= pd.Timedelta(seconds=min_diff / 2)
                else:
                    df_res_gap.index -= (min_diff / 2)
                index_name = s.index.name
                return pd.concat(
                    [s.reset_index(drop=False), df_res_gap.reset_index(drop=False)]
                ).set_index(index_name).sort_index().iloc[:, 0]
        return s

    def downsample(self, s: pd.Series, n_out: int) -> pd.Series:
        # base case: the passed series is empty
        if s.empty:
            return s

        self._supports_dtype(s)

        if len(s) > n_out:
            s = self._downsample(s, n_out=n_out)

        if self.interleave_gaps:
            s = self._interleave_gaps_none(s)

        return s
