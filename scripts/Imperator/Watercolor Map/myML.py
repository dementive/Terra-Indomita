## Created and maintained by Pablo Arbelo Cabrera
## Feel free to use it however you want

import numpy as np

from scipy.special import xlogy
from scipy.special import xlog1py

import dill as pickle

from tqdm.notebook import tqdm

#############################################################
"""
Feed Forward Neural Networks
"""
#############################################################
## Activation functions
def tanh(x):
    return np.tanh(x)
def d_tanh(x):
    return 1-np.square(np.tanh(x))

def sigmoid(x):
    return 1/(1 + np.exp(-x))
def d_sigmoid(x):
    return (1 - sigmoid(x)) * sigmoid(x)

def leakyReLU(x, alpha=0.01):
    return np.maximum(alpha*x,x)
def d_leakyReLU(x, alpha=0.01):
    temp = np.sign(x)
    return np.maximum(alpha*temp,temp)

def ReLU(x):
    return np.maximum(0,x)
def d_ReLU(x):
    temp = np.sign(x)
    return np.maximum(0,temp)

def linear(x):                                          #Only used usually as output layer activation function
    return x
def d_linear(x):
    return np.sign(x)

def softmax(x):                                         #Sum of outputs = 1, pseudoprobability
    e_x = np.exp(x-np.max(x))
    return e_x / e_x.sum(axis=0)
def d_softmax(x):
    temp = softmax(x)
    J = - temp[:, None, :] * temp[None, :, :]
    diagIndex = np.arange(x.shape[0])
    J[diagIndex, diagIndex, :] = temp * (1. - temp)
    return J

class Layer:
    activationFunctions = {
        'sigmoid': (sigmoid, d_sigmoid),
        'softmax': (softmax, d_softmax),
        'tanh': (tanh, d_tanh),
        'ReLU': (ReLU, d_ReLU),
        'leakyReLU': (leakyReLU, d_leakyReLU),
        'linear': (linear, d_linear)
    }

    def __init__(self, inputs, neurons, activationF):                   #Number of inputs, neurons & type of activation function
        self.w = np.random.randn(neurons, inputs) * np.sqrt(2./inputs)  #He-et-al initialization of weights
        self.b = np.zeros((neurons, 1))                                 #Initial biases
        self.act, self.d_act = self.activationFunctions.get(activationF)

        self.m_dw = np.zeros((neurons, inputs))                         #First and second moments, mean and uncentered variance, weights
        self.v_dw = self.m_dw
        self.m_db = np.zeros((neurons, 1))                              #First and second moments, mean and uncentered variance, biases
        self.v_db = self.m_db

    def feedforward(self, x):
        self.x = x                                                      #Input from the previous layer
        self.m = x.shape[1]                                             #Size of the batch
        self.z = self.w @ self.x + self.b @ np.ones((1, self.m))        #Inputs times weights plus biases
        self.y = self.act(self.z)                                       #Output from the current layer
        return self.y
    
    def backprop(self, dJdy, learning_rate, lambd, epoch):
        if self.d_act==d_softmax:
            dJdz = np.einsum('mnr,nnr->nr', dJdy[None,:,:], self.d_act(self.z))
        else: dJdz = np.multiply(dJdy, self.d_act(self.z))              #dJdyl+1 * g'l = dJdz
        dJdw = dJdz @ self.x.T                                          #dJdz * al-1 = dJdw
        dJdb = dJdz @ np.ones((1, self.m)).T                            #dJdz * 1 = dJdb
        dJdx = self.w.T @ dJdz                                          #Information for the next layer

        reg = lambd/self.m*self.w                                       #Regularization term, only applied to the weights
        dJdw += reg

        self.w -= learning_rate * dJdw
        self.b -= learning_rate * dJdb
        return dJdx
    
    def Adam_backprop(self, dJdy, learning_rate, lambd, epoch, beta1=0.9, beta2=0.999, epsilon=1e-07):
        if self.d_act==d_softmax:
            dJdz = np.einsum('mnr,nnr->nr', dJdy[None,:,:], self.d_act(self.z))
        else: dJdz = np.multiply(dJdy, self.d_act(self.z))              #dJdyl+1 * g'l = dJdz
        dJdw = dJdz @ self.x.T                                          #dJdz * al-1 = dJdw
        dJdb = dJdz @ np.ones((1, self.m)).T                            #dJdz * 1 = dJdb
        dJdx = self.w.T @ dJdz                                          #Information for the next layer

        reg = lambd/self.m*self.w                                       #Regularization term, only applied to the weights
        dJdw += reg

        self.m_dw = beta1*self.m_dw + (1-beta1)*dJdw                    #Mean
        self.m_db = beta1*self.m_db + (1-beta1)*dJdb

        self.v_dw = beta2*self.v_dw + (1-beta2)*np.power(dJdw, 2)       #Variance
        self.v_db = beta2*self.v_db + (1-beta2)*np.power(dJdb, 2)

        m_corr = 1-beta1**epoch                                         #Bias corrector terms
        v_corr = 1-beta2**epoch

        self.w -= learning_rate * np.divide(self.m_dw/m_corr, np.power(self.v_dw/v_corr,0.5)+epsilon)
        self.b -= learning_rate * np.divide(self.m_db/m_corr, np.power(self.v_db/v_corr,0.5)+epsilon)
        return dJdx

