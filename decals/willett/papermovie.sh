#!/bin/bash
#
# Example:
# > ./papermovie.sh analysis/decals_gz_analysis.pdf

# Inspiration: https://github.com/brownsys/paper-movies

# Issues:
#   Had to install ImageMagick (several times) with homebrew
#   Fixed font list via http://stackoverflow.com/questions/24696433/why-font-list-is-empty-for-imagemagick
#   Original codec (libx264) did not work on current version of ffmpeg

filename=$1

# Set the remote and/or branches for the git repository
remote=origin
branch=master

# Make sure the branch is currently up to date
git pull $remote $branch
git checkout $branch

# Find only the commits for the file to make into a movie
git log -- $filename  > pdflog
grep "commit" pdflog | awk '{print $2}' > commits.txt
mv commits.txt movie/commits.txt
rm -Rf pdflog

# Download the versioned PDFs by resetting to specific commits
rev=1
while read p; do
    echo "Commit $p"
    git reset --hard $p
    cp $filename movie/$rev.pdf

    # Use ImageMagick to turn the paginated PDF into a single image
    # Note that the tile sizes (and possibly geometry) will change if paper is longer
    # than 14 pages
    montage movie/$rev.pdf -tile 7x2 -background white -geometry 213x275-15+4 movie/$rev.png

    let rev+=1
done < movie/commits.txt

# Modify images in ImageMagick again to make them suitable for movie frames
# Reverse sort in this loop so that the paper goes in chronological order
x=0
for f in `ls -1 movie/*.png | grep -v "movie\-1.png" | sort -nr`; do
    n=`printf "%03d" $x`
    # Rename frames for ffmpeg's format style
    mv $f movie/$n.png
    convert movie/$n.png -crop 1280x568+0+0 movie/a$n.png
    mv -f movie/a$n.png movie/$n.png
    let x+=1
done

# Pick the final filename
arr=$(echo $filename | tr ";" "\n")
IFS='/' read -a fnameonly <<< "$filename"
x=${fnameonly[${#fnameonly[@]}-1]}
IFS='.' read -a stub <<< "$x"

# Create the movie
ffmpeg -r 5 -i movie/%03d.png -vcodec mpeg4 -pix_fmt yuv420p -b 8000k movie/$stub.mov

# Clean up extra files in the folder
rm -f movie/*.pdf
rm -f movie/*.png
rm -f movie/commits.txt

# Checkout the most recent version again
git pull $remote $branch
git checkout $branch
