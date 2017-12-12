# Dicom Scraper

This is currently under development, and builds two docker images that both aim to find and replace potential PHI in dicom images.

 - [ocr](ocr) "optical character recognititon" is an image that runs text (letter detection) on a demo image. You can either detect (just find and report) or clean the data (and save cleaned png images).
 - [manual](manual) uses known manufacturer and machine types to flag images, and then coordinates associated with those findings to clean (black out) the images.
