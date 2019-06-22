from fastecdsa import keys,curve,ecdsa
pub_key_set = {}

def generateKeys(id):
    priv_key,pub_key = keys.gen_keypair(curve.P256)
    pub_key_set[id]=pub_key 
    return [priv_key,pub_key]

def sign_message(message,priv_key):
    r,s = ecdsa.sign(message,priv_key)
    return [r,s]

def verify_message(r,s,message,pub_key):
    return ecdsa.verify((r,s),message,pub_key)
    