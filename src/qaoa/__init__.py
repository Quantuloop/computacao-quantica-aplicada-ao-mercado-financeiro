import json
from os import path
import shutil
import uuid
from ket import quant, dump, cnot, H, RY, RZ, kbw
from os import makedirs


def var_circuit(gamma, beta, num_layers, num_qubits, coefs):
    """
    Implementação do circuito variacional no ket.
    """

    qubits = quant(num_qubits)

    # estado inicial: |+>^n
    H(qubits)

    for layer in range(num_layers):
        # operador gamma
        for i in range(num_qubits):
            for j in range(num_qubits):
                if (i < j):
                    cnot(qubits[i], qubits[j])
                    RZ(gamma[layer]*coefs[j+4], qubits[j])
                    cnot(qubits[i], qubits[j])
        RZ(gamma[layer]*coefs[i], qubits)

        # operador beta (forma variacional: emaranhamento linear)
        RY(beta[layer], qubits)
        for i in range(num_qubits-1):
            cnot(qubits[i], qubits[i+1])
        cnot(qubits[num_qubits-1], qubits[0])
        RY(beta[layer], qubits)

    return qubits


def energy(x, cov, mu, q, B, lamb, num_qubits):
    """
    Energias do hamiltoniano que serão calculadas para os autoestados medidos
    """
    x = [int(i) for i in reversed(f'{x:0{num_qubits}b}')]

    H = -((mu[0]*x[0]+mu[1]*x[1]+mu[2]*x[2]+mu[3]*x[3]) -
          q*(cov[0][1]*x[0]*x[1] + cov[0][2]*x[0]*x[2] +
             cov[0][3]*x[0]*x[3] + cov[1][2]*x[1]*x[2] +
             cov[1][3]*x[1]*x[3] + cov[2][3]*x[2]*x[3]) -
          lamb*(B - x[0]-x[1]-x[2]-x[3])**2)
    return H


class CostFunction:

    def __init__(self, var_circuit, energy, num_shots):
        self.var_circuit = var_circuit
        self.energy = energy
        self.num_shots = num_shots
        self.id = uuid.uuid4().hex

        self.executions = []

    def __call__(self, param):
        kbw.set_dump_type('shots', self.num_shots)
        qubits = self.var_circuit(param[:len(param)//2],
                                  param[len(param)//2:])

        result = dump(qubits).shots
        total = sum(result.values())

        exp_value = 0.0
        for state, count in result.items():
            exp_value += self.energy(state)*(count/total)

        self.executions.append(result)

        return exp_value

    def get_best_execution(self, state):
        best_execution = self.executions[0]
        for execution in self.executions:
            if execution[state] > best_execution[state]:
                best_execution = execution
        return best_execution

    def get_last_execution(self):
        return self.executions[-1]

    def save_executions(self, data_file):
        makedirs(path.dirname(data_file), exist_ok=True)

        try:
            with open(data_file, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            data = {}
        except json.JSONDecodeError:
            try_i = 1
            while True:
                bak_file = f'{data_file}.bak.{try_i}'
                if path.exists(bak_file):
                    try_i += 1
                else:
                    shutil.copy(data_file, bak_file)
                    break
            data = {}

        data[self.id] = self.executions

        with open(data_file, 'w') as file:
            json.dump(data, file)
