import numpy as np
from fastapi import FastAPI, Form
import pandas as pd
from fastapi.responses import HTMLResponse
from starlette.responses import HTMLResponse
from starlette.responses import FileResponse
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import re

def preProcess_data(text):
    text = text.lower()
    new_text = re.sub('[^a-zA-z0-9\s]','',text)
    new_text = re.sub('rt', '', new_text)
    return new_text


app = FastAPI()

data = pd.read_csv('archive/Sentiment.csv')
tokenizer = Tokenizer(num_words=2000, split=' ')
tokenizer.fit_on_texts(data['text'].values)

def my_pipeline(text):
    text_new = preProcess_data(text)
    X = tokenizer.texts_to_sequences(pd.Series(text_new).values)
    X = pad_sequences(X, maxlen=28)
    return X



@app.get('/predict', response_class=HTMLResponse)
def take_inp():
    return '''
        <form method="post">
        <input maxlength="28" name="text" type="text" value="Text Emotion to be tested" />
        <input type="submit" />'''


@app.get('/')
def basic_view():
    return {"WELCOME": "GO TO /docs route, or /post or send post request to /predict "}


@app.get('/landing')
async def get_legacy_data():
    return FileResponse("tolgasuma.png")


@app.post('/predict')
def predict(text:str = Form(...)):
    clean_text = my_pipeline(text) #clean, and preprocess the text through pipeline
    loaded_model = tf.keras.models.load_model('sentiment.h5') #load the saved model 
    predictions = loaded_model.predict(clean_text) #predict the text
    sentiment = int(np.argmax(predictions)) #calculate the index of max sentiment
    probability = max(predictions.tolist()[0]) #calulate the probability
    if sentiment==0:
         t_sentiment = 'negative' #set appropriate sentiment
    elif sentiment==1:
         t_sentiment = 'neutral'
    elif sentiment==2:
         t_sentiment='postive'
    return { #return the dictionary for endpoint
         "ACTUALL SENTENCE": text,
         "PREDICTED SENTIMENT": t_sentiment,
         "Probability": probability
    }


