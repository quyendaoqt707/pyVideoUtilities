
# import random
from time import sleep
import traceback
from PyQt5 import QtCore, QtWidgets, uic
import sys
from PyQt5.QtGui import QPixmap
from moviepy.editor import *
from proglog import TqdmProgressBarLogger
from math import ceil, floor
import threading
# from PIL import Image
import tempfile
from shutil import rmtree
from PyQt5.QtWinExtras import QWinTaskbarProgress, QWinTaskbarButton


class FloatWindow(QtWidgets.QWidget):
    """
    This "window" is a QWidget. If it has no parent, it
    will appear as a free-floating window as we want.
    """
    def __init__(self):
        super().__init__()
        uic.loadUi("FloatWindows.ui", self)
        # FloatWindow.setWindowFlags(QtCore.Qt.WindowType.CustomizeWindowHint | QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowMinimizeButtonHint)
        
        self.setWindowFlags(
        QtCore.Qt.Window |
        QtCore.Qt.CustomizeWindowHint |
        QtCore.Qt.WindowTitleHint |
        QtCore.Qt.WindowStaysOnTopHint 
        )
     
        self.runBtn.clicked.connect(self.floatRunHandle)
        self.isJobRunning=False

        # init WinTaskBarProgess: 
        self.taskbar_button = QWinTaskbarButton()
        self.taskbar_progress = self.taskbar_button.progress()
        self.taskbar_progress.setRange(0, 100)
        self.taskbar_progress.setValue(0)

    def updateTaskBarProgress(self,currentValue):
        self.taskbar_progress.setValue(currentValue)
        # if currentValue>=99:
            # self.isJob Running=False; background-color: Transparent
            # self.runBtn.setStyleSheet("background-color : Transparent")

    def showTaskBarProgress(self):
        # self.taskbar_button = QWinTaskbarButton()
        # self.taskbar_progress = self.taskbar_button.progress()
        # self.taskbar_progress.setRange(0, 100)
        # self.taskbar_progress.setValue(0)
        self.taskbar_progress.show()
        self.taskbar_button.setWindow(self.windowHandle())
    

    def floatRunHandle(self):
        
        # if self.isJobRunning==False:
            # self.isJobRunning=True

        if Ui.floatProfile==1:
            result = Ui.runProfile1(window)
        elif Ui.floatProfile==2:
            result =Ui.runProfile2(window)
        else:
            result =Ui.runProfile3(window)
            

        if result==0:
            self.showTaskBarProgress()
            self.runBtn.setStyleSheet("background-color : lime")
        else:
            self.runBtn.setStyleSheet("background-color : yellow")

    def updateFloatProfileLabel(self):
        if Ui.floatProfile==1:
            text="Videos|Videos"
        elif Ui.floatProfile==2:
            text="Bandicam|Videos"
        else:
            text="BandicamSSD|Videos"

        self.profileLabel.setText(text)
        # self.taskbarProgress.show()
        # self.showEvent()
        



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
#       Widgets :
        self.openFileDialog = QtWidgets.QFileDialog()


#		 Widgets Slot connection from here:
        # Input section
        self.pickInputBtn.clicked.connect(self.pickInputHandle)
        # Output section
        self.pickDestBtn.clicked.connect(self.pickOutputHandle)

        # Config section
        self.defaultLenBtn.clicked.connect(self.pickDefaultLen)
        self.processBtn.clicked.connect(self.processHandle)
        self.selectLenLine.setText("15.8")

        # Auto section
        self.my_logger = MyBarLogger()
        self.progressBar.setValue(0)
        self.run1Btn.clicked.connect(self.runProfile1)
        self.run2Btn.clicked.connect(self.runProfile2)
        self.run3Btn.clicked.connect(self.runProfile3)
        self.my_logger.progressBar_signal.connect(self.progressBar_func)
        # self.my_logger.progressBar_signal.connect(self.progressBar_func)

        # Tab 2: trim video section:
        self.pickLastestBtn.clicked.connect(self.pickLastestFileToTrim)
        self.pickInputBtn_2.clicked.connect(self.pickInputBtn2Handle)
        self.horizontalSlider.valueChanged.connect(self.updateFrameThumbnail)
        self.pickStartBtn.clicked.connect(self.pickStartHandle)
        self.pickEndBtn.clicked.connect(self.pickEndHandle)
        self.pickLeftBtn.clicked.connect(self.pickLeftInnerHandle)
        self.pickRightBtn.clicked.connect(self.pickRightInnerHandle)
        self.trimBtn.clicked.connect(self.trimBtnHandle)
        self.normalizationCheckBox.clicked.connect(self.noAndreCheckBoxHandle)
        self.removeInnerCheckBox.clicked.connect(self.noAndreCheckBoxHandle)
        self.show()


        app.aboutToQuit.connect(self.closeEvent)


        # Float windows:
        
        self.floatActiveBtn.clicked.connect(self.show_float_window)

        self.radioButton.toggled.connect(self.changeFloatProfile)
        self.radioButton_2.toggled.connect(self.changeFloatProfile)
        self.radioButton_3.toggled.connect(self.changeFloatProfile)

        self.w = FloatWindow()
        self.isFloatShow=True
        self.w.show()
        

    floatProfile=1
