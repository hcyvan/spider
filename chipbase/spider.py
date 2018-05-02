import json

import requests
from pyquery import PyQuery


def get_genes_by_sample(sample_id, start=0, length=60):
    url = "http://rna.sysu.edu.cn/chipbase/php/get_regulation_info_table.php"
    payload = dict(
        assembly="hg38",
        downstream="1kb",
        draw=3,
        length=15,
        motif_status="All",
        sample_id="HUMHG01012",
        start=0,
        target_symbol="All lncRNA genes",
        target_type="lncRNA",
        upstream="1kb"
    )
    payload["length"] = length
    payload["start"] = start
    payload["sample_id"] = sample_id
    # print("GET sample_id: {}, length: {}, start: {}".format(sample_id, length, start))
    response = requests.request("POST", url, data=payload)
    return json.loads(response.text)


def get_gene_symbols_by_sample(sample_id, start=0, length=60):
    data = get_genes_by_sample(sample_id, start=start, length=length)
    genes = []
    genes.extend(data['data'])
    total = data['recordsFiltered']
    remain_length = total - len(data['data'])
    while remain_length > 0:
        start = start + len(data["data"])
        data = get_genes_by_sample(sample_id, start, length)
        genes.extend(data['data'])
        remain_length = remain_length - len(data['data'])

    results = []
    for gene in genes:
        results.append([gene['gene_symbol'], gene['gene_type']])
    return results


def get_rp(gene_symbol):
    url = 'http://rna.sysu.edu.cn/chipbase/coexpression_browse.php?organism=human&assembly=hg38&tf_symbol=AR&gene_symbol={}'.format(
        gene_symbol)
    r = requests.get(url=url)
    d = PyQuery(r.content)
    p = d('#coexpression_statistics tr')
    for tr in p.items():
        if 'prostate adenocarcinoma' in tr.text():
            rp = tr.text().split('\n')
            return rp[2], rp[3]
    return None, None


# "HUMHG01012"

def get_gene_sample_pair(sample):
    genes = get_gene_symbols_by_sample(sample)
    results = []
    for gene in genes:
        rp = get_rp(gene[0])
        print("     sample_id: {}, gene symbol: {}".format(sample_id, gene[0]))
        results.append([sample, gene[0], gene[1], rp[0], rp[1]])
    return results


def get_sample_ids():
    with open('sample_ids.txt') as f:
        sample_ids = [x.strip('\n') for x in f.readlines()]
    return sample_ids


sample_ids = get_sample_ids()
for sample_id in sample_ids:
    print('Geting sample_id: {}'.format(sample_id))
    results = get_gene_sample_pair(sample_id)
    for result in results:
        with open('sample_gene_pair.txt', 'a') as f:
            f.write('{},{},{},{}\n  '.format(result[0], result[1], result[2], result[3], result[4]))
