#!/usr/bin/python

from gimpfu import pdb, PF_STRING, register, main,PF_FILE ,PF_BOOL,PF_INT
import shlex
import os

def createTechIcons(timg, tdrawable,file,folder, outFolder,scaleTo):
  for fileName in os.listdir(folder):
    # backGroundImage=pdb.gimp_file_load(file, file)
    # backGroundLayer=backGroundImage.layers[0]
    if fileName[-4:]!=".dds":
      continue
    outFile=outFolder+"/"+"tech_"+fileName
    image=pdb.gimp_file_load(folder+"/"+fileName, folder+"/"+fileName)
    pdb.gimp_image_scale(image,scaleTo,scaleTo)
    pdb.gimp_image_resize(image,52,52,-1,-1)
    for layer in image.layers:
      pdb.gimp_layer_resize_to_image_size(layer)
    # layer_group = pdb.gimp_layer_group_new(image)
    layer_group=pdb.gimp_item_get_parent(image.layers[0])
    layer=pdb.gimp_file_load_layer(image, file)
    pdb.gimp_image_insert_layer(image,layer,layer_group,1)#(image, layer, parent, position)
    for layer in image.layers:
      pdb.gimp_item_set_visible(layer,True)
    layer = pdb.gimp_image_merge_visible_layers(image, 0)
    pdb.gimp_image_set_active_layer(image, layer)
    drawable = pdb.gimp_image_get_active_layer(image)
    # with open("E:/out.txt",'w') as outTxt:
    #   outTxt.write(outFile)
    pdb.file_dds_save(image, drawable, outFile,outFile,0,0,0,0,0,0,0)
    # pdb.gimp_file_save(image, drawable, outFile+".xcf",outFile+".xcf")
    # break


args = [
(PF_FILE , 'file', 'Background file', '.'),
(PF_STRING , 'folder', 'Icon folder', '.'),
(PF_STRING , 'outFolder', 'Output folder', '.'),
(PF_INT , 'scaleTo', 'Pixel Number', 54)
]
#register('layertodds', "Saves layers to dds","Saves layers to dds","Gratak","Gratak",2017,"<Image>/Image/Save to dds", "RGB*, GRAY*",
# [
#                 (PF_INT, "max_width", "Maximum Width", 500),
#                 (PF_INT, "max_height", "Maximum Height", 500),
#                 (PF_BOOL, "copy", "Make a JPEG copy", TRUE),
#         ], layerToDDS)
register('createTechIcons', "Create Tech Icons","Create Tech Icons","Gratak","Gratak","2017","<Image>/Image/Create Tech Icons",'', args, [], createTechIcons)

main()