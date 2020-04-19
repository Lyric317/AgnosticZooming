import AgnosticZooming as az
import AgnosticZooming2 as az2 
import matplotlib.pyplot as plt
import numpy as np
import argparse
import os

parser = argparse.ArgumentParser(description='Dynamic Constract Experiment') 
parser.add_argument('--plot-diff-phi', const = False, nargs = '?')
parser.add_argument('--plot-phi-perf', const = False, nargs = '?')
parser.add_argument('--iteration', const = 100, default = 100, nargs = '?', type = int)
parser.add_argument('--steps', const = 2000, default = 5000, nargs = '?', type = int) 
parser.add_argument('--phi', const = 0.02, default = 0.02, nargs = '?', type = float)
parser.add_argument('--granularity', const = 30, default = 30, nargs = '?', type = int)   
args = parser.parse_args()

V = [0.3, 1]
THETA_H = 0.8
F = np.array([[1,0], [1-THETA_H, THETA_H]])
contract_param = [F, V] 
TYPE = ["uniform", "two type", "homo"]

## moving average for plot 
def moving_average(dta, window):
    shape = dta.shape 
    i = 0 
    new_dta = np.zeros(shape)
    while i <= shape[0] - 1:
        if i < window : 
            new_dta[i] = dta[i]
        else : 
            new_dta[i] = np.mean(dta[i-window:i])
        i += 1 
    return new_dta 

## Run for diff phi 
def plot_diff_phi(granularity, steps, iteration) :
    T = steps  
    PHI = [0.01*i for i in range(1,granularity + 1)]
    for type in TYPE : 
        fig = plt.figure()
        for strat, strat_name in zip([az, az2],["az", "az2"]) : 
            avg_utility = []
            for idx, phi in enumerate(PHI):
                acc_utility = []
                for _ in range(iteration):
                    utility = strat.agnostic_zooming(phi,T,contract_param, type)   
                    acc_utility.append(np.mean(utility)) 
                exp_utility = sum(acc_utility)/len(acc_utility)
                if idx % 10 == 0: 
                    print("We have run {0} iterations({1:.0%})".format(idx, idx / granularity))  
                avg_utility.append(exp_utility)

            plt.plot(PHI, avg_utility, label = strat_name) 
            plt.ylim(-0.5, 0.5)
        
        plt.legend() 
        plt.title("{0} market".format(type)) 
        fig.gca().set_xlabel(r'$\phi$')
        fig.gca().set_ylabel('Average Utility') 
        fig.savefig('./{0}.jpg'.format(type)) 

## Run for single phi 
def plot_phi_performance(phi, iteration, steps) : 
    T = steps 
    
    for type in TYPE : 
        fig = plt.figure()
        for strat, strat_name in zip([az, az2],["az", "az2"]) : 
            acc_utility = np.zeros(T)
            for idx in range(iteration):
                utility = strat.agnostic_zooming(phi,T, contract_param, type) 
                acc_utility += np.array(utility)
            avg_utility = acc_utility / iteration
            
            mov_avg_utility = moving_average(avg_utility, 30)
            l = plt.plot([i for i in range(T)], mov_avg_utility, label = strat_name)
        
        plt.ylim(-0.5, 0.5)
        plt.title("{0} market".format(type)) 
        plt.xlabel("Steps")
        plt.ylabel("Average Utility")
        plt.legend()
        fig.savefig('./phi-{0}-{1}.jpg'.format(phi, type))  

def main() : 
    if args.plot_diff_phi : 
        plot_diff_phi(args.granularity, args.steps, args.iteration) 
    
    if args.plot_phi_perf:
        plot_phi_performance(args.phi, args.iteration, args.steps) 

if __name__ == "__main__":
    main()     