

def get_stylesheet(object_type):
    if object_type == 'QPushButton':
        return __get_qpushbutton_ss()
    elif object_type == 'QTextEdit':
        return __get_qtextedit_ss()
    elif object_type == 'QLineEdit':
        return __get_qlineedit_ss()
    elif object_type == 'QMenuBar':
        return __get_qmenubar_ss()


def __get_qpushbutton_ss():
    ss = str('QPushButton{'
    'border-style: solid;'
    'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-width: 1px;'
'border-radius: 5px;'
'color: rgb(0,0,0);'
'padding: 2px;'
'background-color: rgb(255,255,255);'
'}'
'QPushButton::default{'
'border-style: solid;'
'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-width: 1px;'
'border-radius: 5px;'
'color: rgb(0,0,0);'
'padding: 2px;'
'background-color: rgb(255,255,255);'
'}'
'QPushButton:hover{'
'border-style: solid;'
'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(195, 195, 195), stop:1 rgb(222, 222, 222));'
'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(197, 197, 197), stop:1 rgb(227, 227, 227));'
'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(197, 197, 197));'
'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(195, 195, 195), stop:1 rgb(222, 222, 222));'
'border-width: 1px;'
'border-radius: 5px;'
'color: rgb(0,0,0);'
'padding: 2px;'
'background-color: rgb(255,255,255);'
'}'
'QPushButton:pressed{'
'border-style: solid;'
'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-width: 1px;'
'border-radius: 5px;'
'color: rgb(0,0,0);'
'padding: 2px;'
'background-color: rgb(142,142,142);'
'}'
'QPushButton:disabled{'
'border-style: solid;'
'border-top-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-right-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(217, 217, 217), stop:1 rgb(227, 227, 227));'
'border-left-color: qlineargradient(spread:pad, x1:0, y1:0.5, x2:1, y2:0.5, stop:0 rgb(227, 227, 227), stop:1 rgb(217, 217, 217));'
'border-bottom-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgb(215, 215, 215), stop:1 rgb(222, 222, 222));'
'border-width: 1px;'
'border-radius: 5px;'
'color: #808086;'
'padding: 2px;'
'background-color: rgb(142,142,142);}')
    return ss


def __get_qtextedit_ss():
    ss = str('QPlainTextEdit {'
                                            'border-width: 1px;'
                                            'border-style: solid;'
                                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
    return ss


def __get_qlineedit_ss():
    ss = str('QLineEdit {'
                                            'border-width: 1px;'
                                            'border-style: solid;'
                                            'border-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));}')
    return ss

def __get_qmenubar_ss():
    ss = str('QMenuBar {'
	'background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(207, 209, 207, 255), stop:1 rgba(230, 229, 230, 255));'
'}'
'QMenuBar::item {'
	'color: #000000;'
  	'spacing: 3px;'
  	'padding: 1px 4px;'
	'background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(207, 209, 207, 255), stop:1 rgba(230, 229, 230, 255));'
'}'

'QMenuBar::item:selected {'
  	'background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(0, 113, 255, 255), stop:1 rgba(91, 171, 252, 255));'
	'color: #FFFFFF;'
'}')
    return ss
