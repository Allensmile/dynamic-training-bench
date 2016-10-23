# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Builds the VGG-like network."""

import tensorflow as tf
from inputs import cifar10

# Constants describing the training process.
BATCH_SIZE = 128
NUM_EPOCHS_PER_DECAY = 25  # Epochs after which learning rate decays.
LEARNING_RATE_DECAY_FACTOR = 0.1  # Learning rate decay factor.
MOMENTUM = 0.9  # Momentum
WD_PENALTY = 5e-4  # L2(weights) penalty
INITIAL_LEARNING_RATE = 1e-2  # Initial learning rate.


def weight(name,
           shape,
           initializer=tf.contrib.layers.variance_scaling_initializer(
               factor=2.0, mode='FAN_IN', uniform=False, dtype=tf.float32)):
    """ weight returns a tensor with the requested shape, initialized
      using the provided intitializer (default: He init)."""
    return tf.get_variable(
        name, shape=shape, initializer=initializer, dtype=tf.float32)


def bias(name, shape, initializer=tf.constant_initializer(value=0.0)):
    """Returns a bias variabile initializeted wuth the provided initializer"""
    return weight(name, shape, initializer)


def conv_layer(input_x, shape, stride, padding, wd=0.0):
    """ Define a conv layer.
    Args:
         input_x: a 4D tensor
         shape: weight shape
         stride: a single value supposing equal stride along X and Y
         padding: 'VALID' or 'SAME'
         wd: weight decay
    Rerturns the conv2d op"""
    W = weight("W", shape)
    b = bias("b", [shape[3]])
    # Add weight decay to W
    weight_decay = tf.mul(tf.nn.l2_loss(W), wd, name='weight_loss')
    tf.add_to_collection('losses', weight_decay)
    return tf.nn.bias_add(
        tf.nn.conv2d(input_x, W, [1, stride, stride, 1], padding), b)


def fc_layer(input_x, shape, wd=0.0):
    """ Define a fully connected layer.
    Args:
        input_x: a 4d tensor
        shape: weight shape
        wd: weight decay
    Returns the fc layer"""
    W = weight("W", shape)
    b = bias("b", [shape[1]])
    # Add weight decay to W
    weight_decay = tf.mul(tf.nn.l2_loss(W), wd, name='weight_loss')
    tf.add_to_collection('losses', weight_decay)
    return tf.nn.bias_add(tf.matmul(input_x, W), b)


