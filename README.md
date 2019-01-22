# matrix-puppet-hangouts

This is a Matrix bridge for Google Hangouts.
It logs in as (aka "puppets") both your matrix user and your hangouts user to
establish the bridge. For more information, see:
https://github.com/matrix-hacks/matrix-puppet-bridge

To interact with the google hangouts servers, this bridge uses a python hangouts client library called hangups:
https://github.com/tdryer/hangups

## requirements

### For hangups, python3 is required:
sudo apt install python3 python3-dev
(Or similar for your package manager)

### Install hangups system-wide:
`sudo pip3 install hangups`

## installation

clone this repo

cd into the directory

run `npm install`

## configure

Copy `config.sample.json` to `config.json` and update it to match your setup

### Login to hangouts to save your authentication token.

Run the following

```
mkdir -p ~/.cache/hangups
python3 hangups_client.py --login-and-save-token
```

This saves an authentication token into the default hangups token path (`~/.cache/hangups/` as of this writing).

#### Troubleshooting Login

If you get an error like this

```
Traceback (most recent call last):
  File "/home/keyvan/code/matrix-puppet-hangouts/env/lib/python3.6/site-packages/hangups/auth.py", line 158, in get_auth
    raise GoogleAuthError("Refresh token not found")
hangups.auth.GoogleAuthError: Refresh token not found
```

Then try logging in through a real browser first (lynx should work) to get past the SMS verification.

If you are still having this issue, make sure you turn off "Login with my phone" and "2-step verification". You may be able to turn these back on AFTER you've successfully logged in, but this is unconfirmed.

You can control these settings here: https://myaccount.google.com/security

### register the app service

Generate an `hangouts-registration.yaml` file with `node index.js -r -u "http://your-bridge-server:8090"`

Note: The 'registration' setting in the config.json needs to set to the path of this file. By default, it already is.

Copy this `hangouts-registration.yaml` file to your home server, then edit it, setting its url to point to your bridge server. e.g. `url: 'http://your-bridge-server.example.org:8090'`

Edit your homeserver.yaml file and update the `app_service_config_files` with the path to the `hangouts-registration.yaml` file.

Launch the bridge with ```npm start```.

Restart your HS.

## TODO
* Be able to start a brand new hangouts conversation fully from within a matrix client by choosing participants from your google contacts list. Currently, to start a new conversation this way, you'll have to start the conversation with an official hangouts client where your full contact list is available and once you send a message a bridged room will automatically be created for you. After this, you can carry on the rest of the conversation using your matrix client. Naturally, any incoming message will also automatically create a bridged room for you, so this limitation only applies when creating brand new rooms yourself. See this comment by tfreedman for a proposed solution to this problem - https://github.com/kfatehi/matrix-puppet-facebook/issues/2#issuecomment-274170696 and if you have any better ideas, please let us know!
* Add a bot to each hangouts bridge room and use the bot's presence to indicate whether the bridge is running. This is an easy way to check on the status of the bridge.
* Read receipt support.
* Full image message support in both directions.
* Typing notification support.
