import numpy as np
from skimage.io import imread
from skimage.filters import threshold_otsu
from skimage.transform import resize
import cPickle
import matplotlib
from matplotlib import pyplot as plt
from pylab import fill
from skimage.morphology import closing, square
from skimage.measure import regionprops
from skimage import restoration
from skimage import measure
from skimage.color import (
    label2rgb,
    rgb2gray
)
import matplotlib.patches as mpatches
from pydicom import read_file


class UserData():
    '''class in charge of dealing with User Image input.
       the methods provided are finalized to process the image and return 
       the text contained in it.
    '''
    
    def __init__(self,dicom_file,verbose=False):
        '''reads the dicom image provided by the user as and preprocesses it.
        '''
        dicom = read_file(dicom_file,force=True)
        self.image = dicom.pixel_array
        self.verbose = verbose
        #self.image = imread(image_file, as_grey=True)
        self.preprocess_image()
    
################################################################################

    def preprocess_image(self):
        '''Denoises and increases contrast. 
        '''
        image = restoration.denoise_tv_chambolle(self.image, weight=0.01)
        thresh = threshold_otsu(image)
        self.bw = closing(image > thresh, square(2))
        self.cleared = self.bw.copy()
        return self.cleared 
    
################################################################################

    def get_text_candidates(self):
        '''identifies objects in the image. Gets contours, draws rectangles
           around them and saves the rectangles as individual images.
        '''
        label_image = measure.label(self.cleared)   
        borders = np.logical_xor(self.bw, self.cleared)
        label_image[borders] = -1
        
        samples = None
        coordinates = []
        i=0
        
        for region in regionprops(label_image):

            # NOTE: this is rather rough, to estimate that text is greater
            # than some size but less than others, can be improved upon
            if region.area > 2 and region.area < 200:
                minr, minc, maxr, maxc = region.bbox

                # Add some padding
                margin = 3
                minr, minc, maxr, maxc = minr-margin, minc-margin, maxr+margin, maxc+margin

                roi = self.image[minr:maxr, minc:maxc]
                if roi.shape[0]*roi.shape[1] == 0:
                    continue
                else:
                    if i==0:
                        samples = resize(roi, (20,20))
                        coordinates.append(region.bbox)
                        i+=1
                    elif i==1:
                        roismall = resize(roi, (20,20))
                        samples = np.concatenate((samples[None,:,:], roismall[None,:,:]), axis=0)
                        coordinates.append(region.bbox)
                        i+=1
                    else:
                        roismall = resize(roi, (20,20))
                        samples = np.concatenate((samples[:,:,:], roismall[None,:,:]), axis=0)
                        coordinates.append(region.bbox)
        
        if samples is None:
            return None

        if len(samples) > 3:            
            flattened = samples.reshape((samples.shape[0], -1))
        elif len(samples) == 1:
            return None
        else:
            flattened = samples.reshape(1,400)

        self.candidates = {
                    'fullscale': samples,          
                    'flattened': flattened,
                    'coordinates': np.array(coordinates)
                    }

        if self.verbose:        
            print('Images After Contour Detection')
            print('Fullscale: ', self.candidates['fullscale'].shape)
            print('Flattened: ', self.candidates['flattened'].shape)
            print('Contour Coordinates: ', self.candidates['coordinates'].shape)
            print('============================================================')
        
        return self.candidates 
    
################################################################################

    def select_text_among_candidates(self, model_filename2):
        '''it takes as argument a pickle model and predicts whether the
           objects contain text or not. 
        '''
        with open(model_filename2, 'rb') as fin:
            model = cPickle.load(fin)
            
        is_text = model.predict(self.candidates['flattened'])
        
        self.to_be_classified = {
                                 'fullscale': self.candidates['fullscale'][is_text == '1'],
                                 'flattened': self.candidates['flattened'][is_text == '1'],
                                 'coordinates': self.candidates['coordinates'][is_text == '1']
                                 }

        if self.verbose:
            print('Images After Text Detection')
            print('Fullscale: ', self.to_be_classified['fullscale'].shape)
            print('Flattened: ', self.to_be_classified['flattened'].shape)
            print('Contour Coordinates: ', self.to_be_classified['coordinates'].shape)
            print('Rectangles Identified as NOT containing Text '+ 
                   str(self.candidates['coordinates'].shape[0]-self.to_be_classified['coordinates'].shape[0]) +
                   ' out of '+str(self.candidates['coordinates'].shape[0]))
            print('============================================================')
        
        return self.to_be_classified
    
################################################################################

    def classify_text(self, model_filename36):
        '''it takes as argument a pickle model and predicts character
        '''
        with open(model_filename36, 'rb') as fin:
            model = cPickle.load(fin)
            
        which_text = model.predict(self.to_be_classified['flattened'])
        
        self.which_text = {'fullscale': self.to_be_classified['fullscale'],
                           'flattened': self.to_be_classified['flattened'],
                           'coordinates': self.to_be_classified['coordinates'],
                           'predicted_char': which_text }     

        return self.which_text

