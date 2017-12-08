#!/usr/bin/python

from gimpfu import pdb, PF_STRING, register, main,PF_FILE ,PF_BOOL
import shlex

def layerToDDS(timg, tdrawable,file,argumentFile, outFolder, byName):#, argumentFile,hmm,blub):
    # num_layers, layer_ids = pdb.gimp_image_get_layers(image)
    #with open("E:/out.txt",'w') as outTxt:
      with open(argumentFile,'r') as argfile:
        for l in argfile:
          image = pdb.gimp_file_load(file, file)
          line=shlex.split(l)
          outFile=outFolder+"/"+line[0]
          if outFile[-4:]!=".dds":
            outFile+=".dds"
          for layer in image.layers:
          #   layer = pdb.gimp_image_get_layer_by_name(image, id)
            pdb.gimp_item_set_visible(layer, False)
          layers=[]
          for i in line[1:]:
            #outTxt.write(i+"\n")
            #layers.append(pdb.gimp_layer_copy(image.layers[int(i)],False))
            #pdb.gimp_image_insert_layer(image, layer,image.layers[int(i)], 0)
            if byName:
              pdb.gimp_item_set_visible(pdb.gimp_image_get_layer_by_name(image, i),True)
            else:
              pdb.gimp_item_set_visible(image.layers[int(i)], True)

          # for layer in layers:
          #   outTxt.write("{!s}".format(layer))
          #   pdb.gimp_item_set_visible(layer, True)
          #pdb.gimp_item_set_visible(image.layers[3], True)
          #pdb.gimp_item_set_visible(image.layers[5], True)
          layer = pdb.gimp_image_merge_visible_layers(image, 0)
          pdb.gimp_image_set_active_layer(image, layer)
          drawable = pdb.gimp_image_get_active_layer(image)
          pdb.file_dds_save(image, drawable, outFile,outFile,0,0,0,0,0,0,0)
          pdb.gimp_image_remove_layer(image, layer)
    #pdb.file_dds_save(image, drawable, "E:/test.dds","E:/test.dds")
    #pdb.gimp_file_save(image, drawable, "E:/test.xcf","E:/test.xcf")
    #pdb.gimp_image_delete(image)

args = [
(PF_FILE , 'file', 'Image file', '.'),
(PF_FILE , 'argumentFile', 'Layer File', '.'),
(PF_STRING , 'outFolder', 'Output folder', '.'),
(PF_BOOL , 'byName', 'Layer by Name', True)
]
#register('layertodds', "Saves layers to dds","Saves layers to dds","Gratak","Gratak",2017,"<Image>/Image/Save to dds", "RGB*, GRAY*",
# [
#                 (PF_INT, "max_width", "Maximum Width", 500),
#                 (PF_INT, "max_height", "Maximum Height", 500),
#                 (PF_BOOL, "copy", "Make a JPEG copy", TRUE),
#         ], layerToDDS)
register('layertodds', "Saves layers to dds","Saves layers to dds","Gratak","Gratak","2017","<Image>/Image/Save to dds",'', args, [], layerToDDS)

main()