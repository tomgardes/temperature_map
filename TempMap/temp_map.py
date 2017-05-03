# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TempMap
                                 A QGIS plugin
 Test
                              -------------------
        begin                : 2017-04-22
        git sha              : $Format:%H$
        copyright            : (C) 2017 by Thomas
        email                : thomasgardes.31@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog, QMessageBox
from PyQt4 import QtGui 
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from temp_map_dialog import TempMapDialog
import qgis.core
from qgis.core import *
import os
from qgis.utils import *
import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
from qgis import *






class TempMap:
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
            'TempMap_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)
		
		 
        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Temperature Map')
        

        # TODO: We are going to let the user set this up in a future iteration
        
        self.toolbar = self.iface.addToolBar(u'TempMap')
        self.toolbar.setObjectName(u'TempMap')
		
        

		


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
        return QCoreApplication.translate('TempMap', message)


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

        # Create the dialog (after translation) and keep reference
        self.dlg = TempMapDialog()

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
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TempMap/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'temperature_maps'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Temperature Map'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar
		
    def outputICU(self) :
        """Define path to save output files"""
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file", "", '*.tif')
        self.dlg.barre_icu.setText(filename)
		
    def outputRegression(self) :
        """Define path to save output files"""
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file", "", '*.tif')
        self.dlg.barre_regression.setText(filename)
		
    def outputResidus(self) :
        """Define path to save output files"""
        filename = QFileDialog.getSaveFileName(self.dlg, "Select output file", "", '*.tif')
        self.dlg.barre_residus.setText(filename)
	
    def outputModel(self) : 
		"""Define path to save output files"""
		filename = QFileDialog.getSaveFileName(self.dlg, "Select output file", "", '*.csv')
		self.dlg.barre_modele.setText(filename)


    def run(self,index):
		"""Run method that performs all the real work"""
		
		#Connect buttons "browse" to line edit
		self.dlg.bouton_icu.clicked.connect(self.outputICU)
		self.dlg.bouton_regression.clicked.connect(self.outputRegression)
		self.dlg.bouton_residus.clicked.connect(self.outputResidus)
		self.dlg.bouton_modele.clicked.connect(self.outputModel)
		
		# show the dialog
		self.dlg.show()
		
		#clear all combo boxes
		self.dlg.menu_mnt.clear()
		self.dlg.menu_temperature.clear()
		self.dlg.menu_field.clear()
		self.dlg.menu_mapuce.clear()
		self.dlg.menu_fraction.clear()
		self.dlg.progressBar.setValue(0)
		
				
		#add layers to interface
		mapCanvas = self.iface.mapCanvas() #connect to map canvas 
		layers = self.iface.legendInterface().layers() #get all layers from map canvas
		#Initialize lists for diffents types of layers 
		rasterList=[]
		rasterLayerList = []
		pointList = []
		pointLayerList = []
		polyList = []
		polyLayerList = []
		
		#Add layers in lists depending of their types 
		for i in range (mapCanvas.layerCount()-1,-1,-1):
			layer = layers[i]
			if layer.type() == QgsMapLayer.VectorLayer :
				
				if layer.wkbType() == QGis.WKBPoint :
					pointList.append(layer.name()) #add name for combo boxes
					pointLayerList.append(layer) #add layers for processing 
				else :
					polyList.append(layer.name())
					polyLayerList.append(layer)
					
			else :
				rasterList.append(layer.name())
				rasterLayerList.append(layer)
		
		# Load lists in combo boxes 
		self.dlg.menu_mnt.addItems(rasterList)
		self.dlg.menu_temperature.addItems(pointList)
		self.dlg.menu_mapuce.addItems(polyList)
		self.dlg.menu_fraction.addItems(rasterList)
			
		 
		

		
		def layer_field() :
			""" Method used to change the content of the 'field' combo box depending of the layer set in "temperature" combo box"""
			selectedLayerIndex = self.dlg.menu_temperature.currentIndex() #get name of layer set in 'temperature' combo box 
			selectedLayer = pointLayerList[selectedLayerIndex] #get layer set in 'temperature' combo box
			fields=selectedLayer.pendingFields() #get fields from the layer 
			fieldnames=[field.name() for field in fields] #get fields names 
			self.dlg.menu_field.clear() #clear combo box before add items 
			self.dlg.menu_field.addItems(fieldnames) #add items (fields names) to 'field' combo box 
			
		def state_changed() :
			"""Method used to perform real time changes on the interface when checkBox is checked or unchecked"""
			if self.dlg.checkBox.isChecked() : #Check if checkBox is checked 
				self.dlg.menu_mapuce.setEnabled(False) #Disable 'mapuce' combo box 
				self.dlg.menu_fraction.setEnabled(True) #Enable 'fraction' combo box 
				self.dlg.label_frac.setStyleSheet('color : black') #Set color of label 'fraction' to black 
				self.dlg.label_mapuce.setStyleSheet('color : grey') #Set color of label 'mapuce' to grey 
			else : #if checkBox not checked 
				self.dlg.menu_mapuce.setEnabled(True) #Enable 'mapuce' combo box 
				self.dlg.menu_fraction.setEnabled(False) #Disable 'fraction' combo box 
				self.dlg.label_frac.setStyleSheet('color : grey') #Set color of label 'fraction' to grey 
				self.dlg.label_mapuce.setStyleSheet('color : black') #Set color of label 'mapuce' to black 
			
		def resolve(name, basepath=None):
			"""Function used to get around a bug making pictures on the dialog doesn't display"""
			if not basepath:
				basepath = os.path.dirname(os.path.realpath(__file__))
			return os.path.join(basepath, name)
			
	
		self.dlg.menu_temperature.currentIndexChanged.connect(layer_field) #connect layer_field method to temperature combo box 
		self.dlg.checkBox.stateChanged.connect(state_changed) #connect state_changed method to checkBox 
		
		progress=self.dlg.progressBar #define progress bar widget added from ui file 
		progress.setMaximum(100) #set maximum in percentage for progress bar 
		
		#Set 'help' pictures for each combo box 
		pathIcon = resolve('help.png')
		self.dlg.infoMnt.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoTemp.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoField.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoMapuce.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoInterpolation.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoRegression.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoResidus.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoModele.setPixmap(QtGui.QPixmap(pathIcon))
		self.dlg.infoFrac.setPixmap(QtGui.QPixmap(pathIcon))
		
		

		
		
        # Run the dialog event loop
		result = self.dlg.exec_()
        # See if OK was pressed
		if result:
			
		
				#Check QGIS version 
				version = qgis.utils.QGis.QGIS_VERSION
				versionSplit = version.split('.')
				NumVersion = versionSplit[1]
				qgisVersion = int(NumVersion)

									
				#Define outputs path 
				outputPath1 = self.dlg.barre_icu.text() #Get path values from all lines edits 
				outputPath2 = self.dlg.barre_regression.text()
				outputPath3 = self.dlg.barre_residus.text()
				outputPath4 = self.dlg.barre_modele.text()
				

				
 

				#get current value of combo boxes 
				selectedMntIndex = self.dlg.menu_mnt.currentIndex() 
				selectedMapuceIndex = self.dlg.menu_mapuce.currentIndex()
				selectedTempIndex = self.dlg.menu_temperature.currentIndex()
				selectedFracIndex = self.dlg.menu_fraction.currentIndex() 
				selectedFieldIndex = self.dlg.menu_field.currentIndex()				

				#Check comboboxes content 
				#Check if CheckBox checked 
				BoxChecked = False 
				if self.dlg.checkBox.isChecked() :
					BoxChecked = True 
					
				#check MNT combo box
				if self.dlg.menu_mnt.currentText() == "" : #if combo box is empty 
					QMessageBox.warning(None, "Temperature Map", str("Veuillez indiquer un raster de MNT valide"))	
				#check if fraction and MNT are differents from each other (only whe checkBox is checked) 
				elif self.dlg.menu_fraction.currentText() == self.dlg.menu_mnt.currentText() and BoxChecked :
					QMessageBox.warning(None, "Temperature Map", str("La fraction de ville et le MNT doivent etre deux rasters differents"))
				#check fraction combo box (used only when checkBox is checked)
				elif self.dlg.menu_fraction.currentText() == "" and BoxChecked :
					QMessageBox.warning(None,"Temperature Map", str("Veuillez indiquer un raster de fraction de ville valide"))
				#check Mapuce combo box 
				elif self.dlg.menu_mapuce.currentText() == "" :
					QMessageBox.warning(None, "Temperature Map", str("Veuillez indiquer une couche de donnees MaPUCE valide"))
				#check temperature combo box
				elif self.dlg.menu_temperature.currentText() == "" :
					QMessageBox.warning(None, "Temperature Map", str("Veuillez indiquer une couche de stations valide"))
				#chek field combo box 
				elif self.dlg.menu_field.currentText() == "" :
					QMessageBox.warning(None, "Temperature Map", str("Veuillez indiquer un champ de temperature valide"))	
								


				
				else :

					selectedLayerIndex2 = self.dlg.menu_temperature.currentIndex()
					selectedLayer2 = pointLayerList[selectedLayerIndex2]
					fields=selectedLayer2.pendingFields()
					fieldnames=[field.name() for field in fields]	
					
					#set layers and fields depending of current value of combo boxes 
					fieldTemp = fieldnames[selectedFieldIndex]
					field = fields[selectedFieldIndex]
					stations  = pointLayerList[selectedTempIndex]
					mnt = rasterLayerList[selectedMntIndex]			
					mapuce=polyLayerList[selectedMapuceIndex] 
					frac_user=rasterLayerList[selectedFracIndex]
					crsRefLayer = layers[0]
					idCrsRef = crsRefLayer.crs().authid()
					epsgSplit = idCrsRef.split(':')
					epsg0 = epsgSplit[1]
					epsg = int(epsg0)
					#check inputs 
					print('station =', stations)
					print('mnt=', mnt)
					print('layers =', layers)
					print('mapuce =', mapuce)
					print('layers =', layers)
					print('ESPG=', epsg)	
					print('field type :', field.typeName() ) 
					
					"""if field.typeName() != 'Integer' and field.typeName() != 'Real' :
						QMessageBox.warning(None, "Temperature Map", str("Le champ de temperatures doit etre de type numerique"))"""
					
									
					emprise=processing.runalg("qgis:fixeddistancebuffer", stations, 100,5,1, None) #100m buffer on stations point layer 
					objEmp = processing.getObject(emprise['OUTPUT']) #recuperer buffer stations sous forme de QgsVectorLayer
					rectangle= objEmp.extent() #recuperer l emprise de la couche buffer
					coordinates = rectangle.toString(16) #convertir emprise sous forme de chaine de caractere
					replace = coordinates.replace(":",",",1) #formater la chaine pour utilisation dans la fonction clip raster by extent
					split = replace.split(",") #split de la chaine pour re-composition...
					extent= split[0]+","+split[2]+","+split[1]+","+split[3] #...concatenation pour que l ordre des coordonnes decrivant l emprise corresponde a l ordre utilise dans clip raster by extent
					progress.setValue(10)
					print(extent)
						
						
						
					getPathSave = objEmp.dataProvider().dataSourceUri() #recuperation du chemin d un fichier stocke comme temporaire
					split1 = getPathSave.split('|')
					split2 = split1[0]
					split3 = split2[:-10] #suppression du nom du fichier en fin de chaine
					outputInterpolation = split3 + 'Interpolation.tif' #remplacement du nom du fichier par le nom de la sortie voulu pour le raster calculator
					outputResidus = split3 + 'Residus.tif'
					outputRegression = split3 + 'Regression.tif'
					outputTable = split3 + 'Model.csv'
						
					#Set temporary outputs paths if not outputs paths specified 
					if outputPath1 == '' :
						outputPath1 = outputInterpolation
					if outputPath2 == '' :
						outputPath2 = outputRegression
					if outputPath3 == '' :
						outputPath3 = outputResidus
					if outputPath4 == '' :
						outputPath4 = outputTable 
						
					#Decoupe MNT
					mntExtent = processing.runalg("gdalogr:cliprasterbyextent", mnt, 0, extent, 5,4,75,6,1,0,0,0,'',None) #decoupe du mnt selon l emprise du buffer 100m autour des points
					objMntClip = processing.getObject(mntExtent['OUTPUT'])
					mntPathTest = objMntClip.dataProvider().dataSourceUri()
					iface.addRasterLayer(mntPathTest, "MNT_CLIP")
					
					mntClip = processing.runalg("saga:resampling", mntExtent['OUTPUT'], True, 0,0, extent,100,None) 
					
					
					if self.dlg.checkBox.isChecked() :
						resamplFracVille = processing.runalg("saga:resampling", frac_user, True, 0,0, extent,100,None) #dimensionnement de la fraction de ville utilisateur
						print ("Utilisation fraction perso")
						progress.setValue(50)
					
					else :
					
						#Construction de la fraction de ville
						
						if qgisVersion > 14 :
							#Rasterisation a 100m de resolution a partir des donnees mapuce
							build= processing.runalg("gdalogr:rasterize",mapuce,"BUILD_DENS",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable densite de bati
							road= processing.runalg("gdalogr:rasterize",mapuce,"ROAD_DENS",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable densite de route
							env_area=processing.runalg("qgis:fieldcalculator", mapuce, "ENV/AREA",0,8,3,1,"EXT_ENV_AR/$AREA",None)#calcul de rapport surface enveloppe exterieure / surface de l usr
							env= processing.runalg("gdalogr:rasterize",env_area['OUTPUT_LAYER'],"ENV/AREA",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable surface enveloppe exterieure bati/surface
						
						else : 
					
							#Rasterisation a 100m de resolution a partir des donnees mapuce
							build= processing.runalg("gdalogr:rasterize",mapuce,"BUILD_DENS",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable densite de bati
							road= processing.runalg("gdalogr:rasterize",mapuce,"ROAD_DENS",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable densite de route
							env_area=processing.runalg("qgis:fieldcalculator", mapuce, "ENV/AREA",0,8,3,1,"EXT_ENV_AR/$AREA",None)#calcul de rapport surface enveloppe exterieure / surface de l usr
							env= processing.runalg("gdalogr:rasterize",env_area['OUTPUT_LAYER'],"ENV/AREA",1,100,100,False,5,"",4,75,6,1,False,0,"",None)#rasterisation variable surface enveloppe exterieure bati/surface
				
						#Addition des raster pour former la fraction de ville 
						entries=[] #initialisation de la liste des entrees 
						rast1=QgsRasterCalculatorEntry() #creation premier raster
						rast1.ref = 'rast@1' #definir l appellation du premier raster
						objBuild=processing.getObject(build['OUTPUT']) #recuperer raster sous forme d objet Qgis
						rast1.raster=objBuild #definir le raster
						rast1.bandNumber=1 #definir la bande du raster a utiliser

						entries.append(rast1) #ajout du raster aux entrees
						rast2 = QgsRasterCalculatorEntry() #meme demarche avec deuxieme raster
						objRoad=processing.getObject(road['OUTPUT'])
						rast2.ref = 'rast@2'
						rast2.raster=objRoad
						rast2.bandNumber=1
						entries.append(rast2)
						rast3 = QgsRasterCalculatorEntry() #meme demarche avec troisieme raster
						objEnv=processing.getObject(env['OUTPUT'])
						rast3.ref = 'rast@3'
						rast3.raster=objEnv
						rast3.bandNumber=1
						entries.append(rast3)
						#definition d un chemin d acces pour enregistrer resultat du raster calculator comme fichier temporaire
						getPath = objEnv.dataProvider().dataSourceUri() #recuperation du chemin d un fichier stocke comme temporaire
						splitRetrait = getPath[:-10] #suppression du nom du fichier en fin de chaine
						outputCalc = splitRetrait + 'addition.tif' #remplacement du nom du fichier par le nom de la sortie voulu pour le raster calculator
						outputCalc2 = splitRetrait + 'additionResampl.tif'
						print('output calculator =', outputCalc) #verification 

						calc=QgsRasterCalculator('rast@1+rast@2+rast@3', outputCalc ,'GTiff', objBuild.extent(), objBuild.width(), objBuild.height(),entries) #calculatrice raster
						calc.processCalculation() #execution du calcul
							
							
							
							
					#Dimensionnement des rasters pour interpolation
					resamplFracVille = processing.runalg("saga:resampling", outputCalc, True, 0,0, extent,100,outputCalc2) #dimensionnement de la fraction de ville mapuce
					iface.addRasterLayer(outputCalc2, 'FRACTION_DE_VILLE')
					progress.setValue(50)
							
						
							

					print("jusqu ici tout va bien")

					#==================================================================

					#Regression lineaire multiple

					#Preparation des inputs
					objMnt = processing.getObject(mntClip['USER_GRID']) #recuperation du mnt sous forme d objet QGIS
					pathMnt = objMnt.dataProvider().dataSourceUri() #recuperation du chemin d acces au mnt decoupe, dimensionne pour usage dans la regression
					print(pathMnt)
					objFracVille = processing.getObject(resamplFracVille['USER_GRID']) 
					pathFracVille = objFracVille.dataProvider().dataSourceUri() #recuperation du chemin d acces a la fraction de ville
					print(pathFracVille)
					inputs = pathMnt + ';' + pathFracVille #definition de variables en entree pour l algorithme de regression lineaire
					print ("inputs lmr =", inputs) #verification

						 
					stationsPath = stations.dataProvider().dataSourceUri() #recuperation du chemin de la couche de stations
					splitStationsPath = stationsPath.split("|") #formatage du chemin pour usage dans l algorithme
					stationsPathFinal = splitStationsPath[0] #formatage du chemin pour usage dans l algorithme
					print("stations pour lmr =", stationsPathFinal)#verification
					lmr = processing.runalg("saga:multipleregressionanalysispointsgrids", inputs, stationsPathFinal,fieldTemp,0,True,True,0,5,5,None,outputPath4,None,None,outputPath2) #regression lineaire multiple
					iface.addRasterLayer(outputPath2, "REGRESSION")
					regObj = processing.getObject(outputPath2)
					regObj.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
					
					iface.addVectorLayer(outputPath4, "MODEL", 'ogr')
					progress.setValue(70)
						
						
					#Krigeage des residus
					residualsObj = processing.getObject(lmr['RESIDUALS']) #recuperation puis formatage du chemin de la couche de residus issus de la regression lineaire
					pathResiduals = residualsObj.dataProvider().dataSourceUri()
					splitPathResiduals = pathResiduals.split("|")
					residualsPathFinal = splitPathResiduals[0]
					print("path resdiual kriging =", residualsPathFinal)
					ordinaryKriging = processing.runalg("saga:ordinarykrigingglobal",residualsPathFinal,"RESIDUAL",1,False,False,100,-1,100,1,"a + b * x",True,extent,100,0,outputPath3,None) #krigeage ordinaire des residus
					iface.addRasterLayer(outputPath3, "RESIDUS")
					resObj = processing.getObject(outputPath3)
					resObj.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
					progress.setValue(80)

					#==================================================================

					#Addition des rasters residus + regression
					entries2 = [] #definition des entree pour l addition raster residus + regression 
					rastReg = QgsRasterCalculatorEntry() #definition premier raster (regression lineaire)
					objReg = processing.getObject(lmr['REGRESSION']) 
					rastReg.ref = 'rastReg@1'
					rastReg.raster = objReg
					rastReg.bandNumber=1

					entries2.append(rastReg)

					rastRes = QgsRasterCalculatorEntry() #definition second raster (residus kriges)
					objRes = processing.getObject(ordinaryKriging['USER_GRID'])
					rastRes.ref = 'rastRes@1'
					rastRes.raster = objRes
					rastRes.bandNumber=1

					entries2.append(rastRes)

					getPathTemp = objEmp.dataProvider().dataSourceUri() #recuperation du chemin d un fichier stocke comme temporaire
					splitPathTemp= getPathTemp[:-10] #suppression du nom du fichier en fin de chaine
					outputCalc2 = splitPathTemp + 'icu.tif' #remplacement du nom du fichier par le nom de la sortie voulu pour le raster calculator
					print('output icu =', outputCalc2) #verification 

					calc=QgsRasterCalculator('rastReg@1+rastRes@1', outputPath1 ,'GTiff', objFracVille.extent(), objFracVille.width(), objFracVille.height(),entries2) #calculatrice raster
					calc.processCalculation()
					progress.setValue(100)

					iface.addRasterLayer(outputPath1, "INTERPOLATION")
					interObj = processing.getObject(outputPath1)
					interObj.setCrs(QgsCoordinateReferenceSystem(epsg, QgsCoordinateReferenceSystem.EpsgCrsId))
						
						
					my_crs = core.QgsCoordinateReferenceSystem(epsg, core.QgsCoordinateReferenceSystem.EpsgCrsId)
					iface.mapCanvas().mapRenderer().setDestinationCrs(my_crs)

