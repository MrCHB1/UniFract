# Made with the posibilitiy of PyQt5 and Python

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import numpy as np
from multiprocessing import Pool
from struct import pack, unpack
from numba import jit, jitclass
from numba import int32
import sys
from decimal import *
from mpmath import mp

DefaultCenterX = -0.647011
DefaultCenterY = 0.0
DefaultScale = 0.007

ZoomInFactor = 0.8
ZoomOutFactor = 1 / ZoomInFactor
ScrollStep = 20

PowerRe = "2.0"
PowerIm = "0.0"

fractalType = "Mandelbrot"

customFormula = "c*c"

MaxIterations = "30"

BailoutRadius = "2"

StartRe = "0.0"
StartIm = "0.0"

PrecisionVal = "Single"

StartingP = complex(float(StartRe), float(StartIm))


IsInverse = False

col1R = "1.0"
col1G = "0.0"
col1B = "0.5"

######################################
# This is what does most of the work #
######################################

class RenderThread(QThread):
    global PowerRe
    global PowerIm
    global fractalType
    global customFormula
    global MaxIterations
    global BailoutRadius
    global StartingP
    global StartRe
    global StartIm
    global IsInverse
    global col1R
    global col1G
    global col1B
    global PrecisionVal

    ColormapSize = 512

    renderedImage = pyqtSignal(QImage, np.float128)

    def __init__(self, parent=None):
        QThread.__init__(self)

        self.mutex = QMutex()
        self.condition = QWaitCondition()
        self.centerX = 0.0
        self.centerY = 0.0
        self.scaleFactor = 0.0
        self.devicePixelRatio = 0.0
        self.resultSize = QSize()
        self.colormap = []

        self.customFormula = customFormula

        self.restart = False
        self.abort = False

        for i in range(RenderThread.ColormapSize):
            self.colormap.append(self.rgbFromWaveLength(380.0 + (i * 400.0 / RenderThread.ColormapSize)))

    def __del__(self):
        self.mutex.lock()
        self.abort = True
        self.condition.wakeOne()
        self.mutex.unlock()

        self.wait()

    def render(self, centerX, centerY, scaleFactor, resultSize, devicePixelRatio):
        locker = QMutexLocker(self.mutex)

        self.centerX = centerX
        self.centerY = centerY
        self.scaleFactor = scaleFactor
        self.devicePixelRatio = devicePixelRatio
        self.resultSize = resultSize

        if not self.isRunning():
            self.start(QThread.LowPriority)
        else:
            self.restart = True
            self.condition.wakeOne()

    def run(self):
        while self.isRunning():
            self.mutex.lock()
            devicePixelRatio = self.devicePixelRatio
            resultSize = self.resultSize * devicePixelRatio
            requestedScaleFactor = self.scaleFactor
            scaleFactor = requestedScaleFactor / devicePixelRatio
            centerX = self.centerX
            centerY = self.centerY
            self.mutex.unlock()

            halfWidth = resultSize.width() // 2
            halfHeight = resultSize.height() // 2
            image = QImage(resultSize, QImage.Format_RGB32)
            image.setDevicePixelRatio(devicePixelRatio)

            NumPasses = 8
            curpass = 0

            while curpass < NumPasses:
                Limit = int(BailoutRadius)
                allBlack = True

                for y in range(-halfHeight, halfHeight):
                    if self.restart:
                        break
                    if self.abort:
                        return

                    ay = (centerY + (y * scaleFactor))
                    ayy = 1j * (centerY + (y * scaleFactor))

                    for x in range(-halfWidth, halfWidth):
                        c0 = centerX + (x * scaleFactor) + ayy
                        c = complex(Decimal(StartRe), Decimal(StartIm))

                        ax = centerX + (x * scaleFactor)
                        a1 = ax
                        b1 = ay

                        if PrecisionVal == "Single":
                            c = np.complex64(c)
                            c0 = np.complex64(c0)
                        elif PrecisionVal == "Double":
                            c = np.complex128(c)
                            c0 = np.complex128(c0)
                        elif PrecisionVal == "Triple":
                            c = np.clongdouble(c)
                            c0 = np.clongdouble(c0)
                        elif PrecisionVal == "Quadruple":
                            c = np.complex256(c)
                            c0 = np.complex256(c0)
                        
                        numIterations = 0

                        while numIterations < int(MaxIterations):
                            numIterations += 1
                            if fractalType == "Mandelbrot":
                                c = pow(c, float(PowerRe)) + c0
                                if abs(c) > Limit:
                                    break
                            elif fractalType == "Fast Mandelbrot":
                                a2 = (a1*a1)-(b1*b1)+ax
                                b2 = (a1*b1*2)+ay
                                if (a2*a2)+(b2*b2) > Limit * 2:
                                    break
                                numIterations += 1
                                a1 = (a2*a2)-(b2*b2)+ax
                                b1 = (a2*b2*2)+ay
                                if (a1*a1)+(b1*b1) > Limit * 2:
                                    break
                            elif fractalType == "Tricorn / Mandelbar":
                                if not IsInverse:
                                    c = np.conj(pow(c, float(PowerRe))) + c0
                                else:
                                    c = np.conj(pow(c, float(PowerRe))) + 1/c0
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Burning Ship":
                                if not IsInverse:
                                    c = pow((abs(c.real) + abs(c.imag) * 1j), float(PowerRe)) + c0
                                else:
                                    c = pow((abs(c.real) + abs(c.imag) * 1j), float(PowerRe)) + 1/c0
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "MandelShip":
                                if not IsInverse:
                                    c = pow(c, float(PowerRe)) + c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow((abs(c.real) + abs(c.imag) * 1j), float(PowerRe)) + c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow(c, float(PowerRe)) + c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow(c, float(PowerRe)) + c0
                                    if abs(c) >= Limit:
                                        break
                                else:
                                    c = pow(c, float(PowerRe)) + 1/c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow((abs(c.real) + abs(c.imag) * 1j), float(PowerRe)) + 1/c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow(c, float(PowerRe)) + 1/c0
                                    if abs(c) >= Limit:
                                        break
                                    numIterations += 1
                                    c = pow(c, float(PowerRe)) + 1/c0
                                    if abs(c) >= Limit:
                                        break
                            elif fractalType == "Perpendicular Mandelbrot":
                                c = pow((abs(c.real) - c.imag * 1j), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Perpendicular Burning Ship":
                                c = pow((c.real + abs(c.imag) * 1j), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Perpendicular Celtic":
                                a2 = abs((a1*a1)-(b1*b1)) + ax
                                b2 = abs(a1)*b1*-2+ay
                                if (a2*a2)+(b2*b2) > Limit * 2:
                                    break
                                numIterations += 1
                                a1 = abs((a2*a2)-(b2*b2)) + ax
                                b1 = abs(a2)*b2*-2+ay
                                if (a1*a1)+(b1*b1) > Limit * 2:
                                    break
                            elif fractalType == "Perpendicular Buffalo":
                                a1sqr = a1*a1
                                b1sqr = b1*b1
                                a2sqr = a2*a2
                                b2sqr = b2*b2

                                a2 = abs(a1sqr - b1sqr) + ax
                                b2 = a1 * abs(b1) * -2 + ay
                                if (a1*a1)+(b1*b1) > Limit * 2:
                                    break
                                numIterations += 1
                                a1 = abs(a2sqr - b2sqr) + ax
                                b1 = a2 * abs(b2) * -2 + ay
                                if (a2*a2)+(b2*b2) > Limit * 2:
                                    break
                            elif fractalType == "Mandelbrot Heart":
                                c = pow((abs(c.real)+c.imag*1j), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Buffalo":
                                c = pow(((abs(c.real)+abs(c.imag)*1j)+c0/2), float(PowerRe))+pow(c0/2+(abs(c.real)+abs(c.imag)*1j), float(PowerRe))
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Celtic Mandelbrot":
                                c = pow(((abs(c.real)+c.imag*1j)+c0/2), float(PowerRe))+pow(c0/2+(abs(c.real)+c.imag*1j), float(PowerRe))
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Celtic Mandelbar":
                                c = pow(((abs(c.real)-c.imag*1j)+c0/2), float(PowerRe))+pow(c0/2+(abs(c.real)-c.imag*1j), float(PowerRe))
                                if abs(c) >= Limit:
                                    break
                            elif fractalType == "Celtic Heart":
                                a2 = abs((a1*a1)-(b1*b1))+ax
                                b2 = abs(a1)*b1*2+ay
                                if (a2*a2)+(b2*b2) > Limit * 2:
                                    break
                                numIterations += 1
                                a1 = abs((a2*a2)-(b2*b2))+ax
                                b1 = abs(a2)*b2*2+ay
                                if (a1*a1)+(b1*b1) > Limit * 2:
                                    break
                            elif fractalType == "Ultra Hybrid":
                                # Mandelbrot
                                c = pow(c, float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                                numIterations += 1
                                # Burning Ship
                                c = pow(abs(c.real) + 1j*abs(c.imag), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                                numIterations += 1
                                # Tricorn / Mandelbar
                                c = pow(np.conj(c), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                                numIterations += 1
                                # Perpendicular Mandelbrot
                                c = pow((abs(c.real) - c.imag * 1j), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                                # Perpendicular Burning Ship
                                numIterations += 1
                                c = pow((c.real + abs(c.imag) * 1j), float(PowerRe)) + c0
                                if abs(c) >= Limit:
                                    break
                                numIterations += 1
                            elif fractalType == "Psuedo Mandelbrot":
                                # Basically the mandelbrot except using irrational power values can result in a different mandelbrot.
                                c = c0-pow(c, float(PowerRe))
                                if abs(c) >= Limit:
                                    break

                            # Does not work, need a suggestion from contributors.
                            
                            elif fractalType == "Custom":
                                def custom(c, c0, Limit):
                                    c = c+c0
                                    if abs(c) >= Limit:
                                        return 0
                                    return c
                                custom(c*c, c0, Limit)

                        if numIterations < int(MaxIterations):
                            image.setPixel(x + halfWidth, y + halfHeight,
                                           self.colormap[numIterations % RenderThread.ColormapSize])
                            allBlack = False
                        else:
                            image.setPixel(x + halfWidth, y + halfHeight, qRgb(0, 0, 0))

                if allBlack and curpass == 0:
                    curpass = 4
                else:
                    if not self.restart:
                        self.renderedImage.emit(image, np.float128(requestedScaleFactor))
                    curpass += 1

            self.mutex.lock()
            if not self.restart:
                self.condition.wait(self.mutex)
            self.restart = False
            self.mutex.unlock()

    def rgbFromWaveLength(self, wave):
        global col1R
        global col1G
        global col1B

        r = 0.0
        g = 0.0
        b = 0.0

        if wave >= 380.0 and wave <= 440.0:
            r = -1.0 * (wave - 440.0) / (440.0 - 380.0)
            b = 1.0
        elif wave >= 440.0 and wave <= 490.0:
            g = (wave - 440.0) / (490.0 - 440.0)
            b = 1.0
        elif wave >= 490.0 and wave <= 510.0:
            g = 1.0
            b = -1.0 * (wave - 510.0) / (510.0 - 490.0)
        elif wave >= 510.0 and wave <= 580.0:
            r = (wave - 510.0) / (580.0 - 510.0)
            g = 1.0
        elif wave >= 580.0 and wave <= 645.0:
            r = 1.0
            g = -1.0 * (wave - 645.0) / (645.0 - 580.0)
        elif wave >= 645.0 and wave <= 780.0:
            r = 1.0

        s = 1.0
        if wave > 700.0:
            s = 0.3 + 0.7 * (780.0 - wave) / (780.0 - 700.0)
        elif wave < 420.0:
            s = 0.3 + 0.7 * (wave - 380.0) / (420.0 - 380.0)

        r = pow(r * s, 0.8)
        g = pow(g * s, 0.8)
        b = pow(b * s, 0.8)

        return qRgb(int(r*255), int(g*255), int(b*255))

class MandelbrotWidget(QWidget):
    def __init__(self, parent=None):
        super(MandelbrotWidget, self).__init__(parent)

        self.thread = RenderThread()
        self.pixmap = QPixmap()
        self.pixmapOffset = QPoint()
        self.lastDragPos = QPoint()

        self.centerX = DefaultCenterX
        self.centerY = DefaultCenterY
        self.pixmapScale = DefaultScale
        self.curScale = DefaultScale

        self.thread.renderedImage.connect(self.updatePixmap)

        self.setCursor(Qt.CrossCursor)
        self.resize(550, 429)
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), Qt.black)

        if self.pixmap.isNull():
            painter.setPen(Qt.white)
            painter.drawText(self.rect(), Qt.AlignCenter,
                    "UniFract is getting ready!")
            return

        if self.curScale == self.pixmapScale:
            painter.drawPixmap(self.pixmapOffset, self.pixmap)
        else:
            previewPixmap = self.pixmap.devicePixelRatioF() == QPoint(1, 0)
            if previewPixmap:
                previewPixmap = self.pixmap
            else:
                previewPixmap = self.pixmap.scaled(self.pixmap.size() / self.pixmap.devicePixelRatioF(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            scaleFactor = self.pixmapScale / self.curScale
            newWidth = int(previewPixmap.width() * scaleFactor)
            newHeight = int(previewPixmap.height() * scaleFactor)
            newX = self.pixmapOffset.x() + (previewPixmap.width() - newWidth) / 2
            newY = self.pixmapOffset.y() + (previewPixmap.height() - newHeight) / 2

            painter.save()
            painter.translate(newX, newY)
            painter.scale(scaleFactor, scaleFactor)

            exposed, _ = painter.transform().inverted()
            exposed = exposed.mapRect(self.rect()).adjusted(-1, -1, 1, 1)
            exposed = QRectF(exposed)
            painter.drawPixmap(exposed, previewPixmap, exposed)
            painter.restore()

    def resizeEvent(self, event:QResizeEvent):
        super(MandelbrotWidget, self).resizeEvent(event)
        self.thread.render(self.centerX, self.centerY, self.curScale, self.size(), self.devicePixelRatioF())

    def keyPressEvent(self, event:QKeyEvent):
        if event.key() == Qt.Key_Plus:
            self.zoom(ZoomInFactor)
        elif event.key() == Qt.Key_Minus:
            self.zoom(ZoomOutFactor)
        elif event.key() == Qt.Key_Left:
            self.scroll(-ScrollStep, 0)
        elif event.key() == Qt.Key_Right:
            self.scroll(+ScrollStep, 0)
        elif event.key() == Qt.Key_Down:
            self.scroll(0, -ScrollStep)
        elif event.key() == Qt.Key_Up:
            self.scroll(0, +ScrollStep)
        else:
            super(MandelbrotWidget, self).keyPressEvent(event)

    def wheelEvent(self, event:QWheelEvent):
        numDegrees = event.angleDelta().y() / 8
        numSteps = numDegrees / 15.0

        self.zoom(pow(ZoomInFactor, numSteps))

    def mousePressEvent(self, event:QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.lastDragPos = QPoint(event.pos())

    def mouseMoveEvent(self, event:QMouseEvent):
        if event.buttons() & Qt.LeftButton:
            self.pixmapOffset += event.pos() - self.lastDragPos
            self.lastDragPos = QPoint(event.pos())
            self.update()

    def mouseReleaseEvent(self, event:QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.pixmapOffset += event.pos() - self.lastDragPos
            self.lastDragPos = QPoint()

            pixmapSize = self.pixmap.size() / self.pixmap.devicePixelRatioF()
            deltaX = (self.width() - pixmapSize.width()) / 2 - self.pixmapOffset.x()
            deltaY = (self.height() - pixmapSize.height()) / 2 - self.pixmapOffset.y()
            self.scroll(deltaX, deltaY)

    def updatePixmap(self, image:QImage, scaleFactor:float):
        if not self.lastDragPos.isNull():
            return

        self.pixmap = QPixmap.fromImage(image)
        self.pixmapOffset = QPoint()
        self.lastDragPos = QPoint()
        self.pixmapScale = scaleFactor
        self.update()

    def zoom(self, zoomFactor):
        self.curScale *= zoomFactor
        self.update()
        self.thread.render(self.centerX, self.centerY, self.curScale, self.size(), self.devicePixelRatioF())

    def scroll(self, deltaX, deltaY):
        self.centerX += deltaX * self.curScale
        self.centerY += deltaY * self.curScale
        self.update()
        self.thread.render(self.centerX, self.centerY, self.curScale, self.size(), self.devicePixelRatioF())

class Window(QMainWindow):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)
        global fractal

        self.centerX = DefaultCenterX
        self.centerY = DefaultCenterY
        self.pixmapScale = DefaultScale
        self.curScale = DefaultScale

        self.setWindowTitle("UniFract")

        fractal = MandelbrotWidget(self)
        fractal.move(5, 60)

        self.initUI()

        self.resize(self.width(), self.height() - 90)

        copyrightLabel = QLabel(self)
        copyrightLabel.move(5, self.height()- 28)
        copyrightLabel.setGeometry(copyrightLabel.x(), copyrightLabel.y(), copyrightLabel.width() + self.width(), copyrightLabel.height())
        copyrightLabel.setText("Copyright © UniFract 2020. All rights reserved.")
        copyrightLabel.setStyleSheet("""
            QLabel {
                color: lightGray;
            }
        """)

        self.show()

        self.setMaximumSize(self.width(), self.height())
        self.setMinimumSize(self.width(), self.height())

    def initUI(self):
        global PowerReal
        global PowerImag
        global fractal
        global PowerRe
        global PowerIm
        global FractalType
        global fractalType
        global customFormula
        global formula
        global MaxIterations
        global iterations
        global BailoutRadius
        global bailoutRadius
        global StartingPoint
        global StartReal
        global StartImag
        global IsInverse
        global inverse
        global Precision
        global precision
        global exportBtn

        global col1R
        global col1G
        global col1B

        global R1
        global G1
        global B1

        # Labels

        # Tabs

        tabs = QTabWidget(self)
        tab1 = QWidget(self)
        tab2 = QWidget(self)
        tab3 = QWidget(self)
        
        tabs.addTab(tab1, "Fractal")
        tabs.addTab(tab2, "Rendering")
        tabs.addTab(tab3, "Gradient")
        tabs.resize(280, 430)

        tab1.layout = QFormLayout(self)
        tab2.layout = QFormLayout(self)
        tab3.layout = QFormLayout(self)

        tabs.move(563, 60)

        # Tab 1 (Fractal)

        FractalTypes = ["Mandelbrot", "Fast Mandelbrot", "Tricorn / Mandelbar", "Burning Ship", "Celtic Mandelbrot", "Celtic Mandelbar", "Mandelship", "Buffalo", "Perpendicular Mandelbrot", "Perpendicular Burning Ship", "Perpendicular Celtic", "Mandelbrot Heart", "Celtic Heart", "Ultra Hybrid", "Psuedo Mandelbrot", "Burning Ship Mandelbar", "Custom"]

        FractalType = QComboBox(self)
        FractalType.addItems(FractalTypes)

        FractalType.currentTextChanged.connect(self.changeFractal)

        PowerReal = QLineEdit(self)
        PowerReal.setText("2")
        PowerReal.setValidator(QDoubleValidator())
        PowerReal.setPlaceholderText("Real")
        PowerImag = QLineEdit(self)
        PowerImag.setText("0")
        PowerImag.setValidator(QDoubleValidator())
        PowerImag.setPlaceholderText("Imag")

        PowerReal.textChanged.connect(self.changePower)
        PowerImag.textChanged.connect(self.changePower)

        PowerRow = QHBoxLayout()
        PowerRow.addWidget(PowerReal)
        PowerRow.addWidget(PowerImag)

        CenterReal = QLineEdit(self)
        CenterReal.setText(str(DefaultCenterX))
        CenterReal.setValidator(QDoubleValidator(0.0, 100.0, 100))
        CenterReal.setPlaceholderText("Real")
        CenterImag = QLineEdit(self)
        CenterImag.setText(str(DefaultCenterY))
        CenterImag.setValidator(QDoubleValidator(0.0, 100.0, 100))
        CenterImag.setPlaceholderText("Imag")

        Center = QHBoxLayout()
        Center.addWidget(CenterReal)
        Center.addWidget(CenterImag)

        Zoom = QLineEdit(self)
        Zoom.setText(str(DefaultScale))

        formula = QLineEdit(self)

        formula.setEnabled(False)

        if formula.isEnabled():
            customFormula = formula.text()
            formula.setText(customFormula)
            formula.textChanged.connect(self.customFractal)

        StartingPoint = QHBoxLayout(self)

        StartReal = QLineEdit(self)
        StartReal.setText("0.0")
        StartReal.setPlaceholderText("Real")
        StartReal.setValidator(QDoubleValidator())
        StartImag = QLineEdit(self)
        StartImag.setText("0.0")
        StartImag.setPlaceholderText("Imag")
        StartImag.setValidator(QDoubleValidator())
        StartingPoint.addWidget(StartReal)
        StartingPoint.addWidget(StartImag)

        StartReal.textChanged.connect(self.changeStartingPoint)
        StartImag.textChanged.connect(self.changeStartingPoint)

        inverse = QCheckBox(self)
        inverse.toggled.connect(self.setInverse)

        tab1.layout.addRow("Fractal", FractalType)
        tab1.layout.addRow("Power", PowerRow)
        tab1.layout.addRow("Center", Center)
        tab1.layout.addRow("Starting Point", StartingPoint)
        tab1.layout.addRow("Zoom", Zoom)
        tab1.layout.addRow("Custom Formula", formula)
        tab1.layout.addRow("Inversed", inverse)

        tab1.setLayout(tab1.layout)

        # Tab 2 (Rendering)

        iterations = QLineEdit(self)
        iterations.setText(MaxIterations)
        iterations.textChanged.connect(self.changeIterations)
        iterations.setValidator(QIntValidator())

        bailoutRadius = QLineEdit(self)
        bailoutRadius.setText(BailoutRadius)
        bailoutRadius.textChanged.connect(self.changeBailout)
        bailoutRadius.setValidator(QIntValidator())

        precisionTypes = ["Single", "Double", "Triple", "Quadruple"]

        precision = QComboBox(self)
        precision.addItems(precisionTypes)

        precision.currentTextChanged.connect(self.changePrecision)

        tab2.layout.addRow("Iterations", iterations)
        tab2.layout.addRow("Bailout Radius", bailoutRadius)
        tab2.layout.addRow("Float Precision", precision)

        tab2.setLayout(tab2.layout)

        # Tab 3 (Gradient)

        Color1 = QHBoxLayout(self)
        
        R1 = QLineEdit(self)
        R1.setValidator(QDoubleValidator(0.0, 1.0, 1))
        R1.setText(str(col1R))

        R1.textChanged.connect(self.editGradient)

        G1 = QLineEdit(self)
        G1.setText(str(col1G))

        G1.textChanged.connect(self.editGradient)

        B1 = QLineEdit(self)
        B1.setText(str(col1B))

        B1.textChanged.connect(self.editGradient)

        Color1.addWidget(R1)
        Color1.addWidget(G1)
        Color1.addWidget(B1)

        tab3.layout.addRow("Color 1", Color1)

        tab3.setLayout(tab3.layout)

        # Menus

        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu("&File")
        editMenu = mainMenu.addMenu("&Edit")
        viewMenu = mainMenu.addMenu("&View")
        aboutMenu = mainMenu.addMenu("&About")

        # Sub-Menus
        
        exportMenu = QMenu('&Export', self)
        
        exportNorm = QAction('&Export in current Aspect', self)
        export4k = QAction('&Export in 4k', self)
        export4k.setEnabled(False)

        exportMenu.addAction(exportNorm)
        exportMenu.addAction(export4k)

        exportNorm.triggered.connect(self.export)

        fileMenu.addMenu(exportMenu)

        # Tools
        
        openConfig = QPushButton(self)
        openConfig.move(5, 25)
        openConfig.setText("Open Config")

        saveConfig = QPushButton(self)
        saveConfig.move(openConfig.width() + 5, 25)
        saveConfig.setText("Save Config")

        exportBtn = QPushButton(self)
        exportBtn.move(saveConfig.width()+openConfig.width() + 15, 25)
        exportBtn.setText("Export Image")

        exportBtn.clicked.connect(self.export)

        gradientBtn = QPushButton(self)
        gradientBtn.move(saveConfig.width()+openConfig.width()+exportBtn.width() + 25, 25)
        gradientBtn.setText("Gradient")
        gradientBtn.clicked.connect(self.editGradient)

        InititalBtn = QPushButton(self)
        InititalBtn.move(gradientBtn.x() + 112, gradientBtn.y())
        InititalBtn.setText("Initial State")
        InititalBtn.clicked.connect(self.resetEverything)

        self.resize(850, 600)

    def editGradient(self):
        global col1R
        global col1G
        global col1B
        global R1
        global G1
        global B1

        col1R = R1.text()
        col1G = G1.text()
        col1B = B1.text()

    def changePower(self):
        global Power
        global PowerReal
        global PowerImag
        global PowerRe
        global PowerIm

        if PowerReal.text() != "-" or PowerImag.text() != "" or PowerImag.text() != "-" or PowerImag.text() != "":
            PowerRe = PowerReal.text()
            PowerIm = PowerImag.text()

    def changeFractal(self):
        global fractalType
        global FractalType
        global formula
        global customFormula
        global PowerReal
        global PowerImag

        if FractalType.currentText() == "Custom":
            formula.setEnabled(True)
            formula.setText(str(customFormula))
        elif FractalType.currentText() != "Perpendicular Celtic" and FractalType.currentText() != "Perpendicular Buffalo" and FractalType.currentText() != "Celtic Heart":
            PowerReal.setEnabled(True)
            PowerImag.setEnabled(True)
        else:
            formula.setEnabled(False)
            PowerReal.setEnabled(False)
            PowerImag.setEnabled(False)

        fractalType = FractalType.currentText()

    def changePrecision(self):
        global precision
        global PrecisionVal
        global fractal

        PrecisionVal = precision.currentText()
        fractal.update()

    def customFractal(self):
        global formula
        global customFormula
        global FractalType
        global fractalType

        if formula.text() != "":
            customFormula = formula.text()
            print(customFormula)

    def changeIterations(self):
        global MaxIterations
        global iterations

        if iterations.text() != "":
            MaxIterations = iterations.text()

    def changeBailout(self):
        global BailoutRadius
        global bailoutRadius

        BailoutRadius = bailoutRadius.text()

    def changeStartingPoint(self):
        global StartReal
        global StartImag

        global StartRe
        global StartIm

        if StartReal.text() != "-" or StartReal.text() != "" or StartImag.text() != "-" or StartImag.text() != "":
            StartRe = StartReal.text()
            StartIm = StartImag.text()

    def setInverse(self):
        global IsInverse
        global inverse

        if inverse.isChecked():
            IsInverse = True
        else:
            IsInverse = False

    def export(self):
        global exportBtn
        global fractal

        pixmap = QPixmap(fractal.size())
        fractal.render(pixmap)
        pixmap.save("Fractal.png")

    def resetEverything(self):
        global FractalType
        global fractalType
        global StartReal
        global StartImag
        global PowerReal
        global PowerImag

        fractalType = "Mandelbrot"
        FractalType.setCurrentText("Mandelbrot")
        StartReal.setText("0.0")
        StartImag.setText("0.0")
        PowerReal.setText("2.0")
        PowerImag.setText("0.0")
        RenderThread.centerX = 0.0
        RenderThread.centerY = 0.0

def main():
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    win = Window()
    return app.exec_()

if __name__ == '__main__':
    main()