#	 Global variable from here:
    inputFile = "D:\Videos"
    outputDirectory = "D:\Videos"
    len = 15.8
    default_len = 15.8
    counter = 0

#	 Handle Functions from here:
    # Input section

    def pickInputHandle(self):
        self.inputFile, _filter = self.openFileDialog.getOpenFileName()
        # self.inputLine.setText(os.path.basename(self.inputFile))
        self.inputLine.setText(self.inputFile)
    # Output section

    def pickOutputHandle(self):
        self.outputDirectory = self.openFileDialog.getExistingDirectory()
        self.destLine.setText(self.outputDirectory)
    # Config section

    def pickDefaultLen(self):
        self.len = self.default_len
        self.selectLenLine.setText(str(self.len))

    def processHandle(self):
        self.len = float(self.selectLenLine.text())
        self.inputFile = self.inputLine.text()
        self.outputDirectory = self.destLine.text()
        result = self.convert(self.inputFile, self.outputDirectory, self.len)
        self.counter = self.counter+1

        if result == 0:
            self.statusBar().showMessage(str(self.counter-1)+": --Processing...--")

    # Auto section

    def runProfile1(self):

        inputFile = "D:\Videos"
        inputFile = self.pickLastFile(inputFile)  # absolute address file
        result = self.convert(
            inputFile, self.outputDirectory, self.default_len)
        self.counter = self.counter+1

        if result == 0:
            # self.statusBar().showMessage(str(self.counter-1)+": --Processing...--")
            self.statusBar().showMessage(inputFile+"    : --Processing...--")
            return 0
        else:
            return 1

    def runProfile2(self):

        inputFile = "H:\Documents\Bandicam"
        inputFile = self.pickLastFile(inputFile)  # absolute address file
        result = self.convert(
            inputFile, self.outputDirectory, self.default_len)

        self.counter = self.counter+1
        if result == 0:
            # self.statusBar().showMessage(str(self.counter-1)+": --Processing...--")
            self.statusBar().showMessage(inputFile+"    : --Processing...--")
            return 0
        else:
            return 1

    def runProfile3(self):

        inputFile = "C:\\Users\\RV\\Desktop\\BandicamSSD"
        inputFile = self.pickLastFile(inputFile)  # absolute address file
        result = self.convert(
            inputFile, self.outputDirectory, self.default_len)
        self.counter = self.counter+1

        if result == 0:
            # self.statusBar().showMessage(str(self.counter-1)+": --Processing...--")
            self.statusBar().showMessage(inputFile+"    : --Processing...--")
            return 0
        else:
            return 1



    #	 Slave function from here:

    def progressBar_func(self, i):
        self.progressBar.setValue(i)
        self.w.updateTaskBarProgress(i)
        # if i == 100:
        # self.statusBar().showMessage("---"+str(Ui.counter)+": Done!---")

    def pickLastFile(self, src):
        files = os.listdir(src)
        paths = [os.path.join(src, basename) for basename in files]
        return max(paths, key=os.path.getctime)

    def worker(self, newDest, final):
        final.write_videofile(newDest, logger=self.my_logger)
        # self.statusBar().showMessage("---"+str(self.counter-1)+str(newDest)+": Done!---")
        self.statusBar().showMessage("---"+str(newDest)+"    : Done!---")

    def convert(self, inputFile, destOutput, len):

        prefix = str(self.counter)+"_"

        newBasename = prefix+os.path.basename(inputFile)
        newDest = os.path.join(destOutput, newBasename)

        # loading video dsa gfg intro video
        clip = VideoFileClip(inputFile)
        if clip.duration < 100 and clip.duration > 15.8:

            # getting only first 5 seconds
            # clip = clip.subclip(0, clip.duration)
            final = clip.fx(vfx.speedx, clip.duration/len)
            # new clip with new duration
            # new_clip = clip.set_duration(len)

            # new clip with new duration

            try:
                myThread = threading.Thread(target=self.worker,
                                            args=(newDest, final,))
                myThread.start()

                return 0
            except:
                print(traceback.format_exc())
                print("Error: unable to start thread")
                self.statusBar().showMessage("Error: unable to start thread")
                return 1

        else:
            self.statusBar().showMessage("uhmm, duration > 100s or < 15s. Re-check inputVideo!")
            return 1

    ###### TAB2: TRIM VIDEO #####
    #  from here                #
    #############################
    targetTrimFileName_full = ""
    tempDir = ""
    step = 1

    startTrimPos = 0
    endTrimPos = 0
    leftInner = 0
    rightInner = 0

    removeInnerFlag=False;
    normalizationAfterTrimFlag= False;

    def pickLastestFileToTrim(self):
        self.targetTrimFileName_full = self.pickLastFile(
            self.inputFile)
        self.inputLine2.setText(self.targetTrimFileName_full)
        self.preprocessor()

    def pickInputBtn2Handle(self):
        self.targetTrimFileName_full, _filter = self.openFileDialog.getOpenFileName()
        if self.targetTrimFileName_full != "":
            # self.inputLine.setText(os.path.basename(self.inputFile))
            self.inputLine2.setText(self.targetTrimFileName_full)
            # self.fileExt = os.path.splitext(self.targetTrimFileName_full)[1]
            self.preprocessor()

    def prepareAllFrame(self, listTimeStamp, step):

        if os.path.isdir(self.tempDir) == False:
            os.mkdir(os.path.join(self.tempDir))

        # for i in range(1, nframes, step):
        # This section code is incorrect, duplicate frame was saved!. Why????
            #     thumb_frame_numpyArray = self.trim_clip.get_frame(i)
            #     thumb_image = Image.fromarray(thumb_frame_numpyArray)
            #     thumb_image_filepath = os.path.join(
            #         self.tempDir, f"{i}.jpg")
            #     thumb_image.save(thumb_image_filepath)

        for i in listTimeStamp:
            frame_filepath = os.path.join(self.tempDir, f"{i}.jpg")
            self.trim_clip.save_frame(frame_filepath, i*step)

        self.statusBar().showMessage("Ready!")

    def preprocessor(self):
        self.tempDir = tempfile.gettempdir()
        self.tempDir = os.path.join(self.tempDir, "pyVideoUtilities_tempDir")

        if os.path.isdir(self.tempDir) == True:
            rmtree(self.tempDir)

        self.trim_clip = VideoFileClip(self.targetTrimFileName_full)
        # nframes = self.trim_clip.reader.nframes  # return number of frame in the video

        duration = self.trim_clip.duration

        if duration >= 40:
            maxSlider = 40
            self.step = duration/40
            # listTimeStamp=[x * stepSlider for x in range(0, maxSlider)]
            listTimeStamp = [x for x in range(0, maxSlider+1)]
        else:
            maxSlider = floor(duration)
            self.step = 1
            listTimeStamp = list(range(0, maxSlider))
            listTimeStamp.append(floor(duration))

        self.horizontalSlider.setMaximum(maxSlider)
        self.horizontalSlider.setSingleStep(1)

        # self.prepareAllFrame(listTimeStamp, step)

        try:
            myThread = threading.Thread(target=self.prepareAllFrame,
                                        args=(listTimeStamp, self.step,))
            myThread.start()

            self.statusBar().showMessage("Wait a minute...")

        except:
            print(traceback.format_exc())
            print("Error: unable to start thread")
            self.statusBar().showMessage("Error: unable to start thread")
            # return 1
        sleep(0.35)
        self.currentFrameThumbnail.setPixmap(
            QPixmap(os.path.join(self.tempDir, str(listTimeStamp[0])+".jpg")))

    def updateFrameThumbnail(self):
        # print(self.horizontalSlider.value())
        i = self.horizontalSlider.value()
        self.currentPosSlider.setText(str(round(i*self.step, 2))+'s')
        self.currentFrameThumbnail.setPixmap(
            QPixmap(os.path.join(self.tempDir, f"{i}.jpg")))

    def pickStartHandle(self):
        self.startTrimPos = round(self.horizontalSlider.value()*self.step, 2)
        self.lineEdit_3.setText(str(self.startTrimPos))

    def pickEndHandle(self):
        self.endTrimPos = round(self.horizontalSlider.value()*self.step, 2)
        self.lineEdit_2.setText(str(self.endTrimPos))

    def trimBtnHandle(self):
        try:
            myThread = threading.Thread(target=self.trimSlave,
                                        args=(self.startTrimPos, self.endTrimPos, self.leftInner, self.rightInner,))
            myThread.start()

            self.statusBar().showMessage("Processing...")

        except:
            print(traceback.format_exc())
            print("Error: unable to start thread")
            self.statusBar().showMessage("Error: unable to start thread")
            # return 1

    def pickLeftInnerHandle(self):
        self.leftInner = round(self.horizontalSlider.value()*self.step, 2)
        self.lineEdit_4.setText(str(self.leftInner))

    def pickRightInnerHandle(self):
        self.rightInner = round(self.horizontalSlider.value()*self.step, 2)
        self.lineEdit_5.setText(str(self.rightInner))

    def noAndreCheckBoxHandle(self):  # normalization and remove checkbox handle
        if self.removeInnerCheckBox.isChecked() == True:
            self.removeInnerFlag=True
            self.pickLeftBtn.setEnabled(True)
            self.pickRightBtn.setEnabled(True)
            self.lineEdit_4.setEnabled(True)
            self.lineEdit_5.setEnabled(True)
        else: 
            self.removeInnerFlag=False
            self.leftInner=0
            self.rightInner=0
            self.pickLeftBtn.setEnabled(False)
            self.pickRightBtn.setEnabled(False)
            self.lineEdit_4.setEnabled(False)
            self.lineEdit_5.setEnabled(False)


        if self.normalizationCheckBox.isChecked() == True:
            self.normalizationAfterTrimFlag=True
        else: self.normalizationAfterTrimFlag=False
            


    def trimSlave(self, start, end, left, right):
        # if left == right == 0 and left*right != 0:
        if right!=0:
            prefix = str(start)+"-"+str(left)+'-'+str(right)+"-"+str(end)+'_'
        else:
            prefix = str(start)+"-"+str(end)+'_'

        newBasename = prefix+os.path.basename(self.targetTrimFileName_full)
        newDest = os.path.join(self.outputDirectory, newBasename)
        if os.path.isfile(newDest) == True:
            # self.statusBar().showMessage("File name already exists.")
            newBasename=str(self.counter)+'_'+newBasename;
            newDest = os.path.join(self.outputDirectory, newBasename)
        

        if left == right == 0:
            subClip = self.trim_clip.subclip(start, end)
            self.statusBar().clearMessage()
            subClip.write_videofile(newDest, logger=self.my_logger)
            self.statusBar().showMessage("Trimmed: "+newBasename)
        elif start <= left <= right <= end and end-start-(left-right) > 0:
            subClip = self.trim_clip.subclip(start, end)
            subClip = subClip.cutout(left-start, right-start)
            # subClip = self.trim_clip.cutout(left, right)
            subClip.write_videofile(newDest, logger=self.my_logger)
            self.statusBar().showMessage(
                f"Trimmed and CutOut[{left}-{right}]: "+newBasename)
        else:
            self.statusBar().showMessage("Error: Double-check all positions!")


    def show_float_window(self):
        if self.isFloatShow==False:
            self.isFloatShow= True
            self.w.show()
        else:
            self.isFloatShow= False
            self.w.close()

    def changeFloatProfile(self):
        if self.radioButton.isChecked() == True:
            Ui.floatProfile=1;
            # self.w.updateFloatProfileLabel()
        elif self.radioButton_2.isChecked() == True:
            Ui.floatProfile=2;
            # self.w.updateFloatProfileLabel()
        else:
            Ui.floatProfile=3;
            
        self.w.updateFloatProfileLabel() # G???i m???t method c???a m???t ?????i t?????ng th??ng qua ch??nh n?? th?? ko c???n truy???n self

        # FloatWindow.updateFloatProfileLabel(self.w) 
        # # --> g???i m???t non-static method c???a m???t class th?? c???n truy???n v??o ?????i t?????ng cho method ???? ??? v??? tr?? self


    def closeEvent(self1,self2): 
        # self1 l?? class Ui t???c l?? 'window' object , self2 class QApplication t???c l?? 'app' object
        self1.w.close()
        sys.exit(0)

# Main loop from here:
app = QtWidgets.QApplication(sys.argv)
window = Ui()
app.exec_()
