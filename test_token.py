# test token

import requests
import requests.auth
'''
client_auth = requests.auth.HTTPBasicAuth('p-jcoLKBynTLew', 'gko_LXELoV07ZBNUXrvWZfzE3aI')
post_data = {"grant_type": "password", "username": "reddit_bot", "password": "snoo"}

headers = {"User-Agent": "ChangeMeClient/0.1 by YourUsername"}
response = requests.post("https://www.reddit.com/api/v1/access_token", auth=client_auth, data=post_data, headers=headers)
print(response.json())
'''

def get_auth():
    client_id = 'gUXEKVnrqETGkRnMCnVOiQ'
    URI = 'https://im.nju.edu.cn/sny/list.htm'
    dur = 'temporary'
    scope = 'read'

    url = f'''https://www.reddit.com/api/v1/authorize?client_id={client_id}&response_type=code&
    state=RANDOM_STRING&redirect_uri={URI}&duration={dur}&scope={scope}'''

    re = requests.get(url)
    if re.status_code == 200:
        print(re.content)
        #print(re.json())
    else:
        print(re.status_code)

if __name__ == '__main__':
    get_auth()


