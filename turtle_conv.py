# read one json object from all_products.json file at a time
# and convert it to it's turtle representation
# and write it to all_products.ttl file

import json
import re

def convert_to_turtle_product(object, turtle_file):
    # add label in underscore-separated format
    label = object['Title']
    label = re.sub('[^0-9a-zA-Z ]+', ' ', label)
    label = re.sub(' +', ' ', label)
    label = label.replace(' ', '_')

    turtle_file.write('exr:' + label + '\n')
    turtle_file.write('\t\trdfs:label ' + '"' + object['Title'] + '"' + ' ;\n')
    # rdf:type exs:Product
    turtle_file.write('\t\trdf:type exr:Product ;\n')
    # add price as ^^xsd:float
    turtle_file.write('\t\texs:price ' + '"')
    turtle_file.write(str(object['Price']))
    turtle_file.write('"' + '^^xsd:integer ;\n')
    # add link as exs:link
    turtle_file.write('\t\texs:link ' + '"' + object['Link'] + '"' + '^^xsd:string ;\n')
    # add image as exs:image
    turtle_file.write('\t\texs:image ' + '"' + object['Image'] + '"' + '^^xsd:string ;\n')
    # add rating as ^^xsd:float
    turtle_file.write('\t\texs:rating ' + '"')
    turtle_file.write(str(object['Rating']))
    turtle_file.write('"' + '^^xsd:float ;\n')
    # add manufacturer as exs:manufacturer
    manufacturer = object['Manufacturer']
    manufacturer = re.sub('[^0-9a-zA-Z ]+', ' ', manufacturer)
    manufacturer = re.sub(' +', ' ', manufacturer)
    manufacturer = manufacturer.replace(' ', '_').lower()
    # if manufacturer is not empty
    if manufacturer != '':
        turtle_file.write('\t\texs:manufacturer exr:'+ manufacturer + ' ;\n')
    else:
        # insert rdf:nil
        turtle_file.write('\t\texs:manufacturer rdf:nil ;\n')
    # exs:category 
    turtle_file.write('\t\texs:category ( ')
    # iterate over all categories
    for category in object['Category']:
        # replace all non-alphanumeric characters with empty string
        category = re.sub('[^0-9a-zA-Z ]+', ' ', category)
        # replace multiple spaces with single space
        category = re.sub(' +', ' ', category)
        # add category as exs:category
        turtle_file.write('exr:' + category.replace(' ', '_') + ' ')
    turtle_file.write(') .\n\n')
    

file = open(file='data/all_products.json', mode='r')

data = json.load(file)

for object in data:
    for key in object:
        if type(object[key]) == str:
            object[key] = object[key].replace('"', '')
            object[key] = object[key].replace("'", '')
            object[key] = object[key].replace(',', '')
    
# create a new file to write the turtle representation
turtle_file = open(file='data/all_products.ttl', mode='w')  
turtle_file.write('@prefix exs: <http://example.org/schema#> .\n')
turtle_file.write('@prefix exr: <http://example.org/resource#> .\n')
turtle_file.write('@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n')
turtle_file.write('@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n')
turtle_file.write('@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .\n\n')

# create an empty manufacturer set
manufacturer_set = set()

category_set = set()

for object in data:
    # insert manufacturer in manufacturer_set
    if object['Manufacturer'] != '':
        manufacturer_set.add(object['Manufacturer'])
    convert_to_turtle_product(object, turtle_file)
    for category in object['Category']:
        category_set.add(category)

for manufacturer in manufacturer_set:
    manufacturer_name = manufacturer
    # replace all non-alphanumeric characters with empty string
    manufacturer = re.sub('[^0-9a-zA-Z ]+', ' ', manufacturer)
    # replace multiple spaces with single space
    manufacturer = re.sub(' +', ' ', manufacturer)
    turtle_file.write('exr:' + manufacturer.replace(' ', '_') + '\n')
    turtle_file.write('\t\trdf:type exr:Manufacturer ;\n')
    turtle_file.write('\t\trdfs:label ' + '"' + manufacturer_name + '"' + ' .\n\n')

for category in category_set:
    category_name = category
    # replace all non-alphanumeric characters with empty string
    category = re.sub('[^0-9a-zA-Z ]+', ' ', category)
    # replace multiple spaces with single space
    category = re.sub(' +', ' ', category)
    turtle_file.write('exr:' + category.replace(' ', '_') + '\n')
    turtle_file.write('\t\trdf:type exr:Category ;\n')
    turtle_file.write('\t\trdfs:label ' + '"' + category_name + '"' + ' .\n\n')