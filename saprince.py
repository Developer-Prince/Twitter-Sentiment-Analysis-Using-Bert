# -*- coding: utf-8 -*-
"""SAprince.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/15dmL3D6Z-adiXBRRLH8ZrCCzIfSffotN
"""

import pandas as pd
import numpy as np
import re
import random
import math

# !pip install bs4
# !pip install bert-for-tf2
# !pip install sentencepiece

import tensorflow as tf
import tensorflow_hub as hub
from bs4 import BeautifulSoup
from tensorflow.keras import layers
import bert

# Commented out IPython magic to ensure Python compatibility.
try:
#   %tensorflow_version 2.x
except Exception:
  pass

print(tf.__version__)

"""# 1. DataPreprocessing"""

cols = ["sentiment","id","date","query","user","text"]
dataset = pd.read_csv("/content/drive/MyDrive/BERT INTUITION/training.1600000.processed.noemoticon.csv",
                      header = None,
                      engine = "python",
                      encoding = "latin1",
                      names = cols)

dataset.head()

dataset.drop(["id","query","user","date"] ,axis = 1 , inplace = True)

dataset.head()

def clean_tweet(tweet):
  tweet = BeautifulSoup(tweet,"lxml").get_text()
  # removing all the mentions
  tweet = re.sub(r'@[A-Za-z0-9]+',' ',tweet)
  # removing all the urls
  tweet = re.sub(r'https?://[A-Za-z0-9./]+',' ',tweet)
  # keeping all the letters
  tweet = re.sub(r"[^A-Za-z0-9.!?']",' ',tweet)
  # removing all the whitespaces
  tweet = re.sub(r' +',' ',tweet)

  return tweet

data_clean = [clean_tweet(tweet) for tweet in dataset.text]

data_labels = dataset.sentiment.values
data_labels[data_labels == 4] = 1

data_clean[0]

"""# 2. Tokenization"""

FullTokenizer = bert.bert_tokenization.FullTokenizer
bert_layer = hub.KerasLayer("https://tfhub.dev/tensorflow/bert_en_uncased_L-12_H-768_A-12/4",trainable=False)
vocab_file = bert_layer.resolved_object.vocab_file.asset_path.numpy()
do_lower_case = bert_layer.resolved_object.do_lower_case.numpy()
tokenizer = FullTokenizer(vocab_file=vocab_file,do_lower_case=do_lower_case)

def encode_sentence(sent):
  return tokenizer.convert_tokens_to_ids(tokenizer.tokenize(sent))

data_inputs = [encode_sentence(sent) for sent in data_clean]

word_data = [tokenizer.tokenize(sent) for sent in data_clean]
word_data[0]

how

"""# 3. Dataset Creation"""

data_with_len = [[sent , data_labels[idx] , len(sent)]
                 for idx , sent in enumerate(data_inputs)]
random.shuffle(data_with_len)
data_with_len.sort(key = lambda x:x[2])
sorted_all = [(sent[0],sent[1]) for sent in data_with_len if sent[2] > 7]

data_with_len[0]

sorted_all[0]

all_dataset = tf.data.Dataset.from_generator(lambda: sorted_all,
                                             output_types = (tf.int32,tf.int32))

next(iter(all_dataset))

BATCH_SIZE = 32
all_batched = all_dataset.padded_batch(batch_size = BATCH_SIZE,padded_shapes = ((None,),()))

all_batched

NB_BATCHES = math.ceil(len(sorted_all)/BATCH_SIZE)
NB_BATCHES_TEST = NB_BATCHES//10
all_batched.shuffle(NB_BATCHES)
test_dataset = all_batched.take(NB_BATCHES_TEST)
train_dataset = all_batched.skip(NB_BATCHES_TEST)

print(NB_BATCHES)
print(NB_BATCHES_TEST)
print(test_dataset)
print(train_dataset)

"""# 4. Model Building"""

class DCNN(tf.keras.Model):
  def __init__(self,
               vocab_size,
               emb_dim = 128,
               nb_filters = 50,
               FFN_units = 512,
               nb_classes = 2,
               dropout_rate = 0.1,
               training = False,
               name = 'dcnn'):
    super(DCNN,self).__init__(name = name)

    self.embedding = layers.Embedding(vocab_size , emb_dim)
    self.bigram = layers.Conv1D(filters=nb_filters , 
                                kernal_size = 2,
                                padding = 'valid',
                                activation = 'relu')
    self.trigram = layers.Conv1D(filters=nb_filters , 
                                kernal_size = 3,
                                padding = 'valid',
                                activation = 'relu')
    self.fourgram = layers.Conv1D(filters=nb_filters , 
                                kernal_size = 4,
                                padding = 'valid',
                                activation = 'relu')
    self.pool = layers.GlobalMaxPooling1D()
    self.dense_1 = layers.Dense(units = FFN_units , activation = 'sigmoid')
    self.dropout = layers.Dropout(rate = dropout_rate)

    if nb_classes == 2:
      self.dense_2 = layers.Dense(units = 1,activation = 'sigmoid')
    else:
      self.dense_2 = layers.Dense(units = nb_classes,activation = 'softmax')

  def call(self, inputs, training):
    x = self.embedding(inputs)
    x_1 = self.bigram(x)
    x_1 = self.pool(x_1)
    x_2 = self.bigram(x_1)
    x_2 = self.pool(x_2)
    x_3 = self.bigram(x_2)
    x_3 = self.pool(x_3)

    merged = tf.concat([x_1,x_2,x_3],axis = -1)
    merged = self.dense_1(merged)
    merged = self.dropout(merged , training)
    output = self.dense_2(merged)  
    
    return output

