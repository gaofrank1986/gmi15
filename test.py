import lxml.html as LH
import requests
import json
import pandas as pd
def text(elt):
    return elt.text_content().replace(u'\xa0', u' ')

def pline(l):
    ans=[]
    for i in l:
        tmp = 0
        if '/' not in i:
            for j in i.split("+"):
                j = j.replace('%','')
                j = j.replace('s','')
                tmp+=float(j)
            ans.append(tmp)
        else:
            tmp = i.split("/")[0]
            tmp = tmp.replace('%','')
            tmp = tmp.replace(' ','')
            ans.append(float(tmp))
    return(ans)

def save_json(a):

    with open('./test.json', 'w+') as fp:
        json.dump(a, fp,indent = 4)
        # json.dump(a, fp) 
        
url = 'https://genshin.honeyhunterworld.com/db/char/venti/'
r = requests.get(url)
root = LH.fromstring(r.content)
ww ={}
N=1
for table in root.xpath('//div[@class="skilldmgwrapper"]/table[@class="add_stat_table"]'):
    # header = [text(th) for th in table.xpath('//th')]        # 1
    data = [[text(td) for td in tr.xpath('td')]  
            for tr in table.xpath('tr')]                   # 2
    # data = [row for row in data if len(row)==len(header)]    # 3 
    index = [i[0] for i in data[1:]]
    header = data[0][1:]
    data = [i[1:] for i in data[1:]]
    data = pd.DataFrame(data, columns=header) 
    data.index = index# 4
    print(data)
    ww[N] ={}

    for i in range(len(index)):
        ww[N][index[i]] = pline(data.iloc[i,:])
    N+=1    
save_json(ww)
        
    

