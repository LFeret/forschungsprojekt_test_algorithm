from time import sleep
import argparse
import json
import os
import tensorflow as tf
import numpy as np
import pickle, gzip
import argparse
import requests


CLASSES = 10
EPOCHS = 1


# model function, takes input matrix X = A^{(0)}
def f(X):
    # first affine layer
    A1 = tf.matmul(X, W1) + b1
    # relu layer
    A2 = tf.nn.relu(A1)
    # affine layer
    A3 = tf.matmul(A2, W3) + b3
    # relu layer
    A4 = tf.nn.relu(A3)
    # output layer, affine
    Y = tf.matmul(A4, W5) + b5

    # thoeretically: softmax layer
    return Y


def loss(Y, T):
    return tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits=Y, labels=T))


def get_arguments():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--exp_id',
        type=int,
        required=True,
        help='TODO: Its not clear yet, what exactly the exp_id is.'
    )

    parser.add_argument('--learning_rate', type=float, required=True, help='duh' )
    parser.add_argument('--size_hidden_layers', type=int, required=True, help='size of hidden layers' )
    parser.add_argument('--batch_size', type=int, required=True, help='duh again' )

    FLAGS = parser.parse_args()
    print(FLAGS)
    exp_id = FLAGS.exp_id
    B = FLAGS.batch_size
    LS = FLAGS.size_hidden_layers
    EPS = FLAGS.learning_rate

    return (exp_id, B, LS, EPS)


if __name__ == '__main__':
    exp_id, B, LS, EPS = get_arguments()

    if exp_id is None or exp_id < 0:
        raise Exception('The exp_id is missing!')

    url = 'http://filr.hs-fulda.de/ssf/s/readFile/share/287/-7665987564821315488/publicLink/MNIST.pkl.gz'
    r = requests.get(url, allow_redirects=True)
    open('MNIST.pkl.gz', 'wb').write(r.content)

    with gzip.open("./MNIST.pkl.gz") as df:
        data = pickle.load(df)

    samples = data["data_train"]
    dataShape = samples.shape
    labels = data["labels_train"]

    # creation; shuffling
    nrSamples = dataShape[0]
    allDataTF = tf.data.Dataset.from_tensor_slices((samples, labels)).shuffle(nrSamples)

    # train/test split
    nrTrainSamples = int(nrSamples * 0.7)
    nrTestSamples = int(nrSamples * 0.3)
    traindTF = allDataTF.take(nrTrainSamples)
    testdTF = allDataTF.skip(nrTrainSamples)

    # batching
    traindTF_batches = traindTF.batch(batch_size=B, drop_remainder=True).repeat()
    testdTF_batches = testdTF.batch(batch_size=B, drop_remainder=True).repeat()

    # create model variables
    Z0 = int(np.prod(dataShape[1:]))
    global W1
    global b1

    W1 = tf.Variable(tf.random.uniform([Z0, LS], -0.001, 0.001))
    b1 = tf.Variable(tf.random.uniform([1, LS], -0.001, 0.001 ))

    global W3
    global b3

    W3 = tf.Variable(tf.random.uniform([LS, LS], -0.01, 0.01))
    b3 = tf.Variable(tf.random.uniform([1, LS], -0.001, 0.001))

    global W5
    global b5

    W5 = tf.Variable(tf.random.uniform([LS, CLASSES], -0.001, 0.001))
    b5 = tf.Variable(tf.random.uniform([1, CLASSES], -0.001, 0.001))

    # training loop
    iterationsPerEpoch = nrTrainSamples // B

    # create optimizer object
    varList = [W1, b1, W3, b3, W5, b5]
    opt = tf.keras.optimizers.Adam(learning_rate=EPS)

    it = 0
    for (X, T) in traindTF_batches:
        with tf.GradientTape() as g:
            Y = f(X)
            ce = loss(Y, T)
        # print (varList)
        gradList = g.gradient(ce, varList)

        opt.apply_gradients(zip(gradList, varList))
        print(f"Iteration {it}: train loss = {ce.numpy()}")
        it += 1
        if it > EPOCHS * iterationsPerEpoch:
            break

    # ----------- confusion matrix computation ------------------
    # compute confusion matrix on test set
    # in batches, so as not to exceed memory limits
    # pre-allocate CM
    cm = np.zeros([CLASSES, CLASSES])
    it = -1
    iterationsPerEpoch = nrTestSamples // B
    for (X, T) in testdTF_batches:
        it += 1
        Y = f(X)
        # scalar model outputs and class labels
        YHat = tf.argmax(Y, axis=1)
        THat = tf.argmax(T, axis=1)

        # hard to avoid the for here... possible but less clear...
        for (yhat, that) in zip(YHat, THat):
            cm[int(that), int(yhat)] += 1
        # we iterate exatcly one epoch = all test samples
        if it > iterationsPerEpoch:
            break

    print(cm)

    json_dic = {
        'result': f'{cm}'
    }

    json_string = json.dumps(json_dic)
    this_file_path = os.path.dirname(os.path.abspath(__file__))
    result_folder = os.path.join(this_file_path, 'test_results')
    output_file_path = os.path.join(result_folder, f'{exp_id}_log.json')
    success_file_path = os.path.join(result_folder, 'SUCCESS')

    if not os.path.isdir(result_folder):
        os.mkdir(result_folder)

    if os.path.isfile(output_file_path):
        # delete file
        os.remove(output_file_path)

    if os.path.isfile(success_file_path):
        os.remove(success_file_path)

    with open(output_file_path, 'w') as output_file:
        output_file.write(json_string)

    with open(success_file_path, 'w') as result_file:
        result_file.write('All went well!')
