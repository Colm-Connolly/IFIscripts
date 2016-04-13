'''
WORK IN PROGRESS - BROKEN RIGHT NOW
'''
import subprocess
import sys
import os
import pdb
from glob import glob
import hashlib
import base64
import csv

filename = sys.argv[1]
csvfile  = os.path.expanduser("~/Desktop/myfile.csv")
print csvfile

f = open(csvfile, 'wt')
try:
    writer = csv.writer(f)
    writer.writerow( ('Title 1', 'Title 2', 'Title 3') )
   
finally:
    f.close()
#pdb.set_trace()

wd = os.path.dirname(filename)

os.chdir(wd)
def get_count(variable,typee):
       
    variable = subprocess.check_output(['xml', 'sel', 
                                             '-N', 'x=http://www.smpte-ra.org/schemas/429-8/2007/PKL',
                                             '-t', '-v', typee,
                                             filename ])
    return variable
count = get_count('count',"count(//x:Asset)")

print '\n%s MXFs found - Generating fresh hashes and comparing them against hashes stored in the PKL.XML\n' % count
def getffprobe(variable, streamvalue, which_file):
    variable = subprocess.check_output(['ffprobe',
                                                '-v', 'error',
                                                '-show_entries', 
                                                streamvalue,
                                                '-of', 'default=noprint_wrappers=1:nokey=1',
                                                which_file])
    return variable

def get_cpl(variable,typee,element,xml_file):
    
        
        variable = subprocess.check_output(['xml', 'sel', 
                                                 '-N', 'x=http://www.smpte-ra.org/schemas/429-7/2006/CPL',
                                                 '-t', '-m', typee,
                                                 '-v', element,
                                                 '-n', xml_file ])
        return variable                 
# Find all video files to transcode
video_files =  glob('*.mxf')
xml_files  = glob('*.xml')
mxfhashes = {}
for mxfs in video_files:
    
    mxf_uuid = (getffprobe('mxf_uuid','stream_tags=file_package_umid', mxfs)).replace('\n', '').replace('\r', '')
    mxf_uuid =  mxf_uuid[-32:].lower ()
    mxf_uuid  = mxf_uuid[:8] + '-' + mxf_uuid[8:12] + '-' +  mxf_uuid[12:16] + '-' + mxf_uuid[16:20] + '-' + mxf_uuid[20:32]
    print 'Generating fresh hash for the file %s' % mxfs     
    
    bla = subprocess.check_output(['openssl', 'sha1', '-binary', mxfs])
    b64hash =  base64.b64encode(bla)                  
    mxfhashes[mxf_uuid] = [mxfs,b64hash]
    f = open(csvfile, 'a')
    try:
        writer = csv.writer(f)
        writer.writerow( (b64hash, 'Title 2', 'Title 3') )
   
    finally:
        f.close()

for xmls in xml_files:
    with open(xmls) as f:   # open file
                for line in f:       # process line by line
                    if "http://www.smpte-ra.org/schemas/429-7/2006/CPL" in line:    
                        #print 'found CPL in file %s' %xmls
                        bla = subprocess.check_output(['openssl', 'sha1', '-binary', xmls])
                        b64hash =  base64.b64encode(bla)    
                        xml_uuid = get_cpl('xml_uuid', "x:CompositionPlaylist", "x:Id", xmls).replace('\n', '').replace('\r', '')
                        #print xml_uuid

                        mxfhashes[xml_uuid[-36:]] = [xmls,b64hash]
#print mxfhashes
xml_files =  glob('*.xml')


dict = {}


def get_hash(variable,typee,element):
    
        
        variable = subprocess.check_output(['xml', 'sel', 
                                                 '-N', 'x=http://www.smpte-ra.org/schemas/429-8/2007/PKL',
                                                 '-t', '-m', typee,
                                                 '-v', element,
                                                 '-n', filename ])
        return variable
 

counter = 1    
while counter <= int(count):
    
    picture_files = get_hash('picture_files',"//x:Asset" + "[" + str(counter) + "]" , "x:Hash").replace('\n', '').replace('\r', '')
    
    urn = get_hash('picture_files',"//x:Asset" + "[" + str(counter) + "]" , "x:Id")
    
    counter += 1
    urn = urn.replace('\n', '').replace('\r', '')
    dict[urn[-36:]] = picture_files

#print dict

for key in dict:
    if mxfhashes[key][1] == dict[key]:
       print mxfhashes[key][0] + ' HASH MATCH - GO ABOUT YOUR DAY'
    else:
       print mxfhashes[key][0] + ' HASH MISMATCH - EITHER THE SCRIPT IS BROKEN OR YOUR FILES ARE'
    
    
