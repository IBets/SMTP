import sys
import smtp_lib

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit, QCheckBox, QGroupBox, QGraphicsScene
from PyQt5.QtWidgets import QGraphicsView, QCheckBox, QGroupBox, QGraphicsScene, QTextEdit, QGridLayout, QPushButton, QFileDialog, QMessageBox


WINDOW_TITTLE = "SMTP Client"
WINDOW_WIDTH  = 550
WINDOW_HEIGHT = 475


class SMTPClientWidget(QGraphicsView):
    def __init__(self):    
        self.initScene()
        self.initSMTPConfig()
        self.initEmailMessage()    
        self.initUI()
       
    def initUI(self):

        self.attachments = []
        hbox = QHBoxLayout()

        self.button_attach = QPushButton("Append attachments")
        self.button_send   = QPushButton("Send")
        
        self.button_attach.clicked.connect(self.append_attach)
        self.button_send.clicked.connect(self.send)
        
        hbox.addWidget(self.button_attach)
        hbox.addWidget( self.button_send)
       
        self.vbox.addLayout(hbox)
        widget = QWidget()
        widget.setLayout(self.vbox)
        self.scene.addWidget(widget)

        super().__init__(self.scene)

        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.setWindowTitle(WINDOW_TITTLE)
        self.show()

    def initScene(self):
        self.scene = QGraphicsScene()
        self.vbox  = QVBoxLayout()

    def initSMTPConfig(self):
             
        #SMTP Configuration
    
        self.textServer   = QLineEdit("smtp.mail.ru")
        self.textPort     = QLineEdit("465")     
        self.textUser     = QLineEdit("login1@mail.ru")
        self.textPassword = QLineEdit("qwer12345")
        self.flag         = QCheckBox("Use Authentication")

        group  = QGroupBox("SMTP Configuration")
        layout = QVBoxLayout()
        self.textPassword.setEchoMode(QLineEdit.Password)

        hboxs = [QHBoxLayout(),  QHBoxLayout()]
        hboxs[0].addWidget(QLabel("SMTP Server"))
        hboxs[0].addWidget(self.textServer)
        hboxs[0].addWidget(QLabel("Port"))
        hboxs[0].addWidget(self.textPort)
        hboxs[1].addWidget(self.flag)
        hboxs[1].addWidget(QLabel("SMTP User"))
        hboxs[1].addWidget(self.textUser)
        hboxs[1].addWidget(QLabel("Password"))
        hboxs[1].addWidget(self.textPassword)

        layout.addLayout(hboxs[0])
        layout.addLayout(hboxs[1])
        group.setLayout(layout)   
        
        self.vbox.addWidget(group)
          
    def initEmailMessage(self):
        
        #SMTP EmailMessage

        self.textFrom    = QLineEdit("login1@mail.ru")
        self.textTo      = QLineEdit("login2@mail.ru")
        self.textSubject = QLineEdit("Subject")
        self.textBody    = QTextEdit("Body")

        group  = QGroupBox("Email Message")

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel('From'), 1, 0)
        grid.addWidget(self.textFrom , 1, 1)

        grid.addWidget(QLabel('To'), 2, 0)
        grid.addWidget(self.textTo, 2, 1)

        grid.addWidget(QLabel('Subject'), 3, 0)
        grid.addWidget(self.textSubject, 3, 1)

        grid.addWidget(QLabel('Body'), 4, 0)
        grid.addWidget(self.textBody , 4, 1, 5, 1)
        
        group.setLayout(grid)           
        self.vbox.addWidget(group)
     
    def append_attach(self):

        dialogSelectFiles = QFileDialog()
        dialogSelectFiles.setFileMode(QFileDialog.ExistingFiles) 
        dialogSelectFiles.exec_()
        self.attachments = dialogSelectFiles.selectedFiles()
    
    def send(self):
        msg  = smtp_lib.MSG()
        smtp = smtp_lib.SMTP(self.textServer.text(), int(self.textPort.text()))
        if self.flag.checkState() > 0:         
            smtp.login(self.textUser.text(), self.textPassword.text())
        
        msg["FROM"]    = self.textFrom.text()
        msg["TO"]      = self.textTo.text()
        msg["SUBJECT"] = self.textSubject.text()
        msg["BODY"]    = self.textBody.toPlainText()

        for e in self.attachments:
            msg.attach(e)

        smtp.sendmail(msg)
        QMessageBox.about(self, " ", "Message send")

       
if __name__ == '__main__':

    app = QApplication(sys.argv)
    widget = SMTPClientWidget()
    sys.exit(app.exec_())
