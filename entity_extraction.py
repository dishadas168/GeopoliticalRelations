"""
Helper functions for entity extraction using Petrarch App
"""

import requests
import json
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
import configparser

WNL = nltk.WordNetLemmatizer()

def get_cameo_mappings(config_path):
    parser = configparser.ConfigParser()
    parser.read(config_path)
    mappingfile_name = parser.get('Dictionaries', 'mappingfile_name')
    map_dict = {}
    with open(mappingfile_name, encoding='utf8') as f:
        for line in f:
            split_sent = line.split(":")
            if len(split_sent) > 1:
                cameo_code = split_sent[0].strip()
                goldstein_score = float(split_sent[1].split("]")[0][1:])
                map_dict[cameo_code] = goldstein_score

    return map_dict

def format_parsed_str(parsed_str):
    parsed_str = parsed_str.replace("/", " ")
    if parsed_str.strip().startswith("(ROOT") and parsed_str.strip().endswith(")"):
        parsed_str = parsed_str.strip()[5:-1].strip()
    elif parsed_str.strip()[1:].strip().startswith("("):
        parsed_str = parsed_str.strip()[1:-1]
    parsed = parsed_str.split('\n')
    parsed = [line.strip() + ' ' for line in [line1.strip() for line1 in
                                              parsed if line1] if line]
    parsed = [line.replace(')', ' ) ').upper() for line in parsed]
    treestr = ''.join(parsed)
    return treestr

def send_to_petr(event_dict):
    #Testing Lambda docker locally
    # docker run -p 9000:8080 lambda/petrarch2:2.0
    headers = {'Content-Type': 'application/json'}
    events_data = {'events' : event_dict}
    events_data = {'body' : events_data}
    # print("INPUT : ",events_data)
    petr_url = 'http://localhost:9000/2015-03-31/functions/function/invocations'
    events_r = requests.post(petr_url,  headers=headers, json=events_data)
    events_r = json.loads(events_r.text)
    # print("RAW OUTPUT : ", events_r)
    events_r = json.loads(events_r['body'])
    return events_r

def parse_sentence(input_text):
    """The CoreNLP API produces the expected parse output."""
    #Opens at port 8000
    #Use this command
    #docker run -p 8000:9000 corenlp
    res = requests.post(
        'http://localhost:8000/?properties={"annotators":"parse","outputFormat":"json"}',
        data=bytes(input_text, 'utf-8'))
    json_result = res.json()
    return json_result['sentences'][0]['parse']

# lemmatize
def lemmatize(text):
    text = [WNL.lemmatize(t) for t in text]
    return text

# tokenize
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    return tokens