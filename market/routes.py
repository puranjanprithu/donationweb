from market import app, mail
from flask import render_template , redirect, url_for, flash, request, jsonify, make_response
from market.models import Item , User, PaymentDetail, Category
from market.forms import RegisterForm ,LoginForm, PurchaseItemForm, SellItemForm, DonateMoneyForm ,AddItemForm, TransferMoneyForm
from market import db
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Mail, Message

import os
from werkzeug.utils import secure_filename

def allowed_image(filename):
    if not '.' in filename:
        return False
    ext =filename.rsplit('.',1)[1]
    if ext.upper() in app.config['ALLOWED_IMAGE_EXTENSIONS']:
        return True
    else:
        return False

def allowed_image_filesize(filesize):

    if int(filesize) <= app.config["MAX_IMAGE_FILESIZE"]:
        return True
    else:
        return False

@app.route('/')
def index():
    category= Category.query.all()
    return render_template('home.html',category=category)


@app.route('/market/q',methods=['GET','POST'])
@login_required
def market_page():
    idd=0
    purchase_form= PurchaseItemForm()
    selling_form=SellItemForm()
    donateForm=DonateMoneyForm()

    args=request.args
    if args:
        if "id" in args:
            idd=args.get('id')
            if idd =='0' or int(idd) not in range(1,9):
                items= Item.query.all()
            else:
                items = Item.query.filter_by(category=args.get("id")).all()
    else:
        items= Item.query.all()

    if request.method =='POST':
        # Purchase Item Logic
        if donateForm.submitDMF.data:
            amt=int(donateForm.money.data)

            current_user.budget-=amt
            itemid=request.form["itemid"]
            item=Item.query.filter_by(id=itemid).first()
            item.raised+=amt
            db.session.commit()
            try:
                paydetail=PaymentDetail(
                                        payment_amt=amt,
                                        user_id=current_user.id,
                                        item_id=itemid,
                                        item_name=item.name
                                        )
                db.session.add(paydetail)
                db.session.commit()        
            except:
                flash("some error")             
            flash("Thank you for your kind donation ")


        
        return redirect(url_for('market_page'))
    
    else:
        

        catg=Category.query.all()
        # cat_no=int(cat_no)
        # if cat_no==None or cat_no==0:
        #     items= Item.query.all()
        # else:
        #     items = Item.query.filter_by(category=cat_no).all()

        # items= Item.query.all()
        owned_items= Item.query.filter_by(owner=current_user.id)
        paymentdetail=PaymentDetail.query.filter_by(user_id=current_user.id).order_by(PaymentDetail.id.desc()).limit(5).all()
        return render_template('market.html',items=items, catg=catg, cat_id=idd, donateForm=donateForm, paymentdetail=paymentdetail, purchase_form=purchase_form, owned_items=owned_items, selling_form=selling_form)

@app.route('/new/fundraise',methods=['GET','POST'])
@login_required
def fundraise_page():
    form=AddItemForm()
    if request.method=="POST":
        name= form.name.data
        category=form.category.data
        price= form.price.data
        heading= form.heading.data
        description= form.description.data
        description = "<br>".join(description.split("\n"))

        item= Item(
                    name= name,
                    category=category,
                    price=price,
                    heading=heading,
                    description= description,
                    raised=0,
                    acheived=False,
                    owner=current_user.id,
                )
        db.session.add(item)
        db.session.commit()
        

        flash("New Fundraise created successfully",category="success")
        return redirect(f"/upload-image/donation/{str(item.id)}")
    return render_template("createfundraise.html",form=form)

@app.route('/profile',methods=['GET','POST'])
@login_required
def profile():
    form = TransferMoneyForm()
    if request.method=="POST":
        if form.submitTMF.data:
            itemid=form.itemid.data
            item=Item.query.filter_by(id=itemid).first()
            print(item)
            current_user.budget+=item.raised
            flash(f" {item.raised} added to your wallet successfully !",category="success")
            item.acheived=True
            db.session.commit()
        return redirect(url_for("profile"))
    else:
        return render_template("profile.html" ,form=form)

