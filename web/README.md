# THIS IS STILL UNDER CONSTRUCTION! JUST IGNORE FOR THE MOMENT PLEASE

# PySwitch Emulator

This is a web based configuration/simulation tool for PySwitch. If you just want to use it, you can access the demo of this code here:

https://pyswitch.tunetown.de

## Run locally

If you want to run it locally or do any development to it, you need to install Docker if not already done. Then you can just open a terminal in this folder and run this command:

docker compose up -d

It will link all necessary sources and examples into the container, you can run it at http://localhost

To shut down:

docker compose down

## Deploy to a Server

To deploy the application to a server, you have two choices:
- Use docker (preferred) with the same volume mounts
- Use a normal webspace (must have PHP enabled):
    - Check out the project on your webspace
    - Point your domain to the web/htdocs folder
    - Copy the following folders into the web/htdocs folder:
        - content -> web/htdocs/circuitpy
        - examples -> web/htdocs/examples

For the last step, symlinks also work well.