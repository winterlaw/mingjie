# all the impors
import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash

app = Flask(__name__)

app.config.update(dict(    
    DATABASE=os.path.join(app.root_path, 'app.db'),    
    DEBUG=True,    
    SECRET_KEY='development key'
))

app.config.from_envvar('FLASKR_SETTINGS', silent=True)

def connect_db():
	'''Connects to the specific database.'''
	rv = sqlite3.connect(app.config['DATABASE'])
	rv.row_factory = sqlite3.Row
	return rv

def get_db():
	"""Opens a new database cionnection if there is none yet for the current application context"""
	if not hasattr(g, 'sqlite_db'):
		g.sqlite_db = connect_db()
	return g.sqlite_db

def init_db():
	"""初始化数据库"""
	with app.app_context():
		db = get_db()
		with app.open_resource('schema.sql', mode='r') as f:
			db.cursor().executescript(f.read())
		db.commit()

def insert_db():
	with app.app_context():
		db = get_db()
		db.execute('insert into users(username, password, usertype) values(?,?,?)',('user','password','test'))
		db.commit()

@app.teardown_appcontext
def close_db(error):
	"""Close the datasbase again at the end of the requset"""
	if hasattr(g, 'sqlite_db'):
		g.sqlite_db.close()

@app.route('/')
def show_index():
	db = get_db()
	cur = db.execute('select username, password from users')
	users = [dict(username=row[0], password=row[1]) for row in cur.fetchall()]
	return render_template('index.html', users=users)

@app.route('/login', methods=['GET','POST'])
def login():
	error = None
	if request.method == 'POST':
		db = get_db()
		cur = db.execute('select password from users where username = ?', [request.form['username'],])
		rv = cur.fetchall()
		if rv and request.form['password'] == rv[0][0]:
			session['logged_in'] = True
			flash("Hello, "+request.form['username'])
			return redirect(url_for('show_index'))
		else:
			error = "用户名或密码错误"
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	session.pop('logged_in', None)
	flash('You were logged out')
	return redirect(url_for('show_index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
	error = None
	if request.method == 'POST':
		# if request.form['username'] == '':
		# 	error = "用户名不能为空"
		# elif request.form['password'] == ''：
		# 	error = "密码不能为空"
		# elif request.form['']+
		db = get_db()
		cur = db.execute('select password from users where username = ?', [request.form['username'],])
		rv = cur.fetchall()
		if not rv:
			db.execute('insert into users (username, password, usertype) values(?,?,?)',
				[request.form['username'], request.form['password'], request.form['usertype']])
			db.commit()
			flash('New user was successfully posted')
			return redirect(url_for('show_index'))
		else:
			error = "用户名已存在"
	return render_template('register.html', error=error)

if __name__ == '__main__':
	app.run()