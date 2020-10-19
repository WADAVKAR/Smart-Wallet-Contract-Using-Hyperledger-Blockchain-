#!/usr/bin/env python3

# Copyright 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------
'''
Command line interface for cookiejar TF.
Parses command line arguments and passes to the CookieJarClient class
to process.
'''

import argparse
import logging
import os
import sys
import traceback

from colorlog import ColoredFormatter
from main_server import main_server
from events_client import listen_to_events

import socket


KEY_NAME = 'mycookiejar'
NUMBER_OF_AC=2
# hard-coded for simplicity (otherwise get the URL from the args in main):
#DEFAULT_URL = 'http://localhost:8008'
# For Docker:
DEFAULT_URL = 'http://rest-api:8008'

def create_console_handler(verbose_level):
    '''Setup console logging.'''
    del verbose_level # unused
    clog = logging.StreamHandler()
    formatter = ColoredFormatter(
        "%(log_color)s[%(asctime)s %(levelname)-8s%(module)s]%(reset)s "
        "%(white)s%(message)s",
        datefmt="%H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        })

    clog.setFormatter(formatter)
    clog.setLevel(logging.DEBUG)
    return clog

def setup_loggers(verbose_level):
    '''Setup logging.'''
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(create_console_handler(verbose_level))



def _get_private_keyfile(key_name):
    '''Get the private key for key_name.'''
    home = os.path.expanduser("~")
    key_dir = os.path.join(home, ".sawtooth", "keys")
    return '{}/{}.priv'.format(key_dir, key_name)

def do_bake(args):
    privkeyfile = _get_private_keyfile(KEY_NAME)
    client = main_server(base_url=DEFAULT_URL, key_file=privkeyfile)
    response,ans = client.bake(args)
    #print("Bake Response: {}".format(response))
    return ans

def main():
    '''Entry point function for the client CLI.'''
    
    s = socket.socket()		 
    print("Socket successfully created")
    port = 4000				

    s.bind(('', port))		 
    print("socket binded to %s" %(port)) 

    s.listen(5)	 
    print("socket is listening")			

    while True:
    # Establish connection with client. 
        c, addr = s.accept()	 
        print('Got connection from', addr) 
        c.send(str.encode('Thank you for connecting'))

        arg=c.recv(2048) 
        c.send(str.encode('Thanks,we recieved'))

        arg = arg.decode('utf-8')
        
        arg=arg.replace("'"," ")
    
        arg=arg.split(" , ")
    # Close the connection with the client 
        

        try:
            ###Name a function here
            s1=1
            # Get the commands from cli args and call corresponding handlers
            if (s1)<32 and (s1)>0 :
                ans=do_bake(arg)
                c.send(str.encode(str(ans)))

            else:
                raise Exception("Invalid command: {}".format(args.command))

        except KeyboardInterrupt:
            pass
        except SystemExit as err:
            raise err
        except BaseException as err:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
    s.close() 

if __name__ == '__main__':
    main()
