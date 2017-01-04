# imperirazz
Razzberry interface for Imperihome api

This is a very early release of a interface for bringing razzberry support to Imperihome "ImperiHome Standard System API".
http://www.evertygo.com/imperihome

For now there is only support for dimmable and regular switches, temperature sensors and meter sensor.

There is a very basic authentication that can be enabled. But as this is a very early version there is no guaranted security in it.

Start the script by "python imperirazz.py". By default it will use port 8080 if you want to use another port the just add it after the script name like "python imperirazz.py 3002".

By default it uses anonymous authentication.
For enabling authentication change the lines:

authEnabled = 0 #change to 1 to enable authorization
usernameImperirazz = "username"
passwordImperirazz = "password"

authEnabled to 1
and change username and password to the ones that you have setup in razberry.