## Loss functions
def logloss(y_true, y_pred):                           #Cross-entropy, log loss --> Classification problems
    m = y_true.shape[1]

    #return -1/m*(y_true*np.log(y_pred) + (1-y_true)*np.log(1-y_pred))
    return np.sum(-(xlogy(y_true, y_pred) + xlog1py(1-y_true, -y_pred)))/m
def d_logloss(y_true, y_pred):
    m = y_true.shape[1]
    return 1/m*(y_pred - y_true)/(y_pred - y_pred**2+1e-20)

def MSE(y_true, y_pred):                                           #Mean squared error  --> Regression without outliers
    m = y_true.shape[1]
    return np.sum(2*(y_true-y_pred)**2)/m
def d_MSE(y_true, y_pred):
    m = y_true.shape[1]
    return 1/m*(y_pred-y_true)

#Feed Forward Neural Network ([list with nodes per layer], [list with the name of the desired activation function in each non-input layer], [loss function name])
#@run (X[m,d])
class ANN:
    lossfunctions = {
        'logloss': (logloss, d_logloss),
        'MSE': (MSE, d_MSE)
    }

    ## Model definition
    def __init__(self, nodes=None, activation=None, lossname=None):
        if nodes!=None:
            self.nlayers = len(activation)
            self.nodes = nodes
            if len(activation)!=(len(nodes)-1): print('Error, check activation vector length = node array length')

            self.Xnorm, self.Ynorm = False, False
            # Layer creation
            self.layers = [None]*self.nlayers
            for i in range(self.nlayers):
                self.layers[i] = Layer(nodes[i],nodes[i+1],activation[i])
            self.loss, self.d_loss = self.lossfunctions.get(lossname)

    def defineNorm(self, normType, dataset=False, minimum=False, maximum=False):
        if normType=='Input':
            self.Xnorm = norm0to1(dataset=dataset, minimum=minimum, maximum=maximum)
        elif normType=='Output':
            self.Ynorm = norm0to1(dataset=dataset, minimum=minimum, maximum=maximum)
        else: raise ValueError('Incorrect normType')
    
    ## Model feedforward
    def run(self, x):
        if self.Xnorm is not False: x = self.Xnorm.normalize(x)
        x = self.typeChecks(x)
        if x.shape[0]!=self.nodes[0]: raise ValueError(f'Dimensions do not match; {x.shape[0]} vs {self.nodes[0]}')

        for layer in self.layers:
            x = layer.feedforward(x)
        y = x.T
        if self.Ynorm is not False: y = self.Ynorm.recover(y)
        return y

    ## Special initialization through genetic algorithm
    def trainGA(self, x_train, y_train, generations, popsize, iniOffspring=2, maxminMutation=[0.8,0.02], tqdmDisable=False):
        if self.Xnorm is not False: x_train = self.Xnorm.normalize(x_train)
        if self.Ynorm is not False: y_train = self.Ynorm.normalize(y_train)
        x_train, y_train = self.typeChecks(x_train), self.typeChecks(y_train)
        if x_train.shape[0]!=self.nodes[0]: raise ValueError(f'Dimensions do not match; {x_train.shape[0]} vs {self.nodes[0]}')
        
        maximum = []
        for layer in range(self.nlayers):
            nInputs = self.nodes[layer]
            nNeurons = self.nodes[layer+1]

            maximum.extend([1]*nNeurons)
            factor = np.sqrt(2./nInputs)
            maximum.extend([factor]*(nNeurons*nInputs))
        minimum = [-x for x in maximum]

        def func(array):
            return self.saveRunGA(x_train, y_train, array)

        array, gaCost = GA(lmax=maximum, lmin=minimum, func=func, generations=generations, popsize=popsize, iniOffspring=iniOffspring, 
                            maxminMutation=maxminMutation, tqdmDisable=tqdmDisable)
        self.saveGA(array.T[:,0])
        return gaCost

    def saveRunGA(self, x_train, y_train, array):
        self.saveGA(array.T[:,0])

        y = self.trainRun(x_train)
        J = self.loss(y_train, y)
        return J

    def saveGA(self, array1D):
        count = 0
        for layer in range(self.nlayers):
            nInputs = self.nodes[layer]
            nNeurons = self.nodes[layer+1]
            #Bias
            self.layers[layer].b[:] = np.array(array1D[count:count+nNeurons]).reshape((nNeurons,1))
            count += nNeurons
            #Weights
            self.layers[layer].w[:,:] = np.array(array1D[count:count+nNeurons*nInputs]).reshape((nNeurons,nInputs))
            count += nInputs*nNeurons
        
    ## Model training
    def trainRun(self, x):
        for layer in self.layers:
            x = layer.feedforward(x)
        return x

    def train(self, x_train: np.ndarray, y_train: np.ndarray, epochs, optimizer, lr, lambd, batchSize: int=0, trainTestSplit=0.9, tqdmDisable=False):
        if self.Xnorm is not False: x_train = self.Xnorm.normalize(x_train)
        if self.Ynorm is not False: y_train = self.Ynorm.normalize(y_train)
        x_train, y_train = self.typeChecks(x_train), self.typeChecks(y_train)
        if x_train.shape[0]!=self.nodes[0]: raise ValueError(f'Dimensions do not match; {x_train.shape[0]} vs {self.nodes[0]}')

        nData = x_train.shape[1]
        if batchSize==0: nBatches=1
        else: nBatches = int(round(nData*trainTestSplit/batchSize))
        if nBatches==0: raise ValueError('batchSize bigger than number of datapoints')
        
        idxTrain = np.arange(round(nData*trainTestSplit))
        idxTest = [idx for idx in np.arange(nData) if idx not in idxTrain]
        x_batch = np.array_split(x_train[...,idxTrain], nBatches, axis=1)
        y_batch = np.array_split(y_train[...,idxTrain], nBatches, axis=1)

        #Adam
        if optimizer=='Adam':
            #Recommended values for many cases: lr = 0.001, beta1 = 0.9, beta2 = 0.999, epsilon = 1e-07
            backpropMethod = 'Adam_backprop'
            parameters = {'beta1': 0.9, 'beta2': 0.999, 'epsilon': 1e-07}    
        #Gradient descent
        elif optimizer=='GD':
            backpropMethod = 'backprop'
            parameters = {}
        else:
            raise ValueError('No optimizer found. This library offers GD, BatchGD and Adam')

        # Main loop
        costs, Jtest = [[],[]], None
        bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [t-{elapsed}, eta-{remaining}, {rate_fmt}{postfix}]'
        pbar = tqdm(range(1,epochs+1), desc='Epochs', disable=tqdmDisable, bar_format=bar_format)
        for epoch in pbar:
            for i in range(nBatches):
                y = self.trainRun(x_batch[i])

                dJdy = self.d_loss(y_batch[i], y)
                for layer in reversed(self.layers):
                    dJdy = getattr(layer, backpropMethod)(dJdy, lr, lambd, epoch, **parameters)
            
            if nBatches!=1: y = self.trainRun(x_train[...,idxTrain])
            Jtrain = self.loss(y_train[...,idxTrain], y)

            if trainTestSplit!=1: 
                y = self.trainRun(x_train[...,idxTest])
                Jtest = self.loss(y_train[...,idxTest], y)
                pbar.set_postfix_str(f'loss: {Jtrain:.4e}, testLoss: {Jtest:.4e}')
            else: pbar.set_postfix_str(f'loss: {Jtrain:.4e}')
            costs[0].append(Jtrain), costs[1].append(Jtest)
        
        return costs
    
    ## Model storage
    def storeClass(self, name):
        with open(name+'.pickle', 'wb') as file: #wb is necessary, write-binary
            file.write(pickle.dumps(self.__dict__))

    def loadClass(self, name):
        with open(name+'.pickle', 'rb') as file: #rb is necessary, read-binary
            self.__dict__ = pickle.loads(file.read())

    ## Other
    def typeChecks(self, x):
        x = np.array(x)
        if x.ndim==0: x = np.expand_dims(x, axis=(0,1)) 
        if x.ndim==1: x = np.expand_dims(x, axis=1)
        x = x.T
        if type(x) != np.ndarray: raise ValueError('X and Y must be ndarrays, not np.matrix or similar')

        return x
        

