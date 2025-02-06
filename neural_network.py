import math
import random

def sigmoid(x):
    return 1 / 1 + math.exp(-x)

class NeuralNetwork: 
    def __init__(self, input_size, hidden_size, output_size):
        # Init weights with random values
        self.W1 = [[random.uniform(-1, 1) for _ in range(hidden_size)] for _ in range(input_size)]
        self.b1 = [random.uniform(-1, 1) for _ in range(hidden_size)]
        self.W2 = [[random.uniform(-1, 1) for _ in range(output_size)] for _ in range(hidden_size)]
        self.b2 = [random.uniform(-1, 1) for _ in range(output_size)]

    def forward(self, inputs):
        # Hidden layer
        hidden = []
        # Calculate the hidden layer
        for h in range(len(self.W1[0])): # for each neuron in the hidden layer
            sum_ = 0.0
            for i in range(len(inputs)):
                sum_ += inputs[i] * self.W1[i][h]
            sum_ += self.b1[h]
            hidden.append(sigmoid(sum_))

        # Output layer
        outputs = []
        for o in range(len(self.W2[0])):
            sum_ = 0.0
            for h in range(len(hidden)):
                sum_ += hidden[h] * self.W2[h][o]
            sum_ += self.b2[o]
            outputs.append(sigmoid(sum_))

        return outputs # list of output sized elements
    
    
