import requests

url = "http://172.16.71.198:6060/translate"
data = {
    "source": "hello world",
    "src_lang": "eng_Latn",
    "tgt_lang": "prs_Arab"

}
res = requests.post(url,json=data)

# first check status
if res.status_code == 200:
    print(res.json())  # should return {'translation': ['...']}
else:
    print("Error:", res.status_code)
    print(res.text)