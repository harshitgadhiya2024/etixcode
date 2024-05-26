import requests
import os, json
filepath = os.path.abspath("main.csv")

url = "http://127.0.0.1:5000/"

payload = {}

files=[
  ('uploadfile',('main.csv',open(filepath,'rb'),'text/csv'))
]
headers = {}

response = requests.request("POST", url, headers=headers, data=payload, files=files, timeout=100000)

response_data = json.loads(response.text)
output_data = response_data["output_data"]
with open("requests_log.json", "w") as f:
    json.dump(output_data, f, indent=4)
