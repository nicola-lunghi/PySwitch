# PySwitch Emulator Publisher

This is a PHP based website which manages published PySwitch versions, to always be able to have multiple versions accessible. It is a standalone project, coming with its own docker container.

## How to install on a web server
1. Copy everything in the web/publish-helper/htdocs to your web root.
2. Update the .htaccess file in /versions/create to protect the folder with a login
3. If needed, grant the PHP web user access to modify files in the web root.

## Create Versions

Call the page "/versions/create" to create versions: This page will create a new versions by pulling the current main branch of the PySwitch repository and setting everything up. The .htaccess is updated so the latest version will be shown (depending on the time cloned).

## Usage

Calling the web root will always redirect to the latest version.
Calling /versions will show a page linking to all available versions.
