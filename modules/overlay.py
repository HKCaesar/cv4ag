#!usr/bin/python
'''
Overlay classes and satellite data
'''
import os,csv,json
import utils.gdal_rasterize as gdal_rasterize
from PIL import Image
from functools import partial
from multiprocessing import Pool
from utils.coordinate_converter import CoordConvert
from utils.getImageCoordinates import imageCoordinates
from modules.getFeatures import latLon,find_between
from modules.get_stats import get_stats
from libs.colorlist import colorlist
from libs.foldernames import *

def rasterLayer(i,stats,subpath,size,te):
	'''converts feature geojson to png image'''
	feature=stats[i]
	i+=1
	print "Layer "+str(i)+"/"+str(len(stats))+'\t Processing feature: '+feature
	outFile=subpath+"/f_"+str(i)+".png"
	featureFile =subpath+"/"+featureDataFolder+"/f_"+str(i)+".json" 
	try:
		os.remove(outFile)
	except OSError:
		pass
	gdal_rasterize.rasterize(	\
		featureFile,
		outFile,
		ts=size,		# set resolution
		out_format='PNG',
		init=0,
		te=te,
		burn_values=[i])				# set image limits in te

	#make 0s transparent to prepare for merge	
	img = Image.open(outFile)
	img = img.convert("RGBA")
	datas = img.getdata()
	newData = []
	for item in datas:
	    if item[0] == 0 and item[1] == 0 and item[2] == 0:
		newData.append((0, 0, 0, 0))
	    else:
		newData.append(item)
	img.putdata(newData)
	img.save(outFile, "PNG")

	#os.remove(featureFile)

def createLayer(i,stats,subpath,inputFile,key):
	'''creates sub geojson files with only one feature property'''
	feature=stats[i]
	i+=1
	print "Processing feature:",feature,i,"/",len(stats)
	featureFile = subpath+"/"+featureDataFolder+"/f_"+str(i)+".json"
	if not os.path.isfile(featureFile): 
		print "\tOpening input file... ",
		with open(inputFile,'r') as f:
			elementsInstance=json.load(f)
		print "Done."
		#delete every item that is not feature
		cntdel=0
		print "\tExtracting layers... ",
		for i in range(0,len(elementsInstance['features'])):
			#print elementsInstance['features'][cntdel]['properties']
			if str(elementsInstance['features'][cntdel]['properties'][key])!=feature:
				#print "del", elementsInstance['features'][cnt_featureelement]
				del elementsInstance['features'][cntdel]	
			else:
				cntdel+=1
		#for i in range(0,len(elementsInstance['features'])):
		#	print elementsInstance['features'][i]['properties']
		print "Done."
		print "\tStoring layer file... ",
		try:
			os.remove(featureFile)
		except OSError:
			pass
		with open(featureFile,'w+') as f:
			json.dump(elementsInstance,f)
		print "Done."
	else:
		print "\tFile",featureFile,"already exists."