#############################################################
"""
Gaussian Process
"""
#############################################################
##Kernels
def exponentiatedquadratic(deltax, theta):
    Kij = np.exp(-theta*np.sum(deltax**2, axis=0))
    return Kij

#Gaussian Process Regression (kernel's name)
#@fit (X[d,m], y[1,m]) (Introduce training data)
#@predict (X[d,m]) (Request predictions on a test set)
#@score (X[d,m], y[1,m]) (Predicts y* based on a test set X and compares to the true y)
class GaussianProcess: ## HAVE TO FIX TO X[m,d]
    kernel_list = {
        'gaussian': exponentiatedquadratic
    }

    def __init__(self, kernel):
        self.kernel = self.kernel_list.get(kernel)

    #Makes the correlation matrix from the feature matrix (n features, m samples)
    def Corr(self, X1, X2, theta):
        K = np.zeros((X1.shape[1],X2.shape[1]))
        for i in range(X1.shape[1]):
            for j in range(X2.shape[1]):
                K[i,j] = self.kernel(X1[:,i] - X2[:,j], theta)

        return K
    
    def likelihood(self, theta):
        theta = 10**(theta)
        m_train = self.X.shape[1]
        one = np.ones((m_train, 1))

        K = self.Corr(self.X, self.X, theta) + np.eye(m_train)*1e-10
        K_inv = np.linalg.pinv(K)

        #Optimum mean for maxL
        mu = (one.T @ K_inv @ self.y.T) / (one.T @ K_inv @ one)
        #Optimum variance for maxL
        var = (self.y.T-mu*one).T @ K_inv @ (self.y.T - mu*one) / m_train

        #Log likelihood
        lnL = -(m_train/2)*np.log(var) - 0.5*np.log( np.linalg.det(K) )
        self.K, self.K_inv, self.mu, self.var = K, K_inv, mu, var
        return lnL.flatten()

    def fit(self, X, y, iters):
        self.X, self.y = X, y
        theta_upper = [2]
        theta_lower = [-3]

        #Optimize
        self.theta = SA(theta_upper, theta_lower, self.likelihood, iters)
        self.lnL = self.likelihood(self.theta)
        self.theta = 10**(self.theta)
        print(self.theta)

    def predict(self, X_test):
        m_train = self.X.shape[1]
        one = np.ones((m_train, 1))

        #Correlation matrix between test and train samples
        K_test = self.Corr(self.X, X_test, self.theta)

        #Mean prediction and variance
        mu_test = self.mu + (K_test.T @ self.K_inv @ (self.y.T-self.mu*one)).T
        var_test = self.var * (1 - np.diag(K_test.T @ self.K_inv @ K_test).T)
        return mu_test, var_test

    def score(self, X_test, y_test):
        y_pred, var = self.predict(X_test)
        RMSE = np.sqrt(np.mean((y_pred - y_test)**2))
        return RMSE


