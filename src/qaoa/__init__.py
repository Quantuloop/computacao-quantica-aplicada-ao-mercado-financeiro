import json
import shutil
from ket import quant, dump, cnot, H, RY, RZ


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


def cost_function(param, var_circuit, energy):
    qubits = var_circuit(param[:int((len(param)/2))],
                         param[(int(len(param)/2)):-1])

    result = dump(qubits)
    exp_value = 0.0

    for states, probs in zip(result.states, result.probabilities):
        exp_value += energy(states)*probs

    return exp_value


def save_quantum_state_and_return(result: quant, num_layers, data_file):
    result = dump(result)
    num_layers = str(num_layers)

    try:
        with open(data_file, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    except json.JSONDecodeError:
        shutil.copy(data_file, data_file + '.bak')
        data = {}

    result = {
        str(state): prob for state, prob in zip(result.states, result.probabilities)
    }

    if num_layers not in data:
        data[num_layers] = [result]
    else:
        data[num_layers].append(result)

    with open(data_file, 'w') as file:
        json.dump(data, file)

    return result


def load_probMed_Hmin(state, energy, data_file, n_best=2):
    with open(data_file, 'r') as file:
        data = json.load(file)

    prob_med = {}
    Hmin_med = {}
    best_result = float('-inf')
    best_state = None

    for num_layers in data:
        prob_med[int(num_layers)] = []
        Hmin_med[int(num_layers)] = []
        for quantum_state in data[num_layers]:

            exp_value = 0.0
            for state_in, prob in quantum_state.items():
                exp_value += energy(int(state_in))*prob

                if state_in == str(state):
                    if prob > best_result:
                        best_result = prob
                        best_state = quantum_state
                    prob_med[int(num_layers)].append(prob)

            Hmin_med[int(num_layers)].append(exp_value)

    for layer in prob_med:
        selected = sorted(prob_med[layer])[-n_best:]
        prob_med[layer] = sum(selected)/len(selected)

    for layer in Hmin_med:
        selected = sorted(Hmin_med[layer])[:n_best]
        Hmin_med[layer] = sum(selected)/len(selected)

    return prob_med, Hmin_med, best_state


def num_quantum_executions():
    from ket.base import PROCESS_COUNT
    return PROCESS_COUNT-1
