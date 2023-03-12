#!/bin/bash

recommended_server=$(nordvpn-server-find -r)

sudo openvpn /etc/openvpn/ovpn_tcp/${recommended_server}.tcp.ovpn --auth-user-pass ~/.openvpn-auth
