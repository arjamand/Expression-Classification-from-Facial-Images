# -*- coding: utf-8 -*-
"""Expression Classification from Facial Images|Expw

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/#fileId=https%3A//storage.googleapis.com/kaggle-colab-exported-notebooks/expression-classification-from-facial-images-expw-7431c4d7-d86c-44bc-8a5f-b2bcc772d39b.ipynb%3FX-Goog-Algorithm%3DGOOG4-RSA-SHA256%26X-Goog-Credential%3Dgcp-kaggle-com%2540kaggle-161607.iam.gserviceaccount.com/20241018/auto/storage/goog4_request%26X-Goog-Date%3D20241018T045957Z%26X-Goog-Expires%3D259200%26X-Goog-SignedHeaders%3Dhost%26X-Goog-Signature%3D27cc1b8f334b8a7edfb4794cc0d6e814df3afbee6d5112ed9766b533c4512fffc979106c541617b36d32e496015dea0bcd123f4925bbc3626092cb88ab33142c2149c6b60b8aca1c1469f35fbe6bbcb79b37636fe16131704ff5d44d25ce0c24c2d4fc7cd3e138cb04a12ae6f3eca37ab697c4180cf0c940e31f14594d90a87373b321527bfb023e238533ecc55422ec41a307c1a6544f3341f08514dcc1573e2c4092ffc87f34d4d0c073ae109411901dafb0d81fb776ff2c20f408efa72245fe200d5296da15d0f1c9738a3bd4131bbc45c4865c4219bc3c0920195f211b94022e97a40e5d8d4e40608f9b76296b6d5c3fb34ff6419d4a560daa02b2714ec3
"""

# IMPORTANT: SOME KAGGLE DATA SOURCES ARE PRIVATE
# RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES.
import kagglehub
kagglehub.login()

# IMPORTANT: RUN THIS CELL IN ORDER TO IMPORT YOUR KAGGLE DATA SOURCES,
# THEN FEEL FREE TO DELETE THIS CELL.
# NOTE: THIS NOTEBOOK ENVIRONMENT DIFFERS FROM KAGGLE'S PYTHON
# ENVIRONMENT SO THERE MAY BE MISSING LIBRARIES USED BY YOUR
# NOTEBOOK.

shahzadabbas_expression_in_the_wild_expw_dataset_path = kagglehub.dataset_download('shahzadabbas/expression-in-the-wild-expw-dataset')
minhtmnguyntrn_origin_expw_path = kagglehub.dataset_download('minhtmnguyntrn/origin-expw')
arjamandali_test_images_path = kagglehub.dataset_download('arjamandali/test-images')

print('Data source import complete.')

# Define file paths for labels and images
label_file_path = r"/kaggle/input/expression-in-the-wild-expw-dataset/label.lst"
images_folder_path = r"/kaggle/input/origin-expw/origin/"

# Import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import cv2
import os
import concurrent.futures
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import VGG16
from tensorflow.keras.layers import Dense, Flatten
from tensorflow.keras.models import Model

# Load label data into a pandas DataFrame
df_info = pd.read_csv(label_file_path, sep=" ", header=None)
df_info.columns = ['image_name', 'face_id_in_image', 'face_box_top', 'face_box_left',
                   'face_box_right', 'face_box_bottom', 'face_box_confidence', 'expression_label']

# Display the first few rows of the DataFrame
df_info.head()

# Check the shape of the DataFrame (number of rows and columns)
df_info.shape

# Define a mapping of expression labels to human-readable emotions
emotion_map = {0: 'Angry', 1: 'Disgust', 2: 'Fear', 3: 'Happy', 4: 'Sad', 5: 'Surprise', 6: 'Neutral'}

# Count occurrences of each expression label
emotion_counts = df_info['expression_label'].value_counts(sort=False).reset_index()
emotion_counts.columns = ['expression_label', 'number']

# Map expression labels to emotion names
emotion_counts['expression_label'] = emotion_counts['expression_label'].map(emotion_map)

# Plot class distribution of emotions
print("\n\nPlotting class distribution of emotions.")
plt.figure(figsize=(6, 4))
plt.bar(emotion_counts.expression_label, emotion_counts.number)
plt.title('Class Distribution')
plt.xlabel('Expression Label', fontsize=14)
plt.ylabel('Number', fontsize=12)
plt.xticks(rotation=45)
plt.show()

# Filter out faces with confidence lower than 80
df_sel = df_info[df_info.face_box_confidence > 60]

# Function to process each image: crop the face, resize it, and return the image and label
def process_image(row):
    img_name = row["image_name"]
    x1 = row["face_box_left"]
    y1 = row["face_box_top"]
    x2 = row["face_box_right"]
    y2 = row["face_box_bottom"]
    label = row["expression_label"]
    img_path = os.path.join(images_folder_path, img_name)

    # Read the image
    image = cv2.imread(img_path)

    # Check if the image was loaded successfully
    if image is None:
        return None, None

    # Crop the face region and resize to (64, 64)
    cropped = image[y1:y2, x1:x2]
    if cropped is not None:
        resized_face = cv2.resize(cropped, (64, 64))
        return resized_face, label
    return None, None

