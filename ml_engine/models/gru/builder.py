import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Reduce TF warnings
import tensorflow as tf
from typing import Tuple

def build_gru_model(
    input_shape: Tuple[int, int],
    hidden_size: int,
    dropout: float,
    learning_rate: float
) -> tf.keras.Model:
    """
    Constructs a sequential GRU network for binary classification.
    
    Args:
        input_shape (Tuple[int, int]): (sequence_length, num_features)
        hidden_size (int): Number of units in the GRU layer.
        dropout (float): Dropout rate.
        learning_rate (float): Learning rate for the Adam optimizer.
        
    Returns:
        tf.keras.Model: Compiled Keras model.
    """
    model = tf.keras.Sequential([
        tf.keras.layers.InputLayer(input_shape=input_shape),
        tf.keras.layers.GRU(hidden_size, return_sequences=False),
        tf.keras.layers.Dropout(dropout),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])
    
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)
    
    model.compile(
        optimizer=optimizer,
        loss='binary_crossentropy',
        metrics=['accuracy']
    )
    
    return model
