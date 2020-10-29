from flask import Flask, render_template, request, json, url_for, session, redirect, g
import requests
from flaskext.mysql import MySQL
import bcrypt
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
import os
import Modelo as Modelo
import ModeloContrato as ModeloContrato
import imaplib
import email
import time
from bs4 import BeautifulSoup
import re
import jinja2
import ctypes


app = Flask(__name__)

#contraseña super secreta
app.secret_key ='matangalachanga'

#conectar a la base de datos
app.config['MYSQL_DATABASE_USER'] = 'sepherot_jennifer'
app.config['MYSQL_DATABASE_PASSWORD'] = 'AW4ur5mHBR'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_jenniferBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL()
mysql.init_app(app)

#abrir los archivos
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] ='gofaster'
app.config['UPLOAD_FOLDER2'] ='./static'
app.config['UPLOAD_FOLDER3'] ='./static'
app.config['UPLOAD_FOLDER4'] ='./static'
app.config['UPLOAD_EXTENSIONS'] = '.pdf', '.png' , '.jpeg'
app.config['SESSION_TYPE'] = 'filesystem'

#para guardar el usuario
@app.before_request
def before_request():
   g.user = None
   if 'name' in session:
      g.user = Modelo.buscarU(session['name'])

#pagina inicial
@app.route("/")
def index():
    return render_template("login.html")

#pagina de registro, solo para nosotras  
@app.route('/register', methods=['GET', 'POST'])
def Register():
    if request.method == "POST":
        _n = request.form['Name']
        _l = request.form['Lastname']
        _e = request.form['Email']
        _p = request.form['Password']
        #.encode('utf-8')
        #hash_p = bcrypt.hashpw(_p, bcrypt.gensalt())
        
        #insertar usurio
        if _n and _l and _e and _p:
                Modelo.registro(_n, _l, _e, _p)
                return redirect(url_for('login'))

        #validar que no exista
        cur = mysql.get_db().cursor()
        cur.execute('SELECT * FROM USERS WHERE email=%s', (_e))
        val = cur.fetchone()
        print(val)
        cur.close()

        #si el usuario existe
        if len(val) is not 0:
            if _e == val[3]:
                Modelo.entidades(_e,'REGISTER.FAIL', 'registro fallido')
                return 'Error: Usuario ya existente'

        #si el usuario no existe
        else:
            Modelo.registro(_n, _l, _e, _p)
            session['name'] = val[1]
            session['email'] = val[3]
            Modelo.entidades(session['email'],'REGISTER', 'registro exitoso')
            return render_template('Login.html')      
    else:
        return render_template('Register.html')

#pagina de iniciar sesion
@app.route('/login', methods=['GET','POST'])
def login():
    if g.user:
        return redirect(url_for('aspirantes'))
    if request.method == 'POST':
        session.pop('name', None)
        _e = request.form['Email']
        _p = request.form['Password']
        #print(_e)
        #print(_p)
        
        if (_e and _p):
            cursor = mysql.get_db().cursor()
            cursor.execute('SELECT * FROM USERS WHERE email=%s', (_e))
            user = cursor.fetchone()
            #print(user)
            cursor.close()
            
            #si el usuario existe
            if len(user) > 0:
                #si la contraseña y el usuario es igual a la BD
                if _p == user[4] and _e == user[3]:     
                    session['id'] = user [0]           
                    session['name'] = user[1]
                    #print(session['name'])
                    session['email'] = user[3]
                    #print(session['email'])
                    time.sleep(.5)
                    Modelo.entidades(session['email'],'LOGIN', 'login exitoso')
                    return redirect(url_for('aspirantes'))
                    time.sleep(.5)
                #si la contraseña es diferente
                else:
                    Modelo.entidades(_e,'LOGIN.FAIL', 'login fallido')
                    return render_template('error2.html')
                    #error contraseña o usuario incorrectos
    return render_template('Login.html')
 
#pagina que muestra el error (página en construcción para login)
@app.route("/error")
def error():
    return render_template("error.html")

#pagina para recuperar contraseña si se olvida
@app.route("/recuperar",methods=['GET', 'POST'])
def recuperar():
    if request.method == 'POST':
        _e = request.form['Email']
        Modelo.entidades(_e,'RECUPERAR CONTRASEÑA', 'solicitó recuperar su contraseña')
        time.sleep(.5)
        return redirect(url_for('login'))
    return render_template("recuperar.html")


#AQUI EMPIEZA LO DIFICIL

#pagina donde se ven todos los aspirantes
@app.route('/inicio', methods=['GET', 'POST'])
def aspirantes():
        #aqui se visualizan todos los aspirantes
        consulta = Modelo.select()
        Modelo.entidades(session['email'],'MOSTRAR ASPIRANTES', 'mostrar aspirantes exitoso')
        return render_template("aspirants.html", eventos=consulta)
        

#pagina donde se selecciona solo un aspirante
@app.route('/aspirante', methods=['GET', 'POST'])
def aspirante():
    #aqui se muestra solo un aspirante
    if request.method == 'POST':
       _id = request.form['id']
       consulta = Modelo.buscarU2(_id)
       Modelo.entidades(session['email'],'BUSCAR ID', 'busqueda exitosa')
       return render_template("uno.html", eventos=consulta)
    else:
        Modelo.entidades(session['email'],'BUSCAR ID.FAIL', 'busqueda fallida')
        return render_template('error.html')
    
    return render_template('todos.html')



#validar las identificaciones   
@app.route("/validar",methods=['GET', 'POST'] )
def subdocumentos():
   Modelo.entidades(session['email'],'INGRESAR DOCUMENTOS', 'ingreso a validar identificaciones')
   return render_template("validar.html")


