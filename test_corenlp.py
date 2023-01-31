"""
Test 

Given a text, parse into expected dependency tree, suitable for consumption by Petrarch app
Prerequisites: Docker run CoreNLP
"""

import requests

def test_api_short(input_text):
    """The CoreNLP API produces the expected parse output."""
    res = requests.post(
        'http://localhost:8000/?properties={"annotators":"parse","outputFormat":"json"}',
        data=bytes(input_text, 'utf-8'))
    json_result = res.json()
    return json_result['sentences'][0]['parse']

input_text = "Although they didn't like it, they accepted the offer."
print(test_api_short(input_text))
