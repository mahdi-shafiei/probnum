"""Tests for the random variable implementation."""

import itertools
import unittest

import numpy as np

from tests.testing import NumpyAssertions
from probnum import prob
from probnum.linalg import linops


class RandomVariableTestCase(unittest.TestCase, NumpyAssertions):
    """General test case for random variables."""

    def setUp(self):
        """Scalars, arrays, linear operators and random variables for tests."""
        # Random variable instantiation
        self.scalars = [0, int(1), .1, np.nan, np.inf]
        self.arrays = [np.empty(2), np.zeros(4), np.array([]),
                       np.array([1, 2])]

        # Random variable arithmetic
        self.arrays2d = [np.empty(2), np.zeros(2), np.array([np.inf, 1]),
                         np.array([1, -2.5])]
        self.matrices2d = [np.array([[1, 2], [3, 2]]),
                           np.array([[0, 0], [1.0, -4.3]])]
        self.linops2d = [
            linops.MatrixMult(A=np.array([[1, 2], [4, 5]]))]
        self.randvars2d = [
            prob.RandomVariable(
                distribution=prob.Normal(mean=np.array([1, 2]),
                                         cov=np.array(
                                             [[2, 0], [0, 5]])))]
        self.randvars2x2 = [
            prob.RandomVariable(shape=(2, 2),
                                distribution=prob.Normal(
                                    mean=np.array([[-2, .3], [0, 1]]),
                                    cov=linops.SymmetricKronecker(
                                        A=np.eye(2),
                                        B=np.ones((2, 2)))))
        ]


class RandomVariableInstantiationTestCase(RandomVariableTestCase):
    """Test random variable instantiation."""

    def test_rv_dtype(self):
        """Check the random variable types."""
        pass

    def test_rv_from_number(self):
        """Create a random variable from a number."""
        for x in self.scalars:
            with self.subTest():
                prob.asrandvar(x)

    def test_rv_from_ndarray(self):
        """Create a random variable from an array."""
        for arr in self.scalars:
            with self.subTest():
                prob.asrandvar(arr)

    # def test_rv_from_linearoperator(self):
    #     """Create a random variable from a linear operator."""
    #     for linop in linops:
    #       with self.subTest():
    #           prob.asrandvar(A)


class RandomVariableArithmeticTestCase(RandomVariableTestCase):
    """Test random variable arithmetic and broadcasting."""

    def test_rv_addition(self):
        """Addition with random variables."""
        for (x, rv) in list(itertools.product(self.arrays2d, self.randvars2d)):
            with self.subTest():
                z1 = x + rv
                z2 = rv + x
                self.assertEqual(z1.shape, rv.shape)
                self.assertEqual(z2.shape, rv.shape)
                self.assertIsInstance(z1, prob.RandomVariable)
                self.assertIsInstance(z2, prob.RandomVariable)

    def test_rv_scalarmult(self):
        """Multiplication of random variables with scalar constants."""
        for (alpha, rv) in list(
                itertools.product(self.scalars, self.randvars2d)):
            with self.subTest():
                z = alpha * rv
                self.assertEqual(z.shape, rv.shape)
                self.assertIsInstance(z, prob.RandomVariable)

    def test_rv_broadcasting(self):
        """Broadcasting for arrays and random variables."""
        for alpha, rv in list(
                itertools.product(self.scalars, self.randvars2d)):
            with self.subTest():
                z = alpha + rv
                z = rv - alpha
                self.assertEqual(z.shape, rv.shape)

    def test_rv_dotproduct(self):
        """Dot product of random variables with constant vectors."""
        for x, rv in list(
                itertools.product([np.array([1, 2]), np.array([0, -1.4])],
                                  self.randvars2d)):
            with self.subTest():
                z1 = rv @ x
                z2 = x @ rv
                self.assertIsInstance(z1, prob.RandomVariable)
                self.assertIsInstance(z2, prob.RandomVariable)
                self.assertEqual(z1.shape, ())
                self.assertEqual(z2.shape, ())

    def test_rv_matmul(self):
        """Multiplication of random variables with constant matrices."""
        for A, rv in list(itertools.product(self.matrices2d, self.randvars2d)):
            with self.subTest():
                y2 = A @ rv
                self.assertEqual(y2.shape[0], A.shape[0])
                self.assertIsInstance(y2, prob.RandomVariable)

    def test_rv_linop_matmul(self):
        """Linear operator applied to a random variable."""
        for A, rv in list(itertools.product(self.linops2d, self.randvars2d)):
            with self.subTest():
                y = A @ rv + np.array([-1, 1.1])
                self.assertEqual(y.shape[0], A.shape[0])

    def test_rv_vector_product(self):
        """Matrix-variate random variable applied to vector."""
        for rv in self.randvars2x2:
            with self.subTest():
                x = np.array([[1], [-4]])
                y = rv @ x
                X = np.kron(np.eye(rv.shape[0]), x)
                truemean = rv.mean() @ x
                truecov = X.T @ rv.cov().todense() @ X
                self.assertIsInstance(y, prob.RandomVariable, "The variable y does not have the correct type.")
                self.assertEqual(y.shape, (2, 1), "Shape of resulting random variable incorrect.")
                self.assertAllClose(y.mean(), truemean,
                                    msg="Means of random variables do not match.")
                self.assertAllClose(y.cov().todense(), truecov,
                                    msg="Covariances of random variables do not match.")

    # Random seed
    def test_different_rv_seeds(self):
        """
        Arithmetic operation between two random variables with different seeds.
        """
        pass


class TestEmptyInit(unittest.TestCase):
    """
    Tests that a RandomVariable object can be set up with an empty init.
    """
    def test_empty_init(self):
        """No input."""
        with self.assertRaises(ValueError):
            prob.RandomVariable()

    def test_dtype_init(self):
        """Instantiate a random variable without a distribution."""
        rv = prob.RandomVariable(dtype=int)
        self.assertIsInstance(rv, prob.RandomVariable)

