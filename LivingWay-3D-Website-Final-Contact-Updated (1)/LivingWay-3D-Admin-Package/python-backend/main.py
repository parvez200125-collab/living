import os,json,hmac,hashlib,time,uuid,sqlite3
from pathlib import Path
from datetime import datetime,timezone
from fastapi import FastAPI,Request,HTTPException
from fastapi.responses import JSONResponse,FileResponse
ROOT=Path(__file__).resolve().parent
DB=Path(os.getenv('DATABASE_PATH',str(ROOT/'livingway.db')))
RES={'requests':'New','customers':'Active','projects':'Planning','invoices':'Pending','messages':'Unread','project_files':'Available','approvals':'Pending','notifications':'Unread','activity_log':'Logged'}
SECRET=os.getenv('SESSION_SECRET',''); app=FastAPI(title='LivingWay 3D API')
def db():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row
 for t in RES:c.execute(f'CREATE TABLE IF NOT EXISTS {t}(id TEXT PRIMARY KEY,data TEXT,status TEXT,created_at TEXT,updated_at TEXT)')
 c.commit();return c
def now():return datetime.now(timezone.utc).isoformat()
def ident(p='LW'):return p+'-'+uuid.uuid4().hex[:8].upper()
def session(req):
 try:
  p,s=req.cookies['lw_admin'].rsplit('.',1); assert hmac.compare_digest(s,hmac.new(SECRET.encode(),p.encode(),hashlib.sha256).hexdigest()); d=json.loads(bytes.fromhex(p));return d if d['exp']>time.time() else None
 except:return None
def auth(req):
 s=session(req)
 if not s:raise HTTPException(401,'Unauthorized')
 return s
@app.get('/api/health')
def health():return {'ok':True,'service':'LivingWay Python API'}
@app.post('/api/admin/login')
async def login(req:Request):
 b=await req.json();e=str(b.get('email','')).strip().lower();pw=str(b.get('password',''))
 if not SECRET or not any(e==os.getenv(f'ADMIN{i}_EMAIL','').lower() and hmac.compare_digest(pw,os.getenv(f'ADMIN{i}_PASSWORD','')) for i in (1,2)):raise HTTPException(401,'Invalid credentials or server setup incomplete.')
 p=json.dumps({'email':e,'exp':time.time()+28800},separators=(',',':')).encode().hex();sig=hmac.new(SECRET.encode(),p.encode(),hashlib.sha256).hexdigest();r=JSONResponse({'ok':True,'email':e});r.set_cookie('lw_admin',p+'.'+sig,httponly=True,secure=os.getenv('COOKIE_SECURE','true').lower()=='true',samesite='strict',max_age=28800);return r
@app.post('/api/admin/logout')
def logout():
 r=JSONResponse({'ok':True});r.delete_cookie('lw_admin');return r
@app.get('/api/admin/me')
def me(req:Request):return {'email':auth(req)['email']}
@app.get('/api/admin/overview')
def overview(req:Request):
 auth(req);c=db();o={t:c.execute(f'SELECT count(*) n FROM {t}').fetchone()['n'] for t in RES};o['paidInvoices']=c.execute("select count(*) n from invoices where lower(status)='paid'").fetchone()['n'];o['pendingInvoices']=c.execute("select count(*) n from invoices where lower(status)='pending'").fetchone()['n'];o['revenue']=sum(float((json.loads(x[0]).get('amount') or json.loads(x[0]).get('total') or 0)) for x in c.execute("select data from invoices where lower(status)='paid'").fetchall());c.close();return o
@app.api_route('/api/admin/{resource}',methods=['GET','POST'])
async def collection(resource:str,req:Request):
 s=auth(req)
 if resource not in RES:raise HTTPException(404,'Unknown resource')
 c=db()
 if req.method=='GET':
  rows=c.execute(f'select * from {resource} order by created_at desc limit 500').fetchall();c.close();return [{**json.loads(x['data']),'id':x['id'],'status':x['status'],'created_at':x['created_at'],'updated_at':x['updated_at'],'data':json.loads(x['data'])} for x in rows]
 b=await req.json();rid=str(b.pop('id',ident(resource[:3].upper())));st=str(b.get('status',RES[resource]));t=now();c.execute(f'insert into {resource} values(?,?,?,?,?)',(rid,json.dumps(b),st,t,t));c.commit();c.close();return JSONResponse({'ok':True,'id':rid},201)
@app.api_route('/api/admin/{resource}/{rid}',methods=['GET','PATCH','DELETE'])
async def record(resource:str,rid:str,req:Request):
 auth(req)
 if resource not in RES:raise HTTPException(404,'Unknown resource')
 c=db();x=c.execute(f'select * from {resource} where id=?',(rid,)).fetchone()
 if not x:c.close();raise HTTPException(404,'Not found')
 if req.method=='DELETE':c.execute(f'delete from {resource} where id=?',(rid,));c.commit();c.close();return {'ok':True}
 d=json.loads(x['data'])
 if req.method=='PATCH':
  b=await req.json();d.update(b);c.execute(f'update {resource} set data=?,status=?,updated_at=? where id=?',(json.dumps(d),b.get('status',x['status']),now(),rid));c.commit()
 c.close();return {**d,'id':rid,'status':x['status'],'data':d}
@app.post('/api/request')
async def request_form(req:Request):
 b=await req.json()
 if b.get('_honey'):return {'ok':True}
 name=str(b.get('Full Name','')).strip();email=str(b.get('Email','')).strip();phone=str(b.get('Phone Number','')).strip()
 if not name or not phone or '@' not in email:raise HTTPException(400,'Please provide a name, valid email and phone number.')
 d={**b,'name':name,'customer':name,'email':email,'phone':phone};d.pop('_honey',None);c=db();t=now();rid=ident();c.execute('insert into requests values(?,?,?,?,?)',(rid,json.dumps(d),'New',t,t));c.execute('insert into notifications values(?,?,?,?,?)',(ident('NT'),json.dumps({'title':'New customer request','message':name,'requestId':rid}),'Unread',t,t));c.commit();c.close();return JSONResponse({'ok':True,'id':rid,'message':'Your design request has been received.'},201)
@app.get('/{path:path}')
def static(path:str):
 p=(ROOT.parent/'public'/path).resolve();pub=(ROOT.parent/'public').resolve()
 if pub not in p.parents and p!=pub:raise HTTPException(404)
 if p.is_file():return FileResponse(p)
 if not path or path.endswith('/'):p=pub/(path+'index.html')
 if p.is_file():return FileResponse(p)
 return FileResponse(pub/'index.html')
