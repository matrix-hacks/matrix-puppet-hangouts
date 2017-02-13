# hangouts-bridge

This is a Matrix bridge for Google Hangouts.
It logs in as (aka "puppets") both your matrix user and your hangouts user to
establish the bridge. For more information, see:
https://github.com/AndrewJDR/matrix-puppet-bridge

## requirements

# For hangups, python3 is required:
sudo apt install python3 python3-dev
(Or similar for your package manager)

# Install hangups system-wide:
`sudo pip3 install hangups`

## installation

clone this repo

cd into the directory

run `npm install`

## configure

Copy `config.sample.json` to `config.json` and update it to match your setup

## Login to hangouts to save your authentication token.

Run `python3 hangups_client.py --login-and-save-token`

This saves an authentication token into the default hangups token path (`~/.cache/hangups/` as of this writing).

## register the app service

Generate an `hangouts-registration.yaml` file with `node index.js -r -u "http://your-bridge-server:8090"`

Note: The 'registration' setting in the config.json needs to set to the path of this file. By default, it already is.

Copy this `hangouts-registration.yaml` file to your home server, then edit it, setting its url to point to your bridge server. e.g. `url: 'http://your-bridge-server.example.org:8090'`

Edit your homeserver.yaml file and update the `app_service_config_files` with the path to the `hangouts-registration.yaml` file.

Launch the bridge with ```npm start```.

Restart your HS.

# TODO
* Be able to originate conversations from the Matrix side.
