import os
import json
import datetime
import time

import requests


def get_notice(date_time='2015-01-01', page_size=50, page_index=1):
    payload = {
        'time': date_time,
        'PageSize': page_size,
        'PageIndex': page_index,
        'rt': '50821627',
        'SecNodeType': 0,
        'jsObj': 'jqNVhyQg',
        'CodeType': 1,
        'FirstNodeType': 0,
        'StockCode': ''
    }
    for i in range(20):
        try:
            r = requests.get('http://data.eastmoney.com/notices/getdata.ashx', params=payload)
            break
        except Exception as e:
            time.sleep(20)
            print(e)
            print('Continue....')
            continue
    else:
        print('Net Failed on {}'.format(date_time))
        exit()
    print('{}: {} :{}'.format(page_index, date_time, r.url))
    with open('notice.log', 'a') as log:
        log.write('Get {}: page index {}\n'.format(date_time, page_index))
    try:
        js = r.text
        data = js[js.index('{'):(len(js) - 1)]
        data_dict = json.loads(data)
        return data_dict
    except Exception as e:
        print(e)
        print('Please Change IP...')
        exit()


def get_notice_list(date_time='2015-01-01', page_size=50, page_index=1):
    results = []
    data = get_notice(date_time, page_size, page_index)
    pages = data['pages']
    notices = data['data']
    if notices is not None:
        results.extend(notices)
        for i in range(2, pages + 1):
            data_tmp = get_notice(date_time, page_size, i)
            if data_tmp['data']:
                results.extend(data_tmp['data'])
    with open('notice_list.db', 'a') as f:
        for result in results:
            f.write('---------\n{}\n'.format(json.dumps(result)))
    return results


def get_notices(date_time='2015-01-01'):
    results = []
    notices = get_notice_list(date_time, 50, 1)
    for index, notice in enumerate(notices):
        with open('notice_list.db', 'a') as f:
            for result in results:
                f.write('---------\n{}\n'.format(json.dumps(result)))
        if '董事会' in notice['NOTICETITLE'] and '会议决议' in notice['NOTICETITLE']:
            results.append(dict(title=notice['NOTICETITLE'], url=notice['Url'], date=notice['NOTICEDATE']))
    return results


def get_data_times(end_tag='2015-12-31'):
    end = datetime.datetime.strptime(end_tag, '%Y-%m-%d')
    start = datetime.datetime.strptime('2005-1-1', '%Y-%m-%d')
    delta = datetime.timedelta(days=1)
    tags = [end_tag]
    while True:
        end = end - delta
        if end < start:
            break
        tags.append(end.strftime('%Y-%m-%d'))

    return tags


start_date = '2015-08-15'
point_file = 'date_pointer.txt'
if os.path.exists(point_file):
    with open(point_file) as f:
        lines = list(f.readlines())
    if len(lines) != 0:
        start_date = lines[-1]
        start_date = start_date.strip('\n')
days = get_data_times(end_tag=start_date)
for day in days:
    with open(point_file, 'a') as f:
        f.write('{}\n'.format(day))
    notices = get_notices(day)
    for notice in notices:
        with open('notice.txt', 'a') as f:
            f.write('{}||{}||{}\n'.format(notice['title'], notice['date'], notice['url']))
            print(notice['url'])
