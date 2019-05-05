#!/bin/bash
FILE=/usb.bin
MOUNT=/mnt/usb

case $1 in
stop)
    modprobe -r g_mass_storage
    ;;
refresh)
    sync $MOUNT
    sleep 1
    modprobe -r g_mass_storage
    sleep 1
    modprobe g_mass_storage file=$FILE stall=0 ro=0 removable=1 nofua=1
    sleep 1
    service smbd restart
    umount $MOUNT
    sleep 1
    mount -a
    ;;
*)
    sleep 1
    modprobe g_mass_storage file=$FILE stall=0 ro=0 removable=1 nofua=1
    ;;
esac
