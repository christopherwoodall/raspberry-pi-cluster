#!/usr/bin/env bash
set -euo pipefail;

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root." 1>&2
   exit 1
fi

if [ "$1" == '--help' ] || [ "$1" == '-h' ]; then
    echo "Syntax:   $0 <NETWORK>"
    echo "Example:  $0 192.168.0.0"
    exit
fi


# https://standards-oui.ieee.org/oui/oui.txt
PI_OUI="b8:27:eb|dc:a6:32|e4:5f:01|28:cd:c1"
NETWORK="${1:='192.168.1.0'}"
MASK="24"


grep_arp_table () {
  # Find hosts with a Raspberry Pi OUI
  ip n | egrep "${PI_OUI}" | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'
  exit 0
}


# Command ran with '--arp'
if [ "$1" == '--arp' ]; then
  echo "Results:"
  grep_arp_table
fi


# Update local ARP table
echo "Scanning ${NETWORK}/${MASK} network..."
if `command -v nmap >/dev/null`; then
  echo "Running nmap scan..."
  nmap -n -T5 -p 22 --open --min-parallelism 100 "${NETWORK}/${MASK}" > /dev/null
else
  echo "Running ping scan..."
  for i in {1..254} ; do
    TARGET="${NETWORK%.*}.$i"
    ( ping "${TARGET}" -c 2 -W 1 > /dev/null ) &
  done
  echo "Ping scan finished. Rerun command with '--arp'"
fi

grep_arp_table
