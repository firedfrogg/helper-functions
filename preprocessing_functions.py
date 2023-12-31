# -*- coding: utf-8 -*-
"""preprocessing_functions

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12B548hyuTkPCLIicT6K7veXAJf93uYG2
"""

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Dropout
from tensorflow.keras.optimizers.legacy import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
import numpy as np
import os
import datetime
import random
import string
import shutil
import matplotlib.image as mpimg
from tensorflow import keras
import imgaug.augmenters as iaa
from PIL import Image
import cv2


def load_and_prep_image(filename, img_shape=224, scale=True):
  """
  Reads in an image from filename, turns it into a tensor and reshapes into
  (224, 224, 3).
  """
  # Read in the image
  img = tf.io.read_file(filename)
  # Decode it into a tensor
  img = tf.image.decode_jpeg(img)
  # Resize the image
  img = tf.image.resize(img, [img_shape, img_shape])
  if scale:
    # Rescale the image
    return img/255.
  else:
    return img


def create_tensorboard_callback(dir_name, experiment_name):
  log_dir = dir_name + "/" + experiment_name + "/" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
  tensorboard_callback = tf.keras.callbacks.TensorBoard(
      log_dir=log_dir
  )
  print(f"Saving TensorBoard log files to: {log_dir}")
  return tensorboard_callback


def predict_image(file_path, model, file_path_split):
  # Read it in image and plot it using matplotlib
  img = load_and_prep_image(file_path)
  # Make a prediction
  pred = model.predict(tf.expand_dims(img, axis=0))

  # Get the predicted class
  if len(pred[0]) > 1: # check for multi-class
    pred_class = class_names[pred.argmax()] # if more than one output, take the max
  else:
    pred_class = class_names[int(tf.round(pred)[0][0])] # if only one output, round

    # Plot the image and predicted class
  plt.figure()
  plt.imshow(img)
  plt.title(f"Prediction: {pred_class}. Actual {file_path_split[2]}")
  plt.axis(False)


def generate_random_string(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


def augment_image(image_path, save_path):
    image = cv2.imread(image_path)
    # Define augmentation sequence using imgaug library
    augmenter = iaa.Sequential([
        iaa.Fliplr(0.5),  # horizontal flips
        iaa.Affine(rotate=(-10, 10)),  # random rotations
        iaa.GaussianBlur(sigma=(0, 1.0)),  # Gaussian blur
        iaa.AdditiveGaussianNoise(scale=(0, 0.05 * 255)),  # additive Gaussian noise
    ])
    augmented_image = augmenter.augment_image(image)
    cv2.imwrite(save_path, augmented_image)


def balance(parent_folder_path, target_count):
    subfolders = os.listdir(parent_folder_path)

    for subfolder in subfolders:
        subfolder_path = os.path.join(parent_folder_path, subfolder)
        if not os.path.isdir(subfolder_path):
            continue  # Skip if it's not a subfolder

        images = os.listdir(subfolder_path)
        current_count = len(images)

        if current_count < target_count:
          # Oversample the data
          num_images_to_add = target_count - current_count
          existing_images = random.choices(images, k=num_images_to_add)
          # Augment and save the selected images
          for image_file in existing_images:
            source_path = os.path.join(subfolder_path, image_file)
            random_string = generate_random_string(4)
            target_file = f"augmented_{random_string}_{image_file}"
            target_path = os.path.join(subfolder_path, target_file)
            augment_image(source_path, target_path)

        elif current_count > target_count:
          # Undersample the data
          num_images_to_remove = current_count - target_count
          images_to_remove = random.sample(images, num_images_to_remove)
          # Delete the selected images
          for image_file in images_to_remove:
              image_path = os.path.join(subfolder_path, image_file)
              os.remove(image_path)

        else:
          continue


def load_and_preprocess_data(train_dir, test_dir, valid_dir, target_size, batch_size, shuffle_train, shuffle_test, shuffle_val):
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)
    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(train_dir,
                                                        target_size=target_size,
                                                        batch_size=batch_size,
                                                        class_mode='categorical',
                                                       shuffle=shuffle_train)
    test_generator = test_datagen.flow_from_directory(test_dir,
                                                      target_size=target_size,
                                                      batch_size=batch_size,
                                                      class_mode='categorical',
                                                     shuffle=shuffle_test)
    valid_generator = test_datagen.flow_from_directory(valid_dir,
                                                       target_size=target_size,
                                                       batch_size=batch_size,
                                                       class_mode='categorical',
                                                      shuffle=shuffle_val)

    return train_generator, test_generator, valid_generator


