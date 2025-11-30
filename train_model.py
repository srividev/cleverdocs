import os
import glob
import joblib
import numpy as np
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import accuracy_score, classification_report


# -----------------------------
# 1. Load dataset from folders
# -----------------------------
def load_dataset(base_path="dataset"):
    texts = []
    labels = []

    categories = {
        "invoices": "invoice",
        "receipts": "receipt",
        "contracts": "contract"
    }

    for folder, label in categories.items():
        folder_path = os.path.join(base_path, folder, "*.txt")
        for file_path in glob.glob(folder_path):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
                texts.append(text)
                labels.append(label)

    return texts, labels


# -----------------------------
# 2. Train ML Model
# -----------------------------
def train_model():
    print("Loading dataset...")
    texts, labels = load_dataset()

    print(f"Loaded {len(texts)} samples.")

    # Convert labels to numpy array
    labels = np.array(labels)

    # Text → TF-IDF
    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=5000
    )

    X = vectorizer.fit_transform(texts)

    # Split dataset
    X_train, X_test, y_train, y_test = train_test_split(
        X, labels, test_size=0.2, random_state=42, stratify=labels
    )

    # -----------------------------
    # Train SVM classifier
    # -----------------------------
    print("Training model...")
    model = LinearSVC()
    model.fit(X_train, y_train)

    # -----------------------------
    # Evaluate
    # -----------------------------
    print("Evaluating model...")
    y_pred = model.predict(X_test)

    acc = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {acc * 100:.2f}%\n")
    
    print("Classification Report:")
    print(classification_report(y_test, y_pred))

    # -----------------------------
    # Save model & vectorizer
    # -----------------------------
    os.makedirs("models", exist_ok=True)

    joblib.dump(model, "models/classifier.pkl")
    joblib.dump(vectorizer, "models/vectorizer.pkl")

    print("\nSaved:")
    print("- models/classifier.pkl")
    print("- models/vectorizer.pkl")


if __name__ == "__main__":
    train_model()
