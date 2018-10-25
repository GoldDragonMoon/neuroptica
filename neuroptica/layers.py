import numpy as np

from neuroptica.components import MZILayer, OpticalMesh, PhaseShifterLayer


class NetworkLayer:
	'''
	Represents a logical layer in a neural network (different from ComponentLayer)
	'''

	def __init__(self, input_size: int, output_size: int, initializer=None):
		self.input_size = input_size
		self.output_size = output_size
		self.initializer = initializer

	def forward_pass(self, X):
		raise NotImplementedError('forward_pass() must be overridden in child class!')


class ClementsLayer(NetworkLayer):
	'''
	Performs a unitary NxM operator with MZIs arranged in a Clements decomposition. If M=N then the layer can perform
	any arbitrary unitary operator
	'''

	def __init__(self, N: int, M=None, include_phase_shifter_layer=True, initializer=None):
		super().__init__(N, N, initializer=initializer)

		layers = []
		if include_phase_shifter_layer:
			layers.append(PhaseShifterLayer(N))

		if M is None:
			M = N

		for layer_index in range(M):
			if N % 2 == 0:  # even number of waveguides
				if layer_index % 2 == 0:
					layers.append(MZILayer.from_waveguide_indices(N, list(range(0, N))))
				else:
					layers.append(MZILayer.from_waveguide_indices(N, list(range(1, N - 1))))
			else:  # odd number of waveguides
				if layer_index % 2 == 0:
					layers.append(MZILayer.from_waveguide_indices(N, list(range(0, N - 1))))
				else:
					layers.append(MZILayer.from_waveguide_indices(N, list(range(1, N))))

		self.mesh = OpticalMesh(N, layers)

	def forward_pass(self, X):
		return np.dot(self.mesh.get_transfer_matrix(), X)
