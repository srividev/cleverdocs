CleverDocs – AI Document Classifier

CleverDocs is a lightweight AI-based system that classifies business documents such as invoices, receipts, and contracts using OCR and machine learning. The application extracts text from PDFs or images and predicts the document type through a trained classifier, accessible via a clean web interface or REST API.

Features

OCR text extraction using Tesseract and PyMuPDF

Document classification using TF-IDF + SVM

Web interface built with Flask, HTML, CSS, and JavaScript

REST API endpoint for programmatic access

File preview, confidence score, and JSON result export

Project Structure
cleverdocs/
│── app.py
│── train_model.py
│── requirements.txt
│── templates/
│── static/
│── models/        (local, ignored in Git)
│── dataset/       (local, ignored in Git)
│── uploads/       (local)
│── results/       (local)
│── .gitignore

Installation
git clone https://github.com/srividev/cleverdocs.git
cd cleverdocs
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt


Install Tesseract OCR and update the path in app.py if required.

Running the Application
python app.py


Open the browser at:

http://127.0.0.1:5000


Upload a PDF or image to view extracted text and document classification results.

Training the Model

Place your dataset inside the dataset/ folder and run:

python train_model.py


This generates:

models/classifier.pkl
models/vectorizer.pkl

API Usage

Endpoint:

POST /upload


Example:

curl -X POST -F "file=@sample.pdf" http://127.0.0.1:5000/upload


Response includes predicted document type, confidence score, and text preview.

Dataset & Models

Datasets and model files are stored separately and can be downloaded from GitHub Releases. Extract the dataset into dataset/ and place model files into the models/ directory.

License

This project is for academic and learning purposes.
