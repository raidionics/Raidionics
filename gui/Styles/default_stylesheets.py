
def get_stylesheet(object_type):
    if object_type == 'QGroupBox':
        return get_qgroupbox_stylesheet()
    elif object_type == 'QPushButton':
        return get_qpushbutton_stylesheet()
    elif object_type == 'QSlider':
        return get_qslider_stylesheet()


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


def get_qslider_stylesheet():
    # ss = str("QSlider{"
    #          "border: 2px solid #FF17365D;"
    #          "border-color: #FF17365D;"
    #          "border-radius: 15px;"
    #          # "background-color: rgb(229, 235, 235);"
    #          "}")

    ss = str("QSlider::groove:horizontal { "
             "border: 1px solid #bbb;"
             "background: white;"
             "height: 10px;"
             "border-radius: 4px;"
             "}"
             "             QSlider::sub-page:horizontal {"
             "background: qlineargradient(x1: 0, y1: 0,    x2: 0, y2: 1,"
             "    stop: 0 #66e, stop: 1 #bbf);"
             "background: qlineargradient(x1: 0, y1: 0.2, x2: 1, y2: 1,"
             "    stop: 0 #bbf, stop: 1 #55f);"
             "border: 1px solid #777;"
             "height: 10px;"
             "border-radius: 4px;"
             "}"
             "QSlider::handle:horizontal {"
             "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
             "    stop:0 #eee, stop:1 #ccc);"
             "border: 1px solid #777;"
             "width: 13px;"
             "margin-top: -2px;"
             "margin-bottom: -2px;"
             "border-radius: 4px;"
             "}"
             "QSlider::handle:horizontal:hover {"
             "background: qlineargradient(x1:0, y1:0, x2:1, y2:1,"
             "    stop:0 #fff, stop:1 #ddd);"
             "border: 1px solid #444;"
             "border-radius: 4px;"
             "}"
             "QSlider::sub-page:horizontal:disabled {"
             "background: #bbb;"
             "border-color: #999;"
             "}"
             "QSlider::add-page:horizontal:disabled {"
             "background: #eee;"
             "border-color: #999;"
             "}"
             "QSlider::handle:horizontal:disabled {"
             "background: #eee;"
             "border: 1px solid #aaa;"
             "border-radius: 4px;"
             "}")

    return ss
