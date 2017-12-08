"layertodds.py" has to be placed into the gimp plug-in folder. (something like "C:\Program Files\GIMP 2\lib\gimp\2.0\plug-ins").
If you start GIMP AFTERWARDS, you get a new Option unter "Image": "Save to dds". You can use this both while an image is opened or if not. It opens a window with the following
entries:

Input image and Input drawable (only visible if no file is open): Ignore those. Needed to allow starting both with and without open file.
Image file: 	The xcf file with different layers
Layer file : 	txt file containing the different outputs wanted: Each line is one output file. First entry is filename. 
		Afterwards layers (by name or index, see "Layer by Name"). Names with whitespaces have to be in quotes!
Output folder: 	valid folder (didn't find a way to select a folder, sry)
Layer by Name: 	Decides whether layers are chosen by name or index. Index would be the order in which they are visible in the layer view. 
		Top entry is 0. List can also be accessed from behind (-1 is last, -2 second to last, etc)
