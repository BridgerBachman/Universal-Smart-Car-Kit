"""
__author__ = "Bridger Miles"
__license__ = "GNU General Public License, version 2"
__version__ = "Beta"
__email__ = "10766744@uvu.edu"
__status__ = "Final System Driver Code"
"""

from PyQt5 import QtCore, QtGui, QtWidgets#Imports all of the GUI Libraries for linux.
from PyQt5.QtCore import(QCoreApplication,QObject,QRunnable,QThread,QThreadPool,pyqtSignal)#Imports all Signals and slot libraries for communication between threads.

import RPi.GPIO as GPIO#Imoport the general purpose IO Hardware to send and recieve data for the BSM and the BackupCamera Trigger.
import time, sys, obd, picamera

from PIL import Image #Import Pil image library to overlay backup camera lines.
from time import sleep#Used for waiting and pausing code.
import picamera#import hardware libraries to interface with the physical camera.
from PIL import Image#import image from pil image library.
from time import sleep#import sleep function to pause code execution.

class BackupCameraWorker(QThread):#This thread controls all of the backup camera operations: on, off, image overlay.
    
    def run(self):#Thread code execution starts here.
    
        GPIO.setwarnings(False)#Used for debugging.
        GPIO.setmode(GPIO.BCM)#BCM board convention used.
        GPIO.setup(18, GPIO.OUT,initial=GPIO.HIGH)#Initilize lpin 18 to 3.3V using a built in pull up resistor.
        GPIO.setup(25, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#Initilize pin 25 to 0V using a built in pull udown resistor to remove floating voltages.

        while True:#Run forever.
            if GPIO.input(25):#if signal is recieved ie. meaning the relay is set to nc position because car is in reverse.
                with picamera.PiCamera() as camera:
                    camera.resolution = (800,480)#Set image to match resolution of our screen.
                    camera.framerate = 30#set framerate to 30fps
                    camera.start_preview()#turn on the camera
                    #Using a photo editor scale linesOverlay.png to match your specific cars width and length used for different sized cars.
                    lines = Image.open('linesOverlay.png')#put the guidance lines over the camera.
                    o = camera.add_overlay(lines.tobytes(), lines.size)#converte to bytearray
                    o.alpha = 128#Sets the tranparancy and moves the layers to proper order so backup lines are over image and not hiden under.
                    o.layer = 3
                    while GPIO.input(25):
                        sleep(2)#Check every 2 seconds to see what gear the car is in if reverse remain in loop else a different gear is selected so turn of the backup camera.
            
            
class LiveDataWorker(QThread):#Used to communicate with the cars Engine Control Module Using Serial Bluetooth connection is /mnt to ELM327 Microcontroler to read and write to , ISO9141 can bus.
    #Initilize the rpm, speed, coolant temperature and engine load signals to emit to the gui whenever a value change is detected in cars engine control module. #int is used to save space vs double
    change_rpm = pyqtSignal(int)
    change_speed = pyqtSignal(int)#casting to int.
    change_coolant = pyqtSignal(int)
    change_load = pyqtSignal(int)
    
    def run(self):
        connection = obd.Async(fast=False)#Calling the Async Constructor from the obd/Async.py class.
        
        #Create 4 callback functions. When a new values is detected the correspondingg function is called which adds units to the value and emits the signal from this worker thread to the main thread to the gui.
        def new_speed(s):#define callback function
            if not s.is_null():#if the value is null meaning bad data was recieved do nothing and wait till next valid data is recieved.
                speed = int(s.value.magnitude/1.609)#universal speed is in kilometers so we convert to mp/h for usa. Can be changed to kilometers for universal or other cars.
                self.change_speed.emit(speed)#emit the updated value to be written to the gui.
        
        def new_rpm(r):
            if not r.is_null():
                rpm = int(r.value.magnitude)#remove "revelutions_per_minute" from string and emit signal for faster processing.
                self.change_rpm.emit(rpm)
                
        def new_coolant(c):#update gui with value of coolant temperature
            if not c.is_null():
                cool = int(c.value.magnitude)
                self.change_coolant.emit(cool)
                
        def new_load(l):#update gui with value of engine load.
            if not l.is_null():
                self.change_load.emit(l.value)

            
        connection.watch(obd.commands.RPM, callback=new_rpm)#create watch function from /obd/asynchrounous.py
        connection.watch(obd.commands.SPEED, callback=new_speed)#create a watch function for speed, when new value is detected call the callback function.
        connection.watch(obd.commands.COOLANT_TEMP, callback=new_coolant)
        connection.watch(obd.commands.ENGINE_LOAD, callback=new_load)
        connection.start()#Start the connection.


class TestDataWorker(QThread):#Used for testing and debugging. Simply emits fake values to the gui to ensure each component is responding as expected.
    change_valuemine = pyqtSignal(int)
    def run(self):
        cntt=0;
        while cntt < 150:
            cntt+=1
            time.sleep(3)
            self.change_valuemine.emit(cntt)
            

class BsmDataWorker(QThread):#Used for recieving the data from the microcontorller over serial gpio.
    carRight = pyqtSignal(int)#signal for car on right
    carLeft = pyqtSignal(int)#signal for car on left
    def run(self):#thread execution starts here.
        
        GPIO.setwarnings(False)#Used for debugging.
        GPIO.setmode(GPIO.BCM)#BCM Formatting used to create a standard.

        GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)#both lines are set to 0V using a pulldown resistor and set to listen mode.
        GPIO.setup(26, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        while True:
            #sig=0;#This might cause a flicker but i dont think so.
            if GPIO.input(16):#if car is detected on the right.
                #print("car right")
                sig=1#set the signal to 1 and emit it.
                self.carRight.emit(sig)#emit the signal to the gui
            else:
                sig=0#no car detected.
                self.carRight.emit(sig)#emit 0 signal
            if GPIO.input(26):#same as above but for left blind spot.
                #print("car left")
                sig=1
                self.carLeft.emit(sig)
            else:
                sig=0
                self.carLeft.emit(sig)
            sleep(0.01)#Controls how fast backup cam responds to reverse signal
        


class Ui_MainWindow(object):#This code was mostly auto generated by dragging and droping gui components on the screen.
#some of the layouts, window size, name, object names were modified by hand.
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.showMaximized()
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.centralWidget)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.LaneAssistLeft = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.LaneAssistLeft.setFont(font)
        self.LaneAssistLeft.setObjectName("Left Blindspot")
        self.verticalLayout.addWidget(self.LaneAssistLeft)
        self.BlindSpotLeft = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.BlindSpotLeft.setFont(font)
        self.BlindSpotLeft.setObjectName(" ")
        self.verticalLayout.addWidget(self.BlindSpotLeft)
        self.Redline = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.Redline.setFont(font)
        self.Redline.setObjectName("Redline")
        self.verticalLayout.addWidget(self.Redline)
        self.RpmLcd = QtWidgets.QLCDNumber(self.centralWidget)
        self.RpmLcd.setObjectName("RpmLcd")
        self.verticalLayout.addWidget(self.RpmLcd)
        self.RpmLabel = QtWidgets.QLabel(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RpmLabel.sizePolicy().hasHeightForWidth())
        self.RpmLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.RpmLabel.setFont(font)
        self.RpmLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.RpmLabel.setObjectName("RpmLabel")
        self.verticalLayout.addWidget(self.RpmLabel)
        self.RuntimeLabel = QtWidgets.QLabel(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.RuntimeLabel.sizePolicy().hasHeightForWidth())
        self.RuntimeLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.RuntimeLabel.setFont(font)
        self.RuntimeLabel.setObjectName("RuntimeLabel")
        self.verticalLayout.addWidget(self.RuntimeLabel)
        self.horizontalLayout.addLayout(self.verticalLayout)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.LaneAssistRight = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.LaneAssistRight.setFont(font)
        self.LaneAssistRight.setObjectName("Right Blindspot")
        self.verticalLayout_3.addWidget(self.LaneAssistRight)
        self.BlindSpotRight = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.BlindSpotRight.setFont(font)
        self.BlindSpotRight.setObjectName(" ")
        self.verticalLayout_3.addWidget(self.BlindSpotRight)
        self.BackupCamera = QtWidgets.QPushButton(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.BackupCamera.setFont(font)
        self.BackupCamera.setObjectName("BackupCamera")
        self.verticalLayout_3.addWidget(self.BackupCamera)
        self.SpeedLcd = QtWidgets.QLCDNumber(self.centralWidget)
        self.SpeedLcd.setObjectName("SpeedLcd")
        self.verticalLayout_3.addWidget(self.SpeedLcd)
        self.MphLabel = QtWidgets.QLabel(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MphLabel.sizePolicy().hasHeightForWidth())
        self.MphLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.MphLabel.setFont(font)
        self.MphLabel.setAlignment(QtCore.Qt.AlignCenter)
        self.MphLabel.setObjectName("MphLabel")
        self.verticalLayout_3.addWidget(self.MphLabel)
        self.OilCoolantTemperatureLabel = QtWidgets.QLabel(self.centralWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.OilCoolantTemperatureLabel.sizePolicy().hasHeightForWidth())
        self.OilCoolantTemperatureLabel.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.OilCoolantTemperatureLabel.setFont(font)
        self.OilCoolantTemperatureLabel.setObjectName("OilCoolantTemperatureLabel")
        self.verticalLayout_3.addWidget(self.OilCoolantTemperatureLabel)
        self.horizontalLayout.addLayout(self.verticalLayout_3)
        self.verticalLayout_2.addLayout(self.horizontalLayout)
        self.FuelBar = QtWidgets.QProgressBar(self.centralWidget)
        font = QtGui.QFont()
        font.setPointSize(12)
        self.FuelBar.setFont(font)
        self.FuelBar.setObjectName("FuelBar")
        self.verticalLayout_2.addWidget(self.FuelBar)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)#allow signals and slots to be passed to main window.
        
    def setLcdVal(self, val2):#function to set the rpm value in gui.
        self.RpmLcd.display(val2)
        
    def setLcdValTwo(self, val3):#function to set the speed value in gui.
        self.SpeedLcd.display(val3)
        
    def setProgressVal(self, val):#function to set the engine load value in gui.
        self.FuelBar.setValue(val)
        
    def setLeftBsm(self, valLeft):#function to set the left BlindSpot value in gui.
        if valLeft == 1:
            self.BlindSpotLeft.setStyleSheet('QPushButton {background-color: #FF0000; border: none}')#there is a car make button red
        else:
            self.BlindSpotLeft.setStyleSheet('QPushButton {background-color: #FFFF00; border: none}')#no car turn it back to yellow
            
    def setRightBsm(self, valRight):#function to set the right BlindSpot value in gui.
        if valRight == 1:
            self.BlindSpotLeft.setStyleSheet('QPushButton {background-color: #FF0000; border: none}')#there is a car make button red
        else:
            self.BlindSpotRight.setStyleSheet('QPushButton {background-color: #FFFF00; border: none}')#no car turn it back to yellow.
        
    def setLabelVal(self, val4):#function to set the coolant temperature with proper formatting removing the decimals.
        self.OilCoolantTemperatureLabel.setText("Oil-Coolant Temperature: {}".format(val4))
        #self.BlindSpotLeft.setStyleSheet("background-color : yellow")
        #self.BlindSpotLeft.setStyleSheet('QPushButton {background-color: #A3C1DA; border: none}')
         

    def retranslateUi(self, MainWindow):#This function is constantly called becuase the ui is in fullscreen mode which is a translation to the regular dimensions of the app.
        _translate = QtCore.QCoreApplication.translate#This funtion is used to proportionally scale all ui components in the gui to proper size.
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.LaneAssistLeft.setText(_translate("MainWindow", "Left Lane Assist"))
        self.BlindSpotLeft.setText(_translate("MainWindow", "Left Blind Spot"))
        self.Redline.setText(_translate("MainWindow", "Redline"))
        self.RpmLabel.setText(_translate("MainWindow", "X1000 RPM"))
        self.RuntimeLabel.setText(_translate("MainWindow", "Runtime"))
        self.LaneAssistRight.setText(_translate("MainWindow", "Right Lane Assist"))
        self.BlindSpotRight.setText(_translate("MainWindow", "Right Blind Spot"))
        self.BackupCamera.setText(_translate("MainWindow", "Backup Camera"))
        self.MphLabel.setText(_translate("MainWindow", "MPH"))
        self.OilCoolantTemperatureLabel.setText(_translate("MainWindow", "Oil-Coolant Temperature"))

