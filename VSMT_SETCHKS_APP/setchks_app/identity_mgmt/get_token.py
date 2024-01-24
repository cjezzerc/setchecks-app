import base64, jwt, requests, os

from setchks_app.identity_mgmt.redirect_uri import redirect_uri

def get_token_from_code(code=None):
    client_id=os.environ["COGNITO_CLIENT_ID"]
    client_secret=os.environ["COGNITO_CLIENT_SECRET"]
    token_url="https://vsmt-jc-test1.auth.eu-west-2.amazoncognito.com/oauth2/token"
    message = bytes(f"{client_id}:{client_secret}",'utf-8')
    secret_hash = base64.b64encode(message).decode()
    payload = {
        "grant_type": 'authorization_code',
        "client_id": client_id,
        "code": code,
        # "redirect_uri": 'http://localhost:5000/cognito_test'
        "redirect_uri": redirect_uri
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {secret_hash}"}
        
    resp = requests.post(token_url, params=payload, headers=headers)
    token_dict=((jwt.decode(resp.json()['id_token'], algorithms=["RS256"], options={"verify_signature": False})))
    token_dict['refresh_token']=resp.json()['refresh_token'] # add refresh token to token_dict
    return token_dict

def get_token_from_refresh_token(refresh_token=None):
    client_id=os.environ["COGNITO_CLIENT_ID"]
    client_secret=os.environ["COGNITO_CLIENT_SECRET"]
    token_url="https://vsmt-jc-test1.auth.eu-west-2.amazoncognito.com/oauth2/token"
    message = bytes(f"{client_id}:{client_secret}",'utf-8')
    secret_hash = base64.b64encode(message).decode()
    payload = {
        "grant_type": 'refresh_token',
        "refresh_token": refresh_token
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {secret_hash}"}
        
    resp = requests.post(token_url, params=payload, headers=headers)
    if 'id_token' in resp.json():
        token_dict=((jwt.decode(resp.json()['id_token'], algorithms=["RS256"], options={"verify_signature": False})))
        token_dict['refresh_token']=refresh_token # add refresh token to token_dict
    else:
        token_dict={}
    return token_dict