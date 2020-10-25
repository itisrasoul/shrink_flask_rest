#Import libs
import random
import string

#Create function for generating a string of random letters
def gen_random_letter():
    return ("".join(random.choice(string.ascii_letters) for i in range(10)))