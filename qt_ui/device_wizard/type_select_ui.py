# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'type_select.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFormLayout, QRadioButton, QSizePolicy,
    QSpacerItem, QWidget, QWizardPage)

class Ui_WizardPageDeviceType(object):
    def setupUi(self, WizardPageDeviceType):
        if not WizardPageDeviceType.objectName():
            WizardPageDeviceType.setObjectName(u"WizardPageDeviceType")
        WizardPageDeviceType.resize(490, 477)
        self.formLayout = QFormLayout(WizardPageDeviceType)
        self.formLayout.setObjectName(u"formLayout")
        self.audio_based_radio = QRadioButton(WizardPageDeviceType)
        self.audio_based_radio.setObjectName(u"audio_based_radio")
        self.audio_based_radio.setChecked(True)

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.audio_based_radio)

        self.focstim_radio = QRadioButton(WizardPageDeviceType)
        self.focstim_radio.setObjectName(u"focstim_radio")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.focstim_radio)

        self.neostim_radio = QRadioButton(WizardPageDeviceType)
        self.neostim_radio.setObjectName(u"neostim_radio")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.neostim_radio)

        self.coyote_radio = QRadioButton(WizardPageDeviceType)
        self.coyote_radio.setObjectName(u"coyote_radio")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.coyote_radio)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.formLayout.setItem(4, QFormLayout.LabelRole, self.verticalSpacer)


        self.retranslateUi(WizardPageDeviceType)

        QMetaObject.connectSlotsByName(WizardPageDeviceType)
    # setupUi

    def retranslateUi(self, WizardPageDeviceType):
        WizardPageDeviceType.setWindowTitle(QCoreApplication.translate("WizardPageDeviceType", u"WizardPage", None))
        WizardPageDeviceType.setTitle(QCoreApplication.translate("WizardPageDeviceType", u"Select device type", None))
        self.audio_based_radio.setText(QCoreApplication.translate("WizardPageDeviceType", u"Audio-based three-phase", None))
        self.focstim_radio.setText(QCoreApplication.translate("WizardPageDeviceType", u"FOC-Stim", None))
        self.neostim_radio.setText(QCoreApplication.translate("WizardPageDeviceType", u"NeoStim", None))
        self.coyote_radio.setText(QCoreApplication.translate("WizardPageDeviceType", u"Coyote 3", None))
    # retranslateUi

