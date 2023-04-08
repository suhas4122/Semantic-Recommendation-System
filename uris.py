# read one json object from all_products.json file at a time
# and convert it to it's turtle representation
# and write it to all_products.ttl file

import json
import re

def convert_to_turtle_product(object, uris_file):
    # add label in underscore-separated format
    label = object['Title']
    label = re.sub('[^0-9a-zA-Z ]+', ' ', label)
    label = re.sub(' +', ' ', label)
    label = label.replace(' ', '_')
    uris_file.write("exr:" + label + '\n')
    # print(label)

file = open(file='data/all_products.json', mode='r')

data = json.load(file)

for object in data:
    for key in object:
        if type(object[key]) == str:
            object[key] = object[key].replace('"', '')
            object[key] = object[key].replace("'", '')
            object[key] = object[key].replace(',', '')
    
# create a new file to write the turtle representation
uris_file = open(file='uris.txt', mode='w')  

for object in data:
    convert_to_turtle_product(object, uris_file)