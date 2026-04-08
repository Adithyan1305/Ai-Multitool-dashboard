import urllib.request
import json

url = 'http://localhost:5000/api/math'
data = json.dumps({'query': 'what is square root of 625'}).encode('utf-8')
headers = {'Content-Type': 'application/json'}

try:
    req = urllib.request.Request(url, data=data, headers=headers, method='POST')
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        print('Response:', result)
except Exception as e:
    print('Error:', str(e))