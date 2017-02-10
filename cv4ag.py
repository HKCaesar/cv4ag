#!usr/bin/python
"""
Top Layer for the Computer Vision 4 Agriculture (cv4ag) framework
Lukas Arnold
WB-DIME
Jan 30 2017

The framewoArk consists of four parts

1. Parsing input data
2. Downloading satellite images
3. Overlaying data with sattelite images
4. Training
5. Application
"""
import argparse,sys,os
#import subdirectories to python path
sys.path.append('scripts')
sys.path.append('modules')
sys.path.append('lib')
import parse,get_satellite,overlay,train,clean
#-------------------------------------------------------------------
def ml():
	pass

#----------------------------------------------------------------------
#Main
if __name__ == "__main__":
	# get options from command line
	class myParse(argparse.ArgumentParser): # override error message to show usage
		def error(self, message):
			sys.stderr.write('error: %s\n' % message)
			self.print_help()
			sys.exit(2)
	cmdParser = myParse(\
		description='Machine Learning Framework for Agricultural Data.',
		add_help=True)
	cmdParser.add_argument('module',
		metavar='OPTION',
		type=str,default=False,
		help='The modules to be loaded. OPTION: \n\
			all - all modules (except clear).\n\
			parse - input file parser.\n\
			satellite - get satellite data.\n\
			overlay - overlay classification with satellite data. \n\
			train - train.\n\
			ml - apply machine learning algorithm.\n\
			clear - clear generated data from previous run on input file')
	cmdParser.add_argument('mapbox_token',
		metavar='MAPBOX_TOKEN',
		type=str,default=False,nargs='?',
		help='Mapbox token to download satellite images .')
	cmdParser.add_argument('-i',
		type=str,default=None,metavar='FILE',
		help='Input file. Do not give if data obtained by script.')
	cmdParser.add_argument('-s',metavar='FILE',
		type=str,default=None,
		help='Script file to obtain data')
	cmdParser.add_argument('-o',metavar='PATH',
		type=str,default="data/",
		help='Output folder. Satellite data are put in and read from\
			PATH/sat/.')
	cmdParser.add_argument('-c',metavar='N',
		type=int,default=1000,
		help='Number of satellite images to download.')
	cmdParser.add_argument('-z',metavar='N',
		type=int,default=17,
		help='Zoom level. Min=15, Max=19. See libs/satellite_resolutions.csv for resolutions.')
	cmdParser.add_argument('-x',metavar='N',
		type=int,default=480,
		help='Images have width N pixel.')
	cmdParser.add_argument('-y',metavar='N',
		type=int,default=360,
		help='Images have height N pixel.')
