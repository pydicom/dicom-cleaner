#!/usr/bin/env python3

'''

BSD 3-Clause License

Copyright (c) 2017, Vanessa Sochat
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

* Neither the name of the copyright holder nor the names of its
  contributors may be used to endorse or promote products derived from
  this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

'''

import matplotlib
matplotlib.use('pdf')

from matplotlib.backends.backend_pdf import PdfPages
from deid.utils import write_json
from glob import glob
import tempfile
import argparse
import shutil
import sys
import os


def get_parser():
    parser = argparse.ArgumentParser(
    description="Deid (de-identification) based on header tool.")

    parser.add_argument("--input","-i", dest='folder', 
                        help="input folder to search for images.", 
                        type=str, default=None)

    parser.add_argument("--outfolder","-o", dest='outfolder', 
                        help="full path to save output, will use /data/output folder if not specified", 
                        type=str, default='/data/output')

    parser.add_argument('--save',
                        default='pdf',
                        const='pdf',
                        nargs='?',
                        choices=['png', 'dicom', 'pdf'],
                        help='save as png, dicom, or, pdf (default: %(default)s)')

    parser.add_argument("--detect","-d", dest='detect', 
                        help="Only detect, but don't try to scrub", 
                        default=False, action='store_true')

    parser.add_argument("--deid", dest='deid', 
                        help="deid recipe, if don't want default", 
                        type=str, default=None)

    return parser



def main():

    parser = get_parser()

    try:
        args = parser.parse_args()
    except:
        sys.exit(0)

    from deid.dicom import get_files
    from logger import bot
    from deid.dicom import DicomCleaner

    if args.folder is None:
        bot.error("Please provide a folder with dicom files with --input.")
        sys.exit(1)

    dicom_files = get_files(args.folder)
    client = DicomCleaner(output_folder=args.outfolder, deid=args.deid)
    bot.info('Processing [images]%s [output-folder]%s' %(len(dicom_files), client.output_folder))
    outcomes = {True: 'flagged', False: '  clean'}

    # Keep a list of flagged and clean
    flagged = []
    clean = []
    summary = dict()

    # We will move images into respective folders
    if args.save is "pdf":
        pdf_report = '%s/deid-clean-%s.pdf' %(args.outfolder, len(dicom_files))
        pp = PdfPages(pdf_report)

    # Perform detection one at a time
    for dicom_file in dicom_files:

        dicom_name = os.path.basename(dicom_file)

        # detect --> clean
        result = client.detect(dicom_file)
        client.clean()
        summary[dicom_name] = result
  
        # Generate title/description for result
        title = '%s: %s' %(outcomes[result['flagged']], dicom_name)
        bot.info(title)

        # How does the user want to save data?
        if args.save == "dicom":
            outfile = client.save_dicom()

        elif args.save == "png":
            outfile = client.save_png(title=title)

        # pdf (default)
        else:
           plt = client.get_figure(title=title)
           fig = plt.gcf()
           pp.savefig(fig)
           plt.close(fig)

        # Whether dicom or png, append to respective list
        if args.save is not "pdf":
            if result['flagged']:
                flagged.append(outfile)
            else:
                clean.append(outfile)

    # Save summary json file
    summary_json = '%s/deid-clean-%s.json' %(args.outfolder, len(dicom_files))
    write_json(summary, summary_json)
    bot.info('json data written to %s' %summary_json)

    # When we get here, if saving pdf, close it.
    if args.save == "pdf":
        bot.info('pdf report written to %s' %pdf_report)
        pp.close()

    # Otherwise, move files into respective folders
    else:
        move_files(files=flagged, dest='%s/flagged' %args.outfolder)
        move_files(files=cleaned, dest='%s/clean' %args.outfolder)



def move_files(files, dest):
    ''' move a list of files to a common destination folder
    '''
    if not os.path.exists(dest):
        os.mkdir(dest)

    moved_files = []
    for filey in files:
        new_location = "%s/%s" %(dest, os.path.basename(filey))
        shutil.move(filey, new_location)
        moved_files.append(new_location)
    return moved_files


if __name__ == '__main__':
    main()
