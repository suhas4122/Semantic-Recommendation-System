# load all data from data/all_products.json
import json

with open('data/all_products.json', 'r') as f:
    all_products = json.load(f)
    l = []
    links = []
    titles = set()
    print(len(all_products))
    for product in all_products:
        # search in l if all fields already same
        found = 0
        for obj in l:
            if obj == product:
                found = 1
                break
        if found == 0 and product['Title'] not in titles:
            l.append(product)
            links.append(product['Link'])
            titles.add(product['Title'])

print(len(l))
print(len(titles))
# write l to a new json file

with open('data/all_products.json', 'w') as f:
    json.dump(l, f)

with open('data/links.txt', 'w') as f:
    for line in links:
        f.write(f"{line}\n")