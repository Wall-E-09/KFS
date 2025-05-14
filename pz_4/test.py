import unittest
import numpy as np
from main import LorenzAttractor

class TestLorenzAttractor(unittest.TestCase):
    def setUp(self):
        self.lorenz = LorenzAttractor()
        self.t_span = (0, 40)
        self.t_eval = np.linspace(0, 40, 1000)
        self.initial_state = [1.0, 1.0, 1.0]

    def test_initial_conditions_calculation(self):
        derivatives = self.lorenz.equations(0, self.initial_state)
        expected = [0.0, 26.0, -1.66666667]
        np.testing.assert_array_almost_equal(derivatives, expected, decimal=6)

    def test_solution_shape(self):
        solution = self.lorenz.solve(self.initial_state, self.t_span, self.t_eval)
        self.assertEqual(solution.y.shape, (3, len(self.t_eval)))

    def test_sensitivity_to_initial_conditions(self):
        initial_state2 = [1.0001, 1.0001, 1.0001]
        sol1 = self.lorenz.solve(self.initial_state, self.t_span, self.t_eval)
        sol2 = self.lorenz.solve(initial_state2, self.t_span, self.t_eval)
        final_distance = np.linalg.norm(sol1.y[:, -1] - sol2.y[:, -1])
        self.assertGreater(final_distance, 5)

    def test_attractor_properties(self):
        solution = self.lorenz.solve(self.initial_state, self.t_span, self.t_eval)
        self.assertTrue(np.all(np.abs(solution.y[0]) < 50))
        self.assertTrue(np.all(np.abs(solution.y[1]) < 50))
        self.assertTrue(np.all(np.abs(solution.y[2]) < 100))
        mean_x = np.mean(solution.y[0])
        self.assertAlmostEqual(mean_x, 0, delta=5)

    def test_compare_trajectories_output(self):
        initial_state2 = [1.0001, 1.0001, 1.0001]
        try:
            self.lorenz.compare_trajectories(
                self.initial_state, 
                initial_state2, 
                self.t_span, 
                self.t_eval
            )
        except Exception as e:
            self.fail(f"compare_trajectories викликала виняток: {e}")

if __name__ == "__main__":
    unittest.main()
