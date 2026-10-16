#!/usr/bin/env python3
"""Regenerate index.html from products.json + posted.csv (no network needed).
Usage: python3 build.py [--posted /workspace/instagram_posted.csv] [--days 7]"""
import json,csv,re,sys,html,datetime as dt,os,shutil
here=os.path.dirname(os.path.abspath(__file__))
args=sys.argv[1:]
posted_path=args[args.index('--posted')+1] if '--posted' in args else '/workspace/instagram_posted.csv'
days=int(args[args.index('--days')+1]) if '--days' in args else 7
if os.path.exists(posted_path): shutil.copy(posted_path,os.path.join(here,'posted.csv'))
posted_path=os.path.join(here,'posted.csv')
prods=json.load(open(os.path.join(here,'products.json')))
CATS=[ # (name, emoji, keywords) matched against the product-name part of the title, first match wins
('Home Security & Garden','🌿',['mosquito','bird feeder','bug zapper','irrigation','planter','flower pot','garden','solar','door bottom','sealing strip','self-watering']),
('Drinkware & Lunch','🥤',['water bottle','bottle set','lunch box','mug','sipper','tumbler','kettle','square water bottles','water bottles']),
('Baking, Moulds & Treats','🍫',['mould','mold','donut','ice ball','ice cube','ice cream','coaster','flower plates','tableware','maker mould']),
('Personal Care & Baby','💆',['shaver','razor','hair brush','scalp','ice roller','perfume','bath bomb','teeth','teether','body brush','soap dispenser','toothbrush','crystal soap','grape shaped']),
('Lights & Gadgets','💡',['led','flashlight','keychain']),
('Cleaning & Laundry','🧼',['clean','laundry','washer','duster','scrubber','slime','detergent','washing machine','liquid adding','wax drag','gloves','mop']),
('Food Storage & Containers','🥣',['food storage','storage container','airtight','canister','egg tray','egg storage','egg box','pickle','masala','casserole','serving bowl','fridge storage','storage containers','jar','clear food']),
('Kitchen Tools & Gadgets','🔪',['chopper','slicer','grater','juicer','squeezer','garlic','peeler','pineapple','egg cutter','samosa','scoop','chopping','scraper','salt & pepper','oil ','oil bottle','oil dispenser','meatball','fish','faucet','bottle cleaning','shakers','cutlery','cord organizer','cabinet mat']),
('Home Organisers & Storage','🧺',['organizer','organiser','rack','cart','storage box','storage bin','bins','basket','hanger','shelf','drawer','holder','crate','towel','rolling storage','wall organizer','storage holder','storage rack','dustbin']),
]
def cat(t):
    l=re.split(r'\s[|–—]\s|\s-\s',t)[0].lower()
    for n,e,ks in CATS:
        if any(k in l for k in ks): return n
    return 'More from Arto & ApLiQ'
FEATS=[('airtight','Airtight to keep food fresh'),('leak','Leak-proof design'),('bpa','BPA-free, food-grade'),('stackable','Stackable, saves space'),('collapsible','Folds flat when not in use'),('foldable','Foldable and space-saving'),
('non-slip','Non-slip grip'),('non slip','Non-slip grip'),('non-stick','Non-stick, easy release'),('unbreakable','Tough and unbreakable'),('dishwasher','Dishwasher-safe'),('rechargeable','Rechargeable, ready anywhere'),('self adhesive','Self-adhesive, no drilling'),('self-adhesive','Self-adhesive, no drilling'),
('wall mounted','Wall-mounted space saver'),('wall hanging','Wall-mounted space saver'),('rotating','Smooth 360° rotation'),('insulated','Keeps drinks hot or cold'),('stainless steel','Durable stainless steel'),('silicone','Soft, food-grade silicone'),('transparent','See-through, easy to find things'),('waterproof','Waterproof'),('heavy duty','Heavy-duty build'),('portable','Portable and easy to carry'),('mosquito','Keeps mosquitoes out'),('rolling','Rolls easily where you need it')]
DEFAULT={'Home Security & Garden':'Practical help for balcony, garden and doors.','Drinkware & Lunch':'Made for school, office and travel.','Baking, Moulds & Treats':'Easy, mess-free treats at home.','Kitchen Tools & Gadgets':'Quicker prep for everyday cooking.','Food Storage & Containers':'Keeps your kitchen tidy and food fresh.','Home Organisers & Storage':'Neat, organised space in minutes.','Cleaning & Laundry':'Makes household chores easier.','Personal Care & Baby':'Everyday comfort and care.','Lights & Gadgets':'Handy light wherever you need it.'}
def short(t):
    t=re.split(r'\s[|–—]\s|\s-\s|\(',t)[0].strip()
    t=re.sub(r'\s+',' ',t)
    t=re.sub(r'^(arto|apliq)\s+','',t,flags=re.I)
    return (t[:60].rsplit(' ',1)[0]+'…') if len(t)>62 else t
def brand(t):
    l=t.lower()
    return 'ApLiQ' if l.startswith('apliq') else ('Arto' if l.startswith('arto') else 'Veeha')
def benefit(t,c):
    l=t.lower();out=[]
    for k,v in FEATS:
        if k in l and v not in out: out.append(v)
        if len(out)==2: break
    return ' · '.join(out) if out else DEFAULT.get(c,'Quality everyday home essentials.')
posted={}
if os.path.exists(posted_path):
    for r in csv.DictReader(open(posted_path)): posted[r['asin']]=r['date_posted']
today=dt.date.today()
out=[]
for p in prods:
    c=cat(p['title'])
    out.append({'a':p['asin'],'t':short(p['title']),'b':brand(p['title']),'c':c,'l':benefit(p['title'],c),'i':p['image'],'n':p['units_30d'],'p':posted.get(p['asin'])})
new=[x for x in out if x['p'] and (today-dt.date.fromisoformat(x['p'])).days<=days]
new.sort(key=lambda x:x['p'],reverse=True)
for x in out: x['new']=x in new
order={n:i for i,(n,_,_) in enumerate(CATS)}
catinfo=[{'n':n,'e':e} for n,e,_ in CATS]+[{'n':'More from Arto & ApLiQ','e':'✨'}]
out.sort(key=lambda x:(order.get(x['c'],99),-x['n'],x['t']))
data=json.dumps({'products':out,'cats':catinfo,'new':[x['a'] for x in new],'built':today.isoformat()},ensure_ascii=False,separators=(',',':'))
tpl=open(os.path.join(here,'template.html'),encoding='utf8').read()
open(os.path.join(here,'index.html'),'w',encoding='utf8').write(tpl.replace('/*DATA*/null',data))
print('built',len(out),'products;',len(new),'new this week')

# Optional: single-file version with images inlined (for hosts that only take one file)
if '--inline' in args:
    import base64,io
    from PIL import Image
    h=open(os.path.join(here,'index.html'),encoding='utf8').read()
    def enc(m):
        p=os.path.join(here,m.group(1))
        im=Image.open(p).convert('RGB');im.thumbnail((320,320))
        b=io.BytesIO();im.save(b,'WEBP',quality=72)
        return '"data:image/webp;base64,'+base64.b64encode(b.getvalue()).decode()+'"'
    h=re.sub(r'"(images/[A-Z0-9]+\.jpg)"',enc,h)
    os.makedirs(os.path.join(here,'dist'),exist_ok=True)
    open(os.path.join(here,'dist','index.html'),'w',encoding='utf8').write(h)
    print('inline size',len(h)//1024,'KB')
