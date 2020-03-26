import json
import os
import requests
from webexteamssdk import *
from flask import Flask, request
app = Flask(__name__)

'''
For prototyping, we use ngrok.
We'll request the tunnel and parse the url to use for a webhook
'''
tunnel = json.loads(
    requests.request('GET', url='https://adaptuvecardweex.herokuapp.com/'
                     ).text
)
public_url = tunnel['tunnels'][0]['public_url']

'''
Specify the webex token and roomId to use
'''
token = 'Y2M0MTg0NzQtNmI4Yy00NjZlLThiOGUtMTY3YWUxNGM1M2I4N2RhOTZlNmQtZGYz_PF84_3c801018-052a-4f7e-b2a3-d527f6768f3e'
roomId = 'Y2lzY29zcGFyazovL3VzL1JPT00vYTVmYjAyMjAtNTk4My0xMWVhLWJlMmUtMjNjNjRmZDcyYTQ4'

'''
Using webexteamssdk but also need requests
for attachment action endpoint which is not in sdk yet!
'''
wbx = WebexTeamsAPI(access_token=token)
headers = {
    'Authorization': 'Bearer ' + token
}

'''
Register webhook to ngrok for attachmentActions
'''
for webhook in wbx.webhooks.list():
    wbx.webhooks.delete(webhook.id)

wbx.webhooks.create(
    name='Development - ngrok',
    targetUrl=public_url,
    resource='attachmentActions',
    event='created'
)

'''
Paste Card from adaptivecards.io/designer to a file named card.json 
'''
attachments = []
attachment = {}
attachment['contentType'] = "application/vnd.microsoft.card.adaptive"
attachment['content'] = json.loads(open('card.json').read())
attachments.append(attachment)
'''
Send Message
'''
wbx.messages.create(
    roomId=roomId,
    markdown='.',
    attachments=attachments
)

'''
Receive Data in Webhook and Request Action Payload
'''


@app.route('/', methods=['POST'])
def index():
    action = request.json['data']['id']
    results = requests.request('GET',
                               headers=headers,
                               url=f'{wbx.base_url}attachment/actions/{action}'
    )
    print(json.loads(results.text))
    return ('', 200, None)


if __name__ == '__main__':
    app.run(port=3000, use_reloader=True)
