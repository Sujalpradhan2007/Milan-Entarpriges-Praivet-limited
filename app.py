import os, json, secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

BASE=os.path.dirname(os.path.abspath(__file__))
UPLOAD=os.path.join(BASE,'static','uploads')
os.makedirs(UPLOAD,exist_ok=True)
app=Flask(__name__)
app.config['SECRET_KEY']=os.environ.get('SECRET_KEY') or secrets.token_hex(32)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(BASE,'enterprise.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['MAX_CONTENT_LENGTH']=100*1024*1024
db=SQLAlchemy(app)

class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True); username=db.Column(db.String(80),unique=True,nullable=False); password=db.Column(db.String(255),nullable=False)
class Machine(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150),nullable=False); model=db.Column(db.String(100)); category=db.Column(db.String(100)); price=db.Column(db.String(80)); offer=db.Column(db.String(255)); colors=db.Column(db.String(255)); raw_material=db.Column(db.String(255)); description=db.Column(db.Text); specs=db.Column(db.Text); performance=db.Column(db.Text); image=db.Column(db.String(255)); video=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class RawMaterial(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(150),nullable=False); grade=db.Column(db.String(100)); description=db.Column(db.Text); image=db.Column(db.String(255)); active=db.Column(db.Boolean,default=True)
class FAQ(db.Model):
    id=db.Column(db.Integer,primary_key=True); question=db.Column(db.String(255),nullable=False); answer=db.Column(db.Text,nullable=False); active=db.Column(db.Boolean,default=True)
class Banner(db.Model):
    id=db.Column(db.Integer,primary_key=True); title=db.Column(db.String(150)); subtitle=db.Column(db.String(255)); image=db.Column(db.String(255)); theme=db.Column(db.String(80),default='festival'); active=db.Column(db.Boolean,default=True)
class Inquiry(db.Model):
    id=db.Column(db.Integer,primary_key=True); name=db.Column(db.String(120)); phone=db.Column(db.String(40)); email=db.Column(db.String(150)); subject=db.Column(db.String(255)); message=db.Column(db.Text); machine=db.Column(db.String(150)); created_at=db.Column(db.DateTime,default=datetime.utcnow)
class SiteSettings(db.Model):
    id=db.Column(db.Integer,primary_key=True); company_name=db.Column(db.String(150),default='MILAN ENTERPRISES PVT. LTD.'); background_image=db.Column(db.String(255)); hero_image=db.Column(db.String(255)); whatsapp_number=db.Column(db.String(40),default='7978266937')

def save_file(f):
    if not f or not f.filename:return None
    name=datetime.utcnow().strftime('%Y%m%d%H%M%S%f')+'_'+secure_filename(f.filename)
    f.save(os.path.join(UPLOAD,name)); return name

def login_required(): return session.get('admin') is not None

