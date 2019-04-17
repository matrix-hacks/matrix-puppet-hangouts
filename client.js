const debug = require('debug');
const debugVerbose = debug('verbose:matrix-puppet:hangouts:client');
const EventEmitter = require('events').EventEmitter;
const Promise = require('bluebird');

const resolveData = ({data:{response}}) => {
  return Promise.resolve(response);
};

class Client extends EventEmitter {
  constructor() {
    super();
    this.hangupsProc = null;
  }
  connect() {
    this.hangupsProc = require("child_process").spawn('python3', ['-u', 'hangups_client.py']);

    this.hangupsProc.stderr.on("data", (str) => {
      this.emit('status', str.toString());
      debugVerbose("status message from hangups process:", str.toString());
    });

    this.hangupsProc.stdout.on("data", (str) => {
      debugVerbose("got message from hangups before JSON.parse():", str.toString());
      // XXX:NOTE: See https://github.com/matrix-hacks/matrix-puppet-hangouts/pull/24 for rationale
      try {
        var data = JSON.parse(str);
        debugVerbose("emitting message", data);
        this.emit('message', data);
      } catch(error) {
        debugVerbose("ERROR: incorrect JSON format: ", str.toString());
      }
    });

    console.log('started hangups child');
  }

  send(id, msg) {
    let themsg = { 'cmd': "sendmessage", 'conversation_id':id,  'msgbody': msg };
    debugVerbose('sending message to hangouts subprocess: ', JSON.stringify(themsg));
    this.hangupsProc.stdin.write(JSON.stringify(themsg) + "\n");
    return Promise.resolve();
  }

  sendImage(id, data) {
    let themsg = { 'cmd': "sendimage", 'conversation_id':id,  'msgbody': data.text, 'url': data.url, 'mimetype': data.mimetype };
    debugVerbose('sending message to hangouts subprocess: ', JSON.stringify(themsg));
    this.hangupsProc.stdin.write(JSON.stringify(themsg) + "\n");
    return Promise.resolve();
  }
}

module.exports = Client;
