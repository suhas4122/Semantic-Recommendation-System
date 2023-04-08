import random
import os

# read uris.txt file and create a list of uris
uris = []
uris_file = open(file='data/uris.txt', mode='r')
for line in uris_file:
    # append the uri to the list without the newline character
    uris.append(line[:-1])

# randomly select 100 uris from the list
random_uris = random.sample(uris, 100)

# # create directory to store user history files
# if not os.path.exists('user_history_files'):
#     os.mkdir('user_history_files')

# create a user_histories.txt file
user_histories_file = open(file='data/user_histories.ttl', mode='w')

# make 8 user_history_files, each containing 10 uris randomly selected from the list
for j in range(8):
    user_histories_file.write('exr:user_' + str(j + 1) + '\n')
    user_histories_file.write('\trdf:type exr:User ;\n')
    # select randomly 10 uris from the random_uris list for each user
    user_uris = random.sample(random_uris, 10)  
    for i in range(10):
        user_histories_file.write('\texs:bought ' + user_uris[i])
        if i != len(user_uris) - 1:
            user_histories_file.write(' ;\n')
        else:
            user_histories_file.write(' .\n\n')
