import pickle
from random import choice
from glob import glob
import shutil
import os

# Each higher level folder has some number of subfolders
folders = '/fs/DICOM/sendit/8'


def make_choice(contenders, func=os.path.isdir):
    selection = None
    while selection is None:
        selection = choice(glob('%s/*' %contenders))
        if not func(selection):
            selection = None
    return selection 
    

dicom_files = []
while len(dicom_files) < 100:
    folder = make_choice(folders)
    subfolder = make_choice(folder)
    dicom_file = make_choice(subfolder, func=os.path.isfile)
    print('Making choice for %sth dicom file' %(len(dicom_files)+1))
    dicom_files.append(dicom_file)

# Make sure we have unique files
dicom_files = list(set(dicom_files))
print('Final set includes %s dicom_files' %len(dicom_files))

# Save list in case we need it again
home = os.environ['HOME']
test_location = '%s/TEST' %home
data_location = '%s/TEST/data' %home
os.mkdir(test_location)
os.mkdir(data_location)

# Save list
pickle.dump(dicom_files, open('%s/dicom-sample.pkl' %test_location,'wb')) 

# Let's copy them to a test location (can look up based on index if needed)
for d in range(len(dicom_files)):
    dicom_file = dicom_files[d]
    new_name = '%s/dicom-test-%s.dcm' %(data_location, d)
    shutil.copyfile(dicom_file, new_name)

# Share with everyone (bash)
# chmod -R g+rw $HOME/TEST