#############################################################
"""
Kriging
"""
#############################################################
def basisfunc(x, p, theta):
    phi = np.exp(-theta*np.sum(np.abs(x)**p))
    return phi

#Kriging (TrainingInput[d,m], TrainingOutput[1,m])
#@interpol (X[d,m])
class kriging:  ## HAVE TO FIX TO X[m,d]
    def __init__(self, trainx, trainy):
        self.n = trainx.shape[1]
        self.tx = trainx
        self.ty = trainy
        self.mean = np.mean(trainy)

        self.optimizeptheta(iters=3000)
        print(self.p)
        print(self.theta)
        self.calculateweights()
    
    def lnL(self, vector):
        p = vector[0,0]
        theta = vector[1,0]
        R = np.zeros((self.n,self.n))
        for i in range(self.n):
            for j in range(self.n):
                R[i,j] = basisfunc(self.tx[0,j]-self.tx[0,i],p,theta)

        # Maximum likelihood estimate of the variance MLv
        MLv = (self.ty-self.mean) @ np.linalg.pinv(R) @ (self.ty-self.mean).T
        if MLv[0,0] < 1e-14: return float("NaN")
        lnL = (-self.n/2*np.log(MLv)-0.5*np.linalg.det(R))[0,0]
        return lnL

    def optimizeptheta(self, iters):
        lim_max = [2, 15]
        lim_min = [0, 0]
        x1 = SA(lim_max, lim_min, self.lnL, iters)
        self.p = x1[0,0]
        self.theta = x1[1,0]
        print(self.lnL(x1))
        return

    def calculateweights(self):
        R = np.zeros((self.n,self.n))
        for i in range(self.n):
            for j in range(self.n):
                R[i,j] = basisfunc(self.tx[0,j]-self.tx[0,i],self.p,self.theta)
        #Maximum likelihood estimate of the mean
        self.Rinv = np.linalg.pinv(R)
        self.MLm = np.sum(self.Rinv @ self.ty.T)/np.sum(self.Rinv)
        self.weights = (self.ty-self.MLm) @ self.Rinv
        return
    
    def interpol(self, points):
        m = points.shape[1]
        y = np.zeros((1,m))
        deviation = np.zeros((1,m))
        phinm = np.zeros((self.n,1))
        MLv = (self.ty-self.mean) @ self.Rinv @ (self.ty-self.mean).T
        
        for j in range(m):
            for i in range(self.n):
                phinm[i,0] = basisfunc(points[0,j]-self.tx[0,i],self.p,self.theta)
            y[0,j] = self.MLm + self.weights @ phinm
            deviation[0,j] = MLv*(1-phinm.T @ self.Rinv @ phinm + (1 - np.sum(self.Rinv @ phinm))/np.sum(self.Rinv))
            if deviation[0,j]<0: deviation[0,j] = deviation[0,j]*-1

        return y, deviation**0.5

    
