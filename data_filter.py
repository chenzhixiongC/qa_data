import json
import pandas as pd
from collections import defaultdict



black_word_list = set()

with open('./敏感词库/反动词库（gbk编码）.txt', 'r',encoding='gbk') as f:
    words = [x.strip() for x in f.readlines()]
    black_word_list |= set(words)
# black_word_file = ['./敏感词库/暴恐词库.txt', './敏感词库/反动词库（gbk编码）.txt', './敏感词库/', './敏感词库/']
with open('./敏感词库/暴恐词库.txt', 'r') as f:
    words = [x.strip() for x in f.readlines()]
    black_word_list |= set(words)
    
with open('./敏感词库/色情词库.txt', 'r') as f:
    words = [x.strip() for x in f.readlines()]
    black_word_list |= set(words)




with open('all_baike1.json', 'r') as f:
    data = json.load(f)
keys = list(data.keys())
new_res = defaultdict()

dirty_res =  defaultdict()

for k in keys:
    qa = data[k]
    category, title, desc, answer = qa['category'], qa['title'], qa['desc'], qa['answer']
    for w in black_word_list:
        if w in title or w in answer:
            dirty_res[k] = qa
            break
    else:
        new_res[k] = qa

print(len(new_res))

filter_res = defaultdict()
new_keys= list(new_res.keys())
for k in new_keys:
    qa = new_res[k]
    category, title, desc, answer = qa['category'], qa['title'], qa['desc'], qa['answer']
    if 1 <= len(title) <= 100 and 1 <= len(answer) <= 250:
        filter_res[k] = qa

print(len(filter_res))

with open('all_baike2.json', 'w') as f:
    json.dump(filter_res, f)