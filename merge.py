# merge multiple json files into a single json
import json

json_files = ['data-suhas.json', 'data-aks.json',
    'data-vg1.json', 'data-vg2.json', 'data-vg2.json']

result = list()
for f1 in json_files:
    with open(f1, 'r') as infile:
        result.extend(json.load(infile))

with open('data.json', 'w') as output_file:
    json.dump(result, output_file)

# combine text files into one file
link_files = ['links-suhas.txt', 'links-aks.txt',
    'links-vg1.txt', 'links-vg2.txt', 'links-vg2.txt']

with open('links.txt', 'w') as outfile:
    for fname in link_files:
        with open(fname) as infile:
            for line in infile:
                outfile.write(line)