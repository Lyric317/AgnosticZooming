# -*- coding: utf-8 -*-
"""IncentivesinCS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Ol241XgXJMCQ5gcDoWasI9eJ5F7Ec90A
"""

import numpy as np
import copy
import matplotlib.pyplot as plt
from bisect import bisect_left, bisect
from collections import defaultdict
from environment import * 
# V_H = 1
# V_L = 0.2
# THETA_H = 0.9
# F = np.array([[1,0], [1-THETA_H, THETA_H]])

# def plot_perf_over_time(phi,utilities):
#     fig = plt.figure()
#     l = plt.plot([i for i in range(len(utilities))], utilities,label=phi)
#     plt.plot([i for i in range(len(utilities))], utilities, 'b*')
#     plt.axis([0,5000,-0.3,0.5])
#     fig.savefig('two_times_over_time_'+str(phi)+'.jpg')

def cal_utility(c, x, contract_param):
    F, V = contract_param
    if np.max(np.matmul(F, np.array(x).T) - np.array(c)) < 0 : 
        return 0, 0, 0 
    action_idx = np.argmax(np.matmul(F, np.array(x).T) - np.array(c))
    Pr = F[1,1] #Pr[high outcome|x]
    arb_num = np.random.uniform(0,1) 
    if action_idx == 1 : 
        if arb_num > Pr : 
            Vx = V[0]
            Px = x[0]
        else :   
            Vx = V[1]  
            Px = x[1]
    else : 
        Vx = V[0]
        Px = x[0]
    #Vx = V_H*Pr + V_L*(1-Pr) #expected value
    #Px = x[action_idx] #expected payment
    #Px = x[0] if action_idx == 0 else x[0]+x[1]
    Ux = Vx - Px #requester's utility
    
    return Vx, Px, Ux

class Cell:
    def __init__(self,p,act_times, phi) : 
        self.p = p #p = [p1,p2...], pi is incr in cell C
        self.act_times = act_times #total times cell is activated before round t
        self.HL_act_times = [0,0] # times to choose high or low anchor respectively 
        self.acc_value = [0,0] # [v-,v+], use only self.acc_XXX[0] if len(self.p)==1
        self.acc_payment = [0,0] # [p-, p+]
        self.acc_utility = 0 # accumulated average utility when the cell's chosen
        self.HL_acc_utility = [0,0]
        self.acc_width = 0 # virtual width 
        self.step = 0 # horizon T 
        self.atomic = False  
        self.rad = 0 
        self.phi = phi 
        self.It = 0 

    def upper_confidence(self): #radt(C) = 1 ## it seems constant does not perform better in 2 Dim - YD 
        if self.atomic == 1: #atomic
            It = self.acc_utility + self.rad 
            #It = self.acc_utility + 1
        elif self.atomic == 0: #composite
            It = self.acc_utility + self.acc_width + 5 * self.rad 
            #It = self.acc_utility + self.acc_width + 5 
        self.It = It 
        return It

    ## check if a cell is atomic 
    def check_atomic(self, X_cand) : 
        for i in range(len(self.p)) :  
            low = np.ceil(self.p[i][0] / self.phi)
            high = np.floor(self.p[i][1] / self.phi)
            if high - low + 1 >= 2: 
                self.atomic = 0
                return self.atomic 
            elif high - low + 1 < 1 : 
                self.atomic = -1 
                return self.atomic 

        self.atomic = 1
        return self.atomic 

    ## Post sampled contract and obtain feedback, update the stats 
    def activate_cell(self,c_h, X_cand, step, contract_param):
        c_rad = 16 
        x_cands, x_candsHL_id, hl = self.sample_contract(X_cand, self.phi)  
        Vx, Px, Ux = cal_utility(c_h, x_cands, contract_param) 

        self.acc_payment[hl] = self.acc_payment[hl] * self.act_times / (self.act_times+1) + Px * 1 / (self.act_times+1)
        self.acc_value[hl] = self.acc_value[hl] * self.act_times / (self.act_times+1) + Vx * 1 / (self.act_times+1)
        
        if self.atomic == 0: 
            self.acc_width = (self.acc_value[1] - self.acc_payment[0]) -\
                                (self.acc_value[0] - self.acc_payment[1]) 
        
        self.acc_utility = self.acc_utility * self.act_times / (self.act_times + 1) + Ux * 1 / (self.act_times + 1) 
        self.HL_acc_utility[hl] = self.HL_acc_utility[hl] * self.act_times / (self.act_times + 1) + Ux * 1 / (self.act_times + 1) 
        self.act_times += 1 
        self.HL_act_times[hl] += 1

        # if step > 4500: 
        #     print(["step: ", step, "cost: ", c_h, "x_cands: ", x_cands, "real pay: ",
        #         Px, "Uti: ", Ux, "C range: ", self.p, "phi: ", self.phi, "width :", self.acc_width, 
        #         "It:", self.It])  
        # new strategy adpation, original is * log(T) 
        self.rad = np.sqrt(c_rad * np.log(step)/ self.act_times) if step >= 1 else 0 
        
        return Ux 
    
    
    def sample_contract(self, X_rand, phi):
        """
        Sample either high anchor or low anchor from a Cell.
        Output : hl : high or low anchor 
                x_cands : selected contract to post 
        """
        # x = np.random.uniform(0,1)
        # return p[0] if x < 0.5 else p[-1]
        x_cands = []
        x_cands_id = []
        x_candsL_id = []
        x_candsH_id = []
        
        hl = np.random.choice([0, 1], 1, [0.5, 0.5])[0]

        for i in range(len(self.p)) : # len is 2     
            if self.atomic : 
                x = np.ceil(self.p[i][0] / phi) * phi 
                x_cands.append(x) 
            else : 
                x_low = np.ceil(self.p[i][0] / phi) * phi  
                x_high = np.floor(self.p[i][1] / phi) * phi 
                if hl == 1 : 
                    x_cands.append(x_high)
                else :
                    x_cands.append(x_low)  
                x_candsL_id.append(x_low / phi)
                x_candsH_id.append(x_high / phi) 

        return x_cands, [tuple(x_candsL_id), tuple(x_candsH_id)], hl

## Use center of anchors for partition to 2^m sub-cell,here m = 2  
def quadrantize(cell, sub_cell_p, pos) : 
    for p in cell.p:  
        mid = (p[0] + p[1]) / 2 
        if pos > 0 : 
            temp_sub_cell_p = []
            for sub_p in sub_cell_p : 
                temp_sub_cell_p.append(sub_p + [[p[0],mid]])
                temp_sub_cell_p.append(sub_p + [[mid, p[1]]])
            sub_cell_p = temp_sub_cell_p
        else : 
            sub_cell_p[0] = [[p[0],mid]]
            sub_cell_p[1] = [[mid, p[1]]]
            pos += 1 
                
    return sub_cell_p 


def recover_cell(tgt_cell, 
                 src_HL_act_times,
                 src_value, 
                 src_payment, 
                 src_acc_utility,
                 tgt_hl):
    """
    when partition a space^m, we transfer the the low anchor stats to 
    the cell formed by all low anchor and same for the cell formed by 
    all high anchor 
    """
    tgt_cell.act_times = src_HL_act_times[tgt_hl]
    tgt_cell.acc_value[tgt_hl] = src_value[tgt_hl]
    tgt_cell.acc_payment[tgt_hl] = src_payment[tgt_hl]
    tgt_cell.HL_acc_utility[tgt_hl] = src_acc_utility[tgt_hl] 
    tgt_cell.acc_utility = src_acc_utility[tgt_hl] 

    return tgt_cell 

## Zooming rule : partition the max cell and remove it 
def act_cells(A,max_cell,phi, X_cand):
    # mid = (max_cell.p[-1] + max_cell.p[0])/2
    # p1, p2 = [], []
    # for p in max_cell.p:
    #     if p < mid:
    #         p1.append(p)
    #     else:
    #         p2.append(p)
    # if len(p1) > 0:
    #     A.append(Cell(p1,0))
    # if len(p2) > 0:
    #     A.append(Cell(p2,0))
    # A.remove(max_cell)

    quadrants = quadrantize(max_cell, [[[0]]]*2, 0)  
    for idx, quadrant in enumerate(quadrants) : 
        temp_cell = Cell(quadrant, 0, phi)
        if idx == 0 : 
            temp_cell = recover_cell(temp_cell,
                                 max_cell.HL_act_times,
                                 max_cell.acc_value,
                                 max_cell.acc_payment,
                                 max_cell.HL_acc_utility,
                                 0) 
        if idx == len(quadrants)-1 : 
            temp_cell = recover_cell(temp_cell,
                                 max_cell.HL_act_times,
                                 max_cell.acc_value,
                                 max_cell.acc_payment,
                                 max_cell.HL_acc_utility,
                                 1) 
        # if contain 0 candidate contract, not adding to A 
        if (temp_cell.check_atomic(X_cand) != -1) and (temp_cell.p[0][1] <= temp_cell.p[1][0]):  
            A.append(temp_cell)  

    A.remove(max_cell)

def agnostic_zooming(phi,T, contract_param, type):
    X_cand = [phi * i for i in range(int(1/phi)+1)] 
    A = [Cell([[0,1]] * 2,0,phi)] 
    env = environment(contract_param) 
    utilities = []
    #c_h = np.random.uniform(0,1) #homogenous worker market
    # c_h1 = np.random.uniform(0.1,0.2)
    # c_h2 = np.random.uniform(0.5,0.6)
    for t in range(T):
        # c_h1 = np.random.uniform(0, 0) #low effort level
        # c_h2 = np.random.uniform(c_h1, 1) #high effort level
        c_h = env.cost_simulation(type, t) #two_type market 
        max_It = float('-inf')
        max_cell = A[0]
        max_id = 0 
        for id, cell in enumerate(A):  
            It = cell.upper_confidence()
            ## forced exploration 
            if cell.act_times == 0 : 
                max_cell = cell 
                max_id = id 
                break 

            elif It > max_It:
                max_cell = cell
                max_It = It
                max_id = id 
        
        utility = max_cell.activate_cell(c_h, X_cand, t, contract_param) 
        utilities.append(utility)
        
        if (max_cell.check_atomic(X_cand) == 0 and max_cell.acc_width > 5 * max_cell.rad) : #radt(C) = 0.6
        # if (max_cell.check_atomic(X_cand) == 0 and max_cell.acc_width > 3) : 
            act_cells(A,max_cell, phi, X_cand) 
    
    return utilities



