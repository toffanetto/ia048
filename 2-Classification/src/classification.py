# @toffanetto

import numpy as np
import pandas as pd
import random

NUMBER_OF_CLASSES = 6
NUMBER_OF_ATRIBUTES = 561

STEP = 0.005

def getData(train, raw):
    
    if(train == True and raw == False):
    
        df_X = pd.read_csv("../data/UCI HAR Dataset/train/X_train.txt", sep="\s+", header=None)
        df_y = pd.read_csv("../data/UCI HAR Dataset/train/y_train.txt", names=["Class"])
        
        X = df_X.to_numpy()
        y = df_y.to_numpy()
        return X, y
    
    if(train == False and raw == False):
        df_X = pd.read_csv("../data/UCI HAR Dataset/test/X_test.txt", sep="\s+", header=None)
        df_y = pd.read_csv("../data/UCI HAR Dataset/test/y_test.txt", names=["Class"])
        
        X = df_X.to_numpy()
        y = df_y.to_numpy()
        return X, y
    
def softmax(x,w):
    n = w.shape
    y = np.zeros([x.shape[0],n[0]])
    n_class = np.zeros([x.shape[0]], dtype=np.uint8)
    num = np.zeros([n[0]])
    
    for j in range(x.shape[0]):
    
        for k in range(w.shape[0]):
            num[k] = np.sum((x[j]).dot(w[k].T))
            
        y[j] = np.exp(num)/np.sum(np.exp(num))
        
        n_class[j] = np.argmax(y[j])+1
    
    return y, n_class

def oneHotEncoding(y):
    y_ohe = np.zeros([len(y),NUMBER_OF_CLASSES])
    for i in range(len(y)):
        y_ohe[i,(y[i]-1)] = 1
    return y_ohe

def getJ_CE(y, X, W):
    y_hat, class_y_hat = softmax(X,W)
    J_CE = 0
    
    try:
        for i in range(y.shape[0]):
            for k in range(y.shape[1]):
                J_CE += y[i][k]*np.log(y_hat[i][k])
                
        J_CE /= (y.shape[0]*y.shape[1])
        
    except:
        y_hat = y_hat.T
        for k in range(y.shape[0]):
            J_CE += y[k]*np.log(y_hat[k])
            
        J_CE /= y.shape[0]
            
    return -(J_CE)
            
def getdJ_CEdW(y, y_hat, x):
    e = (y - y_hat)
    dJCE = (x.T*e).T
    
    return dJCE

def validateClassifier(y,X,W):
    y_hat, class_y_hat = softmax(X,W)
    
    hit = 0
    
    for i in range(len(y)):
        if class_y_hat[i] == y[i]:
            hit += 1
    
    return hit/len(y)

def trainClassifier(X, y,epochs,batch):
    W = np.zeros([epochs+1,NUMBER_OF_CLASSES,NUMBER_OF_ATRIBUTES])
    W[0] = np.random.rand(NUMBER_OF_CLASSES, NUMBER_OF_ATRIBUTES)/100 # Rand values in the interval (0, 0,01)
    
    hit_train = [0]
    hit_val = [0]
    J_train = []
    J_val = []
    J = 0
    
    x_val = X[np.int16(len(y)*0.7):len(y)]
    y_val = y[np.int16(len(y)*0.7):len(y)]
    
    X = X[0:np.int16(len(y)*0.7)]
    y = y[0:np.int16(len(y)*0.7)]
    
    y_ohe = oneHotEncoding(y=y)
    y_ohe_val = oneHotEncoding(y=y_val)
    
    r = list(range(len(y)))
    
    if(not batch):
        
        for k in range(epochs):
            random.shuffle(r)
            
            hit = 0
            J = 0

            for i in r:

                Xi = X[i, np.newaxis] 
                
                y_hat, class_y_hat = softmax(Xi,W[0])
                
                if(y[i] == class_y_hat):
                    hit += 1
                
                dJCE = getdJ_CEdW(y=y_ohe[i],y_hat=y_hat,x=Xi)
                
                W[0] = W[0] + STEP*dJCE
                
                #J += getJ_CE(y_ohe,X,W[0])
            
            #J_train.append(J/len(y))
            
            J_train.append(getJ_CE(y_ohe, X, W[0]))
            
            hit_train.append(hit/len(y))
                
            hit_val.append(validateClassifier(y_val,x_val,W[0]))
            J_val.append(getJ_CE(y_ohe_val,x_val,W[0]))
            
        W = W[0]
    
    else:
        
        for k in range(epochs):
            dJCE = 0
            
            hit = 0
            
            random.shuffle(r)

            for i in r:

                Xi = X[i, np.newaxis] 
                
                y_hat, class_y_hat = softmax(Xi,W[k])
                
                if(y[i] == class_y_hat):
                    hit += 1
                
                dJCE += getdJ_CEdW(y=y_ohe[i],y_hat=y_hat,x=Xi)
                
            W[k+1] = W[k] + STEP*dJCE/len(r)
                
            J_train.append(getJ_CE(y_ohe, X, W[k+1]))
            hit_train.append(hit/len(y))
            
            hit_val.append(validateClassifier(y_val,x_val,W[k+1]))
            J_val.append(getJ_CE(y_ohe_val,x_val,W[k+1]))
            
        W = W[np.argmax(hit_val)]
        
    #print(W)
    
    return W, hit_train, hit_val, J_train, J_val
    
def classify(x,W):
    y_hat, class_y_hat = softmax(x=x,w=W)
    return y_hat,class_y_hat

def rateModel(y,y_hat):
    hit_rate = 0
    not_hit_rate = 0
    confusion_matrix = np.zeros([NUMBER_OF_CLASSES,NUMBER_OF_CLASSES])
    
    for i in range(len(y)):
        confusion_matrix[y[i]-1, y_hat[i]-1] += 1
        if (y[i] == y_hat[i]):
            hit_rate += 1
        
    hit_rate /= len(y)
    not_hit_rate = 1 - hit_rate
        
    return confusion_matrix, hit_rate, not_hit_rate