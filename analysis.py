import json
from collections import Counter

# load the data from the JSON file
with open('output.json') as f:
    data = json.load(f)

# get the total number of objects in the list
num_objects = len(data)
print(f'Total number of objects: {num_objects}')

# get the count of duplicate items
item_counts = Counter(json.dumps(d, sort_keys=True) for d in data)
for item, count in item_counts.items():
    if count > 1:
        print(f'{count} instances of item: {item}')
