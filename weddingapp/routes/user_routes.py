
import random,os,requests
from flask import Flask, render_template, make_response, render_template_string, request, redirect, flash,session,jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import values
from weddingapp import app, db
from weddingapp.models import *
from weddingapp.forms import ContactForm, SignupForm
from weddingapp.routes import user_routes

@app.route('/')
def home():
    return render_template('user/index.html')

@app.route('/login/', methods = ["POST", "GET"])
def login():
    if request.method == "GET":
        return render_template('user/login.html')

    else:
        email = request.form["email"]
        password = request.form["pswd1"]

        #retrieve the hashed password belonging to this user.
        userdeets = Guests.query.filter(Guests.guest_email == email).first()
        if userdeets and check_password_hash(userdeets.guest_pwd, password):
            session["guest"] = userdeets.guest_id
            return redirect("/profile")
        else:
            flash("Invalid Credentials")
            return redirect("/login")
        



@app.route("/logout")
def logout():
    session.pop('guest',None)

    return redirect("/login/")

@app.route('/signup', methods=["POST","GET"])
def signup():
    """ We are generating the password hash"""
    sform = SignupForm()

    if request.method == "GET":
        return render_template('user/signup.html',sform=sform)
    else:
        
        if sform.validate_on_submit():
            firstname = request.form.get('firstname')
            lastname = request.form.get('lastname')
            email = request.form.get('email')
            password = request.form.get('password')

            hashed = generate_password_hash(password) # Generating the  hashed password

            guest = Guests(guest_fname=firstname, guest_lname=lastname, guest_email=email, guest_pwd=hashed) # Adding the password into the database.

            db.session.add(guest)
            db.session.commit()
            guestid = guest.guest_id # Retrivinig the guestid
            session["guest"] = guestid # saving the guestid in a session so we can use it elsewhere. 
            
            # return redirect('/profile', theid=theid)
            return render_template('user/profile.html')
        else:
            return render_template("user/signup.html", sform=sform)

    


# @app.route("/submitsignup", methods=["POST"])
# def submitsignup():
#     firstname = request.form.get('firstname')
#     lastname = request.form.get('lastname')
#     email = request.form.get('email')
#     password = request.form.get('password')
    

#     sform = SignupForm()

#     if sform.validate_on_submit():
#         guest = Guests(guest_fname=firstname, guest_lname=lastname, guest_email=email, guest_pwd=password)

#         db.session.add(guest)
#         db.session.commit()
#         return redirect('/profile')
#     else:
#         return render_template("user/signup.html", sform=sform)

@app.route('/profile')
def profile():

    loggedin = session.get('guest')

    if loggedin != None:
        
        guestdeets = db.session.query(Guests).filter(Guests.guest_id == loggedin).first()

        # gift = Gifts.query.all()

        return render_template('user/profile.html', guestdeets=guestdeets)

    else:
        flash("You must be logged in to view this page")
        return redirect("/login")

@app.route('/registry')
def gift_registry():

    loggedin = session.get('guest')

    if loggedin != None:
        promised_gifts=[]
        guestdeets = db.session.query(Guests).filter(Guests.guest_id == loggedin).first()
    #We want to make it that when the customer has selected the gift item it will show as checked once the customer submits. 

        promised = Guest_gift.query.filter(Guest_gift.g_guestid == loggedin).all()
    #This is to filter for gifts with the id of the individual and this is instantiating the object of the Guest_gift table. 

        if promised: # this can come as an empty list, hence you can use this boolean if statement. 
            for p in promised:
                promised_gifts.append(p.g_giftid) #P is also an object here, and we are retrieveing the id of the gift to use in the table. 


        gift = Gifts.query.all()

        return render_template('user/gift_registry.html', guestdeets=guestdeets,gift=gift, promised_gifts=promised_gifts)

    else:
        flash("You must be logged in to view this page")
        return redirect("/login")

