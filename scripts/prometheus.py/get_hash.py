import getpass
import bcrypt

password = "klpASDFR--..732"
hashed_password = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
print(hashed_password.decode())