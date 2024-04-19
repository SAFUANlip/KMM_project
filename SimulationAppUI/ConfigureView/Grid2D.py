from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSimpleTextItem, QGraphicsRectItem
from PyQt5.QtCore import QRectF, Qt, QLineF, QPointF
from PyQt5.QtGui import QTransform, QFont, QPen, QPixmap, QColor

from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QApplication
import sys

class GraphicsPlotNocksTube(QGraphicsItem):

    def __init__(self, parent=None):
        super(GraphicsPlotNocksTube, self).__init__(parent)
        self.m_nocks = list()
        self.m_NocksFont = QFont()
        self.m_nockPen = QPen()
        self.m_boundRect = QRectF()

    def updateNocks(self, nocks):
        for nock in self.m_nocks:
            nock.setParentItem(None)
        self.m_nocks.clear()
        self.m_nocks = nocks
        #for nock in nocks:
            #self.m_nocks.append(nock)
            #nocks.remove(nock)
        if len(self.m_nocks) == 0:
            self.m_boundRect = QRectF()
            return

        item = nocks[0]
        nockPos = item.pos()
        self.m_boundRect = item.boundingRect().translated(nockPos.x(), nockPos.y())
        item.setParentItem(self)
        item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
        item.setFont(self.m_NocksFont)
        item.setPen(self.m_nockPen)
        for i in range(1, len(nocks)):
            item = nocks[i]
            nockPos = item.pos()
            self.m_boundRect|= item.boundingRect().translated(nockPos.x(), nockPos.y())
            item.setParentItem(self)
            item.setFlag(QGraphicsItem.ItemIgnoresTransformations, True)
            item.setFont(self.m_NocksFont)
            item.setPen(self.m_nockPen)

        self.update()

    def boundingRect(self):
        return self.m_boundRect

    def paint(self, painter, option, widget):
        pass

    def font(self):
        return self.m_NocksFont


class GridAxisGuideLines:
    def __init__(self):
        self.lines = list()
        self.showLines = True


class Graphics2DPlotGrid(QGraphicsItem):


    def __init__(self, parent=None):
        super(Graphics2DPlotGrid, self).__init__(parent)
        self.m_mainPen = QPen()
        self.m_secondaryPen = QPen()
        self.m_rect = QRectF()

        self.m_mainPen.setCosmetic(True)
        self.m_secondaryPen.setCosmetic(True)
        self.m_mainPen.setColor(QColor(50, 137, 48))
        self.m_secondaryPen.setColor(QColor(50, 137, 48))

        self.abscissMainLines = GridAxisGuideLines()
        self.abscissSecondaryLines = GridAxisGuideLines()
        self.ordinateMainLines = GridAxisGuideLines()
        self.ordinateSecondaryLines = GridAxisGuideLines()

    def boundingRect(self):
        return self.m_rect

    def rect(self):
        return self.m_rect

    def setRange(self, axisNumber, min, max):
        if axisNumber == 0:
            self.m_rect.setX(min)
            self.m_rect.setWidth(max - min)
        else:
            self.m_rect.setY(min)
            self.m_rect.setHeight(max - min)

    def setMainGrid(self, axisNumber, zero, step):
        pass

    def setSecondaryGrid(self, axisNumber, zero, step):
        pass

    def setMainGridPen(self, pen):
        self.m_mainPen = pen
        self.m_mainPen.setCosmetic(True)

    def setSecondaryGridPen(self, pen):
        self.m_secondaryPen = pen
        self.m_secondaryPen.setCosmetic(True)

    def mainGridPen(self):
        return self.m_mainPen

    def secondaryGridPen(self):
        return self.m_secondaryPen

    def paint(self, painter, option, widget):
        self.paintAxeGuidLines(self.abscissSecondaryLines, painter, self.m_secondaryPen)
        self.paintAxeGuidLines(self.abscissMainLines, painter, self.m_mainPen)
        self.paintAxeGuidLines(self.ordinateSecondaryLines, painter, self.m_secondaryPen)
        self.paintAxeGuidLines(self.ordinateMainLines, painter, self.m_mainPen)
        painter.setPen(self.m_mainPen)
        painter.drawRect(self.m_rect)

    def paintAxeGuidLines(self, axe, painter, linePen):
        if(axe.showLines):
            painter.setPen(linePen)
            painter.drawLines(axe.lines)


class Range:
    def __init__(self):
        self.min = 0
        self.max = 0

class AxisGuideLines:
    def __init__(self):
        self.baseValue = 0.0
        self.step = 0.0


