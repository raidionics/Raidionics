
def get_stylesheet(object_type):
    if object_type == 'QGroupBox':
        return get_qgroupbox_stylesheet()
    elif object_type == 'QPushButton':
        return get_qpushbutton_stylesheet()


def get_qgroupbox_stylesheet():
    ss = str("QGroupBox{"
             "border: 3px solid #FF17365D;"
             "border-color: #FF17365D;"
             "margin-top: 27px;"
             "font-size: 14px;"
             "border-radius: 15px;"
             "}"
             "QGroupBox::title{"
             "border: 2px solid gray;"
             "border-radius: 5px;"
             #"padding:5px 10px 5px 5px;"
             "subcontrol-origin:margin;"
             "subcontrol-position:top left;"
             "background-color: #FF17365D;"
             "color: rgb(255, 255, 255);"
             "}")

    return ss


def get_qpushbutton_stylesheet():
    ss = str("QPushButton{"
             "border: 1px solid #FF17365D;"
             "border-color: #FF17365D;"
             "border-radius: 1px;"
             "background-color: rgb(229, 235, 235);"
             "}")

    return ss
