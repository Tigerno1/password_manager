import hashlib 
import pickle
def secret_password():
    while 1: 
        name = input('Please put in your name("q" for quit): ')
        if name == 'q':
            break
        password = input('Please put in your password: ')
        test = input('Please put in your password again: ')
        if password != test:
            print('The password you put in is wrong !')
            continue
        sha = hashlib.sha1()
        sha.update(name.encode('utf-8'))
        sha.update(password.encode('utf-8'))
        manager_pwd = sha.hexdigest()
        with open('manager_pwd', 'wb') as f:
            pickle.dump(manager_pwd, f)
        break

if __name__ == '__main__':
    secret_password()


