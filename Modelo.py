from flask import Flask, render_template, request, json, session, render_template, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt
import imaplib
import urllib.request
import smtplib
import getpass
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.encoders import encode_base64 
from flaskext.mysql import MySQL
from pathlib import Path
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
#from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from azure.cognitiveservices.vision.computervision.models import TextOperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import re
import os
import time

#Llave azure
KEY = '9a5336a0d1bb46e89d85b0510c8b0798'
ENDPOINT = 'https://gofaster.cognitiveservices.azure.com/'

#servicio de azure
_client = ComputerVisionClient(ENDPOINT, CognitiveServicesCredentials(KEY))

app = Flask(__name__)

app.secret_key ='matangalachanga'

app.config["DEBUG"] = True
app.config['MYSQL_DATABASE_USER'] = 'sepherot_jennifer'
app.config['MYSQL_DATABASE_PASSWORD'] = 'AW4ur5mHBR'
app.config['MYSQL_DATABASE_DB'] = 'sepherot_jenniferBD'
app.config['MYSQL_DATABASE_HOST'] = 'nemonico.com.mx'
mysql = MySQL(app)
mysql.init_app(app)

#mineria de datos
def entidades(_user, _stage, _stageinfo):
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('Insert into ENTITY (user, stage, stage_info) VALUES (%s,%s,%s)', (_user,_stage,_stageinfo))
    conn.commit()

#registrar nuevo usuario
def registro(_n, _l, _e, _p):
    try:
        conn = mysql.connect()
        cursor = conn.cursor()
        ins=cursor.execute("INSERT INTO USERS (name, last_name, email, password) VALUES (%s, %s, %s, %s)", (_n, _l, _e, _p))
        conn.commit()
        if ins:
            return True
        else:
            return False
        
        cursor.close()
    except Exception as e:
        return e

#datos extraidos del correo
def inAspirantes(_nombre, _domicilio, _correo, _puesto, _area, _sueldo, _horas, _fecha, _tipo, correopos):
    try:
        estatus = 1
        conn = mysql.connect()
        cursor = conn.cursor()
        ins=cursor.execute('INSERT INTO ASPIRANTS (nombre, domicilio, correo, puesto, area, sueldo, horas, fecha, tipo, reclutador, estatus) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)', (_nombre, _domicilio, _correo, _puesto, _area, _sueldo, _horas, _fecha, _tipo, correopos,estatus))
        conn.commit()
        if ins:
            return True
        else:
            return False
        
        cursor.close()
    except Exception as e:
        return e

#esto para reenviar el correo a la persona correcta
def Ultimomail():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute('SELECT reclutador FROM ASPIRANTS ORDER BY id DESC LIMIT 1')
    ultima = cursor.fetchall()
    return ultima

#regresas todos los aspirantes
def select():
    cur1 = mysql.get_db().cursor()
    cur1.execute('SELECT * FROM ASPIRANTS')
    aspirantes = cur1.fetchall()
    #print (aspirantes)
    return aspirantes

#buscas aspirante !POR NOMBRE!
def buscarU(_nombre):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM ASPIRANTS WHERE nombre = %s',_nombre)
    aspirante = cur.fetchall()
    return aspirante

#buscas aspirante !POR ID!
def buscarU2(_id):
    cur = mysql.get_db().cursor()
    cur.execute('SELECT * FROM ASPIRANTS WHERE id = %s',_id)
    ident = cur.fetchall()
    return ident


#VALIDACIONES

def INE(busqueda,_nombrearchivo):
    try:
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET INE ='"+ _nombrearchivo +"',  estatus = estatus + 1 WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return render_template("error3.html")
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})



def COMPROBANTE(busqueda,_nombrearchivo):
    try:
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET COMPROBANTE ='"+ _nombrearchivo +"',  estatus = estatus + 1 WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return render_template("error3.html")
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})


def ESCOLARIDAD(busqueda,_nombrearchivo):
    try:
        usuario=busqueda
        if _nombrearchivo and busqueda:            
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET ESCOLARIDAD ='"+ _nombrearchivo +"',  estatus = estatus + 1 WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return render_template("error3.html")
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})

##SERVICIOS COGNITIVOS

def ImagenATextoINE(_busqueda,_urline):
    _url=open(_urline,"rb")
    _resultado=_client.batch_read_file_in_stream(_url, raw=True)
    _url.close()
    ol=_resultado.headers["Operation-Location"]
    oi=ol.split("/")[-1]
    while True:
        _resultado2=_client.get_read_operation_result(oi)
        if _resultado2.status not in [ 'NotStarted' ,  'Running' ]:
            break
        time.sleep(.5)
    _var=_resultado2
    contador= ' '
    if _var.status == TextOperationStatusCodes.succeeded:
        for var in _var.recognition_results:
            for linea in var.lines:
                #print(linea.text)
                contador=contador+ '\n' +linea.text
                
    #print(contador)

    regex = (r"([a-zA-Z0-9]+.+)\n"
	r"FECHA DE NACIMIENTO\n"
	r"(\d{2}/\d{2}/\d{4})\n"
	r"(\w+)\n"
	r"SEXO (\w)\n"
	r"([a-zA-Z0-9]+.+)")

    matches = re.findall(regex, contador, re.MULTILINE)

    regex2 = (r"DOMICILIO\n"
	r"(\D+)\n"
	r"([a-zA-Z0-9]+.+)\n"
	r"(\D+)\n"
	r"([a-zA-Z0-9]+.+)")

    matches2 = re.findall(regex2, contador, re.MULTILINE)
    #print (matches)
    #print (matches2)

    domicilio1 = (matches2[0][1])
    domicilio2 = (matches2[0][3])
    _domicilio = (matches2[0][1]+" "+matches2[0][3])
    #print(_domicilio)
    apellidop = (matches[0][0])
    nacimiento = (matches[0][1])
    apellidom = (matches[0][2])
    nombre = (matches[0][4])
    _nombre = (matches[0][4]+" "+matches[0][0]+" "+matches[0][2])
    #print(_nombre)

    try:
        usuario=_busqueda
        if _busqueda:     
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET nombre ='"+ _nombre +"',  domicilio = '"+ _domicilio +"'  WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})

    return True
    
