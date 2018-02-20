from flask import Flask, render_template, url_for, request, redirect, session, Markup
from json import loads, dumps
import os
from tags import add_tag, change_tag, del_tag, get_all_tags, get_tags as get_dic_tags
from slider import get_slider_images, del_slider_image
from mails import send_mail

app = Flask(__name__)
app.debug = True
app.secret_key = "asdafasdghghaasdaaaasgfhafaasdjfafsdffgsjgshsfg"

images_path = os.path.join(os.path.dirname(__file__), "static", "images", "")
titlestore = os.path.join(os.path.dirname(__file__), "static", "images", 'info.txt')
basa = os.path.join(os.path.dirname(__file__), "basa.txt")

def add_sale(a, s):
    dic = s.get('korsina', {})
    li = []
    for n in dic:
        d = {"count": dic[n]}
        d.update(get_roll(n))
        li.append(d)
    bought = "\n".join(["{} - {}x".format(n, dic[n]) for n in dic])
    summ = str( sum([(int(roll['price']) * roll['count']) for roll in li]) )
    s = """
{name} разместил новый заказ по адресу {street}, {house}/{k} {flat}
Comment: {com}

Связ' по телефону: {tel}

    """.format(**a) + """
Заказ:
{}
    
Сумма заказа: {}rub
Способ оплаты: {}
    """.format(bought, summ, a['pay'])
    send_mail(s)

def get_info():
    try:
        with open(titlestore, 'r', encoding='utf-8') as f:
            return loads(f.read())
    except Exception:
        return {"min_price": 600, "phone": "89128761245", "address": "moscow"}

def renew_info(ra):
    dic = {"min_price": 600, "phone": "89128761245", "address": "moscow"}
    for n in ra:
        dic[n] = ra[n]
    with open(titlestore, 'w', encoding='utf-8') as f:
        f.write(dumps(dic))

def get_rolls():
    with open(basa, "r", encoding="utf-8") as f:
        s = f.read()
    dic = loads(s)
    return dic["rolls"]

def get_roll(full_name):
    name, tag = full_name.rsplit(":", 1)
    rolls = get_rolls()
    for roll in rolls:
        if roll['name'].strip().lower() == name.strip().lower():
            if roll['tags'][0].lower().strip() == tag.strip().lower():
                return roll
    return {"price": 0, "image": "", "name": name}

def renew_rolls(li):
    dic = {"rolls": li}
    with open(basa, "w", encoding="utf-8") as f:
        f.write(dumps(dic))

def get_tags():
    rolls = get_rolls()
    tags = []
    for n in rolls:
        tags += n.get("tags", [])
    return list(set(tags))

#def get_slider_images():
#    s = '"https://cdn.pizzasushiwok.ru/slider/gril.jpg","https://cdn.pizzasushiwok.ru/slider/priziv.jpg"'
#    return Markup(s)

@app.route("/")
def index():
    kors = session.get("korsina", {})
    rolls = get_rolls()
    dic = {}
    for roll in rolls:
        if 'tags' in roll:
            for tag in roll['tags']:
                dic[tag] = dic.get(tag, []) + [roll]
        else:
            dic['специальные'] = dic.get("специальные", []) + [roll]
    try:
        kors_value = sum([kors[n] * int(get_roll(n)['price']) for n in kors])
    except TypeError:
        session.clear()
        kors_value = 0
    for tag in dic:
        dic[tag].sort(key = lambda x: int(x.get('price', 0)))
    slider_images = Markup(",".join(['"'+url_for("static", filename="images/slider/"+n)+'"' for n in get_slider_images()]))
    return render_template("index.html", tag="все", url_for=url_for,
                           dic=dic, # structured rolls 
                           kors = kors, tags=get_all_tags(),
                           cart_value = kors_value, slider_images=slider_images,
                           data=get_info())

##@app.route("/filtered/<tag>")
##def filtered(tag):
##    if tag == "все":
##        return redirect("/")
##    rolls = get_rolls()
##    rolls = [ n for n in rolls if tag.lower() in [word.lower() for word in n.get("tags", [])] ]
##    return render_template("index.html", li=rolls, tag=tag, url_for=url_for,
##                           kors = session.get("korsina", {}), tags=get_tags(), h1=get_title())

@app.route("/del_slide")
def del_slide():
    del_slider_image(request.args['name'])
    return redirect("/adminka")

@app.route("/add_zakaz")
def add_zakaz():
    add_sale(request.args, session)
    return render_template("sale-success.html", url_for=url_for)

