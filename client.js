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
    this.hangupsProc = require("child_process").spawn('python3', ['-u', 'hangups_client.py'], { stdio: [ 'pipe', 'ipc', 2 ] });
    this.hangupsProc.on("message", (data) => {
      debugVerbose("emitting message", data);
      this.emit('message', data);
    });
    console.log('started hangups child');
  }

  send(id, msg) {
    let themsg = { 'cmd': "sendmessage", 'conversation_id':id,  'msgbody': msg };
    debugVerbose('sending message to hangouts subprocess: ', JSON.stringify(themsg));
    this.hangupsProc.stdin.write(JSON.stringify(themsg) + "\n");
  }
}

module.exports = Client;