def ImagenATextoCOMPROBANTE(_busqueda,_urline):
    _url=open(_urline,"rb")
    _resultado=_client.batch_read_file_in_stream(_url, raw=True)
    _url.close()
    ol=_resultado.headers["Operation-Location"]
    oi=ol.split("/")[-1]
    while True:
        _resultado2=_client.get_read_operation_result(oi)
        
        if _resultado2.status not in [ 'NotStarted' ,  'Running' ]:
            break
        time.sleep(1)
    _var=_resultado2
    contador= ' '
    
    if _var.status == TextOperationStatusCodes.succeeded:
        for var in _var.recognition_results:
            for linea in var.lines:
                #print(linea.text)
                contador=contador+ '\n' +linea.text
                #print(" ")
                    
    #print(contador)

    regex = (r"Aguas de la Clu\n"
        r"([a-zA-Z0-9]+.+)\n"
        r"([a-zA-Z0-9]+.+)\n"
        r"([a-zA-Z0-9]+.+),")

    matches = re.findall(regex, contador, re.MULTILINE)
    #print(matches)

    calle = matches[0][0]
    colonia = (matches[0][1])
    codigo = (matches[0][2])
    _domicilio =  (matches[0][0]+" "+matches[0][1]+" "+matches[0][2])
    #print(_domicilio)

    try:
        usuario= _busqueda
        if _busqueda:     
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET domicilio = '"+ _domicilio +"'  WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})

    return True

def ImagenATextoESCOLARIDAD(_busqueda,_urline):
    _url=open(_urline,"rb")
    _resultado=_client.batch_read_file_in_stream(_url, raw=True)
    _url.close()
    ol=_resultado.headers["Operation-Location"]
    oi=ol.split("/")[-1]
    while True:
        _resultado2=_client.get_read_operation_result(oi)
        
        if _resultado2.status not in [ 'NotStarted' ,  'Running' ]:
            break
        time.sleep(1)
    _var=_resultado2
    contador= ' '
    
    if _var.status == TextOperationStatusCodes.succeeded:
        for var in _var.recognition_results:
            for linea in var.lines:
                #print(linea.text)
                contador=contador+ '\n' +linea.text
                #print(" ")
                    
    #print(contador)

    regex = (r"a\n"
	r"([a-zA-Z0-9]+.+)\n"
	r"Por su")

    matches = re.findall(regex, contador, re.MULTILINE)
    _nombre = (matches[0][0])
    #print(_domicilio)

    try:
        usuario= _busqueda
        if _busqueda:     
            conn = mysql.connect()
            cursor = conn.cursor()
            _TABLA="ASPIRANTS"
            sqlCreateSP="UPDATE "+ _TABLA +" SET nombre ='"+ _nombre +"' WHERE id = '"+usuario+"'"
            cursor.execute(sqlCreateSP)
            data=cursor.fetchall()
            if len(data)==0:
                conn.commit()
                return render_template("verificados.html")
            else:
                return render_template("error3.html")
        else:
            return json.dumps({'html':'<span>Datos faltantes</span>'})
    except Exception as e:
        print(json.dumps({'error':str(e)}))
        return json.dumps({'error':str(e)})

    return True


#crear el correo para enviar a firmar el PDF  
def Firma():
    #persona encargada de firmar los contratos, en esta caso sera Elisa (:
    destinatario= 'elisa.gofaster@gmail.com'
    usuraio='j.consultora.a@gmail.com'
    archivo= "Contrato.pdf"
    Asunto = 'Firma de Contrato'
    mensaje = MIMEMultipart("plain")
    mensaje["Subject"]=Asunto
    mensaje["From"]=usuraio
    mensaje["To"]=destinatario
    
    html=f"""
    <html>
    <body>
        Hola <i>{destinatario}</i> te hago llegar el contrato del aspirante solicitado.</br>
        Favor de firmar y reenviar a este mismo correo para continuar con su proces, gracias<br>

    </body>
    </html>
    """
    parte_html=MIMEText(html,"html")
    mensaje.attach(parte_html)
    adjunto=MIMEBase("application","octect-stream")
    adjunto.set_payload(open(archivo,"rb").read())
    encode_base64(adjunto)
    adjunto.add_header("content-Disposition",f"attachment; filename={archivo}")
    mensaje.attach(adjunto)
    mensaje_final= mensaje.as_string()
    server =smtplib.SMTP('smtp.gmail.com')
    server.starttls()
    server.login(usuraio,'Consulta2.ja')
    server.sendmail(usuraio,destinatario,mensaje_final)
    server.quit()