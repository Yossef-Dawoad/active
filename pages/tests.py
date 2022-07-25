import re
from django.test import TestCase
import os
import glob
import ntpath
import sys


files = list()
rec_path  = os.path.join(os.path.abspath(os.getcwd()),'project\\static\\recordings')
output_directory = os.path.join(rec_path , 'mp4Videos\\')

input_directory = output_directory
aviFiles = glob.glob(rec_path + '/*.avi')
# print(aviFiles)
# print('#'*50)

# print('#'*50)
# print(output_directory)
# print('#'*50)
recs =os.listdir(output_directory) 
print()
for counter , rec in enumerate(recs):
    record = {rec:os.path.join(output_directory,rec) , 'counter':counter}
    files.append(record)

def last_videos(path):
    last = list()
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    for counter , rec in enumerate(recs):
        record = {rec:os.path.join(output_directory,rec) , 'counter':counter}
        last.append(record)
        
    for i in range(3):
        last.append(paths[i])
    return last


# print(last_videos(output_directory))
# # files = list()
# rec_path  = os.path.join(os.path.abspath(os.getcwd()),'project\\static\\recordings')
# output_directory = os.path.join(rec_path , 'mp4Videos\\')
# recs =os.listdir(output_directory) 



# print(last_videos(output_directory))

    # return paths
    # return max(paths, key=os.path.getctime )


# files = sorted(
# glob.iglob(recs), key=os.path.getctime, reverse=True) 
# print(files)



# list_of_files = glob.glob('/project/static/recordings/mp4Videos/') 
# latest_file = max(recs, key=os.path.getctime)
# for i in range(3):
# print(newest(output_directory))
  

# print(os.path.join(os.path.abspath(os.getcwd()),'project\\static\\recordings\\'))