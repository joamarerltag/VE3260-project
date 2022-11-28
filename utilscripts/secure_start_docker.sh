#!/usr/bin/env sh
CAP="SETUID SETGID"
CAPADD=""
FIRST=0
for L in $CAP
do
    if [ "$FIRST" = "0" ]; then
        CAPADD="--cap-add $L"
        FIRST=1
    else
        CAPADD="$CAPADD --cap-add $L"
    fi
done
echo $CAPADD
sudo docker run --rm -p $1:80 -d --net mein_netz --ip $3 --cpuset-cpus 0 --cpu-shares 256 --cap-drop ALL $CAPADD $2 