# Process images in parallel using multithreading for efficiency
x = []  # To store processed images
y = []  # To store corresponding labels
def process_images_in_parallel(dataframe):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_row = {executor.submit(process_image, row): row for i, row in dataframe.sample(12000).iterrows()}
        for future in concurrent.futures.as_completed(future_to_row):
            resized_face, label = future.result()
            if resized_face is not None:
                x.append(resized_face)
                y.append(label)

# Run the image processing in parallel
process_images_in_parallel(df_sel)

# Convert the image and label lists into NumPy arrays for model training
X = np.array(x)
y = np.array(y)

# Normalize image data to range [0, 1] for better training performance
X_normalized = X / 255.0

# Sample 3500 images randomly from the dataset (optional step)
sample_size = 35000
random_indices = np.random.choice(len(X_normalized), size=sample_size)
X_sampled = X_normalized[random_indices]
Y_sampled = y[random_indices]

# Encode labels into numerical format (needed for classification tasks)
label_encoder = LabelEncoder()
Y_encoded = label_encoder.fit_transform(Y_sampled)

# Split data into training and testing sets (80% train, 20% test)
X_train, X_test, Y_train, Y_test = train_test_split(X_sampled, Y_encoded, test_size=0.2, random_state=42)

# Load the VGG16 model with pre-trained ImageNet weights, excluding the top layers
vgg16 = VGG16(weights='imagenet', include_top=False, input_shape=(64, 64, 3))

# Freeze the VGG16 layers to prevent them from being updated during training
for layer in vgg16.layers:
    layer.trainable = False

# Add custom classification layers on top of VGG16
x = Flatten()(vgg16.output)
x = Dense(256, activation='relu')(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(7, activation='softmax')(x)  # 7 output classes for the 7 emotions

# Create the final model
model = Model(inputs=vgg16.input, outputs=predictions)

# Compile the model using Adam optimizer and sparse categorical cross-entropy for multi-class classification
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model for 10 epochs with a batch size of 32
print("\n\nTraining the model for 10 epochs with a batch size of 32")
model.fit(X_train, Y_train, batch_size=32, epochs=10, validation_data=(X_test, Y_test))

# Evaluate the model on the test set and print accuracy
loss, accuracy = model.evaluate(X_test, Y_test, batch_size=32)
print(f"Test accuracy: {accuracy:.2f}")

# Train the model again and store the training history for analysis
print("\n\nTraining the model again and store the training history for analysis")

history = model.fit(X_train, Y_train, batch_size=32, epochs=10, validation_data=(X_test, Y_test))

# Extract training and validation loss and accuracy
train_loss = history.history['loss']
val_loss = history.history['val_loss']
train_accuracy = history.history['accuracy']
val_accuracy = history.history['val_accuracy']

import matplotlib.pyplot as plt

# Plot Training and Validation Loss vs. Epoch and Training and Validation Accuracy vs. Epoch side by side


# Create a figure with two subplots (1 row, 2 columns)
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Plot Training and Validation Loss
axes[0].plot(range(1, len(train_loss) + 1), train_loss, label='Training Loss', color='b', linestyle='-', marker='o')
axes[0].plot(range(1, len(val_loss) + 1), val_loss, label='Validation Loss', color='r', linestyle='--', marker='x')
axes[0].set_xlabel('Epoch', fontsize=12)
axes[0].set_ylabel('Loss', fontsize=12)
axes[0].set_title('Training and Validation Loss vs. Epoch', fontsize=14)
axes[0].legend()
axes[0].grid(True)

# Plot Training and Validation Accuracy
axes[1].plot(range(1, len(train_accuracy) + 1), train_accuracy, label='Training Accuracy', color='b', linestyle='-', marker='o')
axes[1].plot(range(1, len(val_accuracy) + 1), val_accuracy, label='Validation Accuracy', color='r', linestyle='--', marker='x')
axes[1].set_xlabel('Epoch', fontsize=12)
axes[1].set_ylabel('Accuracy', fontsize=12)
axes[1].set_title('Training and Validation Accuracy vs. Epoch', fontsize=14)
axes[1].legend()
axes[1].grid(True)

# Adjust layout for better spacing
plt.tight_layout()

# Show the plots
plt.show()

import cv2
import numpy as np
import matplotlib.pyplot as plt

def test_image(model, image_path, label_encoder):
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found.")
        return

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    plt.imshow(image_rgb), plt.axis('off'), plt.show()

    image_preprocessed = np.expand_dims(cv2.resize(image_rgb, (64, 64)) / 255.0, axis=0)
    predicted_label = np.argmax(model.predict(image_preprocessed))

    predicted_emotion = label_encoder.inverse_transform([predicted_label])[0]
    print(f"Predicted Emotion: {emotion_map[predicted_emotion]}")
    return predicted_emotion

# Test the function
test_image(model, '/kaggle/input/test-images/test_image4.jpeg', label_encoder)
test_image(model, '/kaggle/input/test-images/test_image.jpeg', label_encoder)

