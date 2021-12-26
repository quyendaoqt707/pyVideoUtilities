
from posixpath import basename
from types import CellType
from PyQt5 import QtCore, QtWidgets, uic
import sys
from moviepy.editor import *
from proglog import TqdmProgressBarLogger
from math import ceil


class MyBarLogger(TqdmProgressBarLogger, QtWidgets.QWidget):
    def __init__(self) -> None:
        TqdmProgressBarLogger.__init__(self)
        QtWidgets.QWidget.__init__(self)
    progressBar_signal = QtCore.pyqtSignal(int)

    def callback(self, **changes):
        # Every time the logger is updated, this function is called
        if len(self.bars):
            percentage = next(reversed(self.bars.items()))[
                1]['index'] / next(reversed(self.bars.items()))[1]['total']
            # print(percentage)
            # return ceil(percentage*100)
            self.progressBar_signal.emit(ceil(percentage*100))


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("UI.ui", self)


#		 Widgets Slot connection from here:
        self.my_logger = MyBarLogger()
        self.progressBar.setValue(0)
        self.run1Btn.clicked.connect(self.runProfile1)
        self.run2Btn.clicked.connect(self.runProfile2)
        self.run3Btn.clicked.connect(self.runProfile3)
        self.my_logger.progressBar_signal.connect(self.progressBar_func)
        self.show()


#	 Global variable from here:
    destOutput = "D:\Videos"
    len = 15.8
    counter = 0
#	 Handle Functions from here:

    def runProfile1(self):
        self.statusBar().showMessage("--Processing...--")
        fileSrc = "D:\Videos"
        result=self.convert(fileSrc, self.destOutput, self.len)
        self.counter = self.counter+1
        
        if result==0:
            self.statusBar().showMessage("--Done!--")

    def runProfile2(self):
        self.statusBar().showMessage("--Processing...--")
        fileSrc = "H:\Documents\Bandicam"
        result=self.convert(fileSrc, self.destOutput, self.len)

        self.counter = self.counter+1
        if result==0:
            self.statusBar().showMessage("--Done!--")

    def runProfile3(self):
        self.statusBar().showMessage("--Processing...--")
        fileSrc = "C:\\Users\\RV\\Desktop\\BandicamSSD"
        result=self.convert(fileSrc, self.destOutput, self.len)
        self.counter = self.counter+1

        if result==0:
            self.statusBar().showMessage("--Done!--")
        

    #	 Slave function from here:
    def progressBar_func(self, i):
        self.progressBar.setValue(i)

    def pickLastFile(self, src):
        files = os.listdir(src)
        paths = [os.path.join(src, basename) for basename in files]
        return max(paths, key=os.path.getctime)

    def convert(self, src, dest, len):
        prefix = str(self.counter)+"_"
        targetFileName = self.pickLastFile(src)
        newBasename = prefix+os.path.basename(targetFileName)
        newDest = os.path.join(dest, newBasename)

        # newName=prefix+targetFileName

        # loading video dsa gfg intro video
        clip = VideoFileClip(targetFileName)
        if clip.duration < 60 and clip.duration > 15:

            # getting only first 5 seconds
            # clip = clip.subclip(0, clip.duration)
            final = clip.fx(vfx.speedx, clip.duration/Ui.len)
            # new clip with new duration
            # new_clip = clip.set_duration(Ui.len)

            # new clip with new duration
            final.write_videofile(newDest, logger=self.my_logger)
            return 0
        else:
            self.statusBar().showMessage("uhmm, duration > 60s or < 15s. Re-check inputVideo!")
            return 1


# Main loop from here:
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