@app.route("/add_tag")
def addtag():
    add_tag(request.args['tag'], request.args['n'])
    return redirect("/adminka")

@app.route("/change_tag")
def changetag():
    change_tag(request.args['tag'], request.args['new_tag'], request.args['n'])
    return redirect("/adminka")

@app.route("/del_tag")
def deltag():
    del_tag(request.args['name'])
    return redirect("/adminka")

@app.route("/korsina")
def korsina():
    dic = session.get('korsina', {})
    li = []
    for n in dic:
        d = {"count": dic[n]}
        d.update(get_roll(n))
        li.append(d)
    return render_template("index1.html", url_for = url_for,
                           tags=[], data=get_info(), rolls=li, int=int, sum=sum([(int(roll['price']) * roll['count']) for roll in li]))


@app.route("/zakas")
def zakas():
    return render_template("index2.html", data=get_info())


@app.route("/adminka")
def adminka():
    if "admin" in session and session['admin'] == True:
        return render_template("adminka.html", rolls=get_rolls(), data=get_info(), tags=get_dic_tags(), slides=get_slider_images())
    else:
        return render_template("login.html")
        return '<form action="admin_log"><input name="key" type="password" placeholder="Ключ доступа"></form>'

@app.route("/add_slide", methods=["POST"])
def add_slide():
    img = request.files['img']
    img_name = img.filename
    img_link = images_path + "slider/" + img_name
    img.save(img_link)
    return redirect("/adminka")

@app.route("/admin_log")
def admin_log():
    if request.args['key'] == "SUSHIandLOVE2017":
        session['admin'] = True
    return redirect("/adminka")

@app.route("/logout")
def logout():
    session['admin'] = False
    return redirect("/")

@app.route("/change")
def change_title():
    renew_info(request.args)
    return redirect('/')

@app.route('/new_roll')
def new_roll():
    args = request.args
    p = 1
    for i in args.keys():
        if not i == "tags":
            p *= len(args[i])
    if not p:
        return redirect('/adminka')
    session['roll'] = {'name': args['name'], 'price': int(args['price']), 'desc': args['desc'], 'img': '',
                       'tags': [n.strip() for n in args['tags'].split(",")]}
    return render_template('new_roll.html', name = args['name'], price = args['price'], desc = args['desc'],
                               tags = ", ".join(session['roll']['tags']))
        

@app.route("/load_image", methods=["POST"])
def load_image():
    img = request.files['img']
    name = session['roll']['name']
    img_name = name + img.filename
    img_link = images_path + img_name
    img.save(img_link)
    rolls = get_rolls()
    session['roll']['image'] = img_name
    rolls.append(session['roll'])
    renew_rolls(rolls)
    del session['roll']
    return redirect("/adminka")

@app.route("/del_roll")
def del_roll():
    old = get_rolls()
    new = []
    for roll in old:
        if not roll['name'].lower().strip() == request.args['name'].lower().strip():
            new.append(roll)
    renew_rolls(new)
    return redirect("/adminka")

@app.route("/change_roll")
def change_roll():
    old = get_rolls()
    new = []
    for roll in old:
        if roll['name'].lower().strip() == request.args['old_name'].lower().strip():
            roll['name'] = request.args['name']
            roll['price'] = request.args['price']
            roll['tags'] = [tag.strip() for tag in request.args['tags'].split(",")]
            roll['desc'] = request.args['desc']
        new.append(roll)
    renew_rolls(new)
    return redirect("/adminka")


@app.route("/add_tovar")
def add_tovar():
    session.modified = True
    if not 'korsina' in session:
        session['korsina'] = {}
    name = request.args['name']+" : "+request.args['tag']
    session['korsina'][name] = session['korsina'].get(name, 0) + 1
    return redirect("/korsina")

@app.route("/minus_tovar")
def minus_tovar():
    session.modified = True
    if not 'korsina' in session:
        session['korsina'] = {}
    name = request.args['name']+" : "+request.args['tag']
    session['korsina'][name] = session['korsina'].get(name, 0) - 1
    if session['korsina'][name] <= 0:
        del session['korsina'][name]
    return redirect("/korsina")

@app.route("/zero_tovar")
def zero_tovar():
    session.modified = True
    if not 'korsina' in session:
        session['korsina'] = {}
    name = request.args['name']+" : "+request.args['tag']
    del session['korsina'][name]
    return redirect("/korsina")    

if __name__ == "__main__":
    app.run(port=80)
    #print(get_roll("Бирролл фирменный"))

