import processing
from qgis.analysis import QgsRasterCalculator, QgsRasterCalculatorEntry
import qgis.core
import os
from qgis.utils import *

##ICU=name

# Inputs

##mnt=raster
##stations=vector
##fieldTemp=field stations
##mapuce=optional vector
##frac_user=optional raster

#Outputs
##mnt_clip=output raster
##regression=output raster
##frac_ville=output raster
##lr_model=output table
##lr_residuals=output vector
##residuals_kriging=output raster


#Definition de l emprise
emprise=processing.runalg("qgis:fixeddistancebuffer", stations, 100,5,1, None) #buffer de 100m autour des stations

objEmp = processing.getObject(emprise['OUTPUT']) #recuperer buffer stations sous forme de QgsVectorLayer
rectangle= objEmp.extent() #recuperer l emprise de la couche buffer
coordinates = rectangle.toString(16) #convertir emprise sous forme de chaine de caractere
replace = coordinates.replace(":",",",1) #formater la chaine pour utilisation dans la fonction clip raster by extent
split = replace.split(",") #split de la chaine pour re-composition...
extent= split[0]+","+split[2]+","+split[1]+","+split[3] #...concatenation pour que l ordre des coordonnes decrivant l emprise corresponde a l ordre utilise dans clip raster by extent


#Decoupe MNT
mntExtent = processing.runalg("gdalogr:cliprasterbyextent", mnt, 0, extent, 5,4,75,6,1,0,0,0,'',None) #decoupe du mnt selon l emprise du buffer 100m autour des points
mntClip = processing.runalg("saga:resampling", mntExtent['OUTPUT'], True, 0,0, extent,100,mnt_clip)

#====================================================
dataMapuce = []
dataMapuce.append(mapuce)

if dataMapuce != [None] :#Si donnees MAPUCE en entrees:


    #Construction de la fraction de ville

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
    print('output calculator =', outputCalc) #verification 


    calc=QgsRasterCalculator('rast@1+rast@2+rast@3', outputCalc ,'GTiff', objBuild.extent(), objBuild.width(), objBuild.height(),entries) #calculatrice raster
    calc.processCalculation() #execution du calcul

    #Dimensionnement des rasters pour interpolation
    resamplFracVille = processing.runalg("saga:resampling", outputCalc, True, 0,0, extent,100,frac_ville) #dimensionnement de la fraction de ville mapuce
    
else : #Si pas de donnees MAPUCE en entree
    resamplFracVille = processing.runalg("saga:resampling", frac_user, True, 0,0, extent,100,frac_ville) #dimensionnement de la fraction de ville utilisateur




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
print (inputs) #verification

points = processing.getObject(stations) 
stationsPath = points.dataProvider().dataSourceUri() #recuperation du chemin de la couche de stations
splitStationsPath = stationsPath.split("|") #formatage du chemin pour usage dans l algorithme
stationsPathFinal = splitStationsPath[0] #formatage du chemin pour usage dans l algorithme
print(stationsPathFinal)#verification

lmr = processing.runalg("saga:multipleregressionanalysispointsgrids", inputs, stationsPathFinal,fieldTemp,0,True,True,0,5,5,None,lr_model,None,lr_residuals,regression) #regression lineaire multiple

#===================================================================

#Krigeage des residus
residualsObj = processing.getObject(lmr['RESIDUALS']) #recuperation puis formatage du chemin de la couche de residus issus de la regression lineaire
pathResiduals = residualsObj.dataProvider().dataSourceUri()
splitPathResiduals = pathResiduals.split("|")
residualsPathFinal = splitPathResiduals[0]
print(residualsPathFinal)
ordinaryKriging = processing.runalg("saga:ordinarykrigingglobal",residualsPathFinal,"RESIDUAL",1,False,False,100,-1,100,1,"a + b * x",True,extent,100,0,residuals_kriging,None) #krigeage ordinaire des residus

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

calc=QgsRasterCalculator('rastReg@1+rastRes@1', outputCalc2 ,'GTiff', objFracVille.extent(), objFracVille.width(), objFracVille.height(),entries2) #calculatrice raster
calc.processCalculation() 

iface.addRasterLayer(outputCalc2, "Interpolation")

