import json
import os
import re
import pickle
import boto3
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords
import pandas as pd
from io import BytesIO, StringIO

s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

# bucket = "akanksha-twitter-model"
# key = "logistic_model.pkl"

s3 = boto3.resource('s3')
with BytesIO() as data:
    s3.Bucket(os.environ(['BUCKET'])).download_fileobj(os.environ(['KEY']), data)
    data.seek(0)  # move back to the beginning after writing
    cv = pickle.load(data)
    model = pickle.load(data)


def lambda_function(event, context):
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']
    print('key :: ', key, ' bucket :: ', bucket)
    data = get_file_content_from_s3(bucket, str(key.strip()))
    df = pd.read_csv(BytesIO(data))
    file_name = update_file_name(key)
    print("Renaming Done")
    print(len(df['tweet']))
    cleaned_data = preprocess(df['tweet'])
    print("Cleaning Done")

    print("Model extracted")
    result = prediction(cleaned_data)

    url = upload_to_s3(bucket, file_name, pd.DataFrame(cleaned_data, columns=['tweet']))
    print("URL generated :: ", url)
    return {
        'statusCode': 200,
        'body': json.dumps(result),
    }


def get_file_content_from_s3(bucket, key):
    response = s3_client.get_object(Bucket=bucket, Key=key)
    data = response['Body'].read()
    return data


def update_file_name(key):
    name = key.split('.')[0] + "_result.csv"
    return name


def upload_to_s3(bucket, destination_file_name, df):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer)
    s3.Object(bucket, destination_file_name).put(Body=csv_buffer.getvalue())
    url = '{}/{}/{}'.format(s3_client.meta.endpoint_url, bucket, destination_file_name)
    return url


def preprocess(data):
    tokenizer = TweetTokenizer()
    stop_words = set(stopwords.words('english'))
    lemma_function = WordNetLemmatizer()
    my_regex = "@\S+|https?:\S+|http?:\S|[^A-Za-z0-9]+"
    document = []
    for text in data:
        collection = []
        tokens = tokenizer.tokenize(text)
        for token in tokens:
            if token not in stop_words:
                if '#' in token:
                    collection.append(lemma_function.lemmatize(token))
                else:
                    collection.append(
                        lemma_function.lemmatize(re.sub(my_regex, " ", token)))
        document.append(" ".join(collection))
    return " ".join(document)


def prediction(cleaned_data):
    temp = cv.transform([cleaned_data])
    pred = model.predict(temp)
    if pred == 0:
        print('Positive')
        return 'Positive'
    else:
        print('Negative')
        return 'Negative'
