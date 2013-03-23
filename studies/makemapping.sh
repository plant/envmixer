#
# mturk/makemapping.sh
# envmixer
#
# 2013 Brandon Mechtley
# Arizona State University
#
# Create a CSV file where each row has two filenames per .wav file in the directory. The first filename is the original
# filename. The second filename is an MD5 hash of the original filename.
#

for f in *.wav
do 
    echo $f, $(echo $f | md5 -q).wav
done > mapping.txt