@app.route("/submit/registry", methods=['POST'])
def submit_registry():
    loggedin = session.get('guest')

    if loggedin != None:
        selected = request.form.getlist('selected_gift')

#We have use this technique in deleting the previous records before you update a new one to avoid the case of multiple entry of old and new choices being lumped together on the database. 
        db.session.execute(f"DELETE FROM guest_gift WHERE g_guestid='{loggedin}'")
        db.session.commit()

        for s in selected:
            gg=Guest_gift()
            db.session.add(gg)
            gg.g_giftid = s
            gg.g_guestid = loggedin
            
            db.session.commit()

        flash("Thank you. Gifts recorded")
        return redirect('/registry')

    else:
        flash("You must be logged in to view this page")
        return redirect("/login")

@app.route('/message')
def message_us():
    cform = ContactForm()
    return render_template('user/contactus.html', cform=cform)

@app.route('/submitcontact', methods=["POST","GET"])
def submit_contact():
    cform = ContactForm()
    if request.method == "GET":
        return redirect('/submitcontact')
    else:
        if cform.validate_on_submit():
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            message = request.form.get('message')

            m = Contact(con_fullname = fullname, con_email = email, con_message = message)

            db.session.add(m)
            db.session.commit()
            flash('Message sent!')
            return redirect('/')
        else:
            return render_template('user/contactus.html', cform=cform)

@app.route("/user/edit/")
def edit_user():

    myid = session.get('guest')

    deets = Guests.query.filter(Guests.guest_id == myid)

    return render_template("user/user_edit.html", deets=deets)

@app.route("/user/update/profile",methods=["POST"])
def update_user():

    myid = session.get('guest')

    if myid != None:
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        address = request.form.get('address')

        guest_deets = Guests.query.filter(Guests.guest_id == myid).first()

        guest_deets.guest_fname = firstname
        guest_deets.guest_lname = lastname
        guest_deets.guest_address = address

        db.session.commit()

        flash('Profile updated successfully')
        return redirect("/profile")
    else:
        return redirect("/login")

@app.route("/user/Upload")
def pic_upload():
    loggedin = session.get('guest')
    deets = Guests.query.filter(Guests.guest_id == loggedin).all()

    
    if loggedin != None:
        return render_template("user/upload_profile.html", deets=deets )
    else:
        return redirect("/login")

@app.route("/user/submit_upload", methods =["POST"])
def submit_upload():
    loggedin = session.get('guest')

    if loggedin != None:
        # retrieving the file
        if request.files != "":
            fileobj = request.files['profilepix']

            allowed = ['.jpg','.png','.jpeg']
            originalname = fileobj.filename # don't use this oone, it will clash. 


            #this is to get the first part, our goal is to give each file a unique name. 

            newname = random.random() * 10000000 # random has to be imported from python. 

            picturename, ext = os.path.split(originalname) #splits file into 2 parts on the extension. 

            if ext in allowed:
                path = "weddingapp/static/uploads/"+str(newname)+ext

                fileobj.save(f"{path}")

                upfile = Guests.query.filter(Guests.guest_id == loggedin).first()

                upfile.guest_image = str(newname)+ext

                db.session.commit()

                flash("Image successfully uploaded")
            else:
                flash("Invalid Format")
            return redirect('/profile')
        else:
            flash("Please select a valid image")
            return redirect('/user/upload')
    else:
        return redirect('/login')


@app.route("/social")
def forum():
    return render_template("user/forum.html")


@app.route('/send_forum')
def sendforum():
    
    loggedin = session.get('guest')

    if loggedin != None:
        content = request.args.get('suggest')

        comment = Comment(g_guestid=loggedin,comment_content=content)

        db.session.add(comment)
        db.session.commit()

        return "Thank you, your message has been recieved."

    else:
        return "You must be logged in to send comment"

#Below are for ajax demo