@app.route('/register',methods=['GET','POST']) 
def register_page():
    form= RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(username=form.username.data,
                                email_address=form.email_address.data,
                                password=form.password1.data)
        db.session.add(user_to_create)
        db.session.commit()
        login_user(user_to_create)
        flash(f"Account created successfully! You are logged in as {user_to_create}", category='success')
        return redirect(url_for('market_page'))
    if form.errors != {}: #if there are no error from validations
        for err_msg in form.errors.values():
            flash(f'There was an error with creating a user : {err_msg}',category='danger')
                                
    return render_template('register.html',form=form)

@app.route('/login',methods=['GET','POST'])
def login_page():
    form=LoginForm()
    if form.validate_on_submit():
        attempted_user=User.query.filter_by(username=form.username.data).first()
        #check if attempted user!= None and check password is == hashed value of password stored
        if attempted_user and attempted_user.check_password_correction( 
                attempted_password=form.password.data
            ):
                login_user(attempted_user)
                flash(f"Success! You are logged in as {attempted_user.username}", category='success')
                return redirect(url_for('market_page'))
        else:
            flash('Username or password not match! Please try again',category='danger')
    return render_template('login.html',form=form)

@app.route('/logout')
def logout_page():
    logout_user()
    flash("You have been Logged Out!", category='info')
    return redirect(url_for('index'))





def uploadImage(image,typee,id=0):
    if image.filename=="":
        flash("Image must have a file name",category="warning")
        return redirect(request.url)

    if not allowed_image(image.filename):
        flash("That image extension not allowed",category="danger")
        return redirect(request.url)
    else:
        filename=secure_filename(image.filename)
        
    if typee == "profile":
        
        image.save(os.path.join(app.config['IMAGE_UPLOADS']+"\\profile", str(id)+".jpg"))
    elif typee == "donation":
        item=Item.query.filter_by(id=id).first()
        image.save(os.path.join(app.config['IMAGE_UPLOADS']+"\\donation", str(id)+".jpg"))
    else:
        return redirect(request.url)
    flash("Image Saved Successfully",category="success")
    return "File uploaded"

@app.route("/upload-image/<typee>/<int:id>",methods=['GET','POST'])
@login_required
def upload_image(typee,id):
    if request.method=="POST":
        if request.files:
            if not allowed_image_filesize(request.cookies.get('filesize')):
                flash("Image exceeded maximum size",category="warning")
                return redirect(request.url)

            image=request.files["image"]

            uploadImage(image,typee,id)

    return render_template("upload_image.html" ,typee=typee, id=id)


@app.route('/support')
def support():
    return render_template('public/support.html')

@app.route('/guestbook/create-entry',methods=["Post"])
def create_entry():
    req=request.get_json()
    print(req)
    # print(mailit())
    res=make_response(jsonify({"data":mailit(req["name"],req["message"])}),200)
    return res


# @app.route("/mail")
def mailit(sub="CrowdFunding",body="Sent by Crowd funding "):
   msg = Message(
                sub,
                sender ='eazyprints180@gmail.com',
                recipients = ['puranjanprithu@gmail.com']
               )
   msg.body = body
   mail.send(msg)
   return 'Feedback Submitted Successfully'

@app.route('/query')
def query():

    
    args=request.args
    if args:
        print(args)
        

        for k,v in args.items():
            print(k,':',v)

        if 'foo' in args:
            foo=args.get('foo')
        if 'title' in args:
            title=args['title']
        print(foo,'---', title)
        print(request.query_string)

    return "query received", 200

# ?foo=foo&bar=barabanki&title=query+strung

@app.route('/test',methods=["GET","Post"])
def test():
    # GET request
    if request.method == 'GET':
        message = {'greeting':'Hello from Flask!'}
        return jsonify(message)  # serialize and use JSON headers
    # POST request
    if request.method == 'POST':
        print(request.get_json())  # parse as JSON
        return 'Sucesss', 200
    return res ,200

data = list(range(1,300,3))
# print (data)
@app.route('/getdata/<index_no>', methods=['GET','POST'])
def data_get(index_no):
    print(index_no)
    if request.method == 'POST': # POST request
        print(index_no)
        print(request.get_text())  # parse as text
        return 'OK', 200
    
    else: # GET request
        return 't_in = %s ; result: %s ;'%(index_no, data[int(index_no)])

