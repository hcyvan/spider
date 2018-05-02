import re

sample_id_re = re.compile('value="(.*?)"')

with open('regulation_samples.txt') as f:
    lines = f.readlines()
    for line in lines:
        match = sample_id_re.search(line)
        if match:
            print(match.group(1))
