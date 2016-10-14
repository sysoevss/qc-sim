from google.appengine.ext import db

import math
import random

class QC:
    status = 0.0
    guid = ''
    
    def __init__(self, guid):
        self.status = 0.0
        self.guid = guid

    def getStatus(self):
        return str(self.status)
    
    '''
    '  Creates input state
    '
    '''
    def createState(self, schema):
        x = int(schema.split('}')[0][1:].replace(',', '')[::-1], base = 2)
        n = len(schema.split('}')[0][1:].replace(',', ''))
        N = 2 ** n
        state = []
        for i in range(N):
            state.append(complex(0, 0))
            
        state[x] = complex(1, 0)
        self.status = 0
        return state, n, N

    '''
    '  Applies cirsuit scheme to the input
    '
    '''
    def applyScheme(self, state, schema, n):
        gates = schema.split('}')[1][1:].split(',') 
        
        for t in range(0, len(gates), n):
            tact = gates[t : t + n]
                    
            # find the control bit if exists
            control = []
            for i in range(len(tact)):
                if tact[i] == '*':
                    control.append(i)
            
            # Apply gates in tact
            qbit = 0
            for gate in tact:
                state = self.applyGate(state, qbit, n, gate, control)
                qbit += 1
                self.status += 100.0 / len(gates)
                
        return state

    '''
    '  Applies the gate
    '
    '''
    def qubitGate(self, c_i, result, i, n, qbit, A, B, C, D):
        base = 2 ** qbit
        if i & base:                # qubit is |1> so B,D column is applied
            result[i] = result[i] + c_i * D
            i2 = i - base
            result[i2] = result[i2] + c_i * B
        else:                       # qubit is |0> so A,C column is applied
            result[i] = result[i] + c_i * A
            i2 = i + base
            result[i2] = result[i2] + c_i * C
            
        return result
         
    def applyGate(self, state, qbit, n, gate, control):
        # skip on identity and control symbol
        if gate == 'I' or gate == '*':
            return state
        
        # main cycle
        N = 2 ** n
        result = []
        for i in range(N):
            result.append(complex(0,0))
        for i in range(N):
            # check if basis vector i is in superposition
            if state[i] == complex(0, 0):
                continue
            # check if gate is controlled and if any of control bits is 0, then do nothing
            res_control = True
            for c in control: 
                if not (2 ** c & i):
                    res_control = False
                
            if not res_control:
                result[i] = state[i]
                continue
            
            # at last, do the computation
            if gate == 'H':
                sqrt2 = complex(1 / math.sqrt(2), 0)
                result = self.qubitGate(state[i], result, i, n, qbit, sqrt2, sqrt2, sqrt2, -sqrt2)      
            
            if gate[0] == 'R':
                angle = 2 * math.pi / 2 ** int(gate[1])
                phase = complex(math.cos(angle), math.sin(angle))   
                result = self.qubitGate(state[i], result, i, n, qbit, complex(1,0), complex(0,0), complex(0,0), phase)                  
                
            if gate[0] == 'Z':
                result = self.qubitGate(state[i], result, i, n, qbit, complex(1,0), complex(0,0), complex(0,0), complex(-1,0))
                
            if gate[0] == 'X':
                result = self.qubitGate(state[i], result, i, n, qbit, complex(0,0), complex(1,0), complex(1,0), complex(0,0))
    
        return result                  

        
    def measure(self, state):
        for i in range(len(state)):
            state[i] = state[i].real * state[i].real + state[i].imag * state[i].imag
    
        r = random.random()
        temp = 0
        for i in range(len(state)):
            temp += state[i]
            if temp >= r:
                return bin(i)
        
        return bin(len(state) - 1)

'''
'  Measurement
'
'''
def bin(n):
    return "".join([["0", "1"][(n >> i) & 1] for i in reversed(range(20))])