def overlay(outputFolder,inputFile,xpixel=480,ypixel=360,zoomLevel=None,lonshift=0,latshift=0,
	shiftformat=1,top=10,stats=None,count=None,key='Descriptio',epsg=None,
	elements=None,randomImages=False):
	'''
	Overlays images in satiImageFolder
	with data in inputFile
	'''
	
	if not zoomLevel:
		print "Warning: Zoom level not set. Assuming zoom level 17."
		zoomLevel = 17

	#Get list of images
	samples_data = {}
	#set outputFolder to directory above the /sat directory
	if outputFolder[-1]=="/":
		outputFolder=outputFolder[0:-1]
	if outputFolder[-3:]==satDataFolder[1:-1]:
		outputFolder=outputFolder[0:-4]

	#Make directory for subfiles
	subpath=outputFolder+"/"+os.path.split(inputFile)[-1][:-5]
	for subsubpath in ['',trainingDataFolder,checkDataFolder,testDataFolder,featureDataFolder]:
		if not os.path.isdir(subpath+subsubpath):
			os.mkdir(subpath+subsubpath)
			print 'Directory',subpath+subsubpath,'created'

	#load data and check if images in folder
	#has to be png image and start with input filename
	image_files = [f for f in os.listdir(subpath+satDataFolder) if f.endswith('.png') \
		and f.startswith(os.path.split(inputFile)[-1][:-5])] 
	if len(image_files)==0:
		print "Error: No images found in",subpath+satDataFolder[0:-1]
		exit()
	else:
		print "Number of images found:",len(image_files)
		if count:
			print "Create",count,"images"
		else:
			print "Create",len(image_files),"images"

	print 'Get GIS elements...'
	if not elements:
		print 'Opening %s...' % inputFile
		with open(inputFile, 'r') as f:
			elements = json.load(f)
	#Get statistics if not in input
	if not stats:
		stats,freq,_=get_stats(inputFile,top,verbose=True,key=key,\
			elements=elements)
	else:
		freq=None
	#Create json-file for each layer
	print "Create layer files..."
	if os.path.getsize(inputFile)>220000000:
		print "Very large input file of size ~",\
			int(os.path.getsize(inputFile)/1000000),"MB"
		print "Clearing memory...",
		elements=True
		print elements
		for i in range(0,len(stats)):
			createLayer(i,stats,subpath,inputFile,key)
		print 'Reopening %s...' % inputFile
		with open(inputFile, 'r') as f:
			elements = json.load(f)
	#initialize multi-core processing if file size not too large
	else:
		pool = Pool()
		print 'Map to cores...'	
		#create subfile for each feature	
		#pool only takes 1-argument functions
		partial_createLayer=partial\
			(createLayer,stats=stats,subpath=subpath,inputFile=inputFile,key=key) 
		pool.map(partial_createLayer, range(0,len(stats)))
		pool.close()
		pool.join()

	print "Layer files created..."

	#Get coordinate system
	myCoordConvert = CoordConvert()
	code=myCoordConvert.getCoordSystem(elements,epsg)
	#Get imageconverter
	myImageCoord=imageCoordinates(xpixel,ypixel,'libs/zoomLevelResolution.csv',zoomLevel)
	av_lats=[]
	av_lons=[]
	cnt = 1

	for image in image_files:
		#rasterize corresponding data
		print ''
		if count: 		#abort if maximum limit set and cnt above maximum limit
			if cnt>count:
				break
		# The index is between the last underscore and the extension dot
		print str(cnt)+'/'+str(len(image_files))
		index = int(find_between(image,"_",".png"))
		if randomImages: #get coordinates for random images
			av_lon=None
			with open(subpath+satDataFolder+"meta.csv","rb") as csvfile:
				 coordFile = list(csv.reader(csvfile,delimiter=",",quotechar='"'))
			for coord in coordFile:
				if coord[0]==str(index):
					av_lon=coord[1]
					av_lat=coord[2]
					break
			if not av_lon:
				av_lon,av_lat=latLon(elements['features'][index]) # get center points
		else:
			av_lon,av_lat=latLon(elements['features'][index]) # get center points
		#Convert to standard format
		if code != 4319: # if not already in wgs84 standard format
			lotlan= myCoordConvert.convert(av_lon,av_lat)
			longitude=lotlan[0]
			latitude=lotlan[1]
		else: #if already in wgs84 format
			latitude= av_lat
			longitude= av_lot
		print "Coordinates WSG84: "+str(longitude)+','+str(latitude)
		if (av_lon != longitude) and (av_lat != latitude):
			print "Coordinates Native: "+str(av_lon)+','+str(av_lat)
		#Calculate image coordinates in WSG 84
		image_box_lat,image_box_lon= myImageCoord.getImageCoord(latitude,longitude)
		#print 'Coordinates:',latitude,longitude
		#Convert back to original format
		if code != 4319: # if not already in wgs84 standard format
			image_box=\
				myCoordConvert.convertBack(image_box_lon,image_box_lat)
		else:
			image_box=image_box_raw
		image_lat = image_box[1]
		image_lon = image_box[0]	
		#print "Coordinates Native corner: "+str(image_lon[0])+','+str(image_lat[0])
		#print "Coordinates WSG84 corner: "+str(image_box_lon[0])+','+str(image_box_lat[0])

		cnt+=1
		tifile=subpath+trainingDataFolder+\
			os.path.split(image)[-1][0:-4]+"train.png" #path for raster tif file
		print 'Converting',image,'to',os.path.split(tifile)[-1]
		#shift factor
		west=(image_lon[0]+image_lon[2])/2
		south=min(image_lat)
		east=(image_lon[1]+image_lon[3])/2
		north=max(image_lat)
		if shiftformat == 0:					#if fraction as shift unit
			lonshift_calc=lonshift*abs(east-west)
			latshift_calc=latshift*abs(north-south)
		else:
			lonshift_calc=lonshift
			latshift_calc=latshift
		print "Shift applied:"
		print "Longitudinal \t",lonshift_calc
		print "Lateral \t",latshift_calc
		#set rasterize settings
		size=[xpixel,ypixel]
		te=[west-lonshift_calc,south-latshift_calc,\
			east-lonshift_calc,north-latshift_calc] #image bounderies 
		#print te
		print "Image bounderies:"
		print str(image_box_lon[0])[:-5],'\t',\
			str(image_box_lat[0])[:-5],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lon[1])[:-5],'\t',str(image_box_lat[1])[:-5]
		print '\t|\t\t\t\t\t\t\t\t\t\t|\t'
		print '\t|\t\t\t\t\t\t\t\t\t\t|\t'
		print str(image_box_lon[2])[:-5],'\t',\
			str(image_box_lat[2])[:-5],'\t----\t----\t----\t----\t----\t----',\
			str(image_box_lon[3])[:-5],'\t',str(image_box_lat[3])[:-5]
		
		#rasterize
		#rasterLayer(0,stats,subpath,size,te)
		if os.path.getsize(inputFile)>500000000:
			print "Very large input file size ~",\
				int(os.path.getsize(inputFile)/1000000),"MB"
			for i in range(0,len(stats)):
				rasterLayer(i,stats,subpath,size,te)
		else:
			pool = Pool()
			print 'Map to cores...'	
			#pool only takes 1-argument functions, so create partial function
			partial_rasterLayer=\
				partial(rasterLayer,stats=stats,subpath=subpath,size=size,te=te) 
			pool.map(partial_rasterLayer, range(0,len(stats)))
			pool.close()
			pool.join()

		#create output file
		try: #remove output file, if it already exists
			os.remove(tifile)
		except OSError:
			pass
		#merge first two pictures
		print "Merging images..."
		imgFile=subpath+"/f_"+str(1)+".png"
		background = Image.open(imgFile)
		if len(stats)>1:
			imgFile=subpath+"/f_"+str(2)+".png"
			foreground = Image.open(imgFile)
			background.paste(foreground, (0, 0), foreground)
		background.save(tifile)
		if len(stats)>2:
			for i in range(3,len(stats)+1):
				imgFile=subpath+"/f_"+str(i)+".png"
				background = Image.open(tifile)
				foreground = Image.open(imgFile)
				background.paste(foreground, (0, 0), foreground)
				background.save(tifile)

		#Create test images for visual checks
		checkfile=subpath+checkDataFolder+os.path.split(image)[-1][0:-4]+"check.png" #path for check files
		try:
			os.remove(checkfile)
		except OSError:
			pass
		background = Image.open(subpath+satDataFolder+image)
		brightened = Image.open(tifile)
		#brighten up visual images for check file
		#make 0s transparent to prepare for merge	
		datas = brightened.getdata()
		newData = []
		print "Creating check image..."
		try:
			for item in datas:
				for i in range(0,len(stats)):	
					if item[0] == 0 and item[1] == 0 and item[2] == 0 and item[3]==0:
						newData.append(item)
						break
					elif item[0] == i and item[1] == i and item[2] == i and item[3]==255:
						newData.append(colorlist[i-1])
						break
			brightened.putdata(newData)
		except IndexError:
			print "Warning: Color list for visual check file too short"

		background.paste(brightened, (0, 0), brightened)
		background.save(checkfile)

		#convert back to grayscale
		img = Image.open(tifile)
		img = img.convert("L")
		img.save(tifile, "PNG")
		print "Class label image",tifile," and check image created."
	#Clean up side data
	print "Cleanup..."
	for i in range(1,len(stats)+1):
#		try:
#			os.remove(subpath+"/f_"+str(i)+".json")
#		except OSError:
#			pass
		try:
			os.remove(subpath+"/f_"+str(i)+".png")
		except OSError:
			pass
		try:
			os.remove(subpath+"/f_"+str(i)+".png.aux.xml")
		except OSError:
			pass
	print "Overlaying done."
	return stats,freq
#	try:
#		os.rmdir(subpath)
#	except OSError:
#		pass
