from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
import ui_helpwindow
import os
import getpass

global user
user = str(getpass.getuser())

class HelpWindow(QMainWindow, ui_helpwindow.Ui_MainWindow):
    #This class represents the help window, and includes all methods and
    #functions associated with the help window.
    def __init__(self, docwin, parent=None):
        super(HelpWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle(QString('Help'))
        self.page = QWebPage()        
        self.triggerOnce = True     
        #self.triggerOnce is used to counteract the behavior of the QAction 
        #triggered() signal, specifically that the signal is emitted twice 
        #even though the QAction is only clicked once.
        self.findFile = None        
        #self.findFile serves as a reference to the help document that is 
        #experiencing a text search. 
        self.stdBFList = []
        #self.stdBFList is used to store a special history list to be used
        #for the back/forward buttons on the standard window.
        self.stdBFIndex = -1
        #self.stdBFIndex is used to keep track of which document in 
        #self.BFlist is being viewed.
        self.buttonNav = False
        #self.buttonNav is a boolean variable that prevents back/forward
        #button navigation from affecting the history tracking mechanisms.
        self.connect(self.treeWidget,\
                    SIGNAL("itemActivated(QTreeWidgetItem*, int)"),\
                    self.stdDisplayContent)
        #This signal is emitted from the treeWidget in the standard window
        #whenever an item in the tree is selected.
        self.connect(self.webView, SIGNAL("loadFinished(bool)"),\
                    self.onlHistoryTracker)
        #This signal connection ensures that the online history tracker will
        #update the online history whenever a new page is loaded.
        self.connect(self.textBrowser, SIGNAL("sourceChanged(QUrl)"),\
                    self.stdHistoryTracker)
        #This signal connection ensures that the standard history tracker will
        #update the standard history whenever the text browser's source is 
        #changed.
        self.connect(self.stdFindEdit, SIGNAL("textChanged(QString)"),\
                    self.stdFindString)
        #This signal is emitted whenever the standard find edit text field is 
        #altered to ensure that text highlighting will occur automatically.
        self.connect(self.onlFindEdit, SIGNAL("textChanged(QString)"),\
                    self.onlFindString)
        #This signal is emitted whenever the online find edit text field is 
        #altered to ensure that text highlighting will occur automatically.
        with open("C:/Users/" + user + "/.cadnano/onlhistory.txt", 'r')\
            as history:
            fileLines = history.readlines()
        self.onlHistoryDict = eval(fileLines[0].rstrip('\n'))
        self.onlHistoryList = eval(fileLines[1])
        with open("C:/Users/" + user + "/.cadnano/stdhistory.txt", 'r')\
            as history:
            fileLines = history.readlines()
        self.stdHistoryDict = eval(fileLines[0].rstrip('\n'))
        self.stdHistoryList = eval(fileLines[1])
        #These file reading procedures initialize the history dictionaries as 
        #well as the history lists for online and standard help respectively
        #which are all stored externally in text files.
        self.ctrlHeld = False
        #self.ctrlHeld is a boolean variable that keeps track of whether the
        #ctrl button is currently being held or not
        self.stdFindEdit.hide()
        self.stdFindLabel.hide()        
        self.onlFindEdit.hide()
        self.onlFindLabel.hide()
        #All of the "find text" widgets are initially hidden
    """
    Functions for Online and Standard Help
    """
    def on_actionClose_triggered(self):
        #This function closes the help window once the close menu item is 
        #triggered.
        if self.triggerOnce == True:
            self.close()
        self.triggerOnce = not(self.triggerOnce)
        
    def keyReleaseEvent(self, event):
        if event.key() == 16777249:
            self.ctrlHeld = False
            #This key release event is designed to alert the program that the
            #ctrl button is no longer being held.
            
    def keyPressEvent(self, event):
        if event.key() == 16777249:
            self.ctrlHeld = True
        if event.key() == 16777220 and self.stdSearchEdit.hasFocus() == True:
            self.stdExecuteSearch()
        if event.key() == 70 and self.ctrlHeld == True:
            #The event key 70 corresponds to the "F" key.  When it is pressed,
            #the find text line edit for the current help window is revealed 
            #in the GUI
            if self.tabWidget.currentIndex() == 0:
                self.stdFindEdit.show()
                self.stdFindLabel.show()
                self.stdFindEdit.setFocus()
            if self.tabWidget.currentIndex() == 1:
                self.onlFindEdit.show()
                self.onlFindLabel.show()
                self.onlFindEdit.setFocus()
        if event.key() == 16777216:
            #This event handler captures the ESC key.  If it is pressed, and 
            #the find line edit widget has focus, it is hidden
            if self.tabWidget.currentIndex() == 0 and \
            self.stdFindEdit.hasFocus() == True:
                self.stdFindEdit.hide()
                self.stdFindLabel.hide()
            if self.tabWidget.currentIndex() == 1 and \
            self.onlFindEdit.hasFocus() == True:
                self.onlFindEdit.hide()
                self.onlFindLabel.hide()
    """
    Online Help Functions
    """
    def on_onlHomeButton_pressed(self):
        #This function is used to load the main page of the help website.
        self.webView.load(QUrl("http://www.wiki-site.com/"+\
                               "index.php/Cadnano2helpREC17"))
        self.webView.show()
        
    def on_onlBackButton_pressed(self):
        #This function returns the user to the previously viewed page.
        self.webView.back()

    def on_onlForwardButton_pressed(self):
        #This function sends the user closer to the most recently viewed page.
        self.webView.forward()
    
    def on_actionHome_triggered(self):
        #This function is executed when the "Home" menu item is clicked on.
        #The main help page is loaded upon a mouse click.
        if self.triggerOnce == True:
            self.webView.load(QUrl("http://www.wiki-site.com/"+\
                                   "index.php/Cadnano2helpREC17"))
            self.webView.show()
        self.triggerOnce = not(self.triggerOnce)

    def on_actionView_Online_History_triggered(self):
        #This function displays the online history dialog box when the
        #corresponding menu item is clicked.
        if self.triggerOnce == True:
            histdialog = OnlHistoryDialog(self, self)
            histdialog.show()
        self.triggerOnce = not(self.triggerOnce)
   
    def on_actionClear_Online_History_triggered(self):
        #This function resets the standard history dictionary and list, and
        #also rewrites the text file that stores external copies of the
        #dictionary and list.
        self.onlHistoryDict = {}
        self.onlHistoryList = []
        with open("C:/Users/" + user + "/.cadnano/onlhistory.txt", 'w')\
            as history:
            history.write(repr({}) + '\n' + repr([]))
         
    def onlFindString(self):
        #This function uses built in methods to highlight text in the current
        #webpage.  The behavior of the findText function can be customized
        #by including additional "Find Flags" arguments.
        searchString = QString(self.onlFindEdit.text())
        self.webView.findText(searchString)
        
    def onlHistoryTracker(self):
        pageTitle = str(self.webView.page().mainFrame().title())
        pageUrl = str(self.webView.history().currentItem().url())
        pageUrl = pageUrl.lstrip("PyQt4.QtCore.QUrl(u'")
        pageUrl = pageUrl.rstrip("')")
        #The page Url must be stipped of all mark up text.  For some reason,
        #setScheme does not work in this scenario.
        if pageTitle != '':
            #This if statement is used to prevent blank pages from appearing 
            #in the history/
            self.onlHistoryDict.update({pageTitle:pageUrl})
            try:
                self.onlHistoryList.remove(pageTitle)
                #This try/exception handler is necessary for preventing 
                #duplicate page titles from appearing in the history list
            except:
                pass
            self.onlHistoryList.append(pageTitle)
        with open("C:/Users/" + user + "/.cadnano/onlhistory.txt", 'w')\
            as history:
            history.write(repr(self.onlHistoryDict) + '\n'\
                          + repr(self.onlHistoryList))
            #This file IO process maintains the history data in the
            #external online history file.
    """
    Standard Help Function
    """
    def on_stdHomeButton_pressed(self):
        #This function sets the text browser display page to the welcome help
        #page.  The QUrl method fromLocalFile allows the path to be local
        self.textBrowser.setSource(QUrl.fromLocalFile(\
            "ui/help/helpdocs/administrative/StandardHelpHome.html"))

    def on_stdBackButton_pressed(self):
        #This function sets the current page to the previously visited page
        if self.stdBFIndex > 0:
            self.buttonNav = True
            self.stdBFIndex = self.stdBFIndex - 1
            self.textBrowser.setSource(QUrl.fromLocalFile(\
                self.stdBFList[self.stdBFIndex]))
            
    def on_stdForwardButton_pressed(self):
        #This function restores the current page to recent pages after the
        #stdBackButton has been pressed
        if self.stdBFIndex + 1 < len(self.stdBFList):
            self.buttonNav = True
            self.stdBFIndex = self.stdBFIndex + 1            
            self.textBrowser.setSource(QUrl.fromLocalFile(\
                self.stdBFList[self.stdBFIndex]))
            
    def stdDisplayContent(self):
        #This function is used to display help content after a tree widget
        #item has been selected
        if self.treeWidget.currentItem().parent() != None:
            if self.treeWidget.currentItem().parent().text(0) == "Slice View":
                leadstring = "Slice"
            if self.treeWidget.currentItem().parent().text(0) == "Path View":
                leadstring = "Path"
            #The name of each help file includes the text from the label of
            #the parent widget, so the "leadstring" must be captured.
            url = ""
            for letter in str(self.treeWidget.currentItem().text(0)):
                if letter == "/":
                    #The slash character may appear in the text of the current
                    #tree widget item but they cannot appear in the name of
                    #the html help file.
                    pass
                else:
                    url = url + letter
            url = leadstring + url + ".html"
            self.textBrowser.setSource(QUrl.fromLocalFile(\
                "ui/help/helpdocs/content/" + url))
        else:
            #This space is reserved for displaying help content from a tree
            #widget that does not have a parent, but it has not been written
            #yet.
            pass
    """
    Standard History
    """
    def on_actionView_Standard_History_triggered(self):
        #This function displays the standard history dialog box when the
        #corresponding menu item is clicked.
        if self.triggerOnce == True:
            histdialog = StdHistoryDialog(self, self)
            histdialog.show()
        self.triggerOnce = not(self.triggerOnce)     
        
    def on_actionClear_Standard_History_triggered(self):
        #This function resets the standard history dictionary and list, and
        #also rewrites the text file that stores external copies of the
        #dictionary and list.
        self.stdHistoryDict = {}
        self.stdHistoryList = []
        with open("C:/Users/" + user + "/.cadnano/stdhistory.txt", 'w')\
            as history:
            history.write(repr({}) + '\n' + repr([]))
            
    def stdHistoryTracker(self, source):
        source.setScheme("")
        #The method "setScheme" resets the source scheme so that the QString
        #object no longer includes superfluous PyQt mark up conventions
        source = source.toString()
        source = str(source)
        source = source.lstrip('/')
        try:
            source.index('helpdocs/content')
            #Index returns the location of the specified text where it appears
            #in the item that implements the function.  An error is returned
            #if the text does not appear, in which case, the code in the 
            #"try:" section is not executed
            if self.buttonNav == False:
                for i in range(len(self.stdBFList) - self.stdBFIndex - 1):
                    self.stdBFList.pop()
                    #This for loop removes every page in the back/forward list
                    #that has an index larger than the current index.  This 
                    #ensures that if the back button is ever used and a new 
                    #page is accessed afterwards, the forward path is reset.
                self.stdBFIndex = self.stdBFIndex + 1
                self.stdBFList.append(source)
            self.findFile = source
            
            with open(source, 'r') as currentpage:
                pageLines = currentpage.readlines()
            for line in pageLines:
                try:
                    line.index('<H2>')
                    docTitle = line.strip('<H2>')
                    docTitle = line.rstrip('</H2>\n')
                    break
                    #This try/exception handler captures the header of the
                    #current document so that it can eventually be displayed
                    #in the history dialog box.
                except:
                    pass
            self.stdHistoryDict.update({docTitle:source})
            try:
                self.stdHistoryList.remove(docTitle)
                #This try/exception handler is used to prevent duplicates from
                #occurring in the history list.
            except:
                pass
            self.stdHistoryList.append(docTitle)
            with open("C:/Users/" + user + "/.cadnano/stdhistory.txt", 'w')\
                as history:
                history.write(repr(self.stdHistoryDict) + '\n' + \
                              repr(self.stdHistoryList))
                #This file IO process maintains the history data in the
                #external standard history file.
        except:
            pass
        self.buttonNav = False
        #The buttonNav variable is reset to False here in case the history
        #function was triggered by a back/forard event.

    """
    Standard Find String
    """
    def stdFindString(self):
        searchString = str(self.stdFindEdit.text())
        if searchString != '':
            #This if statement prevents empty space from being highlighted.
            #Empty space is different from white space, and it is detectable.
            findLines = []
            #findLines is used to store the edited html text, and it is used 
            #to rewrite the file with highlighted search terms.
            if self.findFile != None:
                #This if statement prevents the find tool from functioning on 
                #inappropriate documents.
                with open(self.findFile, 'r') as openDoc:
                    lines = openDoc.readlines()                    
                    for line in lines:
                        if line[0] == '<' or line[0] == '&':
                            #html code lines that begin with '<' or '&' should
                            #not be highlighted, so they are added to the 
                            #findLines list without any modifications.
                            findLines.append(line)
                        else:
                            if line.lower().count(searchString.lower(), 0,\
                                                  len(line)) > 0:
                                #The "lower()" method ensures that the string
                                #recognition method is not case sensitive.  If
                                #the count is higher than 0, then the
                                #the matched terms are highlighted using html
                                line = line.replace(searchString,\
                                    '<FONT STYLE="BACKGROUND-COLOR: #66CCFF">'\
                                    + searchString + '</FONT>')
                                findLines.append(line)
                            else:
                                findLines.append(line)
                with open("ui/help/helpdocs/administrative/FindResult.html",\
                          'w') as openDoc:
                    for line in findLines:
                        openDoc.write(line)
                self.textBrowser.setSource(QUrl.fromLocalFile(\
                        "ui/help/helpdocs/administrative/FindResult.html"))
                #Because the find result file is in the administrative folder,
                #it cannot be included in the history because of an if clauses 
                #in the standard history tracker.
        else:
            self.buttonNav = True
            #Even though buttons are not used to trigger this function, if
            #there are no matches, the original file must be set as the source
            #and buttonNav must be set to true so that the history is not 
            #upddated.
            self.textBrowser.setSource(QUrl.fromLocalFile(self.findFile))
            self.buttonNav = False    
    """
    Standard Search
    """
    def on_stdSearchButton_pressed(self):
        self.stdExecuteSearch()
        
    def stdExecuteSearch(self):
        searchString = str(self.stdSearchEdit.text())
        #searchString is the verbatim text from the search edit line field.
        helpDocList = os.listdir("ui/help/helpdocs/content/")
        #helpDocList is a complete list of the documents in the specified 
        #dirrectory.
        matchDict = {}
        #matchDict is a dictionary that keeps track of complete string matches
        #in each file with the file path set as the key while the number of 
        #matches is the key item's associated item.
        termMatchDict = {}
        #termMatchDict works the same way as matchDict, but it is used to
        #store matches of individual terms in a search string rather than the 
        #entire search string.
        pSSList = [] 
        #The acronym pSS stands for parsedSearchString.  This is a list of all
        #strings separated by whitespace in the search string.
        searchTerm = ''
        #searchTerm is an empty string that is built from the searchString
        #until whitespace is encountered and it represents the separate words
        #in the search string.
        for letter in searchString:
            #This for loop builds searchTerm letter by letter.  When white-
            #space is encountered, searchTerm is added to pSSList and is 
            #reset to an empty string so that it can be rebuilt.
            if letter != ' ':
                searchTerm = searchTerm + letter
            else:
                if searchTerm != '':
                    pSSList.append(searchTerm)
                searchTerm = ''
        pSSList.append(searchTerm)
        #Since there is generally no whitespace at the end of a search query,
        #the last searchTerm is added to the list without a clause.
        for doc in helpDocList:
            #This for loop iterates through each document in the list so that
            #each help document can be examined for string matches.
            with open("ui/help/helpdocs/content/" + doc, 'r') as openDoc:
                lines = openDoc.readlines()
                searchCount = 0
                #searchCount is used to keep track of the number of complete
                #string matches.
                termCount = 0
                #termCount is used to keep track of the number of single term
                #matches.
                for line in lines:
                    #This for loop is responsible for iterating through each
                    #individual line of the current help file.
                    if line[0:5] == '<meta':
                        #This if clause enables lines that include invisible 
                        #meta data to pass through the subsequent if clause.
                        line = line.lstrip('<meta ')
                        line = line.rstrip('/>')
                    if line[0] != '<' and line[0] != '&':
                        #This if clause prevents lines of html code that are
                        #not part of the main body of text from being included
                        #in the search.  More robust alternative code that
                        #identifies the beginning and end of html script could
                        #be used in the future to eliminate the need for 
                        #strict html coding structure.
                        searchCount = searchCount + line.lower().count(\
                            searchString.lower(), 0, len(line))
                        if searchCount > 0:
                            matchDict.update({doc:searchCount})
                        for term in pSSList:
                            termCount = termCount + line.lower().count(\
                                term.lower(), 0, len(line))
                            if termCount > 0:
                                termMatchDict.update({doc:termCount})
        with open("ui/help/helpdocs/administrative/SearchResults.html", 'r')\
            as SR:
            searchresults = SR.readlines()
        with open("ui/help/helpdocs/administrative/SearchResults.html", 'w')\
            as SR:
            for line in range(len(searchresults)):
                if line == 3 and \
                    (len(matchDict) > 0 or len(termMatchDict) > 0):
                    #The third line in SearchResults.html is left blank for
                    #the search results to all be inserted on one line.
                    matchRank = []
                    #matchRank is a list that stores the ranking numbers for
                    #each document that matches the search.
                    for item in matchDict:
                        #This for loop builds the matchRank list.
                        matchRank.append(matchDict[item])
                    matchRank.sort()
                    #This method arranges the numbers in the matchRank list in
                    #ascending order.
                    matchRank.reverse()
                    #This method reverses the order of the matchRank list so
                    #that it will be in descending order.
                    for rank in matchRank:
                        for duplicate in range(matchRank.count(rank) - 1):
                            #This nested for loop removes duplicate rankings
                            #from the matchRank list.
                            matchRank.remove(rank)
                    results = []
                    #The results list is used to build the final list of help
                    #documents.
                    for rank in matchRank:
                        for item in matchDict:
                            #This nested for loop matches the rankings in the
                            #matchRank list the items in the matchDict.
                            #Because the rank list was sorted, the results
                            #list is built in an order that preserves ranking.
                            try:
                                termMatchDict.pop(item)
                                #This try statement prevents duplicate items
                                #from appearing on the termMatchDict list.
                            finally:
                                if matchDict[item] == rank:
                                    results.append(item)
                    #The method for matching terms is almost identical to the
                    #method for matching the full searchstring.
                    termMatchRank = []
                    for item in termMatchDict:
                       termMatchRank.append(termMatchDict[item])
                    termMatchRank.sort()
                    termMatchRank.reverse()
                    for rank in termMatchRank:
                       for duplicate in range(termMatchRank.count(rank) - 1):
                           termMatchRank.remove(rank)
                    for rank in termMatchRank:
                       for item in termMatchDict:
                           if termMatchDict[item] == rank:
                               results.append(item)
                    resultCount = 0
                    #The result count is used to display the ranking of the
                    #search item in the searchResults.html file.
                    for item in results:
                        #This for loop is responsible for building the search
                        #results list.
                        resultCount = resultCount + 1
                        with open("ui/help/helpdocs/content/" + item, 'r')\
                            as openDoc:
                            docLines = openDoc.readlines()
                            for line in docLines:
                                try:
                                    line.index('<H2>')
                                    line = line.strip('<H2>')
                                    line = line.rstrip('</H2>\n')
                                    break
                                except:
                                    pass
                        SR.write("%s.) " % str(resultCount))
                        SR.write('<a href="../content/' + item +\
                            '">%s</a><p>' % line)
                    SR.write("\n")
                elif line == 3:
                    SR.write("Search Completed: No Results Found\n")
                else:
                    SR.write(searchresults[line])
        self.textBrowser.setSource(QUrl.fromLocalFile(\
            "ui/help/helpdocs/administrative/SearchResults.html"))


class OnlHistoryDialog(QDialog):
    def __init__(self, helpWindow, parent=None):
        #This class builds the online history dialog box from scratch.
        super(OnlHistoryDialog, self).__init__(parent)
        self.helpWindow = helpWindow
        self.textBox = QListWidget()
        self.histKeys = self.helpWindow.onlHistoryDict.keys()
        historyListR = self.helpWindow.onlHistoryList
        historyListR.reverse()
        #This method ensures that the most recent pages appear on the top of
        #the displayed history list.
        for pageTitle in historyListR:
            self.textBox.addItem(QString(pageTitle))
        self.connect(self.textBox, SIGNAL(\
            "itemDoubleClicked(QListWidgetItem *)"), self.itemClicked)
        #This signal ensures that when an item on the history list is clicked
        #on, the page that the item represents will be displayed.
        boxLayout = QHBoxLayout()
        boxLayout.addWidget(self.textBox)
        layout = QGridLayout() 
        layout.addLayout(boxLayout, 1, 0)
        self.setLayout(layout)
        self.setWindowTitle("History")
    
    def itemClicked(self):
        #This function is responsible for displaying a page from the history
        #list once it is selected by the user.
        pageTitle = str(self.textBox.currentItem().text())
        self.helpWindow.webView.load(QUrl(str(\
            self.helpWindow.onlHistoryDict[pageTitle])))
        self.helpWindow.webView.show()


class StdHistoryDialog(QDialog):
    #This class builds the standard history dialog box from scratch.
    def __init__(self, helpWindow, parent=None):
        super(StdHistoryDialog, self).__init__(parent)
        self.helpWindow = helpWindow
        self.textBox = QListWidget()
        historyListR = self.helpWindow.stdHistoryList
        historyListR.reverse()
        #This method ensures that the most recent pages appear on the top of
        #the displayed history list.
        for pageTitle in historyListR:
            self.textBox.addItem(QString(pageTitle))
        self.connect(self.textBox, SIGNAL(\
            "itemDoubleClicked(QListWidgetItem *)"), self.itemClicked)
        #This signal ensures that when an item on the history list is clicked
        #on, the page that the item represents will be displayed.
        boxLayout = QHBoxLayout()
        boxLayout.addWidget(self.textBox)
        layout = QGridLayout() 
        layout.addLayout(boxLayout, 1, 0)
        self.setLayout(layout)
        self.setWindowTitle("History")
    
    def itemClicked(self):
        #This function is responsible for displaying a page from the history
        #list once it is selected by the user.
        pageTitle = str(self.textBox.currentItem().text())
        self.helpWindow.textBrowser.setSource(QUrl.fromLocalFile(\
            str(self.helpWindow.stdHistoryDict[pageTitle])))
        self.helpWindow.textBrowser.show()         