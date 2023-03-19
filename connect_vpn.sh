#!/bin/bash

recommended_server=$(./nordvpn-server-find -r)

sudo openvpn --config /etc/openvpn/ovpn_tcp/${recommended_server}.tcp.ovpn --auth-user-pass ~/.openvpn-auth