@app.route("/ajax_test")
def ajax_test():
    loggedin = session.get('guest')
    guestdeets = Guests.query.filter(Guests.guest_id == loggedin).all()
    
    state = State.query.all()

    return render_template("user/testing.html", guestdeets=guestdeets,state=state)

@app.route("/ajaxtests/checkusername", methods=["POST","GET"])
def ajaxtests_submit():

    user = request.values.get('username')

    chk = Guests.query.filter(Guests.guest_email == user).first()

    if chk == None:
        return "<p class ='lead alert alert-success'> Email is available. </p>"
    else:
        return "<p class ='lead alert alert-danger'> Email have been taken. </p>"

@app.route("/ajaxtests_states")
def ajaxtests_states():
    selected=request.args.get('stateid')

    mylga = Lga.query.filter(Lga.state_id == selected).all()

    retstr=""

    for i in mylga:

        retstr = retstr + f"<option value='{i.lga_id}'>{i.lga_name}</option>"

    return retstr

@app.route("/ajaxtest/final",methods=['POST'])
def ajaxtest_final():

    appended_data = request.form.get('missing')
    firstname = request.form["firstname"]
    lastname = request.form["lastname"]

    # retrieve the file
    fileobj = request.files['image'] #fileobj is an object that has been instantiated. 

    original_name = fileobj.filename #this will be the filename that will be saved. I think that we can go ahead to save this to the database. 

    fileobj.save(f'weddingapp/static/images/{original_name}') #this has saved the file. 

    return jsonify(firstname=firstname,lastname=lastname,appended_data=appended_data,filename=original_name) #filename has been added for the purpose of uploading it to the html document. 

"""Consuming API"""

@app.route("/accommodation")

def accommodation():
    
    username ="guestapp"
    password = 1234
    try:
        rsp = requests.get(("http://127.0.0.1:8080/api/v1.0/getall"),auth=(username,password))

        rsp_json = rsp.json() # converts rsp from HTTP response to Json.

        return render_template("user/accommodation.html", rsp_json=rsp_json)

    except:
        return "Oops, the server is currently under maintenance, pleae try again later."

def get_price(itemid):
    
    deets = Uniform.query.get(itemid)

    if deets != None:
        return deets.uni_price
    else:
        return 0

def generate_ref():
    ref = random.random() *10000000
    return int(ref)

@app.route("/confirmation")
def confirmation():
    loggedin = session.get("guest")
    ref = session.get("reference")
    if loggedin != None:
        deets = Orders.query.join(Order_details,Orders.order_id==Order_details.det_orderid).join(Uniform,Order_details.det_itemid==Uniform.uni_id).filter(Orders.order_by == loggedin, Orders.order_ref == ref).add_columns(Order_details,Uniform).all()

        t = Orders.query.filter(Orders.order_ref == ref).first()
       
        return render_template('user/confirmation_page.html', deets=deets,total=t.order_totalamt)

    else:
        return redirect("/login")

@app.route("/asoebi", methods=['POST','GET'])
def uniform():
    loggedin = session.get('guest')

    if loggedin != None:
        if request.method == 'GET':
            uni = Uniform.query.all()
            return render_template("user/aso_ebi.html", uni=uni, loggedin=loggedin)
        else:
            uniform_selected = request.form.getlist('uniform')
            if uniform_selected:
                #insert into order table
                ref = generate_ref()
                session['reference'] = ref
                ord = Orders(order_by = loggedin, order_status = "Pending", order_ref=ref)
                db.session.add(ord)
                db.session.commit()

                #insert all the items into order_details

                orderid = ord.order_id
                total = 0
                for i in uniform_selected:
                    price = get_price(i)
                    ord_det = Order_details(det_orderid=orderid, det_itemid=i, det_itemprice=price)
                    total = total + price
                    db.session.add(ord_det)
                ord.order_totalamt = total
                db.session.commit()
                
                return redirect("/confirmation")
            else:
                flash('Please make a selection')
                return redirect("/asoebi")

    else:
        return redirect('/login/')