from uitools.qt import QtGui, QtCore
import renderSetup as rs
dialog = None


class MyDialog(QtGui.QWidget):
    def __init__(self):
        super(MyDialog, self).__init__()
        self._setup_ui()
      
    def _setup_ui(self):
        layout = QtGui.QVBoxLayout()

        self.b1 = QtGui.QPushButton("Camera Rig Set-up")
        self.b1.setCheckable(True)
        self.b1.clicked.connect(lambda:self.btnstate(self.b1))
        layout.addWidget(self.b1)
      
        self.b2 = QtGui.QPushButton("Bake Dynamic Joints")
        self.b2.setCheckable(True)
        self.b2.clicked.connect(lambda:self.btnstate(self.b2))
        layout.addWidget(self.b2)

        self.b3 = QtGui.QPushButton("12 to 24 fps")
        self.b3.setCheckable(True)
        self.b3.clicked.connect(lambda:self.btnstate(self.b3))
        layout.addWidget(self.b3)

        self.b4 = QtGui.QPushButton("Smooth Geo")
        self.b4.setCheckable(True)
        self.b4.clicked.connect(lambda:self.btnstate(self.b4))
        layout.addWidget(self.b4)

        self.b5 = QtGui.QPushButton("Constrain Head")
        self.b5.setCheckable(True)
        self.b5.clicked.connect(lambda:self.btnstate(self.b5))
        layout.addWidget(self.b5)

        self.b6 = QtGui.QPushButton("Shadow Light Linker")
        self.b6.setCheckable(True)
        self.b6.clicked.connect(lambda:self.btnstate(self.b6))
        layout.addWidget(self.b6)

        self.setLayout(layout)
        self.setWindowTitle("Render Set-up")

    def btnstate(self,b):
        if self.b1.isChecked():
                print b.text()+" is selected"
                rs.camRigSetup()
                self.b1.setCheckable(False)
   
        if self.b2.isChecked():
                print b.text()+" is selected"
                rs.bakeDynamicJoints()

        if self.b3.isChecked():
                print b.text()+" is selected"
                rs.timeShift()

        if self.b4.isChecked():
                print b.text()+" is selected"
                rs.smoothGeo()          

        if self.b5.isChecked():
                print b.text()+" is selected"
                rs.constrainHead()

        if self.b6.isChecked():
                print b.text()+" is selected"
                rs.shadowLightLinker()


def run():
    
    # Hold onto a reference so that it doesn't automatically close.
    global dialog
    
    if dialog:
        dialog.close()
    
    dialog = MyDialog()
    dialog.show()
