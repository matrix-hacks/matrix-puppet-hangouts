#!/usr/bin/env python3

# Mostly adopted from the hangups example files.

from inspect import getmembers
from pprint import pprint
import hangups
from hangups.ui.utils import get_conv_name

import sys
import json
import queue
import time

from asyncio.streams import StreamWriter, FlowControlMixin
import argparse
import asyncio
import logging
import os

from hangups.auth import CredentialsPrompt, RefreshTokenCache, get_auth
import appdirs

global cachedStdout

def print_jsonmsg(*args, **kwargs):
    global cachedStdout
    print(*args, file=cachedStdout, **kwargs)

class NullCredentialsPrompt(object):
    @staticmethod
    def get_email():
        return ''

    @staticmethod
    def get_password():
        return ''

    @staticmethod
    def get_verification_code():
        return ''

def run_example(example_coroutine, *extra_args):
    """Run a hangups example coroutine.

    Args:
        example_coroutine (coroutine): Coroutine to run with a connected
            hangups client and arguments namespace as arguments.
        extra_args (str): Any extra command line arguments required by the
            example.
    """
    args = _get_parser().parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.WARNING)

    if args.login_and_save_token:
        cookies = hangups.auth.get_auth_stdin(args.token_path)
        #pprint(getmembers(args))
        return
    else:
        # Obtain hangups authentication cookies, prompting for credentials from
        # standard input if necessary.
        refresh_token_cache = RefreshTokenCache(args.token_path)
        try:
            cookies = get_auth(NullCredentialsPrompt(), refresh_token_cache)
        except:
            print("Hangouts login failed. Either you didn't log in yet, or your refresh token expired.\nPlease log in with --login-and-save-token")
            return

    while 1:
        print("Attempting main loop...")
        client = hangups.Client(cookies, max_retries=float('inf'), retry_backoff_base=1.2)
        task = asyncio.ensure_future(_async_main(example_coroutine, client, args))
        loop = asyncio.get_event_loop()

        try:
            loop.run_until_complete(task)
        except KeyboardInterrupt:
            task.cancel()
            loop.run_forever()
        except:
            pass
        finally:
            time.sleep(5)

    try:
        loop.run_until_complete(task)
    except KeyboardInterrupt:
        task.cancel()
        loop.run_forever()
    finally:
        loop.close()


def _get_parser():
    """Return ArgumentParser with any extra arguments."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    dirs = appdirs.AppDirs('hangups', 'hangups')
    default_token_path = os.path.join(dirs.user_cache_dir, 'refresh_token.txt')
    parser.add_argument(
        '--token-path', default=default_token_path,
        help='path used to store OAuth refresh token'
    )
    parser.add_argument(
        '--login-and-save-token', action='store_true',
        help='Perform login and save refresh token'
    )
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='log detailed debugging messages'
    )
    return parser

@asyncio.coroutine
def _async_main(example_coroutine, client, args):
    """Run the example coroutine."""
    # Spawn a task for hangups to run in parallel with the example coroutine.
    task = asyncio.ensure_future(client.connect())

    # Wait for hangups to either finish connecting or raise an exception.
    on_connect = asyncio.Future()
    client.on_connect.add_observer(lambda: on_connect.set_result(None))
    done, _ = yield from asyncio.wait(
        (on_connect, task), return_when=asyncio.FIRST_COMPLETED
    )
    yield from asyncio.gather(*done)

    # Run the example coroutine. Afterwards, disconnect hangups gracefully and
    # yield the hangups task to handle any exceptions.
    try:
        yield from example_coroutine(client, args)
    finally:
        yield from client.disconnect()
        yield from task

reader, writer = None, None

@asyncio.coroutine
def stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = yield from loop.connect_write_pipe(FlowControlMixin, os.fdopen(0, 'wb'))
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    yield from loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer

@asyncio.coroutine
def async_input():
    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = yield from stdio()

    line = yield from reader.readline()
    return line.decode('utf8').strip()

global event_queue
event_queue = queue.Queue()
global user_list, conv_list

def on_event(conv_event):
    global conv_list, event_queue
    #pprint(getmembers(conv_event))
    if isinstance(conv_event, hangups.ChatMessageEvent):
        conv = conv_list.get(conv_event.conversation_id)
        user = conv.get_user(conv_event.user_id)

        try:
            msgJson = json.dumps({
                'status':'success',
                'type':'message',
                'content':conv_event.text,
                'attachments': conv_event.attachments,
                'conversation_id': conv.id_,
                'conversation_name':get_conv_name(conv),
                'photo_url':user.photo_url,
                'user':user.full_name,
                'self_user_id':user_list._self_user.id_.chat_id,
                'user_id':{'chat_id':conv_event.user_id.chat_id, 'gaia_id':conv_event.user_id.gaia_id}
            })
            print_jsonmsg(msgJson)

        except Exception as error:
            print(repr(error))


        #event_queue.put(msgJson)
    #else:
        #print(conv_event.user_id)

def _on_message_sent(future):
    """Handle showing an error if a message fails to send."""
    try:
        future.result()
    except Exception as e:
        # TODO: Properly notify the bridge that a message send failure has
        # occurred, so it can react in some way (e.g. alert the owner with a
        # message).
        print("Message send failure! Exception: %s" % str(e))
    # TODO: Properly notify the bridge that a message has successfully sent so
    # it can react in some way (e.g. set a read receipt on the message showing
    # that the bot read the message)
    #print_jsonmsg(json.dumps({"status":"success"}))

@asyncio.coroutine
def listen_events(client, _):
    global user_list, conv_list
    global event_queue

    user_list, conv_list = (
        yield from hangups.build_user_conversation_list(client)
    )
    #print("my user id");
    #print(user_list._self_user.id_);
    conv_list.on_event.add_observer(on_event)

    #print(client._client_id);
    #print(client._email);
    #hangups.client.
    #print(json.dumps({"cmd":"status", "status":"ready"}))
    #print(hangups.user.)

    while 1:
        try:
            msgtxt = yield from async_input()
            msgtxt = msgtxt.strip()

            # TOOD: take conversation id from other side
            msgJson = json.loads(msgtxt)
            conv = conv_list.get(msgJson['conversation_id'])
            #print("ok, I got: " + msgtxt)

            if msgJson['cmd'] == 'sendmessage':
                segments = hangups.ChatMessageSegment.from_str(msgJson['msgbody'])
                asyncio.ensure_future(
                    conv.send_message(segments)
                ).add_done_callback(_on_message_sent)
            else:
                raise Exception("Invalid cmd specified!")

        except Exception as error:
            print(repr(error))

if __name__ == '__main__':
    cachedStdout = sys.stdout
    sys.stdout = sys.stderr
    run_example(listen_events)
