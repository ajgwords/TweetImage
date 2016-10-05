# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TweetImage
                                 A QGIS plugin
 Tweets an image of your current map canvas
                              -------------------
        begin                : 2015-12-08
        git sha              : $Format:%H$
        copyright            : (C) 2015 by ajggeoger
        email                : llansteffan@hotmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
# Import the PyQt and QGIS libraries
from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

# Initialize Qt resources from file resources.py
import resources

#plugin specific imports
from time import sleep
import sys
import os

#import qgis.utils
# Import the code for the dialog
from tweet_image_dialog import TweetImageDialog
import os.path


class TweetImage:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TweetImage_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TweetImageDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Tweet Image')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TweetImage')
        self.toolbar.setObjectName(u'TweetImage')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TweetImage', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToWebMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TweetImage/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Tweet what you are working on'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.dlg.btnDelAPI.clicked.connect(self.delete_details)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginWebMenu(
                self.tr(u'&Tweet Image'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

##
    def delete_details(self):
        self.iface.messageBar().pushMessage("Success", "You pushed me", duration=3)
        #get plugin location
        plugin_path = os.path.dirname(os.path.realpath(__file__))

        self.dlg.txtCK.setText(str(''))
        self.dlg.txtCKS.setText(str(''))
        self.dlg.txtAT.setText(str(''))
        self.dlg.txtATS.setText(str(''))

        os.remove(os.path.join(plugin_path, "TwitterDetails.txt"))


##
    def run(self):
        """Run method that performs all the real work"""
        try:
            import tweepy
            #print "module tweepy found"
            self.iface.messageBar().pushMessage("Success", "Module Tweepy found", duration=3)
            #QtGui.QMessageBox.about(self, "tweepy found", "Your tweepy installation was found. cool!")
        except ImportError:
            #raise Exception("Tweepy module not installed correctly")
            #QMessageBox.information(self.iface.mainWindow(),"Error","Tweepy not found")
            self.iface.messageBar().pushCritical("Error", "Module Tweepy not found")



        #get plugin location
        plugin_path = os.path.dirname(os.path.realpath(__file__))
        print plugin_path

        # show the dialog
        #self.dlg.show()

        try:
            f = open(os.path.join(plugin_path, "TwitterDetails.txt"),"r")
            print "file found"
            data = f.readlines()
            print data[0][:-1]
            print data[1][:-1]
            print data[2][:-1]
            print data[3][:-1]
            self.dlg.txtCK.setText(str(data[0][:-1]))
            self.dlg.txtCKS.setText(str(data[1][:-1]))
            self.dlg.txtAT.setText(str(data[2][:-1]))
            self.dlg.txtATS.setText(str(data[3][:-1]))
            f.close()
        except:
            pass

        # show the dialog
        self.dlg.show()

        # Run the dialog event loop
        result = self.dlg.exec_()

        #check for txt file and populate boxes if it exists
        consumer_key = self.dlg.txtCK.text()
        #print type(consumer_key)
        consumer_secret = self.dlg.txtCKS.text()
        access_token = self.dlg.txtAT.text()
        access_token_secret = self.dlg.txtATS.text()

        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)

        api = tweepy.API(auth)


        if self.dlg.chkImage.isChecked() == True:
            self.iface.mapCanvas().saveAsImage(os.path.join(plugin_path, "TweetImage.png"))


        # See if OK was pressed
        if result:

            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            #pass
            #QMessageBox.information(self.iface.mainWindow(),"hello world","Test")
            mystatus = self.dlg.txtStatus.text()

            image = os.path.join(plugin_path, "TweetImage.png")
            #message = "This is an automated tweet sent using Tweepy from QGIS"

            #api.update_with_media(image, status=message)
            if len(mystatus) > 0 and self.dlg.chkImage.isChecked() == False:
                api.update_status(mystatus)
            if len(mystatus) > 0 and self.dlg.chkImage.isChecked() == True:
                api.update_with_media(image, mystatus)


            #write contents of txt boxes to file
            #might need to look at order
            f = open(os.path.join(plugin_path, 'TwitterDetails.txt'),'w')
            f.write(self.dlg.txtCK.text()+'\n')
            f.write(self.dlg.txtCKS.text()+'\n')
            f.write(self.dlg.txtAT.text()+'\n')
            f.write(self.dlg.txtATS.text()+'\n')
            f.close()

            #delete image and pngw
            try:
                os.remove(os.path.join(plugin_path, "TweetImage.png"))
                os.remove(os.path.join(plugin_path, "TweetImage.PNGw"))
                #os.remove("TweetImage.pngw")
            except:
                self.iface.messageBar().pushMessage("Error", "Files not deleted", duration=5)
