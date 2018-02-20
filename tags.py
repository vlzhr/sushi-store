from json import loads, dumps
import os

link = os.path.join(os.path.dirname(__file__), "tags.txt")

def get_tags(computed = True):
    with open(link, encoding="utf-8") as f:
        return loads(f.read())['items']

def get_all_tags():
    with open(link, encoding="utf-8") as f:
        dic = loads(f.read())['items']
    li = list(dic.items())
    li.sort(key = lambda x: 0-int(x[1]))
    return [n[0] for n in li]

def save_tags(li):
    with open(link, "w", encoding="utf-8") as f:
        f.write(dumps( {"items": li} ))

def add_tag(t, n):
    li = get_tags()
    li[t] = n
    save_tags(li)

def del_tag(t):
    li = get_tags()
    new = {}
    for n in li:
        if n != t:
            new[n] = li[n]
    save_tags(new)

def change_tag(t, b, ne):
    li = get_tags()
    new = {}
    for n in li:
        if n == t:
            new[b] = ne
        else:
            new[n] = li[n]
    save_tags(new)

    
