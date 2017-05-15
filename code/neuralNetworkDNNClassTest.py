#  Copyright 2016 The TensorFlow Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
"""Convolutional Neural Network Estimator for MNIST, built with tf.layers."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import numpy as np
import tensorflow as tf
import bpy
import math
import random
import datetime

from tensorflow.contrib import learn
from tensorflow.contrib.learn.python.learn.estimators import model_fn as model_fn_lib

tf.logging.set_verbosity(tf.logging.INFO)

bpy.data.scenes[0].render.engine = 'CYCLES'

print('-'*50)

# gather data
scene = bpy.context.scene
render = scene.render
rw,rh,rp = render.resolution_x,render.resolution_y,render.resolution_percentage
rw,rh = int(rw * rp / 100), int(rh * rp / 100)

if 'combined' in bpy.data.images:
    bpy.data.images.remove(bpy.data.images['combined'], do_unlink=True)
bpy.data.images.new('combined', rw, rh)
cimg = bpy.data.images['combined']
cpix = [0 for _ in range(rw) for _ in range(rh) for _ in range(4)]
ctot = [0 for _ in range(rw) for _ in range(rh) for _ in range(4)]
counts = [0 for _ in range(rw) for _ in range(rh)]
prev_pix = cpix[:]
difImArray = [0 for _ in range(rw * rh)]

# set alpha
for ix in range(rw):
    for iy in range(rh):
        cpix[(iy*rw+ix)*4+3] = 1
        ctot[(iy*rw+ix)*4+3] = 1

def renderRegion(x,y,w,h,s, fn):
    global rw,rh,rwp,rhp
    global cimg,cpix,ctot,counts
    
    # ensure we're only working with ints
    x,y,w,h,s = map(int,[x,y,w,h,s])
    
    print('rendering: (%d,%d)x(%d,%d)@%d' % (x,y,w,h,s))
    
    # set up render borders to focus render on specific region
    rl,rr = x - math.floor(w/2), x + math.ceil(w/2)
    rb,rt = y - math.floor(h/2), y + math.ceil(h/2)
    rl,rr = max(0, min(rw-1, rl)),max(0, min(rw-1, rr))
    rb,rt = max(0, min(rh-1, rb)),max(0, min(rh-1, rt))
    render.use_border = True            # tell renderer to use border (below)
    render.use_crop_to_border = False   # keep same size (do not crop)
    # note: render border is [0,1]x[0,1], not [0,width)x[0,height)
    render.border_min_x = rl / rw
    render.border_min_y = 1 - rt / rh
    render.border_max_x = rr / rw
    render.border_max_y = 1 - rb / rh
    
    # set the correct number of samples per pixel
    scene.cycles.samples = s     # not s2
    scene.cycles.aa_samples = s
    scene.cycles.use_square_samples = False
    
    # ensure (probabilistically) that the PRNG uses a different seed
    # for each render 
    scene.cycles.seed = random.randint(0,100000)
    
    # tell blender to render to file located in same folder
    render.filepath = bpy.path.abspath('//../images/%s' % fn)
    
    # do the render!
    bpy.ops.render.render(write_still=True)
    
    # load render into new image (do be deleted)
    img = bpy.data.images.load('//../images/%s' % fn)
    pix = [v*s for v in img.pixels]
    bpy.data.images.remove(img, do_unlink=True) # delete render image
    
    # aggregate
    print('aggregating partial render')
    # leaving a small border...
    for ix in range(rl+1,rr-1):
        for iy in range((rh-1)-rt+1,(rh-1)-rb-1):
            idx,idx4 = iy*rw+ix,(iy*rw+ix)*4
            counts[idx] += s
            for ic in range(3):
                ctot[idx4+ic] += pix[idx4+ic]
                cpix[idx4+ic] = math.pow(ctot[idx4+ic] / counts[idx], 1.0)

def imageDif(im1, im2, x, y, w, h):
    #print(image1, image2)
    global difImArray
    global rw, rh
    maxDif = 0
    maxTuples = [(0,0,0,0)]
#    for ix in range(rw):
#        for iy in range(rh):
#            difImArray[(iy*rw+ix)*4+3] = 1

    lx = x - math.floor(w/2)
    ty = y - math.floor(h/2)
    rx = x + math.ceil(w/2)
    by = y + math.ceil(h/2)
    for row in range(ty, by):
        for col in range(lx, rx):
            pix1 = [im1[((row*rw)+col)*4], im1[((row*rw)+col)*4 + 1], im1[((row*rw)+col)*4 + 2]]
            pix2 = [im2[((row*rw)+col)*4], im2[((row*rw)+col)*4 + 1], im2[((row*rw)+col)*4 + 2]]
            #print(pix1, pix2)
            r = (pix2[0] - pix1[0]) ** 2
            g = (pix2[1] - pix1[1]) ** 2
            b = (pix2[2] - pix1[2]) ** 2
            ave = (r + g + b) / 3
            difImArray[((row*rw)+col)] = ave
#    bpy.data.images.new("difImage", rw, rh)
#    difIm = bpy.data.images["difImage"]
#    difIm.pixels = difImArray
#    difIm.save_render(bpy.path.abspath('//../images/difImage.png'))
#    bpy.data.images.remove(difIm, do_unlink=True)

def main():
    global cpix, difImArray
#    featurePix = np.asarray(cpix, dtype=np.float32)
#    img = bpy.data.images.load('//../images/target.png')
#    targetPix = np.asarray(img.pixels, dtype=np.float32)
#    bpy.data.images.remove(img, do_unlink=True) # delete render image
    targetPix = np.zeros(len(difImArray), dtype=np.int32)
    
    total_samples = 100 * rw * rh
    renderBoxes = [[rw/4, rh/2, rw/2, rh, 20], [(3*rw)/4 , rh/2, rw/2, rh, 20], [rw/8, rh/4, rw/4, rh/2, 40],
    [(3*rw)/8, rh/4, rw/4, rh/2, 40], [(5*rw)/8, rh/4, rw/4, rh/2, 40], [(7*rw)/8, rh/4, rw/4, rh/2, 40], 
    [rw/8, (3*rh)/4, rw/4, rh/2, 40], [(3*rw)/8, (3*rh)/4, rw/4, rh/2, 40], [(5*rw)/8, (3*rh)/4, rw/4, rh/2, 40], 
    [(7*rw)/8, (3*rh)/4, rw/4, rh/2, 40]]
    
    x,y,w,h,s = rw//2,rh//2,rw,rh,10
    renderRegion(x,y,w,h,s, 'full.png')
    
    prev_pix = cpix[:]
    renderRegion(x,y,w,h,s, 'full2.png')
    
    print("Finding Dif Image")
    imageDif(cpix,prev_pix,x,y,w,h)
    prev_pix = cpix[:]
    featurePix = np.asarray(difImArray, dtype=np.float32)
#  Load training and eval data
#  mnist = learn.datasets.load_dataset("mnist")
#  train_data = mnist.train.images  # Returns np.array
#  train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
#  eval_data = mnist.test.images  # Returns np.array
#  eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)

    def features():
        yield featurePix

    difPix = tf.contrib.learn.infer_real_valued_columns_from_input(features())
    
    # Create the Estimator
    nn = learn.DNNClassifier(feature_columns=difPix,
                                hidden_units=[rw*rh, rw*rh, rw*rh],
                                activation_fn=tf.nn.relu,
                                dropout=0.2,
                                n_classes=10,
                                optimizer="SGD")

    # Set up logging for predictions
    # Log the values in the "Softmax" tensor with label "probabilities"
    tensors_to_log = {"pixels"}
    logging_hook = tf.train.LoggingTensorHook(tensors=tensors_to_log, every_n_iter=10)

    # Train the model
    nn.fit(
        x=featurePix,
        y=targetPix,
        steps=1)
        
    print("\n\n\nHello World!!!\n\n\n")

    # Configure the accuracy metric for evaluation
#    metrics = {
#        "accuracy":
#            learn.MetricSpec(
#                metric_fn=tf.metrics.accuracy, prediction_key="render_section"),
#    }
    
    while total_samples > 0:
        # Evaluate the model and print results
#        eval_results = nn.evaluate(
#            x=featurePix, y=targetPix, metrics=metrics)
#        print(eval_results)
        prediction = nn.predict(x=features(), batch_size=1, as_iterable=False)
        print(prediction)
        
        renderSection = renderBoxes[prediction["render_section"][0]]
    
        # render partial high-res
        x,y,w,h,s = renderSection[0], renderSection[1], renderSection[2], renderSection[3], renderSection[4]
        renderRegion(x,y,w,h,s, 'partial.png')
        total_samples = total_samples - (s * w * h)

        # update combined (aggregate) image
        cimg.pixels = cpix
        cimg.save_render(bpy.path.abspath('//../images/combined.png'))
        
        featurePix = np.asarray(cpix, dtype=np.float32)
    print("finished")
  
main()