#!/bin/bash          

if [ $# -gt 0 ]; then

        groups $1 | cut -d: -f2 | cut -d ' ' -f2- | sed 's/ /,/g'

else
        echo "Arguments missing"
fi