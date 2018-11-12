import unittest
from itertools import combinations

from neuroptica.layers import Activation, ClementsLayer
from neuroptica.losses import MeanSquaredError
from neuroptica.models import Sequential
from neuroptica.nonlinearities import *
from neuroptica.optimizers import Optimizer
from tests.base import NeuropticaTest
from tests.test_models import TestModels


class TestNonlinearities(NeuropticaTest):
    '''Tests for Network nonlinearities'''

    def test_Abs(self):
        '''Tests the z->|z| nonlinearity'''
        for N in [8, 9]:
            gamma = self.random_complex_vector(N)
            Z_back = self.random_complex_vector(N)
            backward_results = []

            for mode in ["full", "condensed", "polar"]:
                a = Abs(N, mode=mode)
                back = a.backward_pass(gamma, Z_back)
                backward_results.append(back)

            # Check that backprop results are the same for each mode
            for result1, result2 in combinations(backward_results, 2):
                self.assert_allclose(result1, result1)

    def test_OpticalMesh_adjoint_optimize(self):
        for N in [4, 5]:

            eo_settings = { 'power_tapped':      0.05,
                            'responsivity':      0.80,
                            'mode_area':         1.00,
                            'modulator_voltage': 10.0,
                            'bias_voltage':      10.0,
                            'resistance':        2e5 }

            nonlinearities = [Abs(N, mode="full"),
                              AbsSquared(N),
                              # SoftMax(N),
                              ElectroOpticActivation(N, **eo_settings),
                              SPMActivation(N,1),
                              LinearMask(N, mask=np.random.rand(N))]
            for nonlinearity in nonlinearities:

                print("Testing nonlinearity {}".format(nonlinearity))

                batch_size = 6
                n_samples = batch_size * 4

                X_all = (2 * np.random.rand(N * n_samples) - 1).reshape((N, n_samples))
                Y_all = np.abs(X_all)

                # Make a single-layer model
                model = Sequential([ClementsLayer(N),
                                    Activation(nonlinearity)
                                    ])

                # Use mean squared cost function
                loss = MeanSquaredError

                for X, Y in Optimizer.make_batches(X_all, Y_all, batch_size):
                    # Propagate the data forward
                    Y_hat = model.forward_pass(X)
                    d_loss = loss.dL(Y_hat, Y)

                    # Compute the backpropagated signals for the model
                    gradients = model.backward_pass(d_loss)

                    TestModels.verify_model_gradients(model, X, Y, loss.L, gradients, epsilon=1e-6)





if __name__ == "__main__":
    unittest.main()
