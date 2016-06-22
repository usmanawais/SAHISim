#!/usr/bin/bash

for i in "$@"
do
	lxterminal -e "python $i"
done


