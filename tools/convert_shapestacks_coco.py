#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 28 15:15:34 2019

@author: aditya
"""

import datetime
import json
import os
import re
import fnmatch
from PIL import Image
import numpy as np
from pycococreatortools import pycococreatortools
from pathlib import Path
import skimage
import numpy as np
from matplotlib import pyplot as plt
from pycocotools.coco import COCO
import pylab
import json

ROOT_DIR = '/media/aditya/A69AFABA9AFA85D9/Datasets/shapestacks'
IMG_DIR = '/media/aditya/A69AFABA9AFA85D9/Datasets/shapestacks/jenga_recordings'
ROOT_OUTDIR = '/media/aditya/A69AFABA9AFA85D9/Datasets/shapestacks'
OUTFILE_NAME = 'instances_shapestacks_train2018'

#ROOT_DIR = '/media/aditya/A69AFABA9AFA85D9/Datasets/fat/mixed/val'
#IMAGE_DIR = os.path.join(ROOT_DIR, "kitchen_3")
#ANNOTATION_DIR = os.path.join(ROOT_DIR, "kitchen_3")
#OUTFILE_NAME = 'instances_fat_val2018'

INFO = {
    "description": "Example Dataset",
    "url": "https://github.com/waspinator/pycococreator",
    "version": "0.1.0",
    "year": 2018,
    "contributor": "waspinator",
    "date_created": datetime.datetime.utcnow().isoformat(' ')
}

LICENSES = [
    {
        "id": 1,
        "name": "Attribution-NonCommercial-ShareAlike License",
        "url": "http://creativecommons.org/licenses/by-nc-sa/2.0/"
    }
]

def get_num_blocks(scenario_name):
    r_str = re.search(r'n=\d+', scenario_name).group(0)
    num_blocks = int(r_str.lstrip('n='))
    return num_blocks

def get_seg_file_name(block_num, img_file, scenario_dir):
    base_filename = img_file.replace('rgb-', '').replace('-r=\d+-mono-0.png', '')
    base_filename = re.sub(r'-r=\d+-mono-0.png', '', base_filename)

    seg_file = 'vseg-{}-seg-{}.png'.format(base_filename, block_num)
    seg_file = os.path.join(scenario_dir, seg_file)
    return seg_file 

def filter_for_jpeg(root, IMG_DIR):
    

    scenario_list_file = os.path.join(root, 'predictions.json')
    with open(scenario_list_file) as f:
        scenario_list_dict = json.load(f)
    
    # files = []
    img_seg_files_dict = {}
    for scenario in list(scenario_list_dict.keys()):
        if scenario.endswith('_r') == False:
            scenario_path = os.path.join(IMG_DIR, scenario)
            for img_file in filter(
                lambda f: f.startswith('rgb-') and f.endswith('-mono-0.png'),
                os.listdir(scenario_path)):
                img_file_path = os.path.join(scenario_path, img_file)
                img_key = "{}/{}".format(scenario, img_file)
                # files.append(img_file_path)
                seg_files = []
                for b in range(get_num_blocks(scenario)):
                    seg_files.append(get_seg_file_name(b, img_file, scenario_path))
                img_seg_files_dict[img_key] = seg_files
                # print(seg_files)

    return img_seg_files_dict

def filter_for_annotations(root, files, image_filename):
    file_types = ['*.seg.png']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    basename_no_extension = os.path.splitext(os.path.basename(image_filename))[0]
    file_name_prefix = basename_no_extension + '.*'
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]
    files = [f for f in files if re.match(file_name_prefix, os.path.splitext(os.path.basename(f))[0])]

    return files

def filter_for_labels(root, files, image_filename):
    file_types = ['*.json']
    file_types = r'|'.join([fnmatch.translate(x) for x in file_types])
    basename_no_extension = os.path.splitext(os.path.basename(image_filename))[0]
    file_name_prefix = basename_no_extension + '.*'
    files = [os.path.join(root, f) for f in files]
    files = [f for f in files if re.match(file_types, f)]
    files = [f for f in files if re.match(file_name_prefix, os.path.splitext(os.path.basename(f))[0])]

    return files

def main():
    CLASS_ID = 1
    CATEGORIES = \
        [{
            'id': CLASS_ID,
            'name': 'jenga_block',
            'supercategory': 'shape',
        }]
            
    coco_output = {
        "info": INFO,
        "licenses": LICENSES,
        "categories": CATEGORIES,
        "images": [],
        "annotations": []
    }

    image_global_id = 1
    segmentation_global_id = 1

    # filter for jpeg images
    img_seg_files_dict = filter_for_jpeg(ROOT_DIR, IMG_DIR)
    # print(img_seg_files_dict)
    img_size = (224,224)

    for img_file_path in list(img_seg_files_dict.keys()):
        image_info = pycococreatortools.create_image_info(
                        image_global_id, img_file_path, img_size
                    )
        mask_valid = False
        for seg_file_path in img_seg_files_dict[img_file_path]:
            # Crowd has to be 0 or else no anno get loaded in maskrcnn
            category_info = {'id': CLASS_ID, 'is_crowd': 0}
            # print(seg_file_path)
            binary_mask = np.asarray(Image.open(seg_file_path))
            
            if np.count_nonzero(binary_mask) > 0:
                annotation_info = pycococreatortools.create_annotation_info(
                    segmentation_global_id, image_global_id, category_info, binary_mask,
                    img_size, tolerance=2)
                if annotation_info is not None:
                    coco_output["annotations"].append(annotation_info)
                    mask_valid = True
            
            segmentation_global_id += 1

        if mask_valid == True:
            pass
            coco_output["images"].append(image_info)
        else:
            print("No valid mask")

        if image_global_id % 100 == 0:
            print("Image {}/{}".format(image_global_id, len(list(img_seg_files_dict.keys()))))
        image_global_id = image_global_id + 1

    with open('{}/{}.json'.format(ROOT_OUTDIR, OUTFILE_NAME), 'w') as output_json_file:
        json.dump(coco_output, output_json_file)


if __name__ == "__main__":
    main()