import re

import requests


def is_reject(url):
    r = requests.get(url)
    text = r.text
    with open('notice.db', 'a') as f:
        f.write('>>>>>>\n>>> {}\n{}\n<<<<<<<\n'.format(url, r.text))
    r1 = re.compile('(\d+)\s*票反对')
    r2 = re.compile('反对\s*(\d+)\s*票')
    r3 = re.compile('反对票\s*(\d+)\s*票')
    g1 = re.compile('(\d+)\s*票弃权')
    g2 = re.compile('弃权\s*(\d+)\s*票')
    g3 = re.compile('弃权票\s*(\d+)\s*票')
    for p in [r1, r2, r3, g1, g2, g3]:
        match = p.search(text)
        if not match:
            continue
        num = match.group(1)
        if int(num) > 0:
            return True
    return False


with open('notice.txt') as f:
    lines = f.readlines()

for line in lines:
    line = line.strip('\n')
    notice = line.split('||')
    url = notice[2]
    date = notice[1].split('T')[0]
    title = notice[0]
    code = notice[2].split('/')[5]
    print(url)
    if is_reject(url):
        with open('notice.reject.csv', 'a') as f:
            f.write('{},{},{}\n'.format(code, title, date))
