#!/usr/bin/env python3

'''

The MIT License (MIT)

Copyright (c) 2017-2019 Vanessa Sochat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

'''

from user import UserData
from glob import glob
import tempfile
import argparse
import skimage
import sys
import os
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")


def get_parser():
    parser = argparse.ArgumentParser(
    description="Deid (de-identification) pixel scaping tool.")

    # Single image, must be string
    parser.add_argument("--input","-i", dest='folder', 
                        help="input folder to search for images.", 
                        type=str, default=None)

    parser.add_argument("--outfolder","-o", dest='outfolder', 
                        help="full path to save output, will use /data folder if not specified", 
                        type=str, default=None)

    parser.add_argument("--detect","-d", dest='detect', 
                        help="Only detect, but don't try to scrub", 
                        default=False, action='store_true')


    parser.add_argument("--verbose","-v", dest='verbose', 
                        help="if set, print more image debugging to screen.", 
                        default=False, action='store_true')

    return parser



def main():

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    from deid.dicom import get_files
    from logger import bot

    if args.folder is None:
        bot.error("Please provide a folder with dicom files with --input.")
        sys.exit(1)

    dicom_files = get_files(args.folder)
    number_files = len(list(get_files(args.folder)))

    ##### the following includes all steps to go from raw images to predictions
    ##### pickle models are passed as argument to select_text_among_candidates
    ##### and classify_text methods are result of a previously implemented pipeline.
    ##### just for the purpose of clarity the previous code is provided. 
    ##### The commented code is the one necessary to get the models trained.

    # Keep a record for the user
    result = {'clean':0,
              'detected':0,
              'skipped':0,
              'total': number_files}
    
    # For each file, determine if PHI, for now just alert user
    for dicom_file in dicom_files:

        dicom_name = os.path.basename(dicom_file)

        # Try isn't a great approach, but if we log the skipped, we can debug
        try:
            dicom = UserData(dicom_file,
                             verbose=args.verbose)

            # plots preprocessed image
            if not args.detect:
                dicom_save_name = '/data/%s_preprocessed.png' % dicom_name
                dicom.save_preprocessed_image(dicom_save_name)

            # detects objects in preprocessed image
            candidates = dicom.get_text_candidates()
            clean = True

            if candidates is not None:

                if args.verbose:
                    number_candidates = len(candidates['coordinates'])
                    bot.debug("%s has %s text candidates" % (dicom_name,
                                                             number_candidates))
                # plots objects detected
                # dicom.plot_to_check_save(candidates, 
                #                          'Total Objects Detected', 
                #                          '/data/lao-detect-check.png')

                # selects objects containing text
                saved_model = '/code/data/linearsvc-hog-fulltrain2-90.pickle'
                maybe_text = dicom.select_text_among_candidates(saved_model)

                # plots objects after text detection
                # dicom.plot_to_check_save(maybe_text, 
                #                          'Objects Containing Text Detected', 
                #                          '/data/lao-detect-candidates.png')
                    
                # classifies single characters
                saved_model = '/code/data/linearsvc-hog-fulltrain36-90.pickle'
                classified = dicom.classify_text(saved_model)
                if args.verbose:
                    number_text = len(classified['coordinates'])
                    bot.debug("%s has %s classified text" %(dicom_name, 
                                                            number_text))

                if len(classified) > 0:
                    if args.verbose:
                        bot.warning("%s flagged for text content." % dicom_name)
                    clean = False
                else:
                    bot.info("%s is clean" % dicom_name)

            else:
                bot.info("%s is clean" % dicom_name)
        
            if clean:
                result['clean'] += 1
            else:
                result['detected'] += 1

            # plots letters after classification 
            # dicom.plot_to_check_save(classified, 
            #                          'Single Character Recognition',
            #                           '/data/lao-detect-letters.png')
        
            if not clean and not args.detect:
                dicom.scrape_save('/data/%s_cleaned.png' % dicom_name)

        except:
            bot.error("\nProblem loading %s, skipping" % dicom_name)
            result['skipped']+=1
        print('============================================================')
     
    # Final result
    print('\n=======================FINALRESULT==========================')
    print(os.path.basename(args.folder))
    print("DETECTED: %s" %result['detected'])
    print("SKIPPED:  %s" %result['skipped'])
    print("CLEAN:    %s" %result['clean'])
    print("TOTAL:    %s" %result['total'])
    

if __name__ == '__main__':
    main()

    
################################################################################
## MACHINE LEARNING SECTION
################################################################################
    #from data import OcrData
    #from cifar import Cifar
    #
    # data downloaded from https://www.kaggle.com/c/cifar-10/data
    # cd ocr/ # download files to here
    # 7z x train.7z  
    # 7z x test.7z  

    ####################################################################
    ## 1- GENERATE MODEL TO PREDICT WHETHER AN OBJECT CONTAINS TEXT OR NOT
    ####################################################################
    #
    # CREATES AN INSTANCE OF THE CLASS LOADING THE OCR DATA 
    #data = OcrData('/home/francesco/Dropbox/DSR/OCR/ocr-config.py')
    #data = OcrData('/code/ocr/text-config.py')
    #
    # GENERATES A UNIQUE DATA SET MERGING NON-TEXT WITH TEXT IMAGES
    #data.merge_with_cifar()
    #
    # PERFORMS GRID SEARCH CROSS VALIDATION GETTING BEST MODEL OUT OF PASSED PARAMETERS
    #data.perform_grid_search_cv('linearsvc-hog')
    #
    # TAKES THE PARAMETERS LINKED TO BEST MODEL AND RE-TRAINS THE MODEL ON THE WHOLE TRAIN SET
    #data.generate_best_hog_model()
    #
    # TAKES THE JUST GENERATED MODEL AND EVALUATES IT ON TRAIN SET
    #data.evaluate('/code/data/linearsvc-hog-fulltrain2-90.pickle')


    ####################################################################
    ## 2- GENERATE MODEL TO CLASSIFY SINGLE CHARACTERS
    ####################################################################
    #
    # CREATES AN INSTANCE OF THE CLASS LOADING THE OCR DATA 
    #data = OcrData('/code/ocr/ocr-config.py')
    #
    # PERFORMS GRID SEARCH CROSS VALIDATION GETTING BEST MODEL OUT OF PASSED PARAMETERS
    #data.perform_grid_search_cv('linearsvc-hog')
    #
    # TAKES THE PARAMETERS LINKED TO BEST MODEL AND RE-TRAINS THE MODEL ON THE WHOLE TRAIN SET
    #data.generate_best_hog_model()
    #
    # TAKES THE JUST GENERATED MODEL AND EVALUATES IT ON TRAIN SET
    #data.evaluate('/code/data/linearsvc-hog-fulltrain36-90.pickle')
