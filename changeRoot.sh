#!/bin/bash
ROTFS=$PWD/myContainer
if [ ! -d $ROTFS ];then
    mkdir -p $ROTFS/{bin,proc,etc,var/www}
    cd       $ROTFS/bin/
    cp       /bin/busybox .
    for P in $(./busybox --list | grep -v busybox); do ln -s busybox $P; done;
    cd ..
    cd ..
    cp /etc/mime.types $ROTFS/etc/
    cp -r $PWD/world_wide_web/files $ROTFS/var/www/
    cp $PWD/myServer_static $ROTFS/bin/myServer
    echo "::once:/bin/myServer" >  $ROTFS/etc/inittab
 
fi
 
sudo PATH=/bin unshare -f -p --mount-proc /usr/sbin/chroot $ROTFS bin/init

#  # Inspisere:
#  pstree -p UNSHARE_PID
#  ps -o pid,ppid,uid,tty,cmd PID1 PID2 ...
 
#  # teste: 
#  curl localhost:8080/hallo.txt
#  # Starte et shell med (alle) samme naverom som PID
#  sudo nsenter -t PID -a 
