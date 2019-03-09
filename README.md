# matrix-puppet-hangouts [![#matrix-puppet-bridge:matrix.org](https://img.shields.io/matrix/matrix-puppet-bridge:matrix.org.svg?label=%23matrix-puppet-bridge%3Amatrix.org&logo=matrix&server_fqdn=matrix.org)](https://matrix.to/#/#matrix-puppet-bridge:matrix.org)

This is a Matrix bridge for Google Hangouts.
It logs in as (aka "puppets") both your matrix user and your hangouts user to
establish the bridge. For more information, see:
https://github.com/matrix-hacks/matrix-puppet-bridge

To interact with the google hangouts servers, this bridge uses a python hangouts client library called hangups:
https://github.com/tdryer/hangups

## Requirements

### For hangups, and our own python, python3 (Python 3.5+ for async) is required:
sudo apt install python3 python3-dev
(Or similar for your package manager)

Make sure your python3 is version 3.5+ by running `python3 --version`

### Install hangups system-wide:
`sudo pip3 install hangups`

## Installation

Clone this repo or download a release of the puppet

cd into the directory

run `npm install`

## Configure

Copy `config.sample.json` to `config.json` and update it to match your setup.

You should really only have to edit the `homeserverUrl` and `domain` values. 
If you are running the puppet on the same server as your homeserver, then you should probably
set the `homeserverUrl` value to be `http://127.0.0.1:8008`.


### Login to hangouts to save your authentication token.

Run the following

```
mkdir -p ~/.cache/hangups
python3 hangups_client.py --login-and-save-token
```

This saves an authentication token into the default hangups token path (`~/.cache/hangups/` as of this writing).

#### Troubleshooting Login

##### Refresh token not found

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

##### Authorization code cookie not found

If you get an error that says something along the lines of:

`Login failed (Authorization code cookie not found)`

You may get your refresh token manually using hangups itself:

```
hangups --manual
```
(follow the instructions on screen in order to get the refresh token)

While this will take you into a hangups TUI once everything is done, you can exit it with Control+E.


### Register the app service

Note: `your-bridge-server` is simply the IP address or hostname that your puppet will be running on, as it utilizes its own HTTP server for functionality. 
If you are running Synapse and the puppet on the same system, feel free to use `localhost` or `127.0.0.1`.

Generate an `hangouts-registration.yaml` file with `node index.js -r -u "http://your-bridge-server:8090"`

This command above will ask you to sign in as a user. You should sign in as a user that is an administrator, otherwise you might experience problems.

Note: The 'registration' setting in the config.json needs to set to the path of this file. By default, it already is.

Copy this `hangouts-registration.yaml` file to your home server (or to the homeserver's configuration directory if the puppet and homeserver are the same system), 
then edit it, setting its url to point to your bridge server. e.g. `url: 'http://your-bridge-server.example.org:8090'`. 

Edit your homeserver.yaml file and update the `app_service_config_files` with the path to the `hangouts-registration.yaml` file.

Launch the bridge with ```npm start```.

Restart your HS.

A handy way to control your puppet is through `systemd`. Here is a `systemd` service, that can be called `hangouts-puppet` and placed at `/etc/systemd/system`.
```
[Unit]
Description=Hangouts Matrix Puppet

[Service]
Type=simple
Environment=DEBUG=verbose:matrix-puppet:*
User=my-user-who-is-running-puppet-here
Group=my-group-who-is-running-puppet-here
WorkingDirectory=/my/path/to/downloaded/puppet/here
ExecStart=/usr/bin/npm start
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```
This service will auto-restart when the puppet fails. If you want that to not be the case, remove the lines:
```
Restart=always
RestartSec=3
```

## Discussion, Help and Support

Join us in the [![Matrix Puppet Bridge](https://user-images.githubusercontent.com/13843293/52007839-4b2f6580-24c7-11e9-9a6c-14d8fc0d0737.png)](https://matrix.to/#/#matrix-puppet-bridge:matrix.org) room

## Using this puppet to bridge two group chats
This is a simple hack in order for this puppet to be usable to bridge two group chats, one on Matrix and one on Hangouts.

1. Have a Google account that will be just for this puppet and create your hangups refresh token with this account.
2. Run `register_new_matrix_user -c homeserver.yaml http://localhost:8008` on your Synapse homeserver. Make sure that this user is an administrator.
3. Now run `node index.js -r -u "http://your-bridge-server:8090"`, but use the admin user you created before this in the registration.
4. Follow other steps as detailed to get the puppet running.
5. When the puppet starts successfully with `npm start`, invite the puppet's Google account to the group chat on Hangouts.
6. By default, the sender's name is not shown, which makes it very difficult to bridge two group chats, because you wouldn't know who is who on the Matrix side in Hangouts.
However, if you replace this block of code in `index.js`

```js
sendMessageAsPuppetToThirdPartyRoomWithId(id, text) {
    return this.thirdPartyClient.send(id, text);
}
sendImageMessageAsPuppetToThirdPartyRoomWithId(id, data) {
  return this.thirdPartyClient.sendImage(id, data);
}
```
with:
```js
sendMessageAsPuppetToThirdPartyRoomWithId(id, text, event) {
    return this.thirdPartyClient.send(id, "**" + event.sender.split(":")[0].substring(1) + "**\n" + text);
}
sendImageMessageAsPuppetToThirdPartyRoomWithId(id, data, event) {
  this.sendMessageAsPuppetToThirdPartyRoomWithId(id, "**" + event.sender.split(':')[0].substring(1) + "**", event);
  return this.thirdPartyClient.sendImage(id, data);
}
```
you should be able to see the sender's name from Matrix in the Hangouts chat. 

All this does is the puppet adds a line before every message stating the sender in bold. 
While this only shows the localpart (username without homeserver), if you replace `event.sender.split(":")[0].substring(1)` with just `event.sender`, you will be able to see the username with the homeserver at the end, like `@username:homeserver.here`.

At the end, you should be able to just log in to Riot or your favorite client as that admin user that you created, and invite your real account to the "bridged" room. 
## TODO
* Be able to start a brand new hangouts conversation fully from within a matrix client by choosing participants from your google contacts list. Currently, to start a new conversation this way, you'll have to start the conversation with an official hangouts client where your full contact list is available and once you send a message a bridged room will automatically be created for you. After this, you can carry on the rest of the conversation using your matrix client. Naturally, any incoming message will also automatically create a bridged room for you, so this limitation only applies when creating brand new rooms yourself. See this comment by tfreedman for a proposed solution to this problem - https://github.com/kfatehi/matrix-puppet-facebook/issues/2#issuecomment-274170696 and if you have any better ideas, please let us know!
* Add a bot to each hangouts bridge room and use the bot's presence to indicate whether the bridge is running. This is an easy way to check on the status of the bridge.
* Read receipt support.
* Typing notification support.
