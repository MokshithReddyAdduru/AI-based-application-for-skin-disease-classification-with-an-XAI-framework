
import pandas as pd
import numpy as np
import os
from glob import glob
from sklearn.model_selection import train_test_split

import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, Model, Input

# --- PATHS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
MODEL_SAVE_PATH = os.path.join(BASE_DIR, 'final_model.keras')

# --- CONFIG ---
IMG_SIZE = 64
BATCH_SIZE = 32
EPOCHS = 40   # 🔥 keep 1 for now (quick test), later change to 10–20
NUM_CLASSES = 7


# --- LOAD DATA ---
def load_and_preprocess_data():
    print("\n--- 1. Loading Metadata ---")

    image_pattern = os.path.join(DATA_DIR, '**', '*.jpg')
    all_image_paths = {
        os.path.splitext(os.path.basename(x))[0]: x
        for x in glob(image_pattern, recursive=True)
    }

    csv_path = os.path.join(DATA_DIR, 'HAM10000_metadata.csv')
    metadata_df = pd.read_csv(os.path.abspath(csv_path))

    metadata_df['path'] = metadata_df['image_id'].map(all_image_paths.get)
    metadata_df['age'].fillna(int(metadata_df['age'].mean()), inplace=True)
    metadata_df['dx'] = metadata_df['dx'].astype(str)

    print(f"Total records: {len(metadata_df)}")

    train_df, val_df = train_test_split(
        metadata_df,
        test_size=0.20,
        random_state=42,
        stratify=metadata_df['dx']
    )

    print(f"Train: {len(train_df)}, Val: {len(val_df)}")

    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=15,
        horizontal_flip=True,
        zoom_range=0.1
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    train_gen = train_datagen.flow_from_dataframe(
        dataframe=train_df,
        x_col="path",
        y_col="dx",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    val_gen = val_datagen.flow_from_dataframe(
        dataframe=val_df,
        x_col="path",
        y_col="dx",
        target_size=(IMG_SIZE, IMG_SIZE),
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    return train_gen, val_gen, train_gen.class_indices


# --- MODEL (🔥 FIXED) ---
def create_model(input_shape, num_classes):
    print("\n--- 2. Creating Functional Model ---")

    inputs = Input(shape=input_shape)

    x = layers.Conv2D(32, (3,3), activation='relu', padding='same')(inputs)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(0.25)(x)

    x = layers.Conv2D(64, (3,3), activation='relu', padding='same')(x)
    x = layers.MaxPooling2D()(x)
    x = layers.Dropout(0.25)(x)

    x = layers.Conv2D(128, (3,3), activation='relu', padding='same')(x)

    x = layers.Flatten()(x)
    x = layers.Dense(128, activation='relu')(x)
    x = layers.Dropout(0.5)(x)

    outputs = layers.Dense(num_classes, activation='softmax')(x)

    model = Model(inputs=inputs, outputs=outputs)

    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    return model


# --- MAIN ---
def main():
    train_gen, val_gen, class_indices = load_and_preprocess_data()

    model = create_model((IMG_SIZE, IMG_SIZE, 3), NUM_CLASSES)

    model.summary()

    print("\n--- 3. Training ---")
    model.fit(
        train_gen,
        steps_per_epoch=train_gen.n // train_gen.batch_size,
        epochs=EPOCHS,
        validation_data=val_gen,
        validation_steps=val_gen.n // val_gen.batch_size
    )

    # 🔥 SAVE CLEAN MODEL
    model.save(MODEL_SAVE_PATH)
    print(f"\n✅ Model saved at: {MODEL_SAVE_PATH}")

    # Save class mapping
    np.save(os.path.join(BASE_DIR, 'class_indices.npy'), class_indices)
    print("✅ Class indices saved")


if __name__ == '__main__':
    if not os.path.exists(os.path.join(DATA_DIR, 'HAM10000_metadata.csv')):
        print("❌ Dataset not found!")
    else:
        main()
