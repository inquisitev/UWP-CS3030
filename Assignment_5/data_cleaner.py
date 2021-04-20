import json
with open('./full_dataset.tsv') as data: 

    with open ('ids_only.txt', 'w+') as output:
        i = 0
        line = data.readline()
        while line:
            if i > 10000:
                break
            i += 1
            output.write(line.split('\t')[0] + "\n") 
            line = data.readline()

