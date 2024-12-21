from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
import hashlib
import os

def encrypt_files(key,path):
    files = os.listdir(path)

    hashed = hashlib.sha256(key.encode()).digest()
    key = hashed[:16]
    iv = hashed[16:32]
    
    for filename in files:
        mpath = os.path.join(path,filename)
        
        file = open(mpath,"br")
        data = file.read()
        file.close()
        
        data = pad(data,16)
        assert data[4:8] == b'ftyp'

        cipher = AES.new(key,AES.MODE_CBC,iv)
        newdata = cipher.encrypt(data)

        newpath = "".join(mpath.split(".")[:-1])+".db"
        file = open(newpath,"wb")
        file.write(newdata)
        file.close()

        os.remove(mpath)

def decrypt_files(key,path):
    files = os.listdir(path)

    hashed = hashlib.sha256(key.encode()).digest()
    mykey = hashed[:16]
    iv = hashed[16:32]

    i = 1
    for filename in files:
        mpath = os.path.join(path,filename)
        
        file = open(mpath,"br")
        data = file.read()
        file.close()

        cipher = AES.new(mykey,AES.MODE_CBC,iv)
        newdata = cipher.decrypt(data)
        
        if newdata[4:8] != b'ftyp':
            print(f"INCORRECT KEY! failed in {i} attempt")
            return False

        newdata = unpad(newdata,16)
    
        newpath = "".join(mpath.split(".")[:-1])+".mp4"
        file = open(newpath,"wb")
        file.write(newdata)
        file.close()

        os.remove(mpath)
        i+=1

    print("CORRECT KEY!")
    return key

print("CRYPT")
print("1. Encrypt.")
print("2. Decrypt.")
ch = input("Enter choice:")

if ch=="1":
    path = input("Enter path:")
    files = os.listdir(path)
    assert all([True if item[-4:]==".mp4" else False for item in files])==True,"not all files are .mp4"
    os.system(f"ls {path}")
    key = input("Enter key to encrypt:")
    encrypt_files(key, path)
    print("DONE.")

elif ch=="2":
    path = input("Enter path:")
    files = os.listdir(path)
    assert all([True if item[-3:]==".db" else False for item in files])==True, "not all files are .db"
    os.system(f"ls {path}")
    key = input("Enter key to decrypt:")
    decrypt_files(key, path)  
    print("DONE.")