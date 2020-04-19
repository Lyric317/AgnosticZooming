import numpy as np 

class environment(object) : 
    def __init__(self, contract_params) : 
        self.F, self.V = contract_params 
        self.C = 0  

    def cost_simulation(self, type, step) : 
        if type == "uniform" : 
            c_h1 = np.random.uniform(0.1, 0) #low effort level
            c_h2 = np.random.uniform(c_h1, 1) #high effort level
            self.C = [c_h1, c_h2] # unifrom 

        elif type == "two type" : 
            c_h1 = np.random.uniform(0.1, 0) #low effort level
            c_h2 = np.random.uniform(c_h1, 1, 2) #high effort level
            c_h2 = c_h2[0] if np.random.uniform(0,1) < 0.5 else c_h2[1] 
            self.C = [c_h1, c_h2] # two_type 
        
        elif type == "homo" : 
            if step == 1 : 
                c_h1 = np.random.uniform(0.1, 0) #low effort level
                c_h2 = np.random.uniform(c_h1, 1) #high effort level
                self.C = [c_h1, c_h2] # homo 

        return self.C

    def cal_utility(self, x):
        F, V, C = self.F, self. V, self.C  
        if np.max(np.matmul(F, np.array(x).T) - np.array(C)) < 0 : 
            return 0, 0, 0 
        action_idx = np.argmax(np.matmul(F, np.array(x).T) - np.array(C))
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

        Ux = Vx - Px #requester's utility
        
        return Vx, Px, Ux  