#genera un codigo por defecto de x digitos
import string 
import random 

def Key(digit=4):
    keylist = [random.choice(base_str()) for i in range(digit)] 
    return ("".join(keylist)) 
    
def base_str(): 
    return (string.ascii_letters+string.digits) 
    