#############################################################
"""
Global Optimization [continuous variables]
"""
#############################################################
#Simulated Annealing (maxlim=[1,10,-2...], minlim=[2,11,0...], @func to maximize, iters=1000)
def SA(lmax, lmin, func, iters):## HAVE TO FIX TO X[m,d]
    dim = len(lmax)
    norm = norm0to1(maximum=lmax, minimum=lmin)
    x = np.random.normal(0,1,(dim,1))
    y = func(norm.recover(x))
    Temperature = 4
    xnew = x*1
    for i in range(iters):
        c = (iters-i)/iters
        for d in range(dim):
            value = x[d,0]*(1-c)
            xnew[d,0] = np.random.uniform(value, value+c)
        ynew = func(norm.recover(xnew))
        Temperature = Temperature*0.9
        if np.isnan(ynew) or np.log(np.random.rand())*Temperature > (ynew-y): continue
        else: 
            x = xnew*1
            y = ynew*1
    return norm.recover(x)

#Particle Swarm Optimization (maxlim=[1,10,-2...], minlim=[2,11,0...], @func to maximize, iters=1000)
def PSO(lmax, lmin, func, iters):## HAVE TO FIX TO X[m,d]
    #Initial locations through LHS sampling
    d = len(lmax)
    norm = norm0to1(maximum=lmax, minimum=lmin)
    if d==1:
        npart = 2
        X = np.array([[0, 1]])
    else:
        npart = min(2**(2*d), 100)
        X = staticSampling('LHS', d, npart)

    #Initialization
    swarm = {
        'p': {},        #Individual particle
        'sb': []        #Swarm best
    }
    for p in range(npart):
        swarm['p'][p] = {
            'st': {},
            'pb': {},
            've': {},
        }
        swarm['p'][p]['st'][0] = np.array([X[:,p]]).T
        swarm['p'][p]['st'][1] = func(norm.recover(swarm['p'][p]['st'][0]))
        swarm['p'][p]['pb'] = swarm['p'][p]['st'].copy()
        swarm['p'][p]['ve'][0] = np.zeros((d,1))
    swarm['sb'] = swarm['p'][np.random.choice(npart, 1)[0]]['st'].copy()
    
    #Hyperparameters
    wmax = 0.9  #Weight coefficient
    wmin = 0.4
    c1 = 2.05   #Cognitive (personal effect) coefficient
    c2 = 2.05   #Social (swarm effect) coefficient

    #Main loop, simultaneous updates
    for k in range(iters):
        w = (wmax-wmin)*(iters-k)/iters+wmax
        for p in range(npart):  #Swarm best
            if swarm['sb'][1]<swarm['p'][p]['st'][1]: swarm['sb'] = swarm['p'][p]['st'].copy()

        for p in range(npart):  #Update motion of each particle, as well as its personal best
            temp = np.random.uniform(0,1,2)
            swarm['p'][p]['ve'][0] = w*swarm['p'][p]['ve'][0] + temp[0]*c1*(swarm['p'][p]['pb'][0]-swarm['p'][p]['st'][0]) + temp[1]*c2*(swarm['sb'][0]-swarm['p'][p]['st'][0])
            swarm['p'][p]['st'][0] = swarm['p'][p]['st'][0] + 1/iters*swarm['p'][p]['ve'][0]
            for i in range(d):  #Check in case a particle ventures out of the limited domain
                if swarm['p'][p]['st'][0][i,0] > 1:
                    swarm['p'][p]['st'][0][i,0] = 1
                    swarm['p'][p]['ve'][0][i,0] = swarm['p'][p]['ve'][0][i,0]*0
                elif swarm['p'][p]['st'][0][i,0] < 0:
                    swarm['p'][p]['st'][0][i,0] = 0
                    swarm['p'][p]['ve'][0][i,0] = swarm['p'][p]['ve'][0][i,0]*0
            swarm['p'][p]['st'][1] = func(norm.recover(swarm['p'][p]['st'][0]))
            if swarm['p'][p]['st'][1]>swarm['p'][p]['pb'][1]: swarm['p'][p]['pb'] = swarm['p'][p]['st'].copy() #Particle best

    return norm.recover(swarm['sb'][0])

