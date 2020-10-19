#! /usr/bin/env python3

# Copyright 2017-2018 Intel Corporation
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
'''Sample Sawtooth event client

   To run, start the validator then type the following on the command line:
       ./events_client.py

   For more information, see
   https://sawtooth.hyperledger.org/docs/core/releases/latest/app_developers_guide/event_subscriptions.html
'''

import sys
import traceback
from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf import events_pb2
from sawtooth_sdk.protobuf import client_event_pb2
from sawtooth_sdk.protobuf.validator_pb2 import Message

import socket

# hard-coded for simplicity (otherwise get the URL from the args in main):
# For localhost access:
#DEFAULT_VALIDATOR_URL = 'tcp://localhost:4004'
# For Docker access:
DEFAULT_VALIDATOR_URL = 'tcp://validator:4004'
# Calculated from the 1st 6 characters of SHA-512("cookiejar"):
TP_ADDRESS_PREFIX = 'a4d219f6a96d59f600864c47c965ee8f4806b814a52704da7e58a25e0a'
def server_socket(arg):
    s = socket.socket()          
    
# Define the port on which you want to connect 
    port =3000             
    
    # connect to the server on local computer 
    s.connect(('127.0.0.1', port)) 
	  
	# receive data from the server 
    print(s.recv(1024))
    s.send(str(arg).encode('utf-8'))

    s.close()

def listen_to_events(delta_filters=None):
    '''Listen to cookiejar state-delta events.'''

    # Subscribe to events
    block_commit_subscription = events_pb2.EventSubscription(
        event_type="sawtooth/block-commit")
    state_delta_subscription = events_pb2.EventSubscription(
        event_type="sawtooth/state-delta", filters=delta_filters)
    fine_subscription = events_pb2.EventSubscription(
        event_type="AC is in good condition")    
    problem_subscription = events_pb2.EventSubscription(
        event_type="AC is malfunctioning")
    fixed_subscription = events_pb2.EventSubscription(
        event_type="Maintenance fixed the AC")
    notfixed_subscription = events_pb2.EventSubscription(
        event_type="Maintenance hasn't fixed the AC yet")    
    request = client_event_pb2.ClientEventsSubscribeRequest(
        subscriptions=[fine_subscription,problem_subscription,fixed_subscription,notfixed_subscription])

    # Send the subscription request
    stream = Stream(DEFAULT_VALIDATOR_URL)
    msg = stream.send(message_type=Message.CLIENT_EVENTS_SUBSCRIBE_REQUEST,
                      content=request.SerializeToString()).result()
    assert msg.message_type == Message.CLIENT_EVENTS_SUBSCRIBE_RESPONSE

    # Parse the subscription response
    response = client_event_pb2.ClientEventsSubscribeResponse()
    response.ParseFromString(msg.content)
    assert response.status == \
           client_event_pb2.ClientEventsSubscribeResponse.OK

    # Listen for events in an infinite loop
    print("Listening to events.")
    
    msg = stream.receive().result()
    assert msg.message_type == Message.CLIENT_EVENTS

    # Parse the response
    event_list = events_pb2.EventList()
    event_list.ParseFromString(msg.content)
    print("Received the following events: ----------")
    notification=[]
    for event in event_list.events:
        
        notification.append((event.event_type,event.attributes))
    
        #server_socket(notification)

    # Unsubscribe from events
    request = client_event_pb2.ClientEventsUnsubscribeRequest()
    msg = stream.send(Message.CLIENT_EVENTS_UNSUBSCRIBE_REQUEST,
                      request.SerializeToString()).result()
    assert msg.message_type == Message.CLIENT_EVENTS_UNSUBSCRIBE_RESPONSE

    # Parse the unsubscribe response
    response = client_event_pb2.ClientEventsUnsubscribeResponse()
    response.ParseFromString(msg.content)
    assert response.status == \
           client_event_pb2.ClientEventsUnsubscribeResponse.OK
    return notification


    
    

'''    

def main():
    

    filters = [events_pb2.EventFilter(key="address",
                                      match_string=
                                      TP_ADDRESS_PREFIX + ".*",
                                      filter_type=events_pb2.
                                      EventFilter.REGEX_ANY)]

    try:
        # To listen to all events, pass delta_filters=None :
        #listen_to_events(delta_filters=None)
        listen_to_events(delta_filters=filters)
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
    '''