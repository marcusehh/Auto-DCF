#Neuron Object | Updated P5 sentdex
import numpy as np
import nnfs
from nnfs.datasets import spiral_data

nnfs.init()

'''
#Prior to Ep3

weights1 = [0.2,0.8,-0.5, 1.0]
weights2 = [0.5,-0.91,0.26,-0.5]
weights3 = [-0.26,-0.27,0.17,0.87]

bias1 = 2
bias2 = 3
bias3 = 0.5

#Output for three neurons; each neuron has unique biases and weights
output = [inputs[0]*weights1[0] + inputs[1]*weights1[1] + inputs[2]*weights1[2] + inputs[3]*weights1[3] + bias1,
          inputs[0]*weights2[0] + inputs[1]*weights2[1] + inputs[2]*weights2[2] + inputs[3]*weights2[3] + bias2,
          inputs[0]*weights3[0] + inputs[1]*weights3[1] + inputs[2]*weights3[2] + inputs[3]*weights3[3] + bias3]

print(output)
'''

'''#Must be made into 2D list/array to be used by np.dot()

weights = [[0.2,0.8,-0.5, 1.0],
           [0.5,-0.91,0.26,-0.5],
           [-0.26,-0.27,0.17,0.87]]

biases = [2,3,0.5]

weights2 = [[0.1,-0.14,0.5],
           [-0.5,0.12,-0.33],
           [-0.44,0.73,0.13]]

biases2 = [-1,2,-0.5]

#Uses np.dot() to multiple corresponding cells of weights & inputs
#Transposing array as inputs are no longer just a vector and to NOT have a shape error
layer1_output = np.dot(inputs, np.array(weights).T) + biases
#Takes the output as input
layer2_output = np.dot(layer1_output, np.array(weights2).T) + biases2

print(layer2_output)'''

#Input Data
X = [[1,2,3,2.5],
     [2.0,5.0,-1.0,2.0],
     [-1.5,2.7,3.3,-0.8]]

X,y = spiral_data(100,3)

class Layer_Dense:
    #Whenever a new layer is created, the following runs...
    def __init__(self,n_inputs,n_neurons):
        #Creates a matrix of random weights based on how many inputs are coming in & how many neurons you want-
        #(We multiply by 0.10 to make these weights small)...
        self.weights = 0.10 * np.random.randn(n_inputs,n_neurons)
        #Creates a row of zeroes for biases which is standard practice for neural networks
        self.biases = np.zeros((1, n_neurons))
    def forward(self, inputs):
        #forward method?
        #Smoothly multiplies batches of inputs by the weights and adds the biases
        self.output = np.dot(inputs, self.weights) + self.biases

class Activation_ReLU:
    def forward(self, inputs):
        self.output = np.maximum(0,inputs)

#Here the first hidden layer is created
layer1 = Layer_Dense(2,5)
activation1 = Activation_ReLU()
'''#First "n_neurons" is the output meaning next n_inputs must be the same value, in this case 5
#Creates the second hidden layer
layer2 = Layer_Dense(5,2)'''

layer1.forward(X)
'''print(layer1.output)'''
activation1.forward(layer1.output)
print(activation1.output)