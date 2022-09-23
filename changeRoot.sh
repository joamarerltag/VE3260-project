#!/bin/bash
ROTFS=$PWD/unshare-container2
if [ ! -d $ROTFS ];then
    mkdir -p $ROTFS/{bin,proc,etc,var/www}
    cd       $ROTFS/bin/
    cp       /bin/busybox .
    for P in $(./busybox --list | grep -v busybox); do ln busybox $P; done;
    echo "::once:/bin/httpd -p 8080 -h /var/www" >  $ROTFS/etc/inittab
 
    echo "hallo" >  $ROTFS/var/www/hallo.txt
 
fi
 
sudo PATH=/bin unshare -f -p --mount-proc /usr/sbin/chroot $ROTFS bin/init

#  # Inspisere:
#  pstree -p UNSHARE_PID
#  ps -o pid,ppid,uid,tty,cmd PID1 PID2 ...
 
#  # teste: 
#  curl localhost:8080/hallo.txt
#  # Starte et shell med (alle) samme naverom som PID
#  sudo nsenter -t PID -a 
