import jwt

def token_to_id(token, secret_key):
    '''유저 토큰과 비밀 키를 받아서 토큰을 아이디로 변환하는 함수 
    
    Args: 
        token (str): 유저 토큰 정보 
        secret_key (str): 비밀 키 값
    
    Returns: 
        str: 유저 아이디
    '''

    token = bytes(token[2:-1].encode('ascii'))
    payload= jwt.decode(token, secret_key, algorithms=['HS256'])
    return payload['ID']


def token_to_ph(token, secret_key):
    '''유저 토큰과 비밀 키를 받아서 토큰을 아이디로 변환하는 함수 
    
    Args: 
        token (str): 유저 토큰 정보 
        secret_key (str): 비밀 키 값
    
    Returns: 
        str: 유저 아이디
    '''

    token = bytes(token[2:-1].encode('ascii'))
    payload= jwt.decode(token, secret_key, algorithms=['HS256'])
    return payload['PHONE']