import getpass
import bcrypt

password = "password:CcdHZ^fuq0v8wtq2vHT1"
hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print(hashed_password.decode())