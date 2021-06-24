from flask import Flask,render_template,request,flash,redirect,session
from flask_bootstrap import Bootstrap
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash,check_password_hash
import yaml
import os

app=Flask(__name__)
Bootstrap(app)

#configure teh database info

db=yaml.load(open('db.yaml'))

app.config['MYSQL_HOST']=db['mysql_host']
app.config['MYSQL_USER']=db['mysql_user']
app.config['MYSQL_PASSWORD']=db['mysql_password']
app.config['MYSQL_DB']=db['mysql_db']
app.config['MYSQL_CURSORCLASS']='DictCursor'

mysql=MySQL(app)

app.config['SECRET_KEY']=os.urandom(24)

@app.route('/')
def index():
    cur=mysql.connection.cursor()
    blogs=None
    try:

        results=cur.execute("select blog_id, title,author,body from blog")
        if results>0:
            blogs=cur.fetchall()

        cur.close()
    except Exception as e:
        cur.close()
        print('error',e)
        flash('Unable to retrieve blos from  DB,check logs','danger')
    return render_template('index.html',blogs=blogs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/blogs/<int:id>/')
def blogs(id):
    cur=mysql.connection.cursor()
    blogs=None
    try:
        results=cur.execute("select blog_id, title,author,body from blog where blog_id= {} ".format(int(id)))
        if results>0:
            blog=cur.fetchone()
            print(blog)
        cur.close()
    except Exception as e:
        cur.close()
        print('error',e)
        flash('Unable to retrieve blos from  DB,check logs','danger')
    return render_template('blogs.html',blog=blog)



@app.route('/register/',methods=['GET','POST'])
def register():
    if request.method=='POST':
        form_data=request.form
        if form_data['pass']!=form_data['repass']:
            flash('Password dont match','danger')
            return render_template('register.html')
        else:
            cur=mysql.connection.cursor()
            try:
                firstname,lastname,username,email,password=form_data['firstname'],form_data['lastname'],form_data['username'],form_data['email'],generate_password_hash(form_data['pass'])
                cur.execute("INSERT INTO user(first_name,last_name,username,email,password) VALUES(%s,%s,%s,%s,%s)",(firstname,lastname,username,email,password))
                mysql.connection.commit()
                flash('user successfully created','success')
                print('succes')
                cur.close()
                return redirect('/login')
            except Exception as e:
                cur.close()
                print('error',e)
                flash('Unable to insert into DB,check logs','danger')

    return render_template('register.html')

@app.route('/login/',methods=['GET','POST'])
def login():
    if request.method=='POST':
        form_data=request.form
        if form_data['username']=='':
            flash('Enter user name','warning')
        elif form_data['password']=='':
            flash('Enter password','warning')
        else:
            cur=mysql.connection.cursor()
            try:
                username,password=form_data['username'],form_data['password']
                fetched_values=cur.execute("select * from user where username= %s ",([username]))
                if fetched_values>0:
                    user=cur.fetchone()
                    print(user)

                    if check_password_hash(user['password'],password):
                        session['logged']=True
                        session['firstname']=user['first_name']
                        session['lastname']=user['last_name']
                        flash('Welcome {}  you have been successfully logged in '.format(session['firstname']),'success')
                        #return redirect('/',blogs=None)
                        return redirect('/my-blogs')
                    else:
                        cur.close()
                        flash(f'passwords dont match ','danger')
                        return render_template('login.html')
                else:
                    cur.close()
                    flash('user not found','danger')
                    return render_template('login.html')


            except Exception as e:
                cur.close()
                print('error',e)
                flash('Unable to select user,check logs','danger')
                return render_template('login.html')
    return render_template('login.html')



@app.route('/write-blog/',methods=['GET','POST'])
def write_blog():

    if request.method=='POST':
        print(session)
        form_data=request.form
        if form_data['blogtitle']=='':
            flash('enter a title for blog','warning')
        if form_data['blogarea']=='':
            flash('enter some data for blog','warning')
        else:
            cur=mysql.connection.cursor()
            try:
                title,content=form_data['blogtitle'],form_data['blogarea']
                cur.execute("INSERT INTO blog(title,body,author) VALUES(%s,%s,%s)",(title,content,session['firstname'] +session['lastname']))
                mysql.connection.commit()
                flash('blog post successfully created','success')
                print('succes')
                cur.close()
                return redirect('/')
            except Exception as e:
                cur.close()
                print('error',e)
                flash('Unable to Create Blog,check logs','danger')
    return render_template('write-blog.html')

@app.route('/my-blogs/')
def my_blogs():
    cur=mysql.connection.cursor()
    blogs=None
    try:
        author=session['firstname']+session['lastname']
        print(author)
        results=cur.execute("select blog_id, title,author,body from blog where author=%s",([author]))
        if results>0:
            blogs=cur.fetchall()

        cur.close()
    except Exception as e:
        cur.close()
        print('error',e)
        flash('Unable to retrieve blos from  DB,check logs','danger')

    return render_template('my-blogs.html',blogs=blogs)

@app.route('/edit-blog/<int:id>',methods=['GET','POST'])
def edit_blog(id):
    if request.method=='POST':
        form_data=request.form
        cur=mysql.connection.cursor()
        try:
            title,content=form_data['blogtitle'],form_data['blogarea']
            cur.execute("UPDATE  blog SET title= %s,body= %s where blog_id= %s",(title,content,id))
            mysql.connection.commit()
            flash('blog post successfully created','success')
            print('succes')
            cur.close()
            return redirect('/')
        except Exception as e:
            cur.close()
            print('error',e)
            flash('Unable to Create Blog,check logs','danger')

    cur=mysql.connection.cursor()
    blogs=None
    try:
        results=cur.execute("select blog_id, title,author,body from blog where blog_id= {} ".format(int(id)))
        if results>0:
            blog=cur.fetchone()
            print(blog)
        cur.close()
    except Exception as e:
        cur.close()
        print('error',e)
        flash('Unable to retrieve blos from  DB,check logs','danger')


    return render_template('edit-blog.html',blog=blog)

@app.route('/delete-blog/<int:id>',methods=['GET','POST'])
def delete_blog(id):
    cur=mysql.connection.cursor()
    try:
        cur.execute("Delete from   blog where blog_id= {}".format(id))
        mysql.connection.commit()
        flash('blog post deleted created','success')
        cur.close()

    except Exception as e:
        cur.close()
        print('error',e)
        flash('Unable to delete Blog,check logs','danger')

    return redirect('/my-blogs/')

if __name__=='__main__':
    app.run(debug=True)
