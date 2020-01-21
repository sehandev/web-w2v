# encoding: utf-8

import sys
import os
import pathlib
import numpy as np
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' 


def visualize(model, data_dir, term_name):
    output_path = data_dir + 'visual/' + 'visual_' + term_name
    meta_file = 'tf_metadata_' + term_name + '.tsv'

    pathlib.Path(output_path).mkdir(parents=True, exist_ok=True)
    placeholder = np.zeros((len(model.wv.index2word), model.vector_size))

    with open(os.path.join(output_path, meta_file), 'wb') as file_metadata:
        for i, word in enumerate(model.wv.index2word):
            placeholder[i] = model[word]
            if word == '':
                print("Emply Line, should replecaed by any thing else, or will cause a bug of tensorboard")
                file_metadata.write("{0}".format('<Empty Line>').encode('utf-8') + b'\n')
            else:
                file_metadata.write("{0}".format(word).encode('utf-8') + b'\n')

    # define the model without training
    sess = tf.compat.v1.InteractiveSession()

    embedding = tf.Variable(placeholder, trainable=False, name='w2x_metadata')
    tf.compat.v1.global_variables_initializer().run()

    saver = tf.compat.v1.train.Saver()
    writer = tf.compat.v1.summary.FileWriter(output_path, sess.graph)

    # adding into projector
    config = projector.ProjectorConfig()
    embed = config.embeddings.add()
    embed.tensor_name = 'w2x_metadata'
    embed.metadata_path = meta_file

    # Specify the width and height of a single thumbnail.
    projector.visualize_embeddings(writer, config)
    saver.save(sess, os.path.join(output_path, 'w2x_metadata.ckpt'))
    # print('Run `tensorboard --logdir={0}` to run visualize result on tensorboard'.format(output_path))

    sess.close()
