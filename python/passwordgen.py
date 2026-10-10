import string
import random

print("=== PASSWORD GEN ===")

userpass = int(input("Enter The Char You Want In Pass :"))
ID = userpass
Provider = (string.ascii_lowercase + string.ascii_uppercase + string.digits+string.punctuation)
random.choice(Provider)
Random_Words = random.choice(Provider)
password = ""
for i in range(userpass):
    Random_Words = random.choice(Provider)
    password = password + Random_Words

print("Your password is:", password)