from datetime import datetime, date
import urllib.request
import re
import pytz
from lxml import etree


def parse_student(url, name):
    now_day = datetime.today().now(pytz.timezone('Europe/Samara')).weekday()
    if now_day == 6:
        d1 = date(2020, 1, 4)
        d2 = date.today()
        result = (d2 - d1).days // 7
        site = f'{url}&wk={result + 1}'
    else:
        site = url
    hdr = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'none',
        'Accept-Language': 'en-US,en;q=0.8',
        'Connection': 'keep-alive'}
    try:
        request = urllib.request.Request(site, headers=hdr)
        web = urllib.request.urlopen(request, timeout=5)
        s = web.read()
    except Exception:
        return 0
    html = etree.HTML(s)

    tr_nodes = html.xpath('//table[@bgcolor="3481A6"]/tr')
    td_content = [[td.text for td in tr.xpath('td')] for tr in tr_nodes[1:]]
    h3_content = [[h3.text for h3 in tr.xpath('td//h3')] for tr in tr_nodes[1:]]
    a_content = [[a.text for a in tr.xpath('td//a')] for tr in tr_nodes[1:]]
    swap_content = [html.xpath('//td//text()')]

    step_swap = 0
    swap = []
    cabinet = []
    for x in swap_content[0]:
        if x == " на:":
            swap.append(swap_content[0][step_swap + 1])
        if re.match(r'Кабинет', x) is not None:
            cabinet.append(x)
        step_swap += 1

    weekday = []
    for x in h3_content:
        if not x or x == ['предыдущая неделя', 'следующая неделя']:
            continue
        weekday.append(x[0])

    cut = []
    for x in a_content:
        if x in ([], [None], [None, None, None, None]):
            continue
        if x[0][0] in ("1", '0'):
            cut.append(x[0])

    all_content = []
    step_day = 0
    step_cut = 0
    step_swap = 0
    step_cabinet = 0
    for x in td_content:
        if x == [None] or x == ['\xa0\xa0\xa0']:
            continue
        if x == [None, None, None, None, None, None, None]:
            x = weekday[step_day]
            step_day += 1
        try:
            if x[1] is None:
                x[1] = cut[step_cut]
                step_cut += 1
            if x[3] is None:
                x[3] = swap[step_swap]
                step_swap += 1
            if x[2] in ("Очно", None) and x[3] != "Свободное время":
                x[4] = cabinet[step_cabinet] + 'ентерпослекабинета'
                step_cabinet += 1
        except:
            pass
        all_content.append(x)
    for x in range(len(all_content)):
        try:
            if all_content[x][1].find('1') != -1 and all_content[x][1].find('0') != -1:
                all_content[x][0] = ''
                all_content[x][1] = '🕒 ' + all_content[x][1] + 'ентерпередзначкомпрепода🎓'
        except:
            pass
    with open(f'table/{name}.txt', 'w', encoding='utf-8') as file:
        for x in all_content:
            print(x, sep='\n', file=file)