def inference(images, keep_prob, train_phase=False):
    """Build the CIFAR-10 VGG model.

  Args:
    images: Images returned from distorted_inputs() or inputs().
    keep_prob: tensor for the dropout probability of keep neurons active

  Returns:
    Logits.
  """
    with tf.variable_scope('64'):
        with tf.variable_scope('conv1'):
            conv1 = tf.nn.relu(
                conv_layer(
                    images, [3, 3, 3, 64], 1, 'SAME', wd=WD_PENALTY))
            if train_phase:
                #conv1 = tf.nn.dropout(conv1, keep_prob)
                conv1 = tf.nn.dropout(conv1, 1 - 0.3)

        with tf.variable_scope('conv2'):
            conv2 = tf.nn.relu(
                conv_layer(
                    conv1, [3, 3, 64, 64], 1, 'SAME', wd=WD_PENALTY))

    with tf.variable_scope('pool1'):
        pool1 = tf.nn.max_pool(
            conv2, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    with tf.variable_scope('128'):
        with tf.variable_scope('conv3'):
            conv3 = tf.nn.relu(
                conv_layer(
                    pool1, [3, 3, 64, 128], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv3 = tf.nn.dropout(conv3, keep_prob)
                conv3 = tf.nn.dropout(conv3, 1 - 0.4)

        with tf.variable_scope('conv4'):
            conv4 = tf.nn.relu(
                conv_layer(
                    conv3, [3, 3, 128, 128], 1, 'SAME', wd=WD_PENALTY))

    with tf.variable_scope('pool2'):
        pool2 = tf.nn.max_pool(
            conv4, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    with tf.variable_scope('256'):
        with tf.variable_scope('conv5'):
            conv5 = tf.nn.relu(
                conv_layer(
                    pool2, [3, 3, 128, 256], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv5 = tf.nn.dropout(conv5, keep_prob)
                conv5 = tf.nn.dropout(conv5, 1 - 0.4)

        with tf.variable_scope('conv6'):
            conv6 = tf.nn.relu(
                conv_layer(
                    conv5, [3, 3, 256, 256], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv6 = tf.nn.dropout(conv6, keep_prob)
                conv6 = tf.nn.dropout(conv6, 1 - 0.4)

        with tf.variable_scope('conv7'):
            conv7 = tf.nn.relu(
                conv_layer(
                    conv6, [3, 3, 256, 256], 1, 'SAME', wd=WD_PENALTY))

    with tf.variable_scope('pool3'):
        pool3 = tf.nn.max_pool(
            conv7, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    with tf.variable_scope('512'):
        with tf.variable_scope('conv8'):
            conv8 = tf.nn.relu(
                conv_layer(
                    pool3, [3, 3, 256, 512], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv8 = tf.nn.dropout(conv8, keep_prob)
                conv8 = tf.nn.dropout(conv8, 1 - 0.4)

        with tf.variable_scope('conv9'):
            conv9 = tf.nn.relu(
                conv_layer(
                    conv8, [3, 3, 512, 512], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv9 = tf.nn.dropout(conv9, keep_prob)
                conv9 = tf.nn.dropout(conv9, 1 - 0.4)

        with tf.variable_scope('conv10'):
            conv10 = tf.nn.relu(
                conv_layer(
                    conv9, [3, 3, 512, 512], 1, 'SAME', wd=WD_PENALTY))

    with tf.variable_scope('pool4'):
        pool4 = tf.nn.max_pool(
            conv10, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')

    with tf.variable_scope('512b2'):
        with tf.variable_scope('conv11'):
            conv11 = tf.nn.relu(
                conv_layer(
                    pool4, [3, 3, 512, 512], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv11 = tf.nn.dropout(conv11, keep_prob)
                conv11 = tf.nn.dropout(conv11, 1 - 0.4)

        with tf.variable_scope('conv12'):
            conv12 = tf.nn.relu(
                conv_layer(
                    conv11, [3, 3, 512, 512], 1, 'SAME', wd=WD_PENALTY))

            if train_phase:
                #conv12 = tf.nn.dropout(conv12, keep_prob)
                conv12 = tf.nn.dropout(conv12, 1 - 0.4)

        with tf.variable_scope('conv13'):
            conv13 = tf.nn.relu(
                conv_layer(
                    conv12, [3, 3, 512, 512], 1, 'SAME', wd=WD_PENALTY))

    with tf.variable_scope('pool5'):
        pool5 = tf.nn.max_pool(
            conv13, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='VALID')
        # dropout on max-pooling, mfw
        if train_phase:
            #pool5 = tf.nn.dropout(pool5, keep_prob)
            pool5 = tf.nn.dropout(pool5, 0.5)

        pool5 = tf.reshape(pool5, [-1, 512])

    with tf.variable_scope('fc'):
        fc1 = tf.nn.relu(fc_layer(pool5, [512, 512], wd=WD_PENALTY))

        if train_phase:
            #fc1 = tf.nn.dropout(fc1, keep_prob)
            fc1 = tf.nn.dropout(fc1, 0.5)

    with tf.variable_scope('softmax_linear'):
        logits = fc_layer(fc1, [512, cifar10.NUM_CLASSES], wd=WD_PENALTY)
    return logits


def loss(logits, labels):
    """Add L2Loss to all the trainable variables.
    Args:
      logits: Logits from inference().
      labels: Labels from distorted_inputs or inputs(). 1-D tensor
              of shape [batch_size]

    Returns:
      loss summary,
      Loss tensor of type float.
    """
    # Calculate the average cross entropy loss across the batch.
    labels = tf.cast(labels, tf.int64)
    cross_entropy = tf.nn.sparse_softmax_cross_entropy_with_logits(
        logits, labels, name='cross_entropy_per_example')
    cross_entropy_mean = tf.reduce_mean(cross_entropy, name='cross_entropy')
    tf.add_to_collection('losses', cross_entropy_mean)

    # The total loss is defined as the cross entropy loss plus all of the weight
    # decay terms (L2 loss).
    error = tf.add_n(tf.get_collection('losses'), name='total_loss')
    return tf.scalar_summary('loss', error), error


def train(total_loss, global_step):
    """Train model.
    Create an optimizer and apply to all trainable variables.

    Args:
      total_loss: Total loss from loss().
      global_step: Integer Variable counting the number of training steps
        processed.
    Returns:
      learning_rate_summary: learning ratey summary
      train_op: op for training.
    """
    # Variables that affect learning rate.
    num_batches_per_epoch = cifar10.NUM_EXAMPLES_PER_EPOCH_FOR_TRAIN / BATCH_SIZE
    decay_steps = int(num_batches_per_epoch * NUM_EPOCHS_PER_DECAY)

    # Decay the learning rate exponentially based on the number of steps.
    learning_rate = tf.train.exponential_decay(
        INITIAL_LEARNING_RATE,
        global_step,
        decay_steps,
        LEARNING_RATE_DECAY_FACTOR,
        staircase=True)

    learning_rate_summary = tf.scalar_summary('learning_rate', learning_rate)
    opt = tf.train.MomentumOptimizer(learning_rate, MOMENTUM)
    train_op = opt.minimize(total_loss, global_step=global_step)

    return learning_rate_summary, train_op


def get_model(images, train_phase):
    """ define the model with its inputs.
    Use this function to define the model in training and when exporting the model
    in the protobuf format.

    Args:
        images: model input
        train_phase: set it to True when defining the model, during train

    Return:
        keep_prob_: model dropout placeholder
        logits: the model output
    """
    keep_prob_ = tf.placeholder(tf.float32, shape=(), name="keep_prob_")
    # build a graph that computes the logits predictions from the images
    logits = inference(images, keep_prob_, train_phase=train_phase)

    return keep_prob_, logits