def seed():
    db.create_all()
    # Add new settings columns for existing installations without deleting data.
    existing={row[1] for row in db.session.execute(db.text('PRAGMA table_info(site_settings)')).fetchall()}
    for column, definition in [('hero_image','VARCHAR(255)'),('whatsapp_number','VARCHAR(40)')]:
        if column not in existing: db.session.execute(db.text(f'ALTER TABLE site_settings ADD COLUMN {column} {definition}'))
    db.session.commit()
    if not Admin.query.first():
        admin_username=os.environ.get('ADMIN_USERNAME')
        admin_password=os.environ.get('ADMIN_PASSWORD')
        if admin_username and admin_password:
            db.session.add(Admin(username=admin_username,password=generate_password_hash(admin_password)))
    if Machine.query.count()==0:
        data=[('Precision Cutting Machine','PCM-100','Cutting','₹ Contact','Special Offer','Blue, Grey','MS / SS','Industrial precision cutting solution','Power: 15 kW; Capacity: 1000 mm','Speed: 95|Accuracy: 92|Efficiency: 90'),('Hydraulic Press Machine','HPM-250','Press','₹ Contact','Festival Offer','Blue, White','MS / SS','High-force hydraulic press','Force: 250 Ton; Stroke: 300 mm','Speed: 82|Accuracy: 96|Efficiency: 94'),('CNC Laser Machine','CLM-3015','Laser','₹ Contact','Ask for Quote','Black, Grey','MS / SS / Aluminium','CNC laser cutting platform','Power: 6 kW; Bed: 3000x1500 mm','Speed: 97|Accuracy: 98|Efficiency: 93'),('Automatic Packaging Machine','APM-500','Packaging','₹ Contact','Bundle Offer','Silver, Blue','Plastic / Film','Automated high-speed packaging','Output: 50 packs/min','Speed: 91|Accuracy: 94|Efficiency: 96')]
        for d in data: db.session.add(Machine(name=d[0],model=d[1],category=d[2],price=d[3],offer=d[4],colors=d[5],raw_material=d[6],description=d[7],specs=d[8],performance=d[9]))
    if FAQ.query.count()==0:
        for q,a in [('How can I request a quotation?','Open any machine and use the WhatsApp inquiry or contact form.'),('Can I compare machines?','Yes. Select machines from the Compare section to review performance metrics side by side.'),('Can machine details be updated?','Yes. Admins can edit photos, videos, prices, offers, colors, specifications and performance data.')]: db.session.add(FAQ(question=q,answer=a))
    if Banner.query.count()==0: db.session.add(Banner(title='Festival & Special Offers',subtitle='Discover limited-time machine offers and business solutions.',theme='festival'))
    if not SiteSettings.query.first(): db.session.add(SiteSettings(company_name='MILAN ENTERPRISES PVT. LTD.',whatsapp_number='7978266937'))
    db.session.commit()

@app.context_processor
def inject():
    s=SiteSettings.query.first() or SiteSettings(company_name='MILAN ENTERPRISES PVT. LTD.',whatsapp_number='7978266937')
    return {'wa':s.whatsapp_number or '7978266937','year':datetime.now().year,'settings':s}

@app.route('/')
def home(): return render_template('index.html',machines=Machine.query.filter_by(active=True).all(),banners=Banner.query.filter_by(active=True).all(),faqs=FAQ.query.filter_by(active=True).all())
@app.route('/machines')
def machines():
    q=request.args.get('q',''); cat=request.args.get('category','')
    query=Machine.query.filter_by(active=True)
    if q: query=query.filter((Machine.name.ilike('%'+q+'%'))|(Machine.model.ilike('%'+q+'%')))
    if cat: query=query.filter_by(category=cat)
    cats=[x[0] for x in db.session.query(Machine.category).filter(Machine.category.isnot(None)).distinct().all()]
    return render_template('machines.html',machines=query.order_by(Machine.id.desc()).all(),categories=cats,q=q,cat=cat)
@app.route('/machine/<int:id>')
def machine(id): return render_template('machine.html',m=Machine.query.get_or_404(id))
@app.route('/compare')
def compare(): return render_template('compare.html',machines=Machine.query.filter_by(active=True).all())
@app.route('/api/machines')
def api_machines():
    return jsonify([{'id':m.id,'name':m.name,'model':m.model,'price':m.price,'offer':m.offer,'performance':dict(x.split(':',1) for x in m.performance.split('|') if ':' in x)} for m in Machine.query.filter_by(active=True).all()])
@app.route('/inquiry',methods=['POST'])
def inquiry():
    i=Inquiry(name=request.form.get('name'),phone=request.form.get('phone'),email=request.form.get('email'),subject=request.form.get('subject'),message=request.form.get('message'),machine=request.form.get('machine')); db.session.add(i); db.session.commit(); flash('Your inquiry has been submitted. Our team will contact you.','success'); return redirect(request.referrer or url_for('home'))
