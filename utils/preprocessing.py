import os
import glob
from lxml import objectify
import cv2 as cv

class PreProcessing(object):
    def __init__(self,dir_annotations,dir_images) -> None:
        self.dir_annotations = dir_annotations
        self.dir_images = dir_images
    
    def get_annotations(self)->list:

        """Esse método extrai as informações dos arquivos dos rotulos e os adiciona em um dicionário 
        depois adiciona todos os dicionarios em uma lista e retorna"""

        annotations = glob.glob(self.dir_annotations+'/*')
        dataset = []
        for file in annotations:
            sample = {}
            lxml = objectify.parse(file)
            sample['path_image'] = os.path.join(self.dir_images,lxml.find('filename').text)
            size = lxml.find('size')
            sample['width'] = size.width
            sample['height'] = size.height
            labels = []
            locations = []
            objects = lxml.findall('object')
            for obj in objects:
                xmin = int(obj.bndbox.xmin)
                ymin = int(obj.bndbox.ymin)
                xmax = int(obj.bndbox.xmax)
                ymax = int(obj.bndbox.ymax)
                
                location = [xmin,ymin,xmax,ymax]
                
                label = obj.name.text
                labels.append(label)
                locations.append(location)
            
            sample['labels'] = labels
            sample['locations'] = locations
            
            dataset.append(sample)
        
        return dataset
    
    def resize_annotations(self,size)->list:

        """ redimensiona os bounding boxes para o tamanho da determinado. Esse mapeamento e  feito da seguinte forma:
        novo_x = (nova_largura*atual_x)/atual_largura
        novo_y = (nova_altura*atual_y)/atual_altura """

        dataset = self.get_annotations()
        for sample in dataset:
            new_locations=[]
            for location in sample['locations']:
                new_xmin = int((size[0]*location[0])/sample['width'])
                new_ymin = int((size[1]*location[1])/sample['height'])
                new_xmax = int((size[0]*location[2])/sample['width'])
                new_ymax = int((size[1]*location[3])/sample['height'])
                
                new_location = [new_xmin,new_ymin,new_xmax,new_ymax]
                new_locations.append(new_location)
            sample['locations'] = new_locations
        
        return dataset
    
    def resize_images(self,size) -> list:

        """redimensiona as imagens de para o tamanho especificado"""

        dataset = self.get_annotations()
        images = []
        for sample in dataset:
            img = cv.imread(sample['path_image'])
            img_red = cv.resize(img,size)
            images.append(img_red)
        
        return images

    def resize_dataset(self,size) -> tuple:

        """redimensiona as imagens e os bouding boxes"""

        images = self.resize_images(size)
        annotations = self.resize_annotations(size)

        return (images,annotations)

    