def create_model(input_shape, num_classes):
    model = Sequential([
        Conv2D(16, 3, activation="relu", input_shape=input_shape, padding='same'),
        MaxPool2D(),
        Conv2D(32, 3, activation="relu"),
        MaxPool2D(),
        Conv2D(64, 3, activation="relu"),
        MaxPool2D(),
        Conv2D(128, 3, activation="relu"),
        MaxPool2D(),
        Conv2D(256, 3, activation="relu"),
        MaxPool2D(),
        Flatten(),
        Dense(256, activation="relu"),
        Dropout(0.25),
        Dense(128, activation='relu'),
        Dropout(0.25),
        Dense(num_classes, activation='softmax')
    ])
    return model


def create_model1(input_shape, num_classes):
    model = Sequential([
        Conv2D(32, 3, activation="relu", input_shape=(224, 224, 3), padding='same'),
        Conv2D(32, 3, activation="relu", padding="same"),
        MaxPool2D(),
        Conv2D(64, 3, activation="relu", padding="same"),
        Conv2D(64, 3, activation="relu", padding="same"),
        MaxPool2D(),
        Conv2D(128, 3, activation="relu", padding="same"),
        Conv2D(128, 3, activation="relu", padding="same"),
        MaxPool2D(),
        Conv2D(256, 3, activation="relu", padding="same"),
        Conv2D(256, 3, activation="relu", padding="same"),
        MaxPool2D(),
        Flatten(),
        Dense(128, activation='relu'),
        Dropout(0.25),
        Dense(num_classes, activation='softmax')
        ])
    return model


def compile_model(model, learning_rate):
    model.compile(optimizer=keras.optimizers.Adam(learning_rate=learning_rate), 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])


def train_model(model, train_generator, valid_generator, epochs, dirname=None, experiment_name=None):
    if dirname != None and experiment_name != None:
        history = model.fit(train_generator,
                  epochs=epochs,
                  steps_per_epoch=len(train_generator),
                  validation_data=valid_generator,
                  validation_steps=len(valid_generator),
                   callbacks=[create_tensorboard_callback(dir_name=dirname, experiment_name=experiment_name)])
    else:
        history = model.fit(train_generator,
                  epochs=epochs,
                  steps_per_epoch=len(train_generator),
                  validation_data=valid_generator,
                  validation_steps=len(valid_generator))
    return history


def evaluate_model(model, test_generator):
    loss, accuracy = model.evaluate(test_generator)
    print('Test Loss:', loss)
    print('Test Accuracy:', accuracy)


def load_and_preprocess_data_augmented(train_dir, test_dir, valid_dir, target_size, batch_size):
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255,
                                                                    rotation_range=0.2,
                                                                    zoom_range=0.2,
                                                                    width_shift_range=0.2,
                                                                    height_shift_range=0.3,
                                                                    horizontal_flip=True)
    test_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1. / 255)

    train_generator = train_datagen.flow_from_directory(train_dir,
                                                        target_size=target_size,
                                                        batch_size=batch_size,
                                                        class_mode='categorical')
    test_generator = test_datagen.flow_from_directory(test_dir,
                                                      target_size=target_size,
                                                      batch_size=batch_size,
                                                      class_mode='categorical')
    valid_generator = test_datagen.flow_from_directory(valid_dir,
                                                       target_size=target_size,
                                                       batch_size=batch_size,
                                                       class_mode='categorical')

    return train_generator, test_generator, valid_generator
