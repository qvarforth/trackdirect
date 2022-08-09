#!/bin/bash
CURRENTDIR=$(dirname $0)

cd $CURRENTDIR/../htdocs
mkdir -p tmp

#
# Minimize and move to build dir
#
for file in $(find ../jslib/src/ -name '*.js')
do
    if [[ ${file} != *".min."* ]];then
        newFile="${file##*/}"
        newFile="tmp/${newFile//.js/}.min.js"
        echo "Processing $file -> $newFile"
        python -m jsmin $file > $newFile
        #cp $file $newFile
    else
        newFile="tmp/${file##*/}"
        echo "Processing $file -> $newFile"
        cp $file $newFile
    fi
done

#
# Create the full js file
#
cp tmp/trackdirect.min.js public/js/trackdirect.min.js
rm tmp/trackdirect.min.js
# Note that the order is important (may need to start adding digits in beginning of each js-file)
ls -vr tmp/*.js | xargs cat  >> public/js/trackdirect.min.js

#
# Remove temp dir
#
rm -R tmp

exit 0
