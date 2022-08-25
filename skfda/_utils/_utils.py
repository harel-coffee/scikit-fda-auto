"""Module with generic methods."""

from __future__ import annotations

import functools
import numbers
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
    overload,
)

import numpy as np
import scipy.integrate
from numpy import ndarray
from pandas.api.indexers import check_array_indexer
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.multiclass import check_classification_targets
from typing_extensions import Literal, Protocol

from ..representation._typing import (
    ArrayLike,
    DomainRange,
    DomainRangeLike,
    GridPoints,
    GridPointsLike,
    NDArrayAny,
    NDArrayFloat,
    NDArrayInt,
    NDArrayObject,
)
from ..representation.extrapolation import ExtrapolationLike

RandomStateLike = Optional[Union[int, np.random.RandomState]]

ArrayT = TypeVar("ArrayT", bound=NDArrayAny)

if TYPE_CHECKING:
    from ..representation import FData, FDataGrid
    from ..representation.basis import Basis
    T = TypeVar("T", bound=FData)

    Input = TypeVar("Input", bound=Union[FData, NDArrayFloat])
    Output = TypeVar("Output", bound=Union[FData, NDArrayFloat])
    Target = TypeVar("Target", bound=NDArrayInt)


def _to_grid(
    X: FData,
    y: FData,
    eval_points: Optional[NDArrayFloat] = None,
) -> Tuple[FDataGrid, FDataGrid]:
    """Transform a pair of FDatas in grids to perform calculations."""
    from .. import FDataGrid
    x_is_grid = isinstance(X, FDataGrid)
    y_is_grid = isinstance(y, FDataGrid)

    if eval_points is not None:
        X = X.to_grid(eval_points)
        y = y.to_grid(eval_points)
    elif x_is_grid and not y_is_grid:
        y = y.to_grid(X.grid_points[0])
    elif not x_is_grid and y_is_grid:
        X = X.to_grid(y.grid_points[0])
    elif not x_is_grid and not y_is_grid:
        X = X.to_grid()
        y = y.to_grid()

    return X, y


def _to_grid_points(grid_points_like: GridPointsLike) -> GridPoints:
    """Convert to grid points.

    If the original list is one-dimensional (e.g. [1, 2, 3]), return list to
    array (in this case [array([1, 2, 3])]).

    If the original list is two-dimensional (e.g. [[1, 2, 3], [4, 5]]), return
    a list containing other one-dimensional arrays (in this case
    [array([1, 2, 3]), array([4, 5])]).

    In any other case the behaviour is unespecified.

    """
    unidimensional = False

    if not isinstance(grid_points_like, Iterable):
        grid_points_like = [grid_points_like]

    if not isinstance(grid_points_like[0], Iterable):
        unidimensional = True

    if unidimensional:
        return (_int_to_real(np.asarray(grid_points_like)),)

    return tuple(_int_to_real(np.asarray(i)) for i in grid_points_like)


def _to_domain_range(sequence: DomainRangeLike) -> DomainRange:
    """Convert sequence to a proper domain range."""
    seq_aux = cast(
        Sequence[Sequence[float]],
        (sequence,) if isinstance(sequence[0], numbers.Real) else sequence,
    )

    tuple_aux = tuple(tuple(s) for s in seq_aux)

    if not all(len(s) == 2 and s[0] <= s[1] for s in tuple_aux):
        raise ValueError(
            "Domain intervals should have 2 bounds for "
            "dimension: (lower, upper).",
        )

    return cast(DomainRange, tuple_aux)


@overload
def _cartesian_product(
    axes: Sequence[ArrayT],
    *,
    flatten: bool = True,
    return_shape: Literal[False] = False,
) -> ArrayT:
    pass


@overload
def _cartesian_product(
    axes: Sequence[ArrayT],
    *,
    flatten: bool = True,
    return_shape: Literal[True],
) -> Tuple[ArrayT, Tuple[int, ...]]:
    pass


def _cartesian_product(  # noqa: WPS234
    axes: Sequence[ArrayT],
    *,
    flatten: bool = True,
    return_shape: bool = False,
) -> Union[ArrayT, Tuple[ArrayT, Tuple[int, ...]]]:
    """
    Compute the cartesian product of the axes.

    Computes the cartesian product of the axes and returns a numpy array of
    1 dimension with all the possible combinations, for an arbitrary number of
    dimensions.

    Args:
        axes: List with axes.
        flatten: Whether to return the flatten array or keep one dimension per
            axis.
        return_shape: If ``True`` return the shape of the array before
            flattening.

    Returns:
        Numpy 2-D array with all the possible combinations.
        The entry (i,j) represent the j-th coordinate of the i-th point.
        If ``return_shape`` is ``True`` returns also the shape of the array
        before flattening.

    Examples:
        >>> from skfda._utils import _cartesian_product
        >>> axes = [[0,1],[2,3]]
        >>> _cartesian_product(axes)
        array([[0, 2],
               [0, 3],
               [1, 2],
               [1, 3]])

        >>> axes = [[0,1],[2,3],[4]]
        >>> _cartesian_product(axes)
        array([[0, 2, 4],
               [0, 3, 4],
               [1, 2, 4],
               [1, 3, 4]])

        >>> axes = [[0,1]]
        >>> _cartesian_product(axes)
        array([[0],
               [1]])
    """
    cartesian = np.stack(np.meshgrid(*axes, indexing='ij'), -1)

    shape = cartesian.shape

    if flatten:
        cartesian = cartesian.reshape(-1, len(axes))

    if return_shape:
        return cartesian, shape

    return cartesian  # type: ignore[no-any-return]


def _same_domain(fd: Union[Basis, FData], fd2: Union[Basis, FData]) -> bool:
    """Check if the domain range of two objects is the same."""
    return np.array_equal(fd.domain_range, fd2.domain_range)


@overload
def _reshape_eval_points(
    eval_points: ArrayLike,
    *,
    aligned: Literal[True],
    n_samples: int,
    dim_domain: int,
) -> NDArrayFloat:
    pass


@overload
def _reshape_eval_points(
    eval_points: Sequence[ArrayLike],
    *,
    aligned: Literal[False],
    n_samples: int,
    dim_domain: int,
) -> NDArrayFloat | NDArrayObject:
    pass


@overload
def _reshape_eval_points(
    eval_points: Union[ArrayLike, Sequence[ArrayLike]],
    *,
    aligned: bool,
    n_samples: int,
    dim_domain: int,
) -> NDArrayFloat | NDArrayObject:
    pass


def _reshape_eval_points(
    eval_points: ArrayLike,
    *,
    aligned: bool,
    n_samples: int,
    dim_domain: int,
) -> NDArrayFloat | NDArrayObject:
    """Convert and reshape the eval_points to ndarray.

    Args:
        eval_points: Evaluation points to be reshaped.
        aligned: Boolean flag. True if all the samples
            will be evaluated at the same evaluation_points.
        n_samples: Number of observations.
        dim_domain: Dimension of the domain.

    Returns:
        Numpy array with the eval_points, if
        evaluation_aligned is True with shape `number of evaluation points`
        x `dim_domain`. If the points are not aligned the shape of the
        points will be `n_samples` x `number of evaluation points`
        x `dim_domain`.

    """
    if aligned:
        eval_points = np.asarray(eval_points)
    else:
        eval_points = np.asarray(eval_points)
        eval_points = eval_points.reshape(
            (eval_points.shape[0], -1, dim_domain),
        )

    # Case evaluation of a single value, i.e., f(0)
    # Only allowed for aligned evaluation
    if aligned and (
        eval_points.shape == (dim_domain,)
        or (eval_points.ndim == 0 and dim_domain == 1)
    ):
        eval_points = np.array([eval_points])

    if aligned:  # Samples evaluated at same eval points
        eval_points = eval_points.reshape(
            (eval_points.shape[0], dim_domain),
        )

    else:  # Different eval_points for each sample

        if eval_points.shape[0] != n_samples:
            raise ValueError(
                f"eval_points should be a list "
                f"of length {n_samples} with the "
                f"evaluation points for each sample.",
            )

    return eval_points


def _one_grid_to_points(
    axes: GridPointsLike,
    *,
    dim_domain: int,
) -> Tuple[NDArrayFloat, Tuple[int, ...]]:
    """
    Convert a list of ndarrays, one per domain dimension, in the points.

    Returns also the shape containing the information of how each point
    is formed.
    """
    axes = _to_grid_points(axes)

    if len(axes) != dim_domain:
        raise ValueError(
            f"Length of axes should be {dim_domain}",
        )

    cartesian, shape = _cartesian_product(axes, return_shape=True)

    # Drop domain size dimension, as it is not needed to reshape the output
    shape = shape[:-1]

    return cartesian, shape


class EvaluateMethod(Protocol):
    """Evaluation method."""

    def __call__(
        self,
        __eval_points: NDArrayFloat,  # noqa: WPS112
        extrapolation: Optional[ExtrapolationLike],
        aligned: bool,
    ) -> NDArrayFloat:
        """Evaluate a function."""
        pass


@overload
def _evaluate_grid(
    axes: GridPointsLike,
    *,
    evaluate_method: EvaluateMethod,
    n_samples: int,
    dim_domain: int,
    dim_codomain: int,
    extrapolation: Optional[ExtrapolationLike] = None,
    aligned: Literal[True] = True,
) -> NDArrayFloat:
    pass


@overload
def _evaluate_grid(
    axes: Iterable[GridPointsLike],
    *,
    evaluate_method: EvaluateMethod,
    n_samples: int,
    dim_domain: int,
    dim_codomain: int,
    extrapolation: Optional[ExtrapolationLike] = None,
    aligned: Literal[False],
) -> NDArrayFloat | NDArrayObject:
    pass


@overload
def _evaluate_grid(
    axes: Union[GridPointsLike, Iterable[GridPointsLike]],
    *,
    evaluate_method: EvaluateMethod,
    n_samples: int,
    dim_domain: int,
    dim_codomain: int,
    extrapolation: Optional[ExtrapolationLike] = None,
    aligned: bool,
) -> NDArrayFloat | NDArrayObject:
    pass


def _evaluate_grid(  # noqa: WPS234
    axes: Union[GridPointsLike, Iterable[GridPointsLike]],
    *,
    evaluate_method: EvaluateMethod,
    n_samples: int,
    dim_domain: int,
    dim_codomain: int,
    extrapolation: Optional[ExtrapolationLike] = None,
    aligned: bool = True,
) -> NDArrayFloat | NDArrayObject:
    """
    Evaluate the functional object in the cartesian grid.

    This method is called internally by :meth:`evaluate` when the argument
    `grid` is True.

    Evaluates the functional object in the grid generated by the cartesian
    product of the axes. The length of the list of axes should be equal
    than the domain dimension of the object.

    If the list of axes has lengths :math:`n_1, n_2, ..., n_m`, where
    :math:`m` is equal than the dimension of the domain, the result of the
    evaluation in the grid will be a matrix with :math:`m+1` dimensions and
    shape :math:`n_{samples} x n_1 x n_2 x ... x n_m`.

    If `aligned` is false each sample is evaluated in a
    different grid, and the list of axes should contain a list of axes for
    each sample.

    If the domain dimension is 1, the result of the behaviour of the
    evaluation will be the same than :meth:`evaluate` without the grid
    option, but with worst performance.

    Args:
        axes: List of axes to generated the grid where the
            object will be evaluated.
        evaluate_method: Function used to evaluate the functional object.
        n_samples: Number of samples.
        dim_domain: Domain dimension.
        dim_codomain: Codomain dimension.
        extrapolation: Controls the
            extrapolation mode for elements outside the domain range. By
            default it is used the mode defined during the instance of the
            object.
        aligned: If False evaluates each sample
            in a different grid.
        evaluate_method: method to use to evaluate the points
        n_samples: number of samples
        dim_domain: dimension of the domain
        dim_codomain: dimensions of the codomain

    Returns:
        Numpy array with dim_domain + 1 dimensions with
            the result of the evaluation.

    Raises:
        ValueError: If there are a different number of axes than the domain
            dimension.

    """
    # Compute intersection points and resulting shapes
    if aligned:

        axes = cast(GridPointsLike, axes)

        eval_points, shape = _one_grid_to_points(axes, dim_domain=dim_domain)

    else:

        axes_per_sample = cast(Iterable[GridPointsLike], axes)

        axes_per_sample = list(axes_per_sample)

        eval_points_tuple, shape_tuple = zip(
            *[
                _one_grid_to_points(a, dim_domain=dim_domain)
                for a in axes_per_sample
            ],
        )

        if len(eval_points_tuple) != n_samples:
            raise ValueError(
                "Should be provided a list of axis per sample",
            )

        eval_points = np.asarray(eval_points_tuple)

    # Evaluate the points
    evaluated = evaluate_method(
        eval_points,
        extrapolation=extrapolation,
        aligned=aligned,
    )

    # Reshape the result
    if aligned:

        res = evaluated.reshape(
            [n_samples] + list(shape) + [dim_codomain],
        )

    else:

        res = np.asarray([
            r.reshape(list(s) + [dim_codomain])
            for r, s in zip(evaluated, shape_tuple)
        ])

    return res


def nquad_vec(
    func: Callable[[NDArrayFloat], NDArrayFloat],
    ranges: Sequence[Tuple[float, float]],
) -> NDArrayFloat:
    """Perform multiple integration of vector valued functions."""
    initial_depth = len(ranges) - 1

    def integrate(*args: Any, depth: int) -> NDArrayFloat:  # noqa: WPS430

        if depth == 0:
            f = functools.partial(func, *args)
        else:
            f = functools.partial(integrate, *args, depth=depth - 1)

        return scipy.integrate.quad_vec(  # type: ignore[no-any-return]
            f,
            *ranges[initial_depth - depth],
        )[0]

    return integrate(depth=initial_depth)


def _map_in_batches(
    function: Callable[..., ArrayT],
    arguments: Tuple[Union[FData, NDArrayAny], ...],
    indexes: Tuple[NDArrayInt, ...],
    memory_per_batch: Optional[int] = None,
    **kwargs: Any,
) -> ArrayT:
    """
    Map a function over samples of FData or ndarray tuples efficiently.

    This function prevents a large set of indexes to use all available
    memory and hang the PC.

    """
    if memory_per_batch is None:
        # 256MB is not too big
        memory_per_batch = 256 * 1024 * 1024  # noqa: WPS432

    memory_per_element = sum(a.nbytes // len(a) for a in arguments)
    n_elements_per_batch_allowed = memory_per_batch // memory_per_element
    if n_elements_per_batch_allowed < 1:
        raise ValueError("Too few memory allowed for the operation")

    n_indexes = len(indexes[0])

    assert all(n_indexes == len(i) for i in indexes)

    batches: List[ArrayT] = []

    for pos in range(0, n_indexes, n_elements_per_batch_allowed):
        batch_args = tuple(
            a[i[pos:pos + n_elements_per_batch_allowed]]
            for a, i in zip(arguments, indexes)
        )

        batches.append(function(*batch_args, **kwargs))

    return np.concatenate(batches, axis=0)  # type: ignore[return-value]


def _pairwise_symmetric(
    function: Callable[..., ArrayT],
    arg1: Union[FData, NDArrayAny],
    arg2: Optional[Union[FData, NDArrayAny]] = None,
    memory_per_batch: Optional[int] = None,
    **kwargs: Any,
) -> ArrayT:
    """Compute pairwise a commutative function."""
    dim1 = len(arg1)
    if arg2 is None or arg2 is arg1:
        indices = np.triu_indices(dim1)

        triang_vec = _map_in_batches(
            function,
            (arg1, arg1),
            indices,
            memory_per_batch=memory_per_batch,
            **kwargs,
        )

        matrix = np.empty((dim1, dim1), dtype=triang_vec.dtype)

        # Set upper matrix
        matrix[indices] = triang_vec

        # Set lower matrix
        matrix[(indices[1], indices[0])] = triang_vec

        return matrix

    dim2 = len(arg2)
    indices = np.indices((dim1, dim2))

    vec = _map_in_batches(
        function,
        (arg1, arg2),
        (indices[0].ravel(), indices[1].ravel()),
        memory_per_batch=memory_per_batch,
        **kwargs,
    )

    return vec.reshape((dim1, dim2))


def _int_to_real(array: Union[NDArrayInt, NDArrayFloat]) -> NDArrayFloat:
    """Convert integer arrays to floating point."""
    return array + 0.0


def _check_array_key(array: NDArrayAny, key: Any) -> Any:
    """Check a getitem key."""
    key = check_array_indexer(array, key)
    if isinstance(key, tuple):
        non_ellipsis = [i for i in key if i is not Ellipsis]
        if len(non_ellipsis) > 1:
            raise KeyError(key)
        key = non_ellipsis[0]

    if isinstance(key, numbers.Integral):  # To accept also numpy ints
        key = int(key)
        if key < 0:
            key = len(array) + key

        if not 0 <= key < len(array):
            raise IndexError("index out of bounds")

        return slice(key, key + 1)

    return key


def _check_estimator(estimator):
    from sklearn.utils.estimator_checks import (
        check_get_params_invariance,
        check_set_params,
    )

    name = estimator.__name__
    instance = estimator()
    check_get_params_invariance(name, instance)
    check_set_params(name, instance)


def _classifier_get_classes(y: ndarray) -> Tuple[ndarray, NDArrayInt]:

    check_classification_targets(y)

    le = LabelEncoder()
    y_ind = le.fit_transform(y)

    classes = le.classes_

    if classes.size < 2:
        raise ValueError(
            f'The number of classes has to be greater than'
            f'one; got {classes.size} class',
        )
    return classes, y_ind


_DependenceMeasure = Callable[[np.ndarray, np.ndarray], np.ndarray]


def _compute_dependence(
    X: NDArrayFloat,
    y: NDArrayFloat,
    *,
    dependence_measure: _DependenceMeasure,
) -> NDArrayFloat:
    """
    Compute dependence between points and target.

    Computes the dependence of each point in each trajectory in X with the
    corresponding class label in Y.

    """
    from dcor import rowwise

    # Move n_samples to the end
    # The shape is now input_shape + n_samples + n_output
    X = np.moveaxis(X, 0, -2)

    input_shape = X.shape[:-2]

    # Join input in a list for rowwise
    X = X.reshape(-1, X.shape[-2], X.shape[-1])

    if y.ndim == 1:
        y = np.atleast_2d(y).T
    Y = np.array([y] * len(X))

    dependence_results = rowwise(dependence_measure, X, Y)

    return dependence_results.reshape(  # type: ignore[no-any-return]
        input_shape,
    )
