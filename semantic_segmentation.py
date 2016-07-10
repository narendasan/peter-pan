# -*- coding: utf-8 -*-
"""
This package contains code for the "CRF-RNN" semantic image segmentation method, published in the 
ICCV 2015 paper Conditional Random Fields as Recurrent Neural Networks. Our software is built on 
top of the Caffe deep learning library.
 
Contact:
Shuai Zheng (szheng@robots.ox.ac.uk), Sadeep Jayasumana (sadeep@robots.ox.ac.uk), Bernardino Romera-Paredes (bernard@robots.ox.ac.uk)

Supervisor: 
Philip Torr (philip.torr@eng.ox.ac.uk)

For more information about CRF-RNN, please vist the project website http://crfasrnn.torr.vision.
"""

"""
Filter image generation code using the semantic segmentation library referred to above was writing at Greylock Hackfest - Naren Dasan
"""


caffe_root = 'tps/crfasrnn/caffe/'
import sys
sys.path.insert(0, caffe_root + 'python')

import os
import cPickle
import logging
import numpy as np
import pandas as pd
from PIL import Image as PILImage
#import Image
import cStringIO as StringIO
import caffe
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

MAX_SUBJECTS = 3
MODEL_FILE = 'tps/crfasrnn/python-scripts/TVG_CRFRNN_new_deploy.prototxt'
PRETRAINED = 'tps/crfasrnn/python-scripts/TVG_CRFRNN_COCO_VOC.caffemodel'
PALLETE =  [0,0,0,
            128,0,0,  #Airplane
            0,128,0, #Bicycle
            128,128,0, #Bird
            0,0,128, #Boat
            128,0,128, #Bottle
            0,128,128,  #Bus
            128,128,128, #Car
            64,0,0,  #Cat
            192,0,0, #Chair
            64,128,0, #Cow
            192,128,0, #Dining Table
            64,0,128, #Dog
            192,0,128, #Horse
            64,128,128, #Motorbike
            192,128,128, #Person
            0,64,0, #Potted Plant
            128,64,0, #Sheep
            0,192,0, #Sofa
            128,192,0, #Train
            0,64,128, #TV/Monitor
            128,64,128,
            0,192,128,
            128,192,128,
            64,64,0,
            192,64,0,
            64,192,0,
           192,192,0]

PALLETE_MEANING = [
    "None",
    "Airplane",
    "Bicycle",
    "Bird",
    "Boat",
    "Bottle",
    "Bus",
    "Car",
    "Cat",
    "Chair",
    "Cow",
    "Dining Table",
    "Dog",
    "Horse",
    "Motorbike",
    "Person",
    "Potted Plant",
    "Sheep",
    "Sofa",
    "Train",
    "TV/Monitor",
]

def main():
    image_file = str(sys.argv[1])
    if len(sys.argv) > 2:
        out_path = str(sys.argv[2])
        find_subjects(image_file, out_path)
    else:
        find_subjects(image_file)

def find_subjects(image_file, outpath = "output.jpg"):
    #caffe.set_mode_gpu()
    net = caffe.Segmenter(MODEL_FILE, PRETRAINED)
    input_image = 255 * caffe.io.load_image(image_file)


    width = input_image.shape[0]
    height = input_image.shape[1]
    maxDim = max(width,height)

    image = PILImage.fromarray(np.uint8(input_image))
    image = np.array(image)
    plt.imshow(image)


    mean_vec = np.array([103.939, 116.779, 123.68], dtype=np.float32)
    reshaped_mean_vec = mean_vec.reshape(1, 1, 3);

    # Rearrange channels to form BGR
    im = image[:,:,::-1]
    # Subtract mean
    im = im - reshaped_mean_vec

    # Pad as necessary
    cur_h, cur_w, cur_c = im.shape
    pad_h = 500 - cur_h
    pad_w = 500 - cur_w
    im = np.pad(im, pad_width=((0, pad_h), (0, pad_w), (0, 0)), mode = 'constant', constant_values = 0)
    # Get predictions
    segmentation = net.predict([im])
    segmentation2 = segmentation[0:cur_h, 0:cur_w]
    output_im = PILImage.fromarray(segmentation2)
    output_im.putpalette(PALLETE)

    plt.imshow(output_im)
    plt.savefig('output.png')
    subjects = subject_detection(decode_segmentation(output_im.getcolors()))
    output = create_filter(PILImage.open(image_file), output_im, subjects, outpath)
    return output

def decode_segmentation(colors):
    contents = []
    for c in colors:
        contents.append(PALLETE_MEANING[c[1]])
    return contents

def subject_detection(contents):
    important_contents = []
    while len(contents) != 0 and len(important_contents) <= MAX_SUBJECTS:
        print contents
        if "Person" in contents:
            important_contents.append("Person")
            contents.remove("Person")
            print "person"
            continue
        if "Dog" in contents:
            important_contents.append("Dog")
            contents.remove("Dog")
            print "dog"
            continue
        if "Cat" in contents:
            important_contents.append("Cat")
            contents.remove("Cat")
            print "cat"
            continue
        if "Car" in contents:
            important_contents.append("Car")
            contents.remove("Car")
            print "car"
            continue
        if "Bike" in contents:
            important_contents.append("Bike")
            contents.remove("Bike")
            print "bike"
            continue
        else:
            break
    return important_contents

def create_filter(input_im, output_im, subjects, out_path):
    out = PILImage.new("RGB", input_im.size, "black")
    filter_im = out.load()
    input_im = input_im.convert('RGB')
    output_im = output_im.convert('RGB')
    print type(input_im)
    print type(output_im)
    filter_colors = []
    for s in subjects:
        idx = get_meaning_key(s) * 3
        filter_colors.append((PALLETE[idx], PALLETE[idx + 1],  PALLETE[idx + 2]))
    filter_im = PILImage.new("RGB", output_im.size, "black")
    w, h = output_im.size
    for x in range(0, w):
        for y in range(0, h):
            for f in filter_colors:
                if output_im.getpixel((x,y)) == f:
                    filter_im.im.putpixel((x,y), input_im.getpixel((x,y)))
                    break
    print out_path

    filter_im.save(out_path)
    return filter_im

def get_meaning_key(subject):
    for i in range(0, len(PALLETE_MEANING)):
        if subject == PALLETE_MEANING[i]:
            return i

if __name__ == "__main__":
    main()
