#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pycocotools.coco import COCO
import numpy as np
import skimage.io as io
import matplotlib.pyplot as plt
import pylab

image_directory = '/media/aditya/A69AFABA9AFA85D9/Datasets/fat/mixed/extra/kitchen_0/'
annotation_file = '/media/aditya/A69AFABA9AFA85D9/Datasets/fat/mixed/extra/kitchen_0/instances_fat_train2018.json'

example_coco = COCO(annotation_file)

categories = example_coco.loadCats(example_coco.getCatIds())
category_names = [category['name'] for category in categories]
print('Custom COCO categories: \n{}\n'.format(' '.join(category_names)))

category_names = set([category['supercategory'] for category in categories])
print('Custom COCO supercategories: \n{}'.format(' '.join(category_names)))

category_ids = example_coco.getCatIds(catNms=['square'])
image_ids = example_coco.getImgIds(catIds=category_ids)
image_data = example_coco.loadImgs(image_ids[np.random.randint(0, len(image_ids))])[0]

print(image_data)

plt.figure()
image = io.imread(image_directory + image_data['file_name'])
plt.imshow(image); plt.axis('off')

plt.figure()
plt.imshow(image); plt.axis('off')
pylab.rcParams['figure.figsize'] = (8.0, 10.0)
annotation_ids = example_coco.getAnnIds(imgIds=image_data['id'], catIds=category_ids, iscrowd=None)
annotations = example_coco.loadAnns(annotation_ids)
example_coco.showAnns(annotations)
plt.show()