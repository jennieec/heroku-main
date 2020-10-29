import imaplib
import email
from email.header import decode_header
import webbrowser
import os
from getpass import getpass
import re
import Modelo as Modelo
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

#Correo de respuesta
html = f"""
<html>
<body>
    <p>Buen dia, <br> 
    <p></p>
    Su solicitud para la generación del contrato del aspirante se ha mandado.<br>
    En breve estaremos en contacto con usted. <br>
    Gracias!<br>
    <p></p>
    Excelente día!<br>
</body>
</html>
"""
parte_html = MIMEText(html,"html")
username = "j.consultora.a@gmail.com"
password = "Consulta2.ja"
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(username, password)
status, mensaje = imap.select("INBOX")
#print(mensaje)
N = 1
mensaje = int(mensaje[0])

def _textomail(from_):
    #recupero quien me manda el aspirante
    exp1 = r"<([a-zA-Z0-9]+.+)>"
    correoexp = re.findall(exp1, from_, re.MULTILINE)
    correopos = (correoexp[0])
    #print (correopos)
    return correopos


def _textobody(body):
    #recupero los datos del aspirante
    exp2 = (r"Nombre: ([a-zA-Z0-9]+.+).\n"
	r"Domicilio: ([a-zA-Z0-9]+.+).\n"
    r"Correo: ([a-zA-Z0-9]+.+).\n"
    r"Puesto: ([a-zA-Z0-9]+.+).\n"
    r"Área: ([a-zA-Z0-9]+.+).\n"
    r"Sueldo: ([0-9]+.+).\n"
    r"Horas de trabajo: ([0-9]).\n"
    r"Fecha de ingreso: ([12]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])).\n"
    r"Tipo de contrato: ([a-zA-Z0-9]+.+)")
    bodyexp = re.findall(exp2, body, re.MULTILINE)
    bodypos0 = (bodyexp[0])
    #print(bodypos0)
    return bodyexp


for i in range(mensaje, mensaje -N, -1):
    #print(f"vamos por el mensaje {i}")
    try:
        res, mensaje = imap.fetch(str(i), "(RFC822)")
    except:
        break
    for repuesta in mensaje:
        if isinstance(repuesta,tuple):
            mensaje=email.message_from_bytes(repuesta[1])
            subject=decode_header(mensaje["Subject"])[0][0]
            if isinstance(subject, bytes):
                subject=subject.decode()
            from_ =mensaje.get("From")
            #print("Subject:", subject)
            #print("From: ", from_)

            if mensaje.is_multipart():
                for part in mensaje.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass
                    if content_type == "text/plain" and "attachment" not in content_disposition:
                        correopos = _textomail(from_)
                        bodyexp = _textobody(body)
                        _nombre = (bodyexp[0][0]) 
                        _domicilio = (bodyexp[0][1]) 
                        _correo = (bodyexp[0][2])
                        _puesto = (bodyexp[0][3])
                        _area = (bodyexp[0][4])
                        _sueldo = (bodyexp[0][5])
                        _horas = (bodyexp[0][6])
                        _fecha = (bodyexp[0][7])
                        _tipo = (bodyexp[0][8]) 
                        #print (_fecha) 
                        #print (correopos) 
                        #print (bodyexp)                 
                        try:
                            #insertar en la base de datos
                            _insert = Modelo.inAspirantes(_nombre, _domicilio, _correo, _puesto, _area, _sueldo, _horas, _fecha, _tipo, correopos)
                            print(_insert)
                            Modelo.entidades(correopos,'ENVIO CORREO', 'EL CORREO FUE ENVIADO CORRECTAMENTE')
                            try:
                                server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                                server.login('j.consultora.a@gmail.com','Consulta2.ja')
                                time.sleep(3)
                                _renitente = Modelo.Ultimomail()
                                time.sleep(3)
                                server.sendmail(username,_renitente,parte_html.as_string())
                                server.quit()
                                print("Correo enviado")
                                Modelo.entidades(correopos,'RESPOND MAIL', 'Respuesta enviada exitosamente')
                            except Exception as a:
                                pass

                        except Exception as e:
                            respuesta_re = 'El formato no es el correcto'
                            server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
                            server.login('j.consultora.a@gmail.com','Consulta2.ja')
                            time.sleep(3)
                            _renitente = Modelo.Ultimomail()
                            time.sleep(3)
                            server.sendmail(username,_renitente,parte_html.as_string())
                            server.quit()
                            #print("Correo erroneo enviado")
                            Modelo.entidades(_renitente,'RESPOND EMAIL.FAIL', 'Respuesta de errores enviada exitosamente')



