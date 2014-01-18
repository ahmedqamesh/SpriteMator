#--------------------------------------------------
# Name:             Canvas
# Purpose:          
#
# Author:           Rafael Vasco
# Date:             30/03/13
# License:          
#--------------------------------------------------
from PyQt4.QtCore import Qt, pyqtSignal, QPoint
from PyQt4.QtGui import QPainter, QSizePolicy, QColor, QMouseEvent

from src.display import  Display
from src.canvas_overlay import CanvasOverlay

from src import tools, inks
from src.toolbox import ToolBox
from src.tools import Tool

    
class Canvas(Display):
    
    
    surfaceChanged = pyqtSignal()
    
    colorPicked = pyqtSignal(QColor, QMouseEvent)
    toolStarted = pyqtSignal(Tool)
    toolEnded = pyqtSignal(Tool)

    def __init__(self, parent=None):

        super(Canvas, self).__init__(parent)
        
        
        self._tools = {}
        self._inks = {}
        
        
        self._sprite = None
        self._drawingSurface = None
        self._drawingSurfacePixelData = None
        self._currentTool = None
        self._primaryInk = None
        self._secondaryInk = None
        self._primaryColor = None
        self._secondaryColor = None
        self._pixelSize = 0
        self._drawGrid = True
        
        
        self._absoluteMousePosition = QPoint()
        self._spriteMousePosition = QPoint()
        self._lastButtonPressed = None
        
        # ======================================
        
        self._loadTools()
        self._loadInks()
        
        self._initializeCanvasState()
        
        self._overlaySurface = CanvasOverlay(self)
        self._overlaySurface.turnOff()

        self._toolBox = ToolBox(self)
        self._toolBox.setVisible(False)
        self._initializeToolBox()

        self.setMouseTracking(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(320)
        self.setMinimumHeight(240)

        self.setAttribute(Qt.WA_NoSystemBackground)
    
    
    def primaryColor(self):
        
        return self._primaryColor
    
    def setPrimaryColor(self, color):
        
        self._primaryColor = color
        
    def secondaryColor(self):
        
        return self._secondaryColor
    
    def setSecondaryColor(self, color):
        
        self._secondaryColor = color
    
    def primaryInk(self):
        
        return self._primaryInk
    
    def setPrimaryInk(self, inkName):
        self._primaryInk = self.ink(inkName)
        
    def secondaryInk(self):
        
        return self._secondaryInk
    
    def setSecondaryInk(self, inkName):
        
        self._secondaryInk = self.ink(inkName)
    
    def setCurrentTool(self, name):
        
        self._currentTool = self.tool(name)
        
    def selectToolSlot(self, slot):
        
        self._toolBox.selectToolSlot(slot)
    
    def tool(self, name):
        
        return self._tools[name]
    
    def ink(self, name):
        
        return self._inks[name]
    
    def spriteLoaded(self):
        
        return self._sprite is not None
    
    # ----- PUBLIC API -------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    def setSprite(self, sprite):
        
        if self.spriteLoaded():
            self.unloadSprite()
        
        self._toolBox.setVisible(True)
        
        self._sprite = sprite

        super().setObjectSize(sprite.currentAnimation().frameWidth(),
                              sprite.currentAnimation().frameHeight())
        

        self.refresh()
        
        self.setCursor(Qt.BlankCursor)

    def unloadSprite(self):
        
        self._toolBox.setVisible(False)
        
        self.resetView()
        self.setObjectSize(0, 0)
        
        self._sprite = None
        self._drawingSurface = None
        
        self.update()
        self.setCursor(Qt.ArrowCursor)

    def refresh(self):
        
        self._updateDrawingSurface()

    def clear(self, index=None):

        if not self.spriteLoaded():
            return
        
        animation = self._sprite.currentAnimation()

        if index is None:
            surface = self._drawingSurface
        else:
            surface = animation.currentFrame().surfaceAt(index).image()

        painter = QPainter()
        
        painter.begin(surface)

        painter.setCompositionMode(QPainter.CompositionMode_Clear)
        painter.fillRect(0, 0, surface.width(), surface.height(), Qt.white)

        painter.end()
        
        self.surfaceChanged.emit()
        
        self.update()

    def resize(self, width, height, index=None):

        pass

    def scale(self, sx, sy, index):

        pass


    # ----- EVENTS -----------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------

    def onDrawObject(self, event, painter):

        if not self.spriteLoaded():
            return

        layers = self._sprite.currentAnimation().currentFrame().surfaces()

        for layer in layers:
            painter.drawImage(0, 0, layer.image())
        
        if self._drawGrid and self._zoom >= 16.0:
            
            
            w = self._drawingSurface.width()
            h = self._drawingSurface.height()
            painter.setPen(QColor(0,0,0,80))
            
            for x in range(0, w):
                #xz = x * self._pixelSize
                painter.drawLine(x, 0, x, h)
                
            for y in range(0, h):
                #yz = y * self._pixelSize
                painter.drawLine(0, y, w, y)  
                    
        
    def resizeEvent(self, e):
        
        self._overlaySurface.resize(self.size())
        self._toolBox.resize(self.width(), self._toolBox.height())
        
    def onDelFrameButtonClicked(self):

        self.removeFrame()

    def mousePressEvent(self, e):

        super().mousePressEvent(e)
        
        if not self.spriteLoaded() or self.isPanning():
            
            if self.isPanning():
                
                self._overlaySurface.turnOff()
            
            return
        
        self._updateMouseState(e)
        
        tool = self._currentTool
        
        tool._processMousePress(self, e)
        
        if tool.isActive():
            
            self.toolStarted.emit(tool)
            
            painter = QPainter()
            
            painter.begin(self._drawingSurface)
            
            
            
            tool.blit(painter, self)
    
            painter.end()

        self.update()

    def mouseMoveEvent(self, e):
        
        super().mouseMoveEvent(e)

        if not self.spriteLoaded():
            return
        
        
        self._updateMouseState(e)
        
        
        tool = self._currentTool
        
        tool._processMouseMove(self, e)
        
        if not self._panning:
        
            if tool.isActive():
                
                painter = QPainter()
            
                painter.begin(self._drawingSurface)
        
                tool.blit(painter, self)
        
                painter.end()
        
        
        self.update()

    def mouseReleaseEvent(self, e):
        
        if not self.spriteLoaded():
            return
        
        tool = self._currentTool        
        
        self._updateMouseState(e)
        
        tool._processMouseRelease(self, e)
        
        self.update()
        
        self.toolEnded.emit(tool)
        
        super().mouseReleaseEvent(e)
        
        if not self.isPanning():
            
            self.setCursor(Qt.BlankCursor)
            self._overlaySurface.turnOn()
    
    def wheelEvent(self, e):
        
        if not self.spriteLoaded():
            return
        
        super().wheelEvent(e)
        
    def enterEvent(self, e):
        
        if not self.spriteLoaded():
            return
        
        self.setCursor(Qt.BlankCursor)
        self._overlaySurface.turnOn()
       
    def leaveEvent(self, e):
        
        if not self.spriteLoaded():
            return
        
        self.setCursor(Qt.ArrowCursor)
        
        self._overlaySurface.turnOff()
    
    def _onToolBoxMouseEntered(self):
        
        if not self.spriteLoaded():
            return
        
        self._overlaySurface.turnOff()
    
    def _onToolBoxMouseLeft(self):
         
        if not self.spriteLoaded():
            return
         
        self._overlaySurface.turnOn()
        
    def _onToolBoxToolChanged(self, toolName):
        
        self.setCurrentTool(toolName)
    
    def _onToolBoxPrimaryInkChanged(self, inkName):
        
        self.setPrimaryInk(inkName)
    
    def _onToolBoxSecondaryInkChanged(self, inkName):
        
        self.setSecondaryInk(inkName)
    
    # ---- PRIVATE METHODS ---------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------------------------
    
    def _loadTools(self):

        # Default Tools
        
        self._tools['Pen'] = tools.Pen()
        self._tools['Picker'] = tools.Picker()
        self._tools['Filler'] = tools.Filler()
    
    def _loadInks(self):
        
        # Default Inks
        
        self._inks['Solid'] = inks.Solid()
        self._inks['Eraser'] = inks.Eraser()
    
    def _initializeCanvasState(self):
        
        self._pixelSize = 1
        self._primaryColor = QColor('black')
        self._secondaryColor = QColor('white')
        self._currentTool = self.tool('Pen')
        self._primaryInk = self.ink('Solid')
        self._secondaryInk = self.ink('Eraser')
        
    def _initializeToolBox(self):
        
        self._toolBox.mouseEntered.connect(self._onToolBoxMouseEntered)
        self._toolBox.mouseLeft.connect(self._onToolBoxMouseLeft)
        
        self._toolBox.registerTool(self.tool('Pen'), isDefault=True)
        self._toolBox.registerTool(self.tool('Picker'))
        self._toolBox.registerTool(self.tool('Filler'))
        
        self._toolBox.registerInk(self.ink('Solid'), slot=0)
        self._toolBox.registerInk(self.ink('Eraser'), slot=1)
        
        self._toolBox.toolChanged.connect(self._onToolBoxToolChanged)
        self._toolBox.primaryInkChanged.connect(self._onToolBoxPrimaryInkChanged)
        self._toolBox.secondaryInkChanged.connect(self._onToolBoxSecondaryInkChanged)
        
    def _updateMouseState(self, e):
        
        if e.type() == 2  and e.button() is not None:
            
            self._lastButtonPressed = e.button()
            
        
        objectMousePosition = super().objectMousePos()

        objectMousePosition.setX(round(objectMousePosition.x(), 2))
        objectMousePosition.setY(round(objectMousePosition.y(), 2))
        
        
        self._spriteMousePosition.setX(objectMousePosition.x())
        self._spriteMousePosition.setY(objectMousePosition.y())

    def _updateDrawingSurface(self):

        if not self.spriteLoaded():
            return
        
        self._drawingSurface = self._sprite.currentAnimation().currentFrame().currentSurface().image()
        
        self._drawingSurfacePixelData = self._drawingSurface.bits()
        
        self._drawingSurfacePixelData.setsize(self._drawingSurface.byteCount())
        
        self.update()
        