"""# 5.Training"""

VOCAB_SIZE = len(tokenizer.vocab)
EMB_DIM = 200
NB_FILTERS = 100
FFN_UNITS = 256
NB_CLASSES = 2

DROPOUT_RATE = 0.2

NB_EPOCHS = 5

class DCNN(tf.keras.Model):
    
    def __init__(self,
                 vocab_size,
                 emb_dim=128,
                 nb_filters=50,
                 FFN_units=512,
                 nb_classes=2,
                 dropout_rate=0.1,
                 training=False,
                 name="dcnn"):
        super(DCNN, self).__init__(name=name)
        
        self.embedding = layers.Embedding(vocab_size,
                                          emb_dim)
        self.bigram = layers.Conv1D(filters=nb_filters,
                                    kernel_size=2,
                                    padding="valid",
                                    activation="relu")
        self.trigram = layers.Conv1D(filters=nb_filters,
                                     kernel_size=3,
                                     padding="valid",
                                     activation="relu")
        self.fourgram = layers.Conv1D(filters=nb_filters,
                                      kernel_size=4,
                                      padding="valid",
                                      activation="relu")
        self.pool = layers.GlobalMaxPool1D()
        
        self.dense_1 = layers.Dense(units=FFN_units, activation="relu")
        self.dropout = layers.Dropout(rate=dropout_rate)
        if nb_classes == 2:
            self.last_dense = layers.Dense(units=1,
                                           activation="sigmoid")
        else:
            self.last_dense = layers.Dense(units=nb_classes,
                                           activation="softmax")
    
    def call(self, inputs, training):
        x = self.embedding(inputs)
        x_1 = self.bigram(x) # batch_size, nb_filters, seq_len-1)
        x_1 = self.pool(x_1) # (batch_size, nb_filters)
        x_2 = self.trigram(x) # batch_size, nb_filters, seq_len-2)
        x_2 = self.pool(x_2) # (batch_size, nb_filters)
        x_3 = self.fourgram(x) # batch_size, nb_filters, seq_len-3)
        x_3 = self.pool(x_3) # (batch_size, nb_filters)
        
        merged = tf.concat([x_1, x_2, x_3], axis=-1) # (batch_size, 3 * nb_filters)
        merged = self.dense_1(merged)
        merged = self.dropout(merged, training)
        output = self.last_dense(merged)
        
        return output

Dcnn = DCNN(vocab_size=VOCAB_SIZE,
            emb_dim = EMB_DIM,
            nb_filters = NB_FILTERS,
            FFN_units = FFN_UNITS,
            nb_classes = NB_CLASSES,
            dropout_rate = DROPOUT_RATE)

if NB_CLASSES == 2:
    Dcnn.compile(loss="binary_crossentropy",
                 optimizer="adam",
                 metrics=["accuracy"])
else:
    Dcnn.compile(loss="sparse_categorical_crossentropy",
                 optimizer="adam",
                 metrics=["sparse_categorical_accuracy"])

checkpoint_path = "/content/drive/MyDrive/BERT INTUITION/"
ckpt = tf.train.Checkpoint(Dcnn=Dcnn)
ckpt_manager = tf.train.CheckpointManager(ckpt, checkpoint_path, max_to_keep=1)
class MyCustomCallback(tf.keras.callbacks.Callback):

    def on_epoch_end(self, epoch, logs=None):
        ckpt_manager.save()
        print("Checkpoint saved at {}.".format(checkpoint_path))

Dcnn.fit(train_dataset,
         epochs=NB_EPOCHS,
         callbacks=[MyCustomCallback()])

if ckpt_manager.latest_checkpoint:
    ckpt.restore(ckpt_manager.latest_checkpoint)
    print("Latest checkpoint restored!!")

results = Dcnn.evaluate(test_dataset)
print(results)

def get_prediction(sentence):
    tokens = encode_sentence(sentence)
    inputs = tf.expand_dims(tokens, 0)

    output = Dcnn(inputs, training=False)

    sentiment = math.floor(output*2)

    if sentiment == 0:
        print("Ouput of the model: {}\nPredicted sentiment: negative.".format(
            output))
    elif sentiment == 1:
        print("Ouput of the model: {}\nPredicted sentiment: positive.".format(
            output))

get_prediction("this movie was awesome!")

"""# Trying Some RealWorld Negative Prediction Example"""

get_prediction('Zapier is sooooo confusing to me')

get_prediction("Awful experience. I would never buy this product again")

get_prediction('Your customer service is a nightmare! Totally useless!!')

