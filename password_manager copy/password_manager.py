from random import choice, shuffle
import base64 
from Crypto.Cipher import AES
import hashlib
import pickle
from os import path as os_path, remove, rename
from sys import path 
from enum import Enum

STATUS = Enum('STATUS',  'NORMAL QUIT CONTINUE')

class PasswordManager:
    def __init__(self, file_name, digit=8, special=True):
        self.file_name = file_name
        self.digit = digit
        self.special = special
        self.status = STATUS.NORMAL
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

    def decrept(self, key, text):
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
        with open(self.file_name, 'a') as f:
            f.write(doc)
            f.write('\n')
    
    def __read_file(self, split=False):
        with open(self.file_name, 'r') as f:
            for row in f:
                if row.strip():
                    if split:
                        app_name, user_name, password = row.strip().split('|')
                        yield {'app': app_name, 'user': user_name, 'pwd':password}

                    else: 
                        yield row.strip()

    def __screen(self, name):
        input_name = input(f'Please put in {name}(input "q" for quit; " " & "" for return): ').strip()
        if input_name == 'q': 
            self.status = STATUS.QUIT
            return 
        elif input_name == '':
            self.status = STATUS.CONTINUE
            return 
        else:
            self.status = STATUS.NORMAL
            return input_name 
        
    
    def __query_file(self, key, name, file_name):
        row_list = []
        for row_dict in file_name:
            if row_dict.get(key):
                if row_dict.get(key) == name:
                    print(row_dict)
                    row_list.append(row_dict)
        return row_list

    def __common_query(self, app_name=None, user_name=None):
        if app_name is None:
            app_name = self.__screen('app name')
            if not app_name:
                return

        file_gen = self.__read_file(split=True)
        query_list = self.__query_file('app', app_name, file_gen)
        if len(query_list) == 0:
            print(f'{app_name} does not exist! ')
            return

        if len(query_list) == 1:
            user_name = query_list[0]['user']
            password = query_list[0]['pwd']

        if len(query_list) >1:
            if user_name is None:
                user_name = self.__screen('user name')
                if not user_name:
                    return

            query_result = self.__query_file('user', user_name, query_list)
            if len(query_result) == 0:
                print(f'The {user_name} does not exist! ')
                return 
            else: 
                password = query_result[0]['pwd']

        return app_name, user_name, password
    
                         
    def __delete_file(self, app_name, user_name, password):
        query_name = app_name + '|' + user_name + '|' + password
        with open(self.file_name, 'r') as rf:
            with open(self.file_name + '.tmp', 'w+') as wf:
                for row in rf:
                    if row.strip().startswith(query_name):
                        continue
                    wf.write(row)
        remove(self.file_name)
        rename(self.file_name + '.tmp', self.file_name)
 
    def show_file(self):
        for row in self.__read_file():
            print(row)

    def create_item(self):
        app_name = self.__screen('app name')
        if not app_name:
            return
        user_name = self.__screen('user name')
        if not user_name:
            return
        secret_key = self.__screen('secret key')
        if not secret_key:
            return

        if app_name and user_name and secret_key:
            result = self.__common_query(app_name, user_name)
            if result:
                if result[1] == user_name:
                    print('Item exists!')
                    return 
                    
            password = self.__generate_password()
            print(f'password: {password}')
            encrypted_password = self.__encrypt(secret_key, password)
            doc = app_name + '|' + user_name + '|' + encrypted_password
            self.__write_file(doc)
            print(f'App_name & user_name: {app_name, user_name} has been created !')

    def edit_item(self):
        print('Edit item: ')
        self.delete_item()
        self.create_item()
        print('Finish edition !')
        
    def delete_item(self):
        result = self.__common_query()
        if result:
            app_name, user_name, password = result[0], result[1], result[2]
            self.__delete_file(app_name, user_name, password)
            print(f'App_name & user_name: {app_name, user_name} has been deleted !')

    def show_password(self):
        result = self.__common_query()
        if result:
            app_name, user_name, password = result[0], result[1], result[2]
            secret_key = self.__screen('secret key')
            try:
                password = self.__decrypt(secret_key, password)
                print(f'Show password successfully! App_name: {app_name}, user_name: {user_name}, passsword: {password}. ')
            except:
                print(f'Secret key: {secret_key} is incorrect !')

    def main(self):
        count = 0
        while 1:
            if count >3:
                break

            print('Welcome to password managemnt system !')

            user = self.__screen('your name')
            if self.status == STATUS.QUIT:
                self.status == STATUS.NORMAL
                break
            if self.status == STATUS.CONTINUE:
                self.status == STATUS.NORMAL
                count += 1
                continue

            pwd = self.__screen('password')
            if self.status == STATUS.QUIT:
                self.status == STATUS.NORMAL
                count += 1
                break
            if self.status == STATUS.CONTINUE:
                self.status == STATUS.NORMAL
                continue

            if self.__hash_encrypt(user, pwd) == self.__load_pickle('manager_pwd'):
                print('Log in successfully !')
                count2 = 0
                while 1:
                    if count2 > 3:
                        break

                    for i, j in enumerate(self.function_list):
                        print(i, ' ', j[0])
                    print('q quit')

                    selection = self.__screen('selection')

                    if self.status == STATUS.QUIT:
                        self.status == STATUS.NORMAL
                        break
                    if self.status == STATUS.CONTINUE:
                        self.status == STATUS.NORMAL
                        count2 += 1
                        continue

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
                            getattr(self, self.function_list[selection][1])()
                            if self.status == STATUS.QUIT:
                                self.status == STATUS.NORMAL
                                break
                            if self.status == STATUS.CONTINUE:
                                self.status == STATUS.NORMAL
                                continue

            else:
                count += 1
                print(f'Username or password is wrong ({count}) !')
                continue
            

        
if __name__ == "__main__":
    PasswordManager('all_pass', digit=10).main()
    
    # print(PasswordManager('all_pass', digit=10).decrept('Zyh12911037','18Dwd/hXev055H20YscDVQ=='))
