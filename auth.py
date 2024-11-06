from flask import Flask, request, redirect
import requests

app = Flask(__name__)

CLIENT_ID = '86rcupnam6eweu'
CLIENT_SECRET = '2wXXWfov5f7PqAoG'
REDIRECT_URI = 'https://rtylerh.com/about/'

@app.route('/')
def index():
    authorization_url = ('https://www.linkedin.com/oauth/v2/authorization'
                         '?response_type=code&client_id={}&redirect_uri={}&scope=r_liteprofile%20r_emailaddress%20w_member_social').format(CLIENT_ID, REDIRECT_URI)
    return '<a href="{}">Login with LinkedIn</a>'.format(authorization_url)

@app.route('/auth')
def auth():
    code = request.args.get('code')
    if code:
        # Exchange the authorization code for an access token
        token_url = 'https://www.linkedin.com/oauth/v2/accessToken'
        payload = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': REDIRECT_URI,
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET
        }
        response = requests.post(token_url, data=payload)
        access_token = response.json().get('access_token')
        return 'Access Token: {}'.format(access_token)
    return 'Authorization failed.'

if __name__ == '__main__':
    app.run(debug=True)