#	cmdParser.add_argument('-o1',metavar='PATH',
#		type=str,default="data/",
#		help='Output file after parsing stage.')
#	cmdParser.add_argument('-o2',metavar='PATH',
#		type=str,default="data/",
#		help='Output file after training stage.')
#	cmdParser.add_argument('-o3',metavar='PATH',
#		type=str,default="data/",
#		help='Output file after ml stage.')
	cmdParser.add_argument('-d',metavar='FILETYPE_CODE',
		type=str,default=None,
		help='Specify file type. Will find to detect filetype automatically. \
			Will not prompt for vector conversion if not given.\
			See www.gdal.org/formats_list.html or\
			www.gdal.org/ogr_formats.html \
			(or libs/*_formats.csv for FILETYPE_CODEs.')
	cmdParser.add_argument('--lonshift',metavar='N.N',
		type=float,default=0,
		help='Longitudanal shift of training data.')
	cmdParser.add_argument('--latshift',metavar='N.N',
		type=float,default=0,
		help='Lateral shift of training data .')
	cmdParser.add_argument('--shiftformat',metavar='N',
		type=int,default=0,
		help='Format of longitudinal/lateral shift.\
		0: As fraction of image. 1: Georeferenced unites.')
	cmdParser.add_argument('--top',metavar='N',
		type=int,default=15,
		help='Get N most frequent classes.')
	cmdParser.add_argument('--key',
		type=str,default='Descriptio',
		help='Set parameter key for category in GIS file to classify data.')
	cmdParser.add_argument('--epsg',metavar='N',
		type=int,default=None,
		help='EPSG format for GIS data. Is read from data if not set.')
	cmdParser.add_argument('--layer',metavar='N',
		type=int,default=None,
		help='Number of layer to be trained on.')
	cmdParser.add_argument('--arg1',
		type=str,default=None,
		help='Argument 1 for script.')
	cmdParser.add_argument('--arg2',
		type=str,default=None,
		help='Argument 2 for script.')
	cmdParser.add_argument('--arg3',
		type=str,default=None,
		help='Argument 3 for script.')
	cmdParser.add_argument('--arg4',
		type=str,default=None,
		help='Argument 4 for script.')
	cmdArgs = vars(cmdParser.parse_args())
	selectedModule = cmdArgs.get('module')
	mapboxtoken = cmdArgs.get('mapbox_token')
	inputFile = cmdArgs.get('i')
	outputFolder = cmdArgs.get('o')
	zoomLevel= cmdArgs.get('z')
	datatype = cmdArgs.get('d')
	satelliteCount = cmdArgs.get('c')
	xpixel = cmdArgs.get('x')
	ypixel = cmdArgs.get('y')
	scriptFile = cmdArgs.get('s')
	scriptArg1 = cmdArgs.get('arg1')
	scriptArg2 = cmdArgs.get('arg2')
	scriptArg3 = cmdArgs.get('arg3')
	scriptArg4 = cmdArgs.get('arg4')
	scriptArg4 = cmdArgs.get('arg4')
	lonshift= cmdArgs.get('lonshift')
	latshift= cmdArgs.get('latshift')
	layernumber = cmdArgs.get('layer')
	shiftformat = cmdArgs.get('shiftformat')
	key = cmdArgs.get('key')
	top = cmdArgs.get('top')
	epsg = cmdArgs.get('epsg')
	
	# Execute according to options
	print "Option:",selectedModule
	if selectedModule == 'all':
		inputFile,stats,elements=\
		parse.parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,datatype=datatype,top=top,layernumber=layernumber ,
			key=key,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2,
			scriptArg3=scriptArg3,scriptArg4=scriptArg4)
		get_satellite.get_satellite(inputFile=inputFile,
			mapboxtoken=mapboxtoken,
			count=satelliteCount,
			zoomLevel=zoomLevel,
			outputFolder=outputFolder,
			epsg=epsg,
			xpixel=xpixel,
			ypixel=ypixel,
			elements=elements)
		overlay.overlay(outputFolder,inputFile,
			xpixel=xpixel,
			ypixel=ypixel,
			zoomLevel=zoomLevel,
			lonshift=lonshift,latshift=latshift,
			shiftformat=shiftformat,
			top=top,
			stats=stats,
			count=satelliteCount,
			epsg=epsg,
			key=key,
			elements=elements\
			)
		train.train(outputFolder=outputFolder,
			inputFile=inputFile)
		ml()
	elif selectedModule == 'parse':
		parse.parse(inputFile=inputFile,outputFolder=outputFolder,
			scriptFile=scriptFile,datatype=datatype,top=top,layernumber=layernumber, 
			key=key,
			scriptArg1=scriptArg1,scriptArg2=scriptArg2,
			scriptArg3=scriptArg3,scriptArg4=scriptArg4)
	elif selectedModule == 'satellite':
		get_satellite.get_satellite(inputFile=inputFile,
			mapboxtoken=mapboxtoken,
			count=satelliteCount,
			zoomLevel=zoomLevel,
			epsg=epsg,
			outputFolder=outputFolder,
			xpixel=xpixel,
			ypixel=ypixel)
			
	elif selectedModule == 'overlay':
		overlay.overlay(outputFolder,inputFile,
			xpixel=xpixel,
			ypixel=ypixel,
			zoomLevel=zoomLevel,
			lonshift=lonshift,latshift=latshift,
			shiftformat=shiftformat,
			top=top,
			epsg=epsg,
			count=satelliteCount,
			key=key
			)
	elif selectedModule == 'train':
		train.train(outputFolder=outputFolder,
			inputFile=inputFile)
	elif selectedModule == 'mltrain':
		ml()
	elif selectedModule == 'clear':
		clean.clear(inputFile)
	else:
		print "error - no valid option"
		cmdParser.print_help()
