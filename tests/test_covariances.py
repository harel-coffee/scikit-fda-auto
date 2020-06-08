import unittest

import numpy as np
import skfda


class TestsSklearn(unittest.TestCase):

    def setUp(self):
        unittest.TestCase.setUp(self)

        self.x = np.linspace(-1, 1, 1000)[:, np.newaxis]

    def _test_compare_sklearn(self, cov: skfda.misc.covariances.Covariance):
        cov_sklearn = cov.to_sklearn()
        cov_matrix = cov(self.x, self.x)
        cov_sklearn_matrix = cov_sklearn(self.x)

        np.testing.assert_array_almost_equal(cov_matrix, cov_sklearn_matrix)

    def test_linear(self):

        for variance in [1, 2]:
            for intercept in [0, 1, 2]:
                with self.subTest(variance=variance, intercept=intercept):
                    cov = skfda.misc.covariances.Linear(
                        variance=variance, intercept=intercept)
                    self._test_compare_sklearn(cov)

    def test_polynomial(self):

        for variance in [1, 2]:
            for intercept in [0, 1, 2]:
                for slope in [1, 2]:
                    for degree in [1, 2, 3]:
                        with self.subTest(variance=variance,
                                          intercept=intercept,
                                          slope=slope,
                                          degree=degree):
                            cov = skfda.misc.covariances.Polynomial(
                                variance=variance, intercept=intercept,
                                slope=slope, degree=degree)
                            self._test_compare_sklearn(cov)

    def test_gaussian(self):

        for variance in [1, 2]:
            for length_scale in [0.5, 1, 2]:
                with self.subTest(variance=variance,
                                  length_scale=length_scale):
                    cov = skfda.misc.covariances.Gaussian(
                        variance=variance, length_scale=length_scale)
                    self._test_compare_sklearn(cov)

    def test_exponential(self):

        for variance in [1, 2]:
            for length_scale in [0.5, 1, 2]:
                with self.subTest(variance=variance,
                                  length_scale=length_scale):
                    cov = skfda.misc.covariances.Exponential(
                        variance=variance, length_scale=length_scale)
                    self._test_compare_sklearn(cov)

    def test_white_noise(self):

        for variance in [1, 2]:
            with self.subTest(variance=variance):
                cov = skfda.misc.covariances.WhiteNoise(variance=variance)
                self._test_compare_sklearn(cov)