################################################################################

    def realign_text(self,show=True):
        '''processes the classified characters and reorders them in a 2D space 
           generating a matplotlib image. 
        '''
        max_maxrow = max(self.which_text['coordinates'][:,2])
        min_mincol = min(self.which_text['coordinates'][:,1])
        subtract_max = np.array([max_maxrow, min_mincol, max_maxrow, min_mincol]) 
        flip_coord = np.array([-1, 1, -1, 1])
        
        coordinates = (self.which_text['coordinates'] - subtract_max) * flip_coord
        
        ymax = max(coordinates[:,0])
        xmax = max(coordinates[:,3])
        
        coordinates = [list(coordinate) for coordinate in coordinates]
        predicted = [list(letter) for letter in self.which_text['predicted_char']]
        to_realign = zip(coordinates, predicted)
        
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for char in to_realign:
            ax.text(char[0][1], char[0][2], char[1][0], size=16)
        ax.set_ylim(-10,ymax+10)
        ax.set_xlim(-10,xmax+10)  
               
        if show:
            plt.show()
        return plt


    def realign_text_save(self,output_file):
        '''realign text and save to output file'''
        plt = self.realign_text(show=False)
        plt.savefig(output_file)


################################################################################

    def scrape(self,show=True):
        '''fill coordinates with black. I suppose that's akin to scraping.
        '''
                  
        coordinates = self.which_text["coordinates"]
        coordinates = [list(coordinate) for coordinate in coordinates]
        image = self.image.copy()        
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for coordinate in coordinates:
            minr, minc, maxr, maxc = coordinate
            print("Scrubbing (%s,%s,%s,%s)" %(minr, minc, maxr, maxc))
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                      fill=True, facecolor='black', edgecolor='black', linewidth=2)
            ax.add_patch(rect)
            
            # Add some padding
            margin = 3
            minr, minc, maxr, maxc = minr-margin, minc-margin, maxr+margin, maxc+margin
            ax.imshow(image)
            #fill([minr,minc,maxr,maxc], 'r', alpha=0.2, edgecolor='r')
            
                           
        if show:
            plt.show()
        return plt


    def scrape_save(self,output_file):
        '''realign text and save to output file'''
        plt = self.scrape(show=False)
        plt.savefig(output_file)



################################################################################

    def plot_to_check(self, what_to_plot, title, show=True):
        '''plots images at several steps of the whole pipeline, just to check
           output what_to_plot is the name of the dictionary to be plotted
        '''
        n_images = what_to_plot['fullscale'].shape[0]
        
        fig = plt.figure(figsize=(12, 12))

        if n_images <=100:
            if n_images < 100:
                total = range(n_images)
            elif n_images == 100:
                total = range(100)
           
            for i in total:
                ax = fig.add_subplot(10, 10, i + 1, xticks=[], yticks=[])
                ax.imshow(what_to_plot['fullscale'][i], cmap="Greys_r")  
                if 'predicted_char' in what_to_plot:
                    ax.text(-6, 8, str(what_to_plot['predicted_char'][i]), fontsize=22, color='red')
            plt.suptitle(title, fontsize=20)
            if show:
                plt.show()  
        else:
            total = list(np.random.choice(n_images, 100)) 
            for i, j in enumerate(total):
                ax = fig.add_subplot(10, 10, i + 1, xticks=[], yticks=[])
                ax.imshow(what_to_plot['fullscale'][j], cmap="Greys_r")  
                if 'predicted_char' in what_to_plot:
                    ax.text(-6, 8, str(what_to_plot['predicted_char'][j]), fontsize=22, color='red')
            plt.suptitle(title, fontsize=20)
            if show:
                plt.show()   
        return plt


    def plot_to_check_save(self, what_to_plot, title, output_file):
        '''run plot_to_check, but save to output_file instead'''
        plt = self.plot_to_check(what_to_plot=what_to_plot, 
                            title=title,
                            show=False)
        plt.savefig(output_file)



    def doprint(self,image,output_file):
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(12, 12))
        ax.imshow(image)
        plt.savefig(output_file)    
        plt.close()
    
################################################################################
  
    def plot_preprocessed_image(self,show=True):
        '''plots pre-processed image. The plotted image is the same as obtained at the end
        of the get_text_candidates method.
        '''
        image = restoration.denoise_tv_chambolle(self.image, weight=0.1)
        thresh = threshold_otsu(image)
        bw = closing(image > thresh, square(2))
        cleared = bw.copy()
        
        label_image = measure.label(cleared)
        borders = np.logical_xor(bw, cleared)
       
        label_image[borders] = -1
        image_label_overlay = label2rgb(label_image, image=image)
        
        fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(12, 12))
        ax.imshow(image_label_overlay)
        
        for region in regionprops(label_image):
            if region.area < 5:
                continue
        
            minr, minc, maxr, maxc = region.bbox
            rect = mpatches.Rectangle((minc, minr), maxc - minc, maxr - minr,
                                      fill=False, edgecolor='red', linewidth=2)
            ax.add_patch(rect)
        
        if show:
            plt.show()       
        return plt


    def save_preprocessed_image(self,output_file):
        '''save a preprocessed image'''
        plt = self.plot_preprocessed_image(show=False)
        plt.savefig(output_file)
