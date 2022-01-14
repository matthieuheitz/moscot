from abc import ABC, abstractmethod
from typing import Any, Union, Optional

import numpy.typing as npt

from moscot.tmp.solvers._data import Tag, TaggedArray
from moscot.tmp.solvers._output import BaseSolverOutput

ArrayLike = Union[npt.ArrayLike, TaggedArray]


class BaseSolver(ABC):
    @abstractmethod
    def _prepare_input(
        self,
        x: TaggedArray,
        y: Optional[TaggedArray] = None,
        a: npt.ArrayLike = None,
        b: npt.ArrayLike = None,
        **kwargs: Any,
    ) -> Any:
        pass

    @abstractmethod
    def _set_eps(self, data: Any, eps: Optional[float] = None) -> Any:
        pass

    @abstractmethod
    def _solve(self, data: Any, **kwargs: Any) -> BaseSolverOutput:
        pass

    def _check_marginals(self, output: BaseSolverOutput) -> None:
        # TODO(michalk8): implement me
        pass

    def __call__(
        self,
        x: ArrayLike,
        y: Optional[ArrayLike] = None,
        a: Optional[npt.ArrayLike] = None,
        b: Optional[npt.ArrayLike] = None,
        xx: Optional[ArrayLike] = None,
        yy: Optional[ArrayLike] = None,
        eps: Optional[float] = None,
        tau_a: Optional[float] = 1.0,
        tau_b: Optional[float] = 1.0,
        **kwargs: Any,
    ) -> BaseSolverOutput:
        def to_tagged_array(arr: Optional[ArrayLike], tag: Tag) -> Optional[TaggedArray]:
            if arr is None:
                return None
            tag = Tag(tag)
            if not isinstance(arr, TaggedArray):
                return TaggedArray(arr, tag=tag)
            # force new tag
            return TaggedArray(arr.data, tag=tag)
        if not isinstance(x, TaggedArray):  # currently we don't provide x_tag as kwarg, hence we would always convert tags here
            x = to_tagged_array(x, kwargs.pop("x_tag", Tag.POINT_CLOUD))
        if not isinstance(x, TaggedArray):
            y = to_tagged_array(y, kwargs.pop("y_tag", Tag.POINT_CLOUD))
        if not isinstance(x, TaggedArray):
            xx = to_tagged_array(xx, kwargs.pop("xx_tag", Tag.COST_MATRIX) if yy is None else Tag.POINT_CLOUD)
        if not isinstance(x, TaggedArray):
            yy = to_tagged_array(yy, kwargs.pop("yy_tag", Tag.POINT_CLOUD))

        # TODO(michalk8): create TaggedArray here if not passed, taking x_tag/y_tag/xy_tag from kwargs
        # TODO(michak8): filter kwargs
        data = self._prepare_input(x, y, a, b, xx=xx, yy=yy, tau_a=tau_a, tau_b=tau_b)
        data = self._set_eps(data, eps)
        res = self._solve(data, **kwargs)
        self._check_marginals(res)
        return res
