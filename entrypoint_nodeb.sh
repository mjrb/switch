#!/usr/bin/env bash
ip route del default
ip route add 172.42.0.0/16 dev eth0
ip route add default via 172.42.2.3
yes sleep 1 | bash
