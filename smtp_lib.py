import base64
import socket
import ssl

class MSG:
    ATTACH_TYPE = { 'html': 'text/html', 'doc': 'application/msword', 'jpg': 'image/jpeg' }

    def __init__(self):
        self.dict = {}
        self.attachments = {}

    def __getitem__(self, key):
        return self.dict[key]

    def __setitem__(self, key, value):
        self.dict[key] = value

    def attach(self, filename):
        with open(filename, 'rb') as f:       
            self.attachments[filename] = ( MSG.ATTACH_TYPE[filename.split('.')[-1]], base64.b64encode(f.read()).decode())

class SMTP:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.username = None
        self.password = None    

    def login(self, username, password):
        self.username = username
        self.password = password

    def sendmail(self, msg):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as smtp_sock:
            smtp_sock.connect((self.host, self.port))
            with ssl.wrap_socket(smtp_sock) as ssl_sock:
                data = ssl_sock.recv(1024)
                for e in self._request(msg):
                    ssl_sock.send((e + '\r\n').encode('utf-8'))
                    print("SEND: ", e)
                    print("GET: ", ssl_sock.recv(1024).decode())

    def _data(self, msg):
        data =  ''
        data += 'From: {} \n'.format(msg["FROM"])
        data += 'To: {} \n'.format(msg["TO"])
        data += 'Subject: =?UTF-8?B?{}?=\n'.format(self._encode(msg["SUBJECT"]))
        
        global_boundary = 'global_boundary'
        data += 'Content-Type: multipart/mixed; boundary={};\n'.format(global_boundary)

        data += "--{}\n".format(global_boundary)
        data += 'Content-Type: text/plain; charset=utf8\n'
        data += 'Content-Transfer-Encoding: base64\n\n'    
        data += "{}\n".format(self._encode(msg["BODY"])) 

        for e in msg.attachments:
            data += "--{}\n".format(global_boundary)
            data += 'Content-Type: {}\n'.format(msg.attachments[e][0])
            data += 'Content-Transfer-Encoding: base64\n'
            data += 'Content-Disposition:attachment; filename={}\n\n'.format(e)
            data += '{}\n'.format(msg.attachments[e][1])

        data += "--{}\n".format(global_boundary)
        data += '\n.'
        return data
                    
    def _request(self, msg):

        requst = None

        if self.username is None:
            requst = [ 'EHLO '       + msg["FROM"].split("@")[0],
                       'MAIL FROM: ' + msg["FROM"],
                       'RCPT TO: '   + msg["TO"],
                       'DATA',
                       self._data(msg),
                       'QUIT' ]

        else:         
             requst = [ 'EHLO '       + msg["FROM"].split("@")[0],
                        'AUTH LOGIN',
                        self._encode(self.username),
                        self._encode(self.password),
                        'MAIL FROM: ' + msg["FROM"],
                        'RCPT TO: '   + msg["TO"],
                        'DATA',
                        self._data(msg),
                        'QUIT' ]
        return requst

    def _encode(self, data):
        return base64.b64encode(data.encode('utf-8')).decode()
