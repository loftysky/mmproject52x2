from uitools.qt import QtGui, QtCore
import renderSetup as rs
dialog = None


class MyDialog(QtGui.QWidget):
    def __init__(self):
        super(MyDialog, self).__init__()
        self._setup_ui()
      
    def _setup_ui(self):
        layout = QtGui.QVBoxLayout()

        self.b1 = QtGui.QCheckBox("Camera Rig Set-up")
        self.b1.stateChanged.connect(lambda:self.btnstate(self.b1))
        layout.addWidget(self.b1)
      
        self.b2 = QtGui.QCheckBox("Bake Dynamic Joints")
        self.b2.toggled.connect(lambda:self.btnstate(self.b2))
        layout.addWidget(self.b2)

        self.b3 = QtGui.QCheckBox("12 to 24 fps")
        self.b3.toggled.connect(lambda:self.btnstate(self.b3))
        layout.addWidget(self.b3)

        self.b4 = QtGui.QCheckBox("Smooth Geo")
        self.b4.toggled.connect(lambda:self.btnstate(self.b4))
        layout.addWidget(self.b4)

        self.b5 = QtGui.QCheckBox("Constrain Head")
        self.b5.toggled.connect(lambda:self.btnstate(self.b5))
        layout.addWidget(self.b5)

        self.b6 = QtGui.QCheckBox("Shadow Light Linker")
        self.b6.toggled.connect(lambda:self.btnstate(self.b6))
        layout.addWidget(self.b6)

        self.setLayout(layout)
        self.setWindowTitle("Render Set-up")

    def btnstate(self,b):
        if b.text() == "Camera Rig Set-up":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.camRigSetup()
   
        if b.text() == "Bake Dynamic Joints":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.bakeDynamicJoints()

        if b.text() == "12 to 24 fps":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.timeShift()

        if b.text() == "Smooth Geo":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.smoothGeo()          

        if b.text() == "Constrain Head":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.constrainHead()

        if b.text() == "Shadow Light Linker":
            if b.isChecked() == True:
                print b.text()+" is selected"
                rs.shadowLightLinker()


def run():
    
    # Hold onto a reference so that it doesn't automatically close.
    global dialog
    
    if dialog:
        dialog.close()
    
    dialog = MyDialog()
    dialog.show()
