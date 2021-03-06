import numpy as np
import h5py
import matplotlib.pyplot as plt
import testCases #参见资料包，或者在文章底部copy
from dnn_utils import sigmoid, sigmoid_backward, relu, relu_backward #参见资料包
import lr_utils #参见资料包，或者在文章底部copy

np.random.seed(1)

def initialize_parameters(n_x,n_h,n_y):
    #初始化W，B
    W1 = np.random.randn(n_h,n_x) * 0.01
    b1 = np.zeros(shape=(n_h,1))
    W2 = np.random.randn(n_y,n_h) * 0.01
    b2 = np.zeros(shape=(n_y,1))

    parameters = {
        "W1":W1,
        "b1":b1,
        "W2":W2,
        "b2":b2
    }

    return parameters


def initialize_parameters_deep(layers_dims):#youwenti
    np.random.seed(3)
    parameters = {}
    L = len(layers_dims)

    for l in range(1, L):
        parameters["W" + str(l)] = np.random.randn(layers_dims[l], layers_dims[l - 1]) / np.sqrt(layers_dims[l - 1])
        parameters["b" + str(l)] = np.zeros((layers_dims[l], 1))

    # 确保我要的数据的格式是正确的
        assert (parameters["W" + str(l)].shape == (layers_dims[l], layers_dims[l - 1]))
        assert (parameters["b" + str(l)].shape == (layers_dims[l], 1))

    return parameters

def linear_forward(A,W,b):
    Z = np.dot(W,A)+b
    A_prev = A
    cache = (A_prev,W,b)
    return (Z,cache)

def linear_activation_forward(A_prev,W,b,activation):
    if(activation == "sigmoid"):
        Z,linear_cache = linear_forward(A_prev,W,b)
        A,activation_cache = sigmoid(Z)
    elif (activation == "relu"):
        Z,linear_cache = linear_forward(A_prev,W,b)
        A,activation_cache = relu(Z)

    cache = (linear_cache,activation_cache)
    return (A,cache)    # 当前层新生成的A，上一次的A_prev，本层的W，b，本层生成的Z


def L_model_forward(X,parameters):
    caches = []
    A = X
    L = len(parameters)//2
    #前L-1层使用ReLU迭代向前传播，每层传播完把A，W，b记录下来
    for l in range(1,L):
        A_prev = A  #相当于A[0] = X
        A,cache = linear_activation_forward(A_prev,parameters["W"+str(l)],parameters["b"+str(l)],"relu")
        #更新A和每层的新的输出A
        #cache里面装的是对于层L而言，上一层传过来的输出A[L-1]，本层的W_L和W_b
        caches.append(cache)

    AL,cache = linear_activation_forward(A,parameters["W"+str(L)],parameters["b"+str(L)],"sigmoid")
    #使用最后一层的sigmoid激活函数,AL是最终的输出
    caches.append(cache)
    assert (AL.shape == (1, X.shape[1]))
    return AL, caches

def compute_cost(AL,Y):

    m = Y.shape[1]

    temp = np.multiply(Y,np.log(AL))+np.multiply(1-Y,np.log(1-AL))

    cost = -np.sum(temp,axis=1,keepdims= True)/m

    cost = np.squeeze(cost)

    return cost

def linear_backward(dZ,cache):


    A_prev,W,b = cache
    m = A_prev.shape[1]

    dW = np.dot(dZ,A_prev.T)/m
    db = np.sum(dZ,axis = 1,keepdims= True)/m
    dA_prev = np.dot(W.T,dZ)

    return dA_prev, dW, db


def linear_activation_backward(dA,cache,activation="relu"):

    linear_cache,activation_cache = cache

    #linear_cache:A_prev,W,b
    #activation_cache:Z

    if(activation == "sigmoid"):
        dZ = sigmoid_backward(dA,activation_cache)
        dA_prev,dW,db = linear_backward(dZ,linear_cache)

    elif(activation == "relu"):
        dZ = relu_backward(dA,activation_cache)
        dA_prev,dW,db = linear_backward(dZ, linear_cache)

    return dA_prev,dW,db

def L_model_backward(AL,Y,caches):

    grads = {}
    L = len(caches)                                     #L代表层的数量
    dAL = -(np.divide(Y,AL)-np.divide((1-Y),(1-AL)))    #第一部反向传播时用到的dAL要初始化

    #使用最后一层的cache数据:A_[L-1] W[L] b[L]
    #注意caches数组是从0开始的，因此caches代表最后一层的cache数据
    current_cache = caches[L-1]
    grads["dA" + str(L-1)], grads["dW" + str(L)], grads["db" + str(L)] = linear_activation_backward(dAL, current_cache,"sigmoid")
    #因为linear_activation_backward得到的是dA_prev，dW，dB 即dA[L-1],dW[L],db[L]，所以第一项dA记作"dA_[L-1]"


    for l in reversed(range(L-1)):
        current_cache = caches[l]
        dA_prev_temp,dW_temp,db_temp = linear_activation_backward(grads["dA"+str(l+1)],current_cache,"relu")
        grads["dA" + str(l)] = dA_prev_temp
        grads["dW" + str(l + 1)] = dW_temp
        grads["db" + str(l + 1)] = db_temp

    return grads

