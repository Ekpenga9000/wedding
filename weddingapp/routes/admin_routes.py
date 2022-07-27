import re
from flask import Flask, render_template, make_response, render_template_string, request, redirect, flash,session, url_for
from sqlalchemy import values,desc
from datetime import datetime
from weddingapp import app, db, csrf
from weddingapp.models import *

@app.route("/admin", methods=['POST','GET'])
@csrf.exempt 
def admin_home():
    if request.method == 'GET':
        return render_template('/admin/admin_login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('pswd')

        ad = Admin.query.filter(Admin.admin_username == username, Admin.admin_pwd == password).first()

        if ad:
            adminid = ad.admin_id
            admin_fullname = ad.admin_name
            session['adminid'] = adminid
            session['adminname'] = admin_fullname
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials')
            return redirect('/admin')

# def session_validate(func):
#     def wrapper():
#         if session.get('adminid') != None and session.get('adminname') != None:
#             return render_template('/admin/admin_dashboard.html')
#         else:
#             return redirect('/admin')
#     return wrapper

@app.route('/admin/dashboard', methods=['POST','GET'])
def admin_dashboard():
    if session.get('adminid') != None and session.get('adminname') != None:
        return render_template('/admin/admin_dashboard.html')
    else:
        return redirect('/admin')


@app.route('/admin/logout')
def admin_logout():

    session.pop('adminid', None)
    session.pop('adminname', None)

    return redirect('/admin')

@app.after_request #To clear Cache.
def clear_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"

    return response

"""Deleting the gift"""

@app.route("/admin/delete/<id>")
def delete_gift(id):
    x = Gifts.query.get(id)

    db.session.delete(x)
    db.session.commit()
    return redirect('/admin/manage_gifts')

"""Edit the gift """

@app.route('/admin/edit/<id>')
def edit(id):

    myid = Gifts.query.get(id)
    return render_template('admin/edit_gift.html', myid=myid)

"""Update Gift"""

@app.route('/admin/update', methods=['POST'])
def update_gift():
    
    getgift = request.form.get('gift')
    getid = request.form.get('id')

    if getgift != None and getid != None and getgift != ''and getid != '':
        giftupdate = Gifts.query.get(getid)
        giftupdate.gift_name = getgift

        db.session.commit()
        flash("<p class ='alert alert-success'> Your gift have been updated successfully<p>")
        return redirect('/admin/manage_gifts')
    else:
        return redirect('/admin/edit/<id>')
    

@app.route('/admin/manage_gifts')
def manage_gifts():
    if session.get('adminid') != None and session.get('adminname') != None:
        p = Gifts.query.order_by(Gifts.gift_name.desc()).all()
        # p = Gifts.query.order_by(Gifts.gift_name.desc()).offset(1).limit(2).all()
        return render_template('/admin/allgifts.html', p=p)
    else:
        return redirect('/admin')

@app.route("/admin/manage/guest")
def guest_manage():

    guest = Guests.query.all()
    # guest = db.session.query(Guests).order_by(Guests.guest_fname.desc()).all()

    return render_template('admin/guest_manage.html', guest=guest)

@app.route('/admin/add/gift', methods=["POST","GET"])
def add_gift():
    if session.get('adminid') != None and session.get('adminname') != None:
        if request.method=='GET':
            return render_template('admin/newgift.html')
        else:
            giftname = request.form.get('gift')
            
            if giftname == None:
               return redirect('/admin/add/gift')
            else:

                gift = Gifts(gift_name= giftname)
                db.session.add(gift)
                db.session.commit()
                return redirect('/admin/manage_gifts')
                   
    else:
        return render_template('/admin')