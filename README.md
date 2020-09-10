# switch
This is a attempt at writing a program to switch packets. it uses python
and linux AF_PACKET to get a raw ethernet socket. there is a docker setup with
3 containers (a switch and two nodes).

there is a little bit of wonkieness with trying to switch packets out to the open internet, but server times i have been able to ping one node from the other
The way i have the docker virtual networking setup causes some issues. I may be able to make everything work by making the program act as a router instead of a simple switch.