if __name__ == "__main__":#Program execution starts here. This is the first code that is run in the entire project.
    import sys
    app = QtWidgets.QApplication(sys.argv)#instantiate the app.
    MainWindow = QtWidgets.QMainWindow()#Instantiate a windowsl.
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)#instantiate the ui and cast to the main window.
    MainWindow.show()#show the main window to the gui.
        
    ThreadLiveData = LiveDataWorker()#Instantiate the live data thread.
    ThreadLiveData.change_rpm.connect(ui.setLcdVal)#connect the thread to the signal and slots to pass data back and fourth.
    ThreadLiveData.change_speed.connect(ui.setLcdValTwo)
    ThreadLiveData.change_coolant.connect(ui.setLabelVal)
    ThreadLiveData.change_load.connect(ui.setProgressVal)
    ThreadLiveData.start()#Start the thread.
    
    #SampleDataWorker
    #UNCOMMENT THIS TO TEST THE BUTTON COLORING
    #ThreadSampleData = SampleDataWorker()
    #ThreadSampleData.change_valuemine.connect(ui.setLabelVal)
    #ThreadSampleData.start()
    
    #BSMWorker
    ThreadBsmData = BsmDataWorker()#Instantiate the blind spot monitoring thread.
    ThreadBsmData.carRight.connect(ui.setRightBsm)#connect carright to bool signal in thread
    ThreadBsmData.carLeft.connect(ui.setLeftBsm)#connect carKeft to bool signal in thread
    ThreadBsmData.start()#Start the thread.
    
    Thread1 = BackupCameraWorker()#Instantiate the  backup camera thread.
    Thread1.start()
    
    ret = app.exec_()#executes the gui listens for input.
    #quit the threads here.
    connection.stop()#gracefylly shutdown the obd connection.
    Thread1.exit()#functions to stop the thread these are autocalled when application is force shut down by removing key from ignition.
    ThreadBsmData.exit()
    ThreadLiveData.exit()
    sys.exit(ret)#exit the program and emith the return status to the terminal.

