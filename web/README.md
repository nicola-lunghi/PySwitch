# PySwitch Web User Interface

To run the UI in docker locally, just use compose:

docker compose up -d

It will ink the PySwitch library into the htdocs/pyswitch folder, and you can test on localhost:80.

To deploy the application to a server, either use docker (preferred) or point your domain to the web/htdocs folder and create a symlink to the pyswitch library (content/lib/pyswitch).