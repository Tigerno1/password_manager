from random import choice, shuffle
import base64 
from Crypto.Cipher import AES
import hashlib
import pickle
from os import path as os_path 
from sys import path 


class PasswordManager:
    def __init__(self, file_name, digit=8, special=True):
        self.file_name = file_name
        self.digit = digit
        self.special = special
        self.function_list = [('show all files', 'show_file'),
                                ('create an item', 'create_item'), 
                                ('edit an item',  'edit_item'), 
                                ('delete an item', 'delete_item'), 
                                ('show one password', 'show_password')]

        file_path = os_path.join(os_path.dirname(os_path.abspath(__file__)), file_name)
        if not os_path.exists(file_path):
            f = open(file_name, 'w')
            f.close()

    def __generate_password(self):
        result = []
        for i in range(0, self.digit):
            if i % 4 == 0:
                result.append(choice('1234567890'))
            if i % 4 == 1:
                result.append(choice('abcdefghijklmnopqrstuvwxyz'))
            if i % 4 == 2:
                result.append(choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
            if self.special:
                if i % 4 == 3:
                    result.append(choice('!$%()+,-.:;>?@[]`{}'))
        shuffle(result)
        return "".join(result)

    def __add_to_16(self, value):
        while len(value) % 16 != 0:
            value += '\0'
        return str.encode(value) 

    def __encrypt(self, key, text):
        aes = AES.new(self.__add_to_16(key), AES.MODE_ECB)  
        encrypt_aes = aes.encrypt(self.__add_to_16(text))  
        encrypted_text = str(base64.encodebytes(encrypt_aes), encoding='utf-8') 
        return encrypted_text

    def __decrypt(self, key, text):
        aes = AES.new(self.__add_to_16(key), AES.MODE_ECB)  
        base64_decrypted = base64.decodebytes(text.encode(encoding='utf-8'))  
        decrypted_text = str(aes.decrypt(base64_decrypted), encoding='utf-8').replace('\0', '') 
        return decrypted_text

    def __hash_encrypt(self, user, pwd):
        sha1 = hashlib.sha1()
        sha1.update(user.encode('utf-8'))
        sha1.update(pwd.encode('utf-8'))
        info = sha1.hexdigest()
        return info 

    def __load_pickle(self, file_path):
        with open(file_path, 'rb') as f:
            info = pickle.load(f)
        return info
    
    def __write_file(self, doc):
        with open(self.file_name, 'a+') as f:
            f.write(doc)
            f.write('\n')
    
    def __read_file(self):
        with open(self.file_name, 'r') as f:
            for row in f.readlines():
                if row.strip(): 
                    print(row)

    def __query_file(self, key):
        with open(self.file_name, 'r') as f:
            for row in f.readlines():
                if row.strip():
                    app_name, user_name, password = row.split('|')
                    if app_name == key:
                        return user_name, password
                         
    def __delete_file(self, key):
        data = ''
        with open(self.file_name, 'r+') as f:
            for row in f.readlines():
                if row.strip():
                    app_name, _, _ = row.split('|')
                    if app_name == key:
                        print('Identify file successfully !')
                        continue
                    data += row 
        with open(self.file_name, 'w') as f:
            f.write(data)
    
    def show_file(self):
        self.__read_file()

    def create_item(self):
        app_name = input('Please put in App name(input "q" for quit): ')
        if app_name == 'q':
            return 'q'

        elif self.__query_file(app_name):
            return 

        else:
            nick_name = input('Please put in your name or email: ')
            secret_key = input('Please put in your secret key: ')
            password = self.__generate_password()
            print(f'password: {password}')
            encrypted_password = self.__encrypt(secret_key, password)
            doc = app_name + '|' + nick_name + '|' + encrypted_password
            self.__write_file(doc)

    def edit_item(self):
        app_name = input('Please put in App name(input "q" for quit): ')
        if app_name == 'q':
            return 'q'
        self.__delete_file(app_name)
        self.create_item()
    
    def delete_item(self):
        app_name = input('Please put in App name(input "q" for quit): ')
        if app_name == 'q':
            return 'q'
        self.__delete_file(app_name)

    def show_password(self):
        app_name = input('Please put in App name(input "q" for quit): ')
        if app_name == 'q':
            return 'q'
        secret_key = input('Please put in your secret key: ')
        if not self.__query_file(app_name):
            print(f'{app_name} does not exist !')
            return
        nick_name, password = self.__query_file(app_name)
        try:
            password = self.__decrypt(secret_key, password)
        except:
            print(f'Secret key: {secret_key} is incorrect !')
        print(f'nick_name: {nick_name}, password: {password}')

    @property
    def main(self):
        count = 0
        while 1:
            print('Welcome to password managemnt system !')
            user = input('Please put in your name(input "q" for quit): ').strip()
            if user == 'q':
                break
            pwd = input('Please put in your password: ').strip()

            if self.__hash_encrypt(user, pwd) == self.__load_pickle('manager_pwd'):
                print('log in successfully !')
                count2 = 0
                while 1:
                    for i, j in enumerate(self.function_list):
                        print(i, ' ', j[0])
                    print('q quit')

                    selection = input('Please put in your selection: ').strip()
                    
                    if selection == 'q' or count2 > 3:
                        break

                    elif not selection.isdigit():
                        print('The choice you put in should be numberic !')
                        count2 += 1
                        continue

                    elif int(selection) >= len(self.function_list):
                        print('Selection out of range !')
                        count2 += 1
                        continue

                    else:
                        selection = int(selection)
                        if hasattr(self, self.function_list[selection][1]):
                            quit = getattr(self, self.function_list[selection][1])()
                            if quit == 'q':
                                break

            else:
                count += 1
                print(f'Username or password is wrong ({count}) !')
                if count > 3: 
                    break
                continue
            

        
if __name__ == "__main__":
    PasswordManager('all_pass', digit=10).main()