class GraphicsPlotItem(QGraphicsItem):

    def __init__(self, parent=None):
        super(GraphicsPlotItem, self).__init__(parent)
        self.gridItem = Graphics2DPlotGrid(self)
        self.abscissText = QGraphicsSimpleTextItem(self)
        self.ordinateText = QGraphicsSimpleTextItem(self)
        self.ordinaateFont = QFont()
        self.abscissFont = QFont()

        self.rect = QRectF()
        self.m_sceneDataRect = QRectF()
        self.ordinateMainNocks = GraphicsPlotNocksTube(self)
        self.abscissMainNocks = GraphicsPlotNocksTube(self)
        self.ordinateSecondaryNocks = GraphicsPlotNocksTube(self)
        self.abscissSecondaryNocks = GraphicsPlotNocksTube(self)

        self.ordinateText.setRotation(-90)

        self.gridItem.setFlag(QGraphicsItem.ItemClipsChildrenToShape)
        self.gridItem.setRange(0, 1, 2)
        self.gridItem.setRange(1, 1, 2)
        
        self.ordinateSecondaryNocks.hide()
        self.abscissSecondaryNocks.hide()

        self.abscissMainLines = AxisGuideLines()
        self.abscissSecondaryLines = AxisGuideLines()
        self.ordinateMainLines = AxisGuideLines()
        self.ordinateSecondaryLines = AxisGuideLines()

        self.abscissRange = Range()
        self.ordinateRange = Range()
        self.isAutoGrid = True
        self.isAutoSecondaryGrid = True

    def compose(self):
        self.abscissText.setFont(self.abscissFont)

        # Composite by height
        dataHeight = self.rect.height() - 2*(self.abscissText.boundingRect().height())
        if dataHeight < 0.5*self.rect.height():
            pass
            #TODO decrease font size

        # Compose by width
        dataWidth = self.rect.width()-2*self.ordinateText.boundingRect().height()
        if dataWidth< 0.5*self.rect.width():
            pass
            #TODO decrease font size

        self.ordinateMainNocks.setPos(-self.ordinateMainNocks.boundingRect().width(), -5*self.ordinateMainNocks.font().pointSizeF()/4.0)
        self.m_sceneDataRect.setRect(self.rect.width()-dataWidth, 0, dataWidth, dataHeight)

        self.abscissText.setPos( (dataWidth - self.abscissText.boundingRect().width()) / 2.0 + self.m_sceneDataRect.y(), self.rect.bottom() - self.abscissText.boundingRect().height())
        self.ordinateText.setPos(0, (dataHeight - self.ordinateText.boundingRect().width())/2.0 + self.m_sceneDataRect.y())
        self.calculateAndSetTransForm()
        self.update()

    def calculateAndSetTransForm(self):
        scaleX = self.m_sceneDataRect.width() / self.gridItem.rect().width()
        scaleY = self.m_sceneDataRect.height() / self.gridItem.rect().height()
        transform = QTransform.fromTranslate( - self.gridItem.rect().x()*scaleX + self.m_sceneDataRect.x(), - self.gridItem.rect().y()*scaleY + self.m_sceneDataRect.y() );
        transform.scale(scaleX, -scaleY);
        self.gridItem.setTransform(transform)
        self.ordinateMainNocks.setTransform(transform)
        #self.ordinateSecondaryNocks.setTransform(transform)
        self.abscissMainNocks.setTransform(transform)
        #self.abscissSecondaryNocks.setTransform(transform)

    def autoSetRange(self):
        pass
    def autoSetGrid(self):
        pass

    def calculteOrdLine(self, guides, lines, nocksList):
        if guides.step == 0:
            return
        nocksList.clear()
        k = int((self.ordinateRange.min - guides.baseValue) // guides.step)
        minValue = k * guides.step + guides.baseValue
        count = int((self.ordinateRange.max - minValue) // guides.step) + 1

        # TODO додумать что делать, если направляющая всего одна
        if count > 0:
            lines.clear()
            for i in range(count):
                guidCoordinate = minValue + i * guides.step
                lines.append(QLineF(self.abscissRange.max, guidCoordinate, self.abscissRange.min, guidCoordinate))
                nocksList.append(QGraphicsSimpleTextItem(str(guidCoordinate)))
                nocksList[-1].setPos(self.abscissRange.min, guidCoordinate)
        else:
            lines.clear()

    def calculateOrdinateGrid(self):
        nocksList = list()

        self.calculteOrdLine(self.ordinateMainLines, self.gridItem.ordinateMainLines.lines, nocksList)
        self.ordinateMainNocks.updateNocks(nocksList)
        nocksList = list()
        self.calculteOrdLine(self.ordinateSecondaryLines, self.gridItem.ordinateSecondaryLines.lines, nocksList)
        self.ordinateSecondaryNocks.updateNocks(nocksList)

    def calculteAbsLine(self, guides, lines, nocksList):
        if guides.step == 0:
            return
        nocksList.clear()
        k = int((self.abscissRange.min - guides.baseValue) / guides.step)
        minValue = k * guides.step + guides.baseValue
        count = int((self.abscissRange.max - minValue) / guides.step) + 1

        # TODO додумать что делать, если направляющая всего одна
        if count > 0:
            lines.clear()
            for i in range(count):
                guidCoordinate = minValue + i * guides.step
                lines.append(QLineF( guidCoordinate, self.ordinateRange.max, guidCoordinate, self.ordinateRange.min))
                nocksList.append(QGraphicsSimpleTextItem(str(guidCoordinate)))
                nocksList[-1].setPos(guidCoordinate, self.ordinateRange.min)
        else:
            lines.clear()

    def calculateAbscissGrid(self):
        nocksList = list()
        self.calculteAbsLine(self.abscissMainLines, self.gridItem.abscissMainLines.lines, nocksList)
        self.abscissMainNocks.updateNocks(nocksList)
        nocksList = list()
        self.calculteAbsLine(self.abscissSecondaryLines, self.gridItem.abscissSecondaryLines.lines, nocksList)
        self.abscissSecondaryNocks.updateNocks(nocksList)

    def boundingRect(self):
        return self.rect

    def paint(self, painter, option, widget):
        pass

    def setAxisText(self, axisNumber, text):
        useText = self.abscissText
        if axisNumber == 1:
            useText = self.ordinateText
        useText.setText(text)
        self.compose()

    def axisText(self, axisNumber):
        useText = self.abscissText
        if axisNumber == 1:
            useText = self.ordinateText
        return useText.text();

    def setAxisTextFont(self, axisNumber, font):
        if axisNumber == 0:
            self.abscissFont = font
        else:
            self.ordinaateFont = font
        self.compose()

    def axisTextFont(self, axisNumber):
        if axisNumber == 0:
            return self.abscissFont
        return self.ordinaateFont

    def setRect(self, rect):
        self.prepareGeometryChange()
        self.rect = rect
        self.compose()

    def autoGridSetValue(self, guidesMain, guidesSecondary, min, max):
        if self.isAutoGrid:
            guidesMain.baseValue = min
            guidesMain.step = (max-min)/10.0

        if self.isAutoSecondaryGrid or self.isAutoGrid:
            guidesSecondary.baseValue = guidesMain.baseValue
            guidesSecondary.step = guidesMain.step/2.0

    def setAxisRange(self, axisNumber, min, max):
        if min >= max:
            return 
        self.gridItem.setRange(axisNumber, min, max)

        if axisNumber == 0:
            self.abscissRange.min = min
            self.abscissRange.max = max
            self.autoGridSetValue(self.abscissMainLines, self.abscissSecondaryLines, min, max)
            
        else:
            self.ordinateRange.min = min
            self.ordinateRange.max = max
            self.autoGridSetValue(self.ordinateMainLines, self.ordinateSecondaryLines, min, max)
            
        self.calculateAbscissGrid()
        self.calculateOrdinateGrid()
        self.compose()

    def setAbscissaRange(self, min, max):
        self.setAxisRange(0, min, max)

    def setOrdinateRange(self, min, max):
        self.setAxisRange(1, min, max)

    def setAxisAutoRange(self, axisNumber, isAuto):
        pass

    def axisRange(self, axisNumber):
        if axisNumber == 0:
            return self.abscissRange.min, self.abscissRange.max
        else: 
            return self.ordinateRange.min, self.ordinateRange.max

    def axisAutoRange(self, axisNumber):
        pass
    def setAutoGrid(self, value):
        pass
    def isAutoGrid(self):
        pass

    def setMainGridLinePen(self, pen):
        self.gridItem.setMainGridPen(pen)
    
    def mainGridLinePen(self):
        return self.gridItem.mainGridPen()

    def setSecondaryGridLinePen(self, pen):
        self.gridItem.setSecondaryGridPen(pen)

    def secondayGridLinePen(self):
        return self.gridItem.secondaryGridPen()

    def setMainGridLine(self, axisNumber, baseValue, step):
        pass
    def setSecondaryLineAuto(self, isAuto):
        pass
    def setSecondaryGridLine(self, axisNumber, step):
        pass


class TestView(QGraphicsView):
    def __init__(self, parent=None):
        super(TestView, self).__init__(parent)
    def resizeEvent(self, event):
        self.fitInView(self.sceneRect(), Qt.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    graphicsView = TestView()
    scene = QGraphicsScene()
    graphicsView.setScene(scene)
    graphicsView.setGeometry(0,0, 1150, 1050)
    graphicsView.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    graphicsView.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    graphicsView.setTransformationAnchor(QGraphicsView.AnchorViewCenter)
    graphicsView.setResizeAnchor(QGraphicsView.AnchorViewCenter)
    graphicsView.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
    graphicsView.show()

    plot = GraphicsPlotItem()
    scene.addItem(plot)
    plot.setRect(QRectF(0, 0, 1000, 1000))
    plot.setAxisText(0, "x, м")
    plot.setAxisText(1, "y, м")
    plot.setAbscissaRange(-100000, 100000)
    plot.setOrdinateRange(-200000, 200000)
    scene.setSceneRect(plot.boundingRect())
    item = QGraphicsRectItem(-20, -20, 40, 40)
    scene.addItem(item)
    item.setPos(plot.gridItem.mapToScene(QPointF(60000, 40000)))
    print(plot.gridItem.mapFromScene(item.scenePos()))
    sys.exit(app.exec_())