@app.route('/admin/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        a=Admin.query.filter_by(username=request.form.get('username')).first()
        if a and check_password_hash(a.password,request.form.get('password')): session['admin']=a.username; return redirect(url_for('dashboard'))
        flash('Invalid login details.','danger')
    return render_template('login.html')
@app.route('/admin/logout')
def logout(): session.clear(); return redirect(url_for('login'))
@app.route('/admin')
def dashboard():
    if not login_required(): return redirect(url_for('login'))
    return render_template('admin.html',machines=Machine.query.order_by(Machine.id.desc()).all(),materials=RawMaterial.query.all(),faqs=FAQ.query.all(),banners=Banner.query.all(),inquiries=Inquiry.query.order_by(Inquiry.created_at.desc()).all())
@app.route('/admin/machine/save',methods=['POST'])
def save_machine():
    if not login_required(): return redirect(url_for('login'))
    mid=request.form.get('id'); m=Machine.query.get(mid) if mid else Machine()
    for f in ['name','model','category','price','offer','colors','raw_material','description','specs','performance']: setattr(m,f,request.form.get(f,''))
    m.active=request.form.get('active')=='on'
    im=save_file(request.files.get('image')); vid=save_file(request.files.get('video'))
    if im:m.image=im
    if vid:m.video=vid
    db.session.add(m); db.session.commit(); flash('Machine saved successfully.','success'); return redirect(url_for('dashboard'))
@app.route('/admin/machine/delete/<int:id>')
def delete_machine(id):
    if login_required(): db.session.delete(Machine.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('dashboard'))
@app.route('/admin/material/save',methods=['POST'])
def save_material():
    if not login_required(): return redirect(url_for('login'))
    x=RawMaterial.query.get(request.form.get('id')) if request.form.get('id') else RawMaterial(); x.name=request.form.get('name'); x.grade=request.form.get('grade'); x.description=request.form.get('description'); x.active=True; im=save_file(request.files.get('image')); x.image=im or x.image; db.session.add(x); db.session.commit(); return redirect(url_for('dashboard'))
@app.route('/admin/material/delete/<int:id>')
def delete_material(id):
    if login_required(): db.session.delete(RawMaterial.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('dashboard'))
@app.route('/admin/faq/save',methods=['POST'])
def save_faq():
    if not login_required(): return redirect(url_for('login'))
    x=FAQ.query.get(request.form.get('id')) if request.form.get('id') else FAQ(); x.question=request.form.get('question'); x.answer=request.form.get('answer'); x.active=True; db.session.add(x); db.session.commit(); return redirect(url_for('dashboard'))
@app.route('/admin/faq/delete/<int:id>')
def delete_faq(id):
    if login_required(): db.session.delete(FAQ.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('dashboard'))
@app.route('/admin/banner/save',methods=['POST'])
def save_banner():
    if not login_required(): return redirect(url_for('login'))
    x=Banner.query.get(request.form.get('id')) if request.form.get('id') else Banner(); x.title=request.form.get('title'); x.subtitle=request.form.get('subtitle'); x.theme=request.form.get('theme','festival'); x.active=True; im=save_file(request.files.get('image')); x.image=im or x.image; db.session.add(x); db.session.commit(); return redirect(url_for('dashboard'))
@app.route('/admin/banner/delete/<int:id>')
def delete_banner(id):
    if login_required(): db.session.delete(Banner.query.get_or_404(id)); db.session.commit()
    return redirect(url_for('dashboard'))
@app.route('/admin/settings/save',methods=['POST'])
def save_settings():
    if not login_required(): return redirect(url_for('login'))
    x=SiteSettings.query.first() or SiteSettings(); x.company_name=request.form.get('company_name','MILAN ENTERPRISES PVT. LTD.').strip() or 'MILAN ENTERPRISES PVT. LTD.'; x.whatsapp_number=''.join(ch for ch in request.form.get('whatsapp_number','7978266937') if ch.isdigit()) or '7978266937'
    im=save_file(request.files.get('background_image')); hero=save_file(request.files.get('hero_image'))
    if im: x.background_image=im
    if hero: x.hero_image=hero
    db.session.add(x); db.session.commit(); flash('Company settings saved successfully.','success'); return redirect(url_for('dashboard'))

with app.app_context(): seed()
if __name__=='__main__': app.run(debug=os.environ.get('FLASK_DEBUG')=='1',host='0.0.0.0',port=int(os.environ.get('PORT',5000)))