def update_parameters(parameters,grads, learning_rate):

    L = len(parameters) // 2
    for l in range(L):
        parameters["W"+str(l+1)] = parameters["W"+str(l+1)] - learning_rate * grads["dW" + str(l + 1)]
        parameters["b" + str(l + 1)] = parameters["b" + str(l + 1)] - learning_rate * grads["db" + str(l + 1)]

    return parameters


def two_layer_model(X, Y, layers_dims, learning_rate=0.0075, num_iterations=3000, print_cost=False, isPlot=True):
    np.random.seed(1)
    grads = {}
    costs = []
    (n_x, n_h, n_y) = layers_dims
    #n_x:数据维数
    #n_h：隐藏层节点数
    #n_y：输出层节点数

    """
    初始化参数
    """
    parameters = initialize_parameters(n_x, n_h, n_y)

    W1 = parameters["W1"]
    b1 = parameters["b1"]
    W2 = parameters["W2"]
    b2 = parameters["b2"]

    """
    开始进行迭代
    """
    for i in range(0, num_iterations):
        # 前向传播
        A1, cache1 = linear_activation_forward(X, W1, b1, "relu")
        A2, cache2 = linear_activation_forward(A1, W2, b2, "sigmoid")

        # 计算成本
        cost = compute_cost(A2, Y)

        # 后向传播
        ##初始化后向传播
        dA2 = - (np.divide(Y, A2) - np.divide(1 - Y, 1 - A2))

        ##向后传播，输入：“dA2，cache2，cache1”。 输出：“dA1，dW2，db2;还有dA0（未使用），dW1，db1”。
        dA1, dW2, db2 = linear_activation_backward(dA2, cache2, "sigmoid")
        dA0, dW1, db1 = linear_activation_backward(dA1, cache1, "relu")

        ##向后传播完成后的数据保存到grads
        grads["dW1"] = dW1
        grads["db1"] = db1
        grads["dW2"] = dW2
        grads["db2"] = db2

        # 更新参数
        parameters = update_parameters(parameters, grads, learning_rate)
        W1 = parameters["W1"]
        b1 = parameters["b1"]
        W2 = parameters["W2"]
        b2 = parameters["b2"]

        # 打印成本值，如果print_cost=False则忽略
        if i % 100 == 0:
            # 记录成本
            costs.append(cost)
            # 是否打印成本值
            if print_cost:
                print("第", i, "次迭代，成本值为：", np.squeeze(cost))
    # 迭代完成，根据条件绘制图
    if isPlot:
        plt.plot(np.squeeze(costs))
        plt.ylabel('cost')
        plt.xlabel('iterations (per tens)')
        plt.title("Learning rate =" + str(learning_rate))
        plt.show()

    # 返回parameters
    return parameters

def predict(X, y, parameters):
    """
    该函数用于预测L层神经网络的结果，当然也包含两层

    参数：
     X - 测试集
     y - 标签
     parameters - 训练模型的参数

    返回：
     p - 给定数据集X的预测
    """

    m = X.shape[1]
    n = len(parameters) // 2  # 神经网络的层数
    p = np.zeros((1, m))

    # 根据参数前向传播
    probas, caches = L_model_forward(X, parameters)

    for i in range(0, probas.shape[1]):
        if probas[0, i] > 0.5:
            p[0, i] = 1
        else:
            p[0, i] = 0

    print("准确度为: " + str(float(np.sum((p == y)) / m)))

    return p


def L_layer_model(X, Y, layers_dims, learning_rate=0.0075, num_iterations=3000, print_cost=False,isPlot=True):
    costs = []
    parameters = initialize_parameters_deep(layers_dims)
    for i in range(num_iterations):
        Al,caches = L_model_forward(X,parameters)
        #AL是最终sigmoid后的输出,cache里面装的是各层的信息
        # 例如对于第一层：cache[0]={A_0,W_1,b_1}

        cost = compute_cost(Al,Y)
        #利用最终输出计算损失函数

        grads = L_model_backward(Al,Y,caches)
        #反向传播，得到梯度

        parameters = update_parameters(parameters,grads,learning_rate)

        if i % 100 == 0:
            # 记录成本
            costs.append(cost)
            # 是否打印成本值
            if print_cost:
                print("第", i, "次迭代，成本值为：", np.squeeze(cost))

    if isPlot:
        plt.plot(np.squeeze(costs))
        plt.ylabel('cost')
        plt.xlabel('iterations (per tens)')
        plt.title("Learning rate =" + str(learning_rate))
        plt.show()
    return parameters

train_set_x_orig , train_set_y , test_set_x_orig , test_set_y , classes = lr_utils.load_dataset()

train_x_flatten = train_set_x_orig.reshape(train_set_x_orig.shape[0], -1).T
test_x_flatten = test_set_x_orig.reshape(test_set_x_orig.shape[0], -1).T

train_x = train_x_flatten / 255
train_y = train_set_y
test_x = test_x_flatten / 255
test_y = test_set_y

n_x = 12288
n_h = 8
n_y = 1
layers_dims = (n_x,n_h,n_y)

layers_dims = [12288, 20, 7, 5, 1] #  5-layer model
parameters = L_layer_model(train_x, train_y, layers_dims, num_iterations = 2500, print_cost = True,isPlot=True)

predictions_train = predict(train_x, train_y, parameters) #训练集
predictions_test = predict(test_x, test_y, parameters) #测试集