#identificaciones no validadas
@app.route('/nonval')
def nonval():
    Modelo.entidades(session['email'],'VALIDACION.FAIL', 'validacion fallida')
    return render_template("error3.html")

#identificaciones validadas
@app.route("/verificados")
def verificados():
    Modelo.entidades(session['email'],'VALIDAR', 'validacion exitosa')
    return render_template("verificados.html")

#ingresar INE
@app.route('/Ine',methods= ['POST','GET'])
def Ine():
        #para comprobar que sea la misma persona
        busqueda= Modelo.buscarU2(session['id'])
        #aqui se abre el documento
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            #se llama a la funcion que hara el parseo de la foto
            Modelo.INE(busqueda,_nombrearchivo)  
            file.save(os.path.join(app.config['UPLOAD_FOLDER2'], filename))
            success = True

        if success:
            resp = json.jsonify({'message' : 'Files successfully uploaded'})
            _nombrearchivo=filename
            _urline="./static/"+filename
            Modelo.ImagenATextoINE(busqueda,_urline)
            resp.status_code = 201
            Modelo.entidades(session['email'],'CARGAR INE', 'carga de INE exitoso')
            #return resp
            return redirect(url_for('verificados'))
        else:
            Modelo.entidades(session['email'],'CARGAR INE.FAIL', 'carga de INE fallido')
            return redirect(url_for('nonval'))
       #return render_template("validar.html")

#ingresar COMPROBANTE
@app.route('/COMPROBANTE',methods= ['POST','GET'])
def COMPROBANTE():
        #para comprobar que sea la misma persona
        busqueda= Modelo.buscarU2(session['id'])
        #aqui se abre el documento
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            #se llama a la funcion que hara el parseo de la foto
            Modelo.COMPROBANTE(busqueda,_nombrearchivo)  
            file.save(os.path.join(app.config['UPLOAD_FOLDER3'], filename))
            success = True

        if success:
            resp = json.jsonify({'message' : 'Files successfully uploaded'})
            _nombrearchivo=filename
            _urline="./static/"+filename
            Modelo.ImagenATextoCOMPROBANTE(busqueda,_urline)
            resp.status_code = 201
            Modelo.entidades(session['email'],'CARGAR COMPROBANTE', 'carga de COMPROBANTE exitoso')
            return resp
            return redirect(url_for('verificados'))
        else:
            Modelo.entidades(session['email'],'CARGAR COMPROBANTE.FAIL', 'carga de COMPROBANTE fallido')
            return redirect(url_for('nonval'))
       #return render_template("validar.html")


#ingresar ESCOLARIDAD
@app.route('/ESCOLARIDAD',methods= ['POST','GET'])
def ESCOLARIDAD():
        #para comprobar que sea la misma persona
        busqueda= Modelo.buscarU2(session['id'])
        #aqui se abre el documento
        files = request.files.getlist('files[]')
        errors = {}
        success = False
        for file in files:
         if file:
            filename = secure_filename(file.filename)
            _nombrearchivo=filename
            #se llama a la funcion que hara el parseo de la foto
            Modelo.ESCOLARIDAD(busqueda,_nombrearchivo)  
            file.save(os.path.join(app.config['UPLOAD_FOLDER4'], filename))
            success = True

        if success:
            resp = json.jsonify({'message' : 'Files successfully uploaded'})
            _nombrearchivo=filename
            _urline="./static/"+filename
            Modelo.ImagenATextoESCOLARIDAD(busqueda,_urline)
            resp.status_code = 201
            Modelo.entidades(session['email'],'CARGAR CERTIFICADO', 'carga de CERTIFICADO exitoso')
            return resp
            return redirect(url_for('verificados'))
        else:
            Modelo.entidades(session['email'],'CARGAR CERTIFICADO.FAIL', 'carga de CERTIFICADO fallido')
            return redirect(url_for('nonval'))
       #return render_template("validar.html")
       

#pagina donde se crea el PDF
@app.route('/contrato', methods=['GET', 'POST'])
def contrato():
    if request.method == 'POST':
        _n = request.form['Nombre']
        _d = request.form['Domicilio']
        _p = request.form['Puesto']
        _a = request.form['Area']
        _s = request.form['Sueldo']
        _h = request.form['Horas']
        _f = request.form['Fecha']
        _t = request.form['Tipo']
        
        if (_n and _d and _p and _a and _s and _h and _f and _t):
            ModeloContrato.PDF(_n, _d, _p, _a, _s, _h, _f, _t)
            time.sleep(.5)
            Modelo.entidades(session['email'],'CREAR PDF', 'creación del PDF exitosa')
            return redirect(url_for('contrato2'))
        else:
            Modelo.entidades(session['email'],'CREAR PDF.FAIL', 'creación del PDF fallida')
            return redirect(url_for('error'))    
    return render_template('uno.html')

#pagina para avisar que se creo el PDF
@app.route('/contrato2')
def contrato2():
    return render_template('contrato2.html')

#pagina para mandar el PDF por correo
@app.route('/email')
def emaild():
    Modelo.entidades(session['email'],'ENVIAR PDF', 'envió del PDF exitoso')
    Modelo.Firma()
    return render_template('contratofirmado.html')

#pagina para finalizar el proceso del aspirante (cuando ya esten sus identificaciones y contrato firmado)
@app.route('/finalizar')
def finalizar():
    Modelo.entidades(session['email'],'FINALIZAR', 'finalizar el proceso exitoso')
    return render_template('finalizado.html')


