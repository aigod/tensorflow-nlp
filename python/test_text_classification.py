#! /usr/bin/env python

import tensorflow as tf
import numpy as np
import os
import time
import datetime
import data_helpers
from text_cnn import TextCNN
from tensorflow.contrib import learn
import data_helpers.load as load_utils
import data_helpers.vocab as vocab_utils
import csv

# Parameters
# ==================================================

# Data Parameters
tf.flags.DEFINE_string("data", "../data/dataset/sample_data/train.tsv", "Data source tab separated files. It's possible to provide more than 1 file using a comma")

# Eval Parameters
tf.flags.DEFINE_integer("batch_size", 64, "Batch Size (default: 64)")
tf.flags.DEFINE_string("checkpoint_dir", "", "Checkpoint directory from training run")
tf.flags.DEFINE_boolean("eval_train", False, "Evaluate on all training data")

# Misc Parameters
tf.flags.DEFINE_boolean("allow_soft_placement", True, "Allow device soft device placement")
tf.flags.DEFINE_boolean("log_device_placement", False, "Log placement of ops on devices")


FLAGS = tf.flags.FLAGS
FLAGS._parse_flags()
print("\nParameters:")
for attr, value in sorted(FLAGS.__flags.items()):
    print("{}={}".format(attr.upper(), value))
print("")



'''
# CHANGE THIS: Load data. Load your own data here
if FLAGS.eval_train:
    x_raw, y_test = data_helpers.load_data_and_labels(FLAGS.positive_data_file, FLAGS.negative_data_file)
    y_test = np.argmax(y_test, axis=1)
else:
    x_raw = ["a masterpiece four years in the making", "everything is off."]
    y_test = [1, 0]


# Load data
print("Loading data...")
files_list = FLAGS.data.split(",")
x_text, y = load_utils.load_data_and_labels(files_list)

# Build vocabulary
max_element_length = max([len(x.split(" ")) for x in x_text]) 
# max_element_length = 20

word_dict, reversed_dict = load_utils.build_dict(x_text, FLAGS.output_dir)

x = load_utils.transform_text(x_text, word_dict, max_element_length)

x = np.array(x)
y = np.array(y)
'''


x_text = ["super beautiful like it very much best love", "terrible sad shit fuck worst ruined"]
y = [1, 0]

# Map data into vocabulary
dict_path = os.path.join(FLAGS.checkpoint_dir, "..", "vocab_words")
word_dict, _ = vocab_utils.load_dict(x_text, FLAGS.output_dir)

x = vocab_utils.transform_text(x_text, word_dict)

x = np.array(x)
y = np.array(y)

print("\nEvaluating...\n")

# Evaluation
# ==================================================
checkpoint_file = tf.train.latest_checkpoint(FLAGS.checkpoint_dir)
graph = tf.Graph()
with graph.as_default():
    session_conf = tf.ConfigProto(
      allow_soft_placement=FLAGS.allow_soft_placement,
      log_device_placement=FLAGS.log_device_placement)
    sess = tf.Session(config=session_conf)
    with sess.as_default():
        # Load the saved meta graph and restore variables
        saver = tf.train.import_meta_graph("{}.meta".format(checkpoint_file))
        saver.restore(sess, checkpoint_file)

        # Get the placeholders from the graph by name
        input_x = graph.get_operation_by_name("input_x").outputs[0]
        # input_y = graph.get_operation_by_name("input_y").outputs[0]
        dropout_keep_prob = graph.get_operation_by_name("dropout_keep_prob").outputs[0]

        # Tensors we want to evaluate
        predictions = graph.get_operation_by_name("output/predictions").outputs[0]

        # Generate batches for one epoch
        batches = data_helpers.batch_iter(list(x), FLAGS.batch_size, 1, shuffle=False)

        # Collect the predictions here
        all_predictions = []

        for x_batch in batches:
            batch_predictions = sess.run(predictions, {input_x: x_batch, dropout_keep_prob: 1.0})
            all_predictions = np.concatenate([all_predictions, batch_predictions])

# Print accuracy if y_test is defined
if y is not None:
    correct_predictions = float(sum(all_predictions == y))
    print("Total number of test examples: {}".format(len(y)))
    print("Accuracy: {:g}".format(correct_predictions/float(len(y))))

# Save the evaluation to a csv
predictions_human_readable = np.column_stack((np.array(x_raw), all_predictions))
out_path = os.path.join(FLAGS.checkpoint_dir, "..", "prediction.csv")
print("Saving evaluation to {0}".format(out_path))
with open(out_path, 'w') as f:
    csv.writer(f).writerows(predictions_human_readable)