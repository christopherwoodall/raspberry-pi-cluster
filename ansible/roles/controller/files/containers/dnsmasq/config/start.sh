#! /bin/sh
chown -R $PUID:$PGID /config

GROUPNAME=$(getent group $PGID | cut -d: -f1)
USERNAME=$(getent passwd $PUID | cut -d: -f1)

if [ ! $GROUPNAME ]; then
  addgroup -g $PGID dnsmasq_group
  GROUPNAME=dnsmasq_group
fi

if [ ! $USERNAME ]; then
  adduser -G $GROUPNAME -u $PUID -D dnsmasq_user
  USERNAME=dnsmasq_user
fi

dnsmasq -C /config/dnsmasq.conf -8 - -R -k 2>&1 | su $USERNAME -c 'tee -a /config/dnsmasq.log'

# dnsmasq -q -d --conf-file=/config/dnsmasq.conf --dhcp-broadcast 2>&1 | su $USERNAME -c 'tee -a /config/dnsmasq.log'