# The MIT License
#
# Copyright (c) 2011 Wyss Institute at Harvard University
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# http://www.opensource.org/licenses/mit-license.php

import os
from PyQt4.QtGui import *
from PyQt4.QtCore import *#SIGNAL, QString, Qt
from cadnano import app
from .helpwindow import HelpWindow

class HelpSystem():
    #This class is responsible for establishing connections between the main
    #caDNAno window and the help window.
    def __init__(self, docwin, firstuse):         
        app().documentControllers.add(self)
        self.win = docwin
        #self.win points to the class instance of the caDNAno mainwindow
        self.helpWin = HelpWindow(docwin)
        #self.helpWin points to the class instance of the help window
        self.createConnections()
        self.cmHelp = None
        #self.cmHelp stores the path of the help document that is associated
        #with an item in the main window that the user right clicks on
        self.win.leftToolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.win.rightToolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        #setContextMenuPolicy enables the use of context menu signals.  Note
        #that this is not the same as connecting the signal to a function
        self.win.sliceGraphicsView.mouseMoveEvent = self.sliceViewMouseMove
        self.win.pathGraphicsView.mouseMoveEvent = self.pathViewMouseMove
        #Lines 48 and 49 capture mouse move events from the QGraphicsWindows in
        #the main window so that the graphics items that users are dealing with
        #frequently can be monitored.
        
        if firstuse == True:
            self.win.helplabel.setText(QString("It appears as though this is your first time using CaDNAno 2, would you like to view a tutorial?"))
            #firstuse a boolean variable that is established right when the
            #application is started.  If the application was started for the
            #first time, the message will be displayed.
        else:
            #If the application is not being used for the first time, help
            #prompting widgets are hidden.
            self.win.ignoreButton.hide()
            self.win.showHelpButton.hide()
            self.win.helplabel.hide()
        
    def pathViewMouseMove(self, event):
        #This function displays the class name of a graphic item in the path 
        #view for potential item use tracking in the future.
        print self.win.pathGraphicsView.itemAt(event.pos()).__class__.__name__

        
    def sliceViewMouseMove(self, event):        
        #This function displays the class name of a graphic item in the slice 
        #view for potential item use tracking in the future.
        print self.win.sliceGraphicsView.itemAt(event.pos()).__class__.__name__

    def standardHelpClicked(self):
        #This function triggers the display of standard help and is triggered 
        #clicking the "Show Standard Help" QAction menu item
        self.helpWin.tabWidget.setCurrentIndex(0)
        self.helpWin.textBrowser.setSource(QUrl.fromLocalFile(\
            "ui/help/helpdocs/administrative/StandardHelpHome.html"))
        self.helpWin.show()
        
    def networkHelpClicked(self):
        self.helpWin.textBrowser.setSource(QUrl.fromLocalFile("ui/help/helpdocs/administrative/StandardHelpHome.html"))
        if os.system("ping www.wiki-site.com -n 1") == 1:
            #If the site hosting help documents cannot respond to the ping 
            #request then the help window will still appear but it will 
            #notify the user of connection problems.
            self.helpWin.webView.load(QUrl("ui/help/helpdocs/ConnectionError.html"))
            self.helpWin.webView.show() 
            self.helpWin.tabWidget.setCurrentIndex(1)
            self.helpWin.show()
        else:
            #If the site does respond to the ping request then the appropriate
            #page is accessed.
            self.helpWin.webView.load(QUrl("http://www.wiki-site.com/index.php/Cadnano2helpREC17"))
            self.helpWin.webView.show() 
            self.helpWin.tabWidget.setCurrentIndex(1)            
            self.helpWin.show()
        
    def ignoreClicked(self):
        #This function hides the help prompting widgets when the ignore button
        #is clicked.
        self.win.ignoreButton.hide()
        self.win.showHelpButton.hide()
        self.win.helplabel.hide()
        
    def showHelpClicked(self):
        self.helpWin.show()
        
    def rightToolBarContextMenu(self, event):
        if self.win.rightToolBar.actionAt(event) != None:
            #This script builds a context menu from scratch
            cm = QMenu()
            self.actionHelp = QAction(cm)
            self.actionHelp.triggered.connect(self.quickHelp)
            self.actionHelp.setText("Help")
            cm.addAction(self.actionHelp)      
            cm.exec_(self.win.rightToolBar.mapToGlobal(event))
        
    def leftToolBarContextMenu(self, event):
        if self.win.leftToolBar.actionAt(event) != None:    
            #This script builds a context menu from scratch    
            cm = QMenu()
            self.actionHelp = QAction(cm)
            self.actionHelp.triggered.connect(self.quickHelp)
            self.actionHelp.setText("Help")
            cm.addAction(self.actionHelp)        
            cm.exec_(self.win.leftToolBar.mapToGlobal(event))
            
    def quickHelp(self):
        #This function is triggered when the context menu item is selected
        self.helpWin.tabWidget.setCurrentIndex(0)
        self.helpWin.textBrowser.setSource(QUrl.fromLocalFile(\
            "ui/help/helpdocs/content/" + self.cmHelp))
        self.helpWin.show()

    #The following definitions are used to change the quick help file based on
    #hovering events.
    def actionSliceEditHover(self):
        self.cmHelp = "SliceEdit.html"
    def actionSliceFirstLastHover(self):
        self.cmHelp = "SliceFirstLast.html"
    def actionSliceMoveHover(self):
        self.cmHelp = "SliceMove.html"
    def actionSliceRenumHover(self):
        self.cmHelp = "SliceRenum.html"
    def actionSliceDeleteLastHover(self):
        self.cmHelp = "SliceDelete.html"
    def actionPathEditHover(self):
        self.cmHelp = "PathEdit.html"
    def actionPathMoveHover(self):
        self.cmHelp = "PathMove.html"
    def actionPathBreakHover(self):
        self.cmHelp = "PathBreak.html"
    def actionPathEraseHover(self):
        self.cmHelp = "PathErase.html"
    def actionPathForceHover(self):
        self.cmHelp = "PathForce.html"
    def actionPathInsertionHover(self):
        self.cmHelp = "PathInsertion.html"
    def actionPathSkipHover(self):
        self.cmHelp = "PathSkip.html"    
    def actionAutoStapleHover(self):
        self.cmHelp = "PathStaple.html"

    def createConnections(self):
        """
        Organizational method to collect signal/slot connectors.
        """
        self.win.actionStandard_Help.triggered.connect(\
            self.standardHelpClicked)
        self.win.actionNetwork_Help.triggered.connect(\
            self.networkHelpClicked)
        self.win.ignoreButton.pressed.connect(\
            self.ignoreClicked)
        self.win.showHelpButton.pressed.connect(\
            self.showHelpClicked)
        self.win.actionDeleteLast.hovered.connect(\
            self.actionSliceDeleteLastHover)
        self.win.actionSliceSelect.hovered.connect(\
            self.actionSliceEditHover)
        self.win.actionSliceMove.hovered.connect(\
            self.actionSliceMoveHover)
        self.win.actionSliceFirst.hovered.connect(\
            self.actionSliceFirstLastHover)
        self.win.actionSliceLast.hovered.connect(\
            self.actionSliceFirstLastHover)
        self.win.actionRenumber.hovered.connect(\
            self.actionSliceRenumHover)
        self.win.leftToolBar.customContextMenuRequested.connect(\
            self.leftToolBarContextMenu)
        self.win.rightToolBar.customContextMenuRequested.connect(\
            self.rightToolBarContextMenu)
        self.win.actionPathSelect.hovered.connect(\
            self.actionPathEditHover)
        self.win.actionPathMove.hovered.connect(\
            self.actionPathMoveHover)
        self.win.actionPathBreak.hovered.connect(\
            self.actionPathBreakHover)

        self.win.actionPathForce.hovered.connect(\
            self.actionPathForceHover)
        self.win.actionPathInsertion.hovered.connect(\
            self.actionPathInsertionHover)
        self.win.actionPathSkip.hovered.connect(\
            self.actionPathSkipHover)
        self.win.actionAutoStaple.hovered.connect(\
            self.actionAutoStapleHover)


