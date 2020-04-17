import AgnosticZooming as az
import AgnosticZooming as az2 
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

V = [1, 0.2]
THETA_H = 0.9
F = np.array([[1,0], [1-THETA_H, THETA_H]])
contract_param = [F, V] 

## Run for diff phi 
def plot_diff_phi(granularity, steps, iteration) :
    T = steps  
    PHI = [0.01*i for i in range(1,granularity + 1)]
    fig = plt.figure()
    for strat, strat_name in zip([az, az2],["az", "az2"]) : 
        avg_utility = []
        for idx, phi in enumerate(PHI):
            acc_utility = []
            for _ in range(iteration):
                utility = strat.agnostic_zooming(phi,T,contract_param)  
                acc_utility.append(sum(utility)/len(utility))
            exp_utility = sum(acc_utility)/len(acc_utility)
            if idx % 10 == 0: 
                print("We have run {0} iterations({1:.0%})".format(idx, idx / granularity))  
            avg_utility.append(exp_utility)

        plt.plot(PHI, avg_utility, label = strat_name) 
        plt.ylim(-0.2, 0.5)
    
    plt.legend() 
    fig.gca().set_xlabel(r'$\phi$')
    fig.gca().set_ylabel('Average Utility') 
    fig.savefig('./two_type.jpg')

## Run for single phi 
def plot_phi_performance(phi, iteration, steps) : 
    T = steps 
    acc_utility = np.zeros(T)
    for _ in range(iteration):
        utility = az.agnostic_zooming(phi,T, contract_param)
        acc_utility += np.array(utility)
    avg_utility = np.array(acc_utility)/iteration

    fig = plt.figure()
    l = plt.plot([i for i in range(T)], avg_utility)
    plt.ylim(-0.2, 0.5)
    plt.plot([i for i in range(T)], avg_utility)
    fig.savefig('./phi-{0}.jpg'.format(phi)) 

def main() : 
    if args.plot_diff_phi : 
        plot_diff_phi(args.granularity, args.steps, args.iteration) 
    
    if args.plot_phi_perf:
        plot_phi_performance(args.phi, args.iteration, args.steps) 

if __name__ == "__main__":
    main()     