#Genetic Algorithm (maxlim=[1,10,-2...], minlim=[2,11,0...], @func to MINIMIZE, generations=300, populationsize=100, initial_offspring=2)
def GA(lmax, lmin, func, generations, popsize, iniOffspring=2, maxminMutation=[0.8,0.02], tqdmDisable=False):
    #Initial population through LHS sampling
    genes = len(lmax)
    halfGenes = round(genes/2)
    norm = norm0to1(maximum=lmax, minimum=lmin)
    if genes==1:
        X = np.random.uniform(0, 1, (popsize, genes))
    else:
        X = staticSampling('LHS', genes, popsize).T 

    # Sort results from lowest to highest
    Y = [func(norm.recover(X[i:i+1,:])) for i in range(popsize)]
    Y_sort = np.argsort(Y)
    nMutations = round(maxminMutation[0]*genes)

    #Main loop
    costs = []
    bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [t-{elapsed}, eta-{remaining}, {rate_fmt}{postfix}]'
    pbar = tqdm(range(1,generations+1), desc='Generations', disable=tqdmDisable, bar_format=bar_format)
    for g in pbar:
        elitistindex = Y_sort[:2]                               #The two best do not suffer changes
        deadBornindex = Y_sort[-iniOffspring:]                  #Death of the worst to give space to new specimens 
        for child in range(iniOffspring):                  #Crossover
            parentindex = np.random.choice(Y_sort[:-iniOffspring], size=2, replace=False)
            X[deadBornindex[child],:] = X[parentindex[0],:]

            geneSplit = np.random.choice(genes, size=halfGenes, replace=False)
            for gene in geneSplit:
                X[deadBornindex[child],gene] = X[parentindex[1],gene]
        
        for individual in range(popsize):               #Mutation
            if individual in elitistindex: continue
            mutationindex = np.random.choice(genes, size=nMutations, replace=False)
            for gene in mutationindex:
                X[individual,gene] = np.random.uniform(0,1)
        
        Y = [func(norm.recover(X[i:i+1,:])) for i in range(popsize)]
        Y_sort = np.argsort(Y)
        best = Y_sort[0]

        #Adaptive crossover: The better individuals become, the better it is to breed
        if iniOffspring<popsize*0.95 and g>generations*0.3: iniOffspring = min(iniOffspring+1, popsize-2)
        #Adaptive mutation: The earlier it is, the better it is to develop random mutations
        nMutations = round(genes*((maxminMutation[0]-maxminMutation[1])*(1-g/generations)+maxminMutation[1]))
        
        pbar.set_postfix_str(f'funcValue: {Y[best]}')
        costs.append(Y[best])

    return norm.recover(X[best:best+1,:]), costs 

