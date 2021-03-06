# -*- coding: utf-8 -*-
"""Project Time Series - Monthly Sunspots.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YV3PuFU6RpcUX1dsrjYITA8V-jhfx9ey
"""

# Nama : Debora Udania Simanjuntak
# Kelas : Belajar Pengembangan Machine Learning

# Import the libraries and data
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt

data=pd.read_csv("monthly-sunspots.csv")
data.head()

data=data[600:]

data.info()

skala=(max(data.Sunspots)-min(data.Sunspots))*0.1
skala

# Visualize the data

plt.plot(data.Month,data.Sunspots)

# Split the data into train and test
length=len(data)

train=data[1:round(length*0.8)]
test=data[round(length*0.8):]

sunspots_train=train.Sunspots.values
month_train=train.Month.values
sunspots_test=test.Sunspots.values
month_test=test.Month.values

sunspots_train=sunspots_train.reshape((-1,1))
sunspots_test=sunspots_test.reshape((-1,1))

# Make a function to return label and atribute from the dataset
import tensorflow as tf
from keras.layers import Dense, LSTM,Dropout
from keras.models import Sequential

def windowed_dataset(series, window_size, batch_size, shuffle_buffer):
    series = tf.expand_dims(series, axis=-1)
    ds = tf.data.Dataset.from_tensor_slices(series)
    ds = ds.window(window_size + 1, shift=1, drop_remainder=True)
    ds = ds.flat_map(lambda w: w.batch(window_size + 1))
    ds = ds.shuffle(shuffle_buffer)
    ds = ds.map(lambda w: (w[:-1], w[-1:]))
    return ds.batch(batch_size).prefetch(1)

train_set =windowed_dataset(sunspots_train.reshape((len(train),)),120,40,1000)

test_set=windowed_dataset(sunspots_test.reshape((len(test),)),120,40,1000)

# Build the model

model=Sequential([LSTM(60,return_sequences=True),
                  LSTM(60),
                  Dropout(0.5),
                  Dense(30,activation='relu'),
                  Dense(10,activation='relu'),
                  Dense(1)])

optimizer = tf.keras.optimizers.SGD(learning_rate=1.0000e-04, momentum=0.9)
model.compile(loss=tf.keras.losses.Huber(),
              optimizer=optimizer,
              metrics=["mae"])

# Make callback function
import tensorflow as tf
class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    if(logs.get('mae')<skala ) and (logs.get('val_mae')<skala):
      print("\mae and val_mae have reached < 10 percent skala!")
      self.model.stop_training = True
callbacks = myCallback()

# Train the Model
history = model.fit(train_set,epochs=100,validation_data=test_set,callbacks=[callbacks])

plt.plot(history.history.get('mae'))
plt.plot(history.history.get('val_mae'))
plt.xlabel('epochs')
plt.ylabel('mae')
plt.legend(['train','test'])
plt.ylim(0,100)
plt.show()

plt.plot(history.history.get('loss'))
plt.plot(history.history.get('val_loss'))
plt.xlabel('epochs')
plt.ylabel('loss')
plt.legend(['train','test'])
plt.show()

