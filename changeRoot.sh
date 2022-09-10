#!/bin/sh
 
mkdir www/bin
cd www/bin

cp /bin/busybox .
 
PRGS=$(./busybox --list)
for P in $PRGS; do
	ln -s busybox $P;
done
