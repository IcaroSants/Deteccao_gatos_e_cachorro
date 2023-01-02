import numpy as np
import random
import json
class Generator(object):

    def IoU(self,annotate,centroids):
        """ calcula o IoU entre a largura e altura de uma amostra com o centroide """

        w, h = annotate
        simalarities = []

        for centroid in centroids:
            c_w, c_h = centroid

            if c_w >= w and c_h >= h:
                similarity = w*h/(c_w*c_h)
            elif c_w >= w and c_h<=h:
                 similarity = w*c_h/(w*h + (c_w-w)*c_h)
            elif c_w<= w and c_h>=h:
                 similarity = c_w*h/(w*h + c_w*(c_h - h))
            else:
                similarity =  (c_w*c_h)/(w*h)
            
            simalarities.append(similarity)

        return np.array(simalarities)
    
    def k_means(self,annotations,num_anchor):
        """Descobre os clusters que serão as ancoras para a yolo. Os centroides são iniciados aletoriamente, 
        depois as amostras são associadas aos clusters de menor distancia ( nesse caso a metrica de distancia é a de jaccard)
        apos isso os clusters são atualizados e o processo se repete ate não haver mais mudanças de clusters."""

        ann_num = annotations.shape[0]
        prev_assigments = np.ones(ann_num)*(-1)
        iterations = 0

        indices = [random.randrange(annotations.shape[0]) for i in range(num_anchor)]
        centroids = annotations[indices]
        anchor_dim = annotations.shape[1]

        while True:
            iterations+=1
            distances = []
            for i in range(ann_num):
                d = 1 - self.IoU(annotations[i],centroids)
                distances.append(d)
            distances = np.array(distances)
            
            
            assigments = np.argmin(distances,axis=1)
            
            

            if (assigments == prev_assigments).all():
                return centroids
            
            centroid_sums = np.zeros((num_anchor,anchor_dim),np.float)
            for i in range(ann_num):
                centroid_sums[assigments[i]]+=annotations[i]
            for j in range(num_anchor):
                centroids[j] = centroid_sums[j]/(np.sum(assigments==j) + 1e-6)
            
            prev_assigments = assigments.copy()
            
    def calculate_anchor(self, annotations, num_anchor, size_image, grid):
        
        object_dimensions=[]
        for sample in annotations:
            for location in sample['locations']:
                pos_w = (location[2]-location[0])/size_image[0] # xmax-xmin/grid_w
                pos_h = (location[3] - location[1])/size_image[1] #ymax-ymin/grid_h

                object_dimensions.append((pos_w,pos_h))
        
        object_dimensions = np.array(object_dimensions)
        centroids = self.k_means(object_dimensions,num_anchor)

        return centroids
    
    def calculate_IoU_bbox(self,bbox1,bbox2):
        """Calcular o IoU entre 2 bounding boxes"""
        i_xmin = np.maximum(bbox1[0],bbox2[0])
        i_ymin = np.maximum(bbox1[1],bbox2[1])
        i_xmax = np.minimum(bbox1[2],bbox2[2])
        i_ymax = np.minimum(bbox1[3],bbox2[3])

        i_width = np.maximum(i_xmax-i_xmin +1,np.array(0.0))
        i_height = np.maximum(i_ymax-i_ymin +1,np.array(0.0))

        area_intersection = i_width*i_height

        bbox1_width = bbox1[2] - bbox1[0]
        bbox1_height = bbox1[3] - bbox1[1]

        area_bbox1 = bbox1_width* bbox1_height

        bbox2_width = bbox2[2] - bbox2[0]
        bbox2_height = bbox2[3] - bbox2[1]
        area_bbox2 = bbox2_width* bbox2_height
        
        area_union =  area_bbox1 + area_bbox2 - area_intersection
        iou = area_intersection / area_union

        return iou
    
    
         