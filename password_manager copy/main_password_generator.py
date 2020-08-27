import hashlib 
import pickle
def secret_password(name, password):
    sha = hashlib.sha1()
    sha.update(name.encode('utf-8'))
    sha.update(password.encode('utf-8'))
    manager_pwd = sha.hexdigest()
    with open('manager_pwd', 'wb') as f:
        pickle.dump(manager_pwd, f)

if __name__ == "__main__":
    name = ''
    password = ''
    secret_password(name, password)