#############################################################
"""
Normalization (norm0to1_minmax, norm0to1)
"""
#############################################################
#@Normalize or @recover a matrix of points (X[m,d])
class norm0to1: #Knowing the initial dataset
    '''
    Has to be either a pandas dataframe or np.array X[m,d], without strings
    '''
    def __init__(self, dataset=False, minimum=False, maximum=False):
        if dataset is False and minimum is False and maximum is False: raise ValueError('Introduce either the dataset or the limits for each dimension')
        elif minimum is not False and maximum is not False:
            self.d = len(maximum)
            self.max, self.min = np.array(maximum), np.array(minimum)
        else:
            self.d = dataset.shape[1]
            self.max, self.min = dataset.max(), dataset.min()

    def normalize(self, data):                  #X is a matrix with m rows/points and d columns/dimensions
        Y = self.check(data)
        Y = (Y-self.min)/(self.max-self.min)
        return Y

    def recover(self, normalizedData):
        Y = self.check(normalizedData)
        Y = Y*(self.max-self.min)+self.min
        return Y

    def check(self, data):
        if data.ndim==0: Y = np.expand_dims(data, axis=(0,1)) 
        elif data.ndim==1: Y = np.expand_dims(data, axis=1)
        else: Y = data
        
        if Y.shape[1] != self.d: raise ValueError(f'Unmatching dimensions: {self.d} vs. {data.shape[1]}')
        return Y

