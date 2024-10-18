# Facial Expression Recognition Project

This project focuses on developing a facial expression recognition system utilizing the **Expression in-the-Wild (ExpW)** dataset. The dataset consists of **91,793 face images** labeled across seven fundamental expression categories: **angry, disgust, fear, happy, sad, surprise, and neutral**. The primary goal is to create a robust model capable of accurately identifying human emotions in real-world scenarios.

## Project Overview

- **Dataset:** The Expression in-the-Wild (ExpW) dataset, which provides a rich variety of facial expressions.
- **Model Training:** The model is trained using a deep learning approach over **10 epochs**, achieving:
  - **Training Accuracy:** 98%
  - **Validation Accuracy:** 92%
  - **Test Accuracy:** 91%

## Key Features

- **Hyperparameter Tuning:** Key hyperparameters like learning rate and batch size were optimized using grid search to enhance model performance.
- **Data Division:**
  - **Training Set:** 70%
  - **Validation Set:** 10%
  - **Test Set:** 20%
  
  This division ensures robust model evaluation and performance assessment.

## Implementation

The project utilizes Python and popular libraries such as TensorFlow/Keras for model development and training. The architecture is designed to efficiently learn and generalize from the dataset, providing a reliable tool for recognizing facial expressions.

