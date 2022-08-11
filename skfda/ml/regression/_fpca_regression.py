from typing import Callable, Optional, TypeVar
from __future__ import annotations

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.utils.validation import check_is_fitted

from ..._utils._sklearn_adapter import BaseEstimator, RegressorMixin
from ...misc.regularization import L2Regularization
from ...preprocessing.dim_reduction import FPCA
from ...representation import FData
from ...representation.basis import Basis


class FPCARegression(
    BaseEstimator,
    RegressorMixin,
):
    r"""Regression using Functional Principal Components Analysis.

    It performs Functional Principal Components Analysis to reduce the dimension
    of the functional data, and then uses a linear regression model to
    relate the transformed data to a scalar value.

    Args:
        n_components: Number of principal components to keep.
        intercept: If True, the linear model is calculated with an intercept.
            Defaults to ``True``.
        regularization: Regularization parameter for the principal component
            analysis. If None then no regularization is applied. Defaults to
            ``None``.
        components_basis: Basis used for the principal components. If None
            then the basis of the input data is used. Defaults to None.
            It is only used if the input data is a FDataBasis object.

    Attributes:
        n\_components\_: Number of principal components used.
        components\_: Principal components.
        explained\_variance\_: Amount of variance explained by
            each of the selected components.
        explained\_variance\_ratio\_: Percentage of variance
            explained by each of the selected components.
        singular\_values\_: Singular values associated to each
            of the selected components.

    Examples:
        Using the Berkeley Growth Study dataset, we can fit the model.
        >>> import skfda
        >>> dataset = skfda.datasets.fetch_growth()
        >>> fd = dataset["data"]
        >>> y = dataset["target"]
        >>> reg = skfda.ml.regression.FPCARegression(n_components=2)
        >>> reg.fit(fd, y)
        FPCARegression()

        Then, we can predict the target values and calculate the
        score.
        >>> score = reg.score(fd, y)
        >>> reg.predict(fd) # doctest:+ELLIPSIS
        array([...])

    """

    def __init__(
        self,
        n_components: int = 2,
        intercept: bool = True,
        regularization: L2Regularization[FData] | None = None,
        components_basis: Basis | None = None,
    ) -> None:
        self.n_components = n_components
        self.intercept = intercept
        self.regularization = regularization
        self.components_basis = components_basis

    def fit(
        self,
        X: FData,
        y: np.ndarray,
    ) -> "FPCARegression":
        """Fit the model according to the given training data.

        Args:
            X: Functional data.
            y: Target values.

        Returns:
            self

        """
        self._fpca = FPCA(
            n_components=self.n_components,
            centering=True,
            regularization=self.regularization,
            components_basis=self.components_basis,
        )

        X_transformed = self._fpca.fit_transform(X)

        # If the variables are not centered, an intercept term has to be
        # calculated
        self._linear_model = LinearRegression(fit_intercept=self.intercept)
        self._linear_model.fit(X_transformed, y)

        self.n_components_ = self.n_components
        self.components_ = self._fpca.components_
        self.explained_variance_ = self._fpca.explained_variance_
        self.explained_variance_ratio_ = self._fpca.explained_variance_ratio_
        self.singular_values_ = self._fpca.singular_values_

        return self

    def predict(
        self,
        X: FData,
    ) -> np.ndarray:
        """Predict using the linear model.

        Args:
            X: Functional data.

        Returns:
            Target values.

        """
        check_is_fitted(self, ["_fpca", "_linear_model"])

        return self._linear_model.predict(self._fpca.transform(X))