#############################################################
"""
Sampling Techniques (staticSampling)
"""
#############################################################
#Static Sampling (Type of LH, space dimension d, number of points p)
def staticSampling(ntype, d, npoints):## HAVE TO FIX TO X[m,d]
    p = npoints
    def fullrandom(p):                       #Uniformly spread randomized points
        matrix = np.zeros((d,p))    #Matrix with dimensions-rows and points-columns
        for j in range(p):
            matrix[:,j] = np.random.uniform(low=0, high=1, size=d)
        return matrix

    def fullfactorial(p):           #The given p is the number of divisions along the first dimension, the true number of points is (p+d-1)!/(d-1)!
        pd = p*1
        p = pd*1
        matrix = np.array([range(pd)])/(pd-1)
        for i in range(1,d):
            pd = pd+1
            p = p*pd
            matrixtemp = matrix*1
            matrix = np.concatenate((matrix, np.zeros((1,int(p/pd)))), axis=0)
            for j in range(1,pd):
                temp = np.concatenate((matrixtemp, np.ones((1,int(p/pd)))*j/(pd-1)), axis=0)
                matrix = np.concatenate((matrix, temp), axis=1)
        print(str(p)+' points')
        return matrix, p


    def LS(p):                        #Latin sample divided in p partitions, and a point in the middle to illustrate them
        psize = 1/p
        matrix = np.zeros((d,p))
        for i in range(d): matrix[i,:] = np.random.choice(p, p, replace=False)
        return (np.ones_like(matrix)*0.5+matrix)*psize

    def LSoptim(p):                   #LS optimized through pairwise random permutations
        matrix = LS(p)
        iters = int(p*2+800)

        for k in range(iters):
            points = np.random.choice(p,2,replace=False)
            dim = np.random.choice(d,1,replace=False)[0]
            temp = matrix[dim,points[0]]

            phiold = phip_reduced(matrix, p, points[0], points[1])
            matrix[dim,points[0]] = matrix[dim,points[1]]
            matrix[dim,points[1]] = temp
            phinew = phip_reduced(matrix, p, points[0], points[1])
            if phinew>phiold:
                matrix[dim,points[1]] = matrix[dim,points[0]]
                matrix[dim,points[0]] = temp
        return matrix

    def LHS(p):                               #LS with random points inside the partitions
        psize = 1/p
        matrix = LS(p)
        return np.random.uniform(low=matrix-0.1*psize*np.ones_like(matrix), high=matrix+0.1*psize*np.ones_like(matrix), size=(d,p))

    def LHSoptim(p):                          #LSoptim with random points inside the partitions
        psize = 1/p
        matrix = LSoptim(p)
        return np.random.uniform(low=matrix-0.1*psize*np.ones_like(matrix), high=matrix+0.1*psize*np.ones_like(matrix), size=(d,p))

    def SLHS(p):                               #Sliced Latin Hypercube Sample or Design, divided in T slices of LHS M partitions, resulting in t x m = p (points), ##WORK IN PROGRESS
        T = 3 #Levels of the categorical variable, nº of slices
        M = 4 #Points per slice
        p = M*T
        psize = 1/p
        X = {}
        matrix = np.zeros((d,p))
        for t in range(T):
            X[t] = np.zeros((d,M),dtype=int)
            for i in range(d): X[t][i,:] = np.random.choice(M, M, replace=False)
        for i in range(d):
            for m in range(M):
                temp = np.random.choice(np.arange(m*T,m*T+T),T,replace=False)
                for t in range(T):
                    index = np.where(X[t][i,:]==m)[0][0]
                    matrix[i,index+M*t] = temp[t]
        return np.random.uniform(low=psize*matrix, high=psize*matrix+psize*np.ones_like(matrix), size=(d,p))

    def TPLHS(p):                              #Translational Propagation Latin Hypercube Sample or Design
        nb = 2**d               #Number of blocks
        pb = int(np.ceil(p/nb)) #Number of points per block
        mp = int(pb*nb)         #Number of points before trimming the design to match p points

        if pb>1: seedl = LSoptim(int(pb))
        elif pb==1: seedl = 0.5*np.ones((d,1))
        X = seedl*(mp/2)-np.ones_like(seedl)

        for i in range(d):      #Construction of the LH
            temp = X[:,:] + np.ones_like(X)
            temp[i,:] = temp[i,:] + (mp/2-1)*np.ones_like(temp[i,:])
            X = np.concatenate((X, temp), axis=1)            

        for k in range(mp-p):   #Reducing and scaling to p points
            index = np.where(X[0,:]==np.amax(X[0,:]))[0][0]
            for i in range(d):
                for j in range(len(X[i,:])):
                    if j==index: continue
                    elif X[i,j]>X[i,index]: X[i,j] = X[i,j]-1
            X = np.delete(X, index, axis=1)
        return X*(1/(p-1))

    def iter_maximin(p):                       #Maximin design by iteration
        psize = 1/p
        matrix = fullrandom(p)
        iters = 150
        a = 1/iters*np.log(0.0001/0.1)

        for k in range(iters):
            step = 0.1*np.exp(a*k)

            for i in range(p):
                dold = d
                point = matrix[:,i]
                for j in range(p):
                    if i==j: continue
                    dnew = np.sum((point-matrix[:,j])**2)
                    if dnew<dold:
                        dold = dnew
                        index = j
                if distancetowall(point)<psize:
                    matrix[:,i] = (1-step)*point+0.5*step*np.ones(d)
                    continue
                matrix[:,i] = (1+step)*point-step*matrix[:,index]
        return matrix
   
    def phip_reduced(matrix, p, index1, index2):
        if p>160:                               #For very large values of p, we can't compute phi but it's equal to 1/mindist in the limit
            k_old = np.sqrt(np.sum((matrix[:,index1]-matrix[:,index2])**2))
            for j in range(p):
                if j==index1 or j==index2: continue
                k = np.sum((matrix[:,index1]-matrix[:,j])**2)**0.5
                if k<k_old: k_old = k
                k = np.sum((matrix[:,index2]-matrix[:,j])**2)**0.5
                if k<k_old: k_old = k
            return 1/k_old

        phi = np.sum((matrix[:,index1]-matrix[:,index2])**2)**(-0.5*p)
        for j in range(p):
            if j==index1 or j==index2: continue
            phi += np.sum((matrix[:,index1]-matrix[:,j])**2)**(-0.5*p)
            phi += np.sum((matrix[:,index2]-matrix[:,j])**2)**(-0.5*p)
        phi = phi**(1/p)
        return phi

    def distancetowall(vector):
        dist0 = np.amin(vector)
        dist1 = np.amax(vector)
        return np.minimum(dist0, 1-dist1)

    if ntype=='fullrandom': matrix = fullrandom(p)
    elif ntype=='fullfactorial': matrix, p = fullfactorial(p)
    elif ntype=='LS': matrix = LS(p)
    elif ntype=='LSoptim': matrix = LSoptim(p)
    elif ntype=='LHS': matrix = LHS(p)
    elif ntype=='LHSoptim': matrix = LHSoptim(p)
    elif ntype=='SLHS': matrix = SLHS(p)
    elif ntype=='TPLHS': matrix = TPLHS(p)
    elif ntype=='iter_maximin': matrix = iter_maximin(p)
    else: print('Error, LHS method not found')

    return matrix

#############################################################
"""
Miscellaneous
"""
#############################################################
class negative:
    def __init__(self, f):
        self.func = f
    def neg(self, x): return self.func(x)*-1