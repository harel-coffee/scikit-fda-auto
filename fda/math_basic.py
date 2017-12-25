"""This module defines the basic mathematic operations for classes defined
in this package.

"""
from fda.FDataGrid import FDataGrid
import numpy
import scipy.stats.mstats
import scipy.integrate


__author__ = "Miguel Carbajo Berrocal"
__license__ = "GPL3"
__version__ = ""
__maintainer__ = ""
__email__ = ""
__status__ = "Development"


def mean(fdatagrid):
    """ Computes the mean of all the samples in a FDataGrid object.

    Args:
        fdatagrid (FDataGrid): Object containing all the samples whose mean
            is wanted.

    Returns:
        FDataGrid: A FDataGrid object with just one sample representing the
        mean of all the samples in the original FDataGrid object.

    """
    return FDataGrid([numpy.mean(fdatagrid.data_matrix, 0)],
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def var(fdatagrid):
    """ Computes the variance of a set of samples in a FDataGrid object.

    Args:
        fdatagrid (FDataGrid): Object containing all the set of samples
        whose variance is desired.

    Returns:
        FDataGrid: A FDataGrid object with just one sample representing the
        mean of all the samples in the original FDataGrid object.

    """
    return FDataGrid([numpy.var(fdatagrid.data_matrix, 0)],
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def gmean(fdatagrid):
    """ Computes the geometric mean of all the samples in a FDataGrid object.

    Args:
        fdatagrid (FDataGrid): Object containing all the samples whose
            geometric mean is wanted.

    Returns:
        FDataGrid: A FDataGrid object with just one sample representing the
        geometric mean of all the samples in the original FDataGrid object.

    """
    return FDataGrid([scipy.stats.mstats.gmean(fdatagrid.data_matrix, 0)],
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def cov(fdatagrid):
    """ Calculates the covariance matrix representing the covariance of the
    functional samples at the observation points.

    Args:
        fdatagrid (FDataGrid): Object containing different samples of a
        functional variable.

    Returns:
        numpy.darray: Matrix of covariances.

    """
    return numpy.cov(fdatagrid.data_matrix)


def sqrt(fdatagrid):
    """ Performs a element wise square root operation.

    Args:
        fdatagrid (FDataGrid): Object to whose elements the square root
            operation is going to be applied.

    Returns:
        FDataGrid: Object whose elements are the square roots of the original.

    """
    return FDataGrid(numpy.sqrt(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def absolute(fdatagrid):
    """ Gets the absolute value of all elements in the FDataGrid object.

    Args:
        fdatagrid (FDataGrid): Object from whose elements the absolute value
            is going to be retrieved.

    Returns:
        FDataGrid: Object whose elements are the absolute values of the
            original.

    """
    return FDataGrid(numpy.absolute(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def around(fdatagrid, decimals=0):
    """ Rounds all elements of the object.

    Args:
        fdatagrid (FDataGrid): Object to whose elements are going to be
            rounded.
        decimals (int, optional): Number of decimals wanted. Defaults to 0.

    Returns:
        FDataGrid: Object whose elements are rounded.

    """
    return FDataGrid(numpy.around(fdatagrid.data_matrix, decimals),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def exp(fdatagrid):
    """ Performs a element wise exponential operation.

    Args:
        fdatagrid (FDataGrid): Object to whose elements the exponential
            operation is going to be applied.

    Returns:
        FDataGrid: Object whose elements are the result of exponentiating
            the elements of the original.

    """
    return FDataGrid(numpy.exp(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def log(fdatagrid):
    """ Performs a element wise logarithm operation.

    Args:
        fdatagrid (FDataGrid): Object to whose elements the logarithm
            operation is going to be applied.

    Returns:
        FDataGrid: Object whose elements are the logarithm of the original.

    """
    return FDataGrid(numpy.log(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def log10(fdatagrid):
    """ Performs a element wise base 10 logarithm operation.

    Args:
        fdatagrid (FDataGrid): Object to whose elements the base 10 logarithm
            operation is going to be applied.

    Returns:
        FDataGrid: Object whose elements are the base 10 logarithm of the
            original.

    """
    return FDataGrid(numpy.log10(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def log2(fdatagrid):
    """ Performs a element wise binary logarithm operation.

    Args:
        fdatagrid (FDataGrid): Object to whose elements the binary logarithm
            operation is going to be applied.

    Returns:
        FDataGrid: Object whose elements are the binary logarithm of the
            original.

    """
    return FDataGrid(numpy.log2(fdatagrid.data_matrix),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def cumsum(fdatagrid):
    """ Returns the cumulative sum of the samples.

    Args:
        fdatagrid (FDataGrid): Object over whose samples the cumulative sum is
            going to be calculated.

    Returns:
        FDataGrid: Object with the sample wise cumulative sum.

    """
    return FDataGrid(numpy.cumsum(fdatagrid.data_matrix, axis=0),
                     fdatagrid.sample_points, fdatagrid.sample_range,
                     fdatagrid.names)


def inner_product(fdatagrid, fdatagrid2):
    """ Calculates the inner product amongst all the samples in two
    FDataGrid objects.

    For each pair of samples f and g the inner product is defined as:

    .. math::
        <f, g> = \\int_a^bf(x)g(x)dx

    The integral is approximated using Simpson's rule.

    Args:
        fdatagrid (FDataGrid): First FDataGrid object.
        fdatagrid2 (FDataGrid): Second FDataGrid object.

    Returns:
        numpy.darray: Matrix with as many rows as samples in the first
        object and as many columns as samples in the second one. Each
        element (i, j) of the matrix is the inner product of the ith sample
        of the first object and the jth sample of the second one.

    Examples:
        The inner product of the :math:'f(x) = x` and the constant
        :math:`y=1` defined over the interval [0,1] is the area of the
        triangle delimited by the the lines y = 0, x = 1 and y = x; 0.5.

        >>> x = numpy.linspace(0,1,1001)
        >>> fd1 = FDataGrid(x,x)
        >>> fd2 = FDataGrid(numpy.ones(len(x)),x)
        >>> inner_product(fd1, fd2)
        array([[ 0.5]])

        If the FDataGrid object contains more than one sample

        >>> fd1 = FDataGrid([x, numpy.ones(len(x))], x)
        >>> fd2 = FDataGrid([numpy.ones(len(x)), x] ,x)
        >>> inner_product(fd1, fd2).round(2)
        array([[ 0.5 ,  0.33],
               [ 1.  ,  0.5 ]])

    """
    # Checks
    if not numpy.array_equal(fdatagrid.sample_points,
                             fdatagrid2.sample_points):
        raise ValueError("Sample points for both objects must be equal")

    # Creates an empty matrix with the desired size to store the results.
    _matrix = numpy.empty([fdatagrid.n_samples, fdatagrid2.n_samples])
    # Iterates over the different samples of both objects.
    for i in range(fdatagrid.n_samples):
        for j in range(fdatagrid2.n_samples):
            # Calculates the inner product using Simpson's rule.
            _matrix[i, j] = (scipy.integrate.simps(fdatagrid.data_matrix[i] *
                                                   fdatagrid2.data_matrix[j],
                                                   x=fdatagrid.sample_points))
    return _matrix


def norm_lp(fdatagrid, p=2):
    """ Calculates the norm of all the samples in a FDataGrid object.

    For each sample sample f the lp norm is defined as:

    .. math::
        \\lVert f \\rVert = \\left( \\int_D \\lvert f \\rvert^p dx \\right)^{
        \\frac{1}{p}}

    Where D is the domain over which the functions are defined.

    The integral is approximated using Simpson's rule.

    Args:
        fdatagrid (FDataGrid): FDataGrid object.
        p (int, optional): p of the lp norm. Must be greater or equal
            than 1. Defaults to 2.

    Returns:
        numpy.darray: Matrix with as many rows as samples in the first
        object and as many columns as samples in the second one. Each
        element (i, j) of the matrix is the inner product of the ith sample
        of the first object and the jth sample of the second one.

    Examples:
        Calculates the norm of a FDataGrid containing the functions y = 1
        and y = x defined in the interval [0,1].

        >>> x = numpy.linspace(0,1,1001)
        >>> fd = FDataGrid([numpy.ones(len(x)), x] ,x)
        >>> norm_lp(fd).round(2)
        array([ 1.  ,  0.58])

        The lp norm is only defined if p >= 1.

        >>> norm_lp(fd, p = 0.5)
        Traceback (most recent call last):
            ....
        ValueError: p must be equal or greater than 1.

    """
    # Checks that the lp normed is well defined
    if p < 1:
        raise ValueError("p must be equal or greater than 1.")

    # Computes the norm, approximating the integral with Simpson's rule.
    return scipy.integrate.simps(numpy.abs(fdatagrid.data_matrix) ** p,
                                 x=fdatagrid.sample_points
                                 ) ** (1 / p)


def metric(fdatagrid, fdatagrid2, norm=norm_lp, **kwargs):
    """ Calculates the distance between all possible pairs of one sample of
    the first FDataGrid object and one of the second one.

    For each pair of samples f and g the distance between them is defined as:

    .. math::
        d(f, g) = d(f, g) = \\lVert f - g \\rVert

    The norm is specified as a parameter but defaults to the l2 norm.

    Args:
        fdatagrid (FDataGrid): First FDataGrid object.
        fdatagrid2 (FDataGrid): Second FDataGrid object.
        norm (Function, optional): Norm function used in the definition of
            the distance.
        **kwargs (dict, optional): parameters dictionary to be passed to the
            norm function.

    Returns:
        numpy.darray: Matrix with as many rows as samples in the first
        object and as many columns as samples in the second one. Each
        element (i, j) of the matrix is the distance between the ith sample
        of the first object and the jth sample of the second one.


    Examples:
        Computes the distances between an object containing functional data
        corresponding to the functions y = 1 and y = x defined over the
        interval [0, 1] and another ones containing data of the functions y
        = 0 and y = x/2. The result then is an array 2x2 with the computed
        l2 distance between every pair of functions.

        >>> x = numpy.linspace(0, 1, 1001)
        >>> fd = FDataGrid([numpy.ones(len(x)), x], x)
        >>> fd2 =  FDataGrid([numpy.zeros(len(x)), x/2 + 0.5], x)
        >>> metric(fd, fd2).round(2)
        array([[ 1.  ,  0.29],
               [ 0.58,  0.29]])


        If the functional data are defined over a different set of points of
        discretisation the functions returns an exception.

        >>> x = numpy.linspace(0, 2, 1001)
        >>> fd2 =  FDataGrid([numpy.zeros(len(x)), x/2 + 0.5], x)
        >>> metric(fd, fd2)
        Traceback (most recent call last):
            ....
        ValueError: Sample points for both objects must be equal

    """
    # Checks
    if not numpy.array_equal(fdatagrid.sample_points,
                             fdatagrid2.sample_points):
        raise ValueError("Sample points for both objects must be equal")
        # Creates an empty matrix with the desired size to store the results.
    _matrix = numpy.empty([fdatagrid.n_samples, fdatagrid2.n_samples])
    # Iterates over the different samples of both objects.
    for i in range(fdatagrid.n_samples):
        for j in range(fdatagrid2.n_samples):
            _matrix[i, j] = norm(fdatagrid[i] - fdatagrid2[j], **kwargs)
    # Computes the metric between x and y as norm(x -y).
    return _matrix


def fpca(fdatagrid, n=2, normalise=True):
    """ Functional Principal Components Analysis.

    Performs Principal Components Analysis to reduce dimensionality and
    obtain the principal modes of variation for a functional data object.

    """
    fdatagrid = fdatagrid - mean(fdatagrid)  # centers the data
    # singular value decomposition
    u, s, v = numpy.linalg.svd(fdatagrid.data_matrix)
    principal_directions = v.T  # obtain the eigenvectors matrix
    eigenvalues = (numpy.diag(s) ** 2) / (fdatagrid.n_samples - 1)
    scores = u @ s  # functional principal scores

    if normalise:
        # TODO normalise
        pass
    return scores, principal_directions, eigenvalues