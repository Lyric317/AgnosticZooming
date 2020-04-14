import AgnosticZooming as az
import matplotlib.pyplot as plt

## Run for diff phi 
avg_utility = []
granularity = 30
PHI = [0.01*i for i in range(1,granularity + 1)]
for iteration, phi in enumerate(PHI):
    acc_utility = []
    for _ in range(10):
        utility = az.agnostic_zooming(phi)
        acc_utility.append(utility)
    exp_utility = sum(acc_utility)/len(acc_utility)
    if iteration % 10 == 0: 
        print("We have run {0} iterations({1:.0%})".format(iteration, iteration / granularity))  
    avg_utility.append(exp_utility)

fig = plt.figure()
l = plt.plot(PHI, avg_utility)
plt.ylim(-0.2, 0.5)
plt.plot(PHI, avg_utility)
plt.show()
fig.savefig('two_type.jpg')