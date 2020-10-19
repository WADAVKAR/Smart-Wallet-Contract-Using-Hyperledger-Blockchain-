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
CookieJarClient class interfaces with Sawtooth through the REST API.
It accepts input from a client CLI/GUI/BUI or other interface.
'''

import hashlib
import base64
import random
import time
import requests
import yaml

from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.batch_pb2 import Batch

from events_client import *

import sys
import traceback
from sawtooth_sdk.messaging.stream import Stream
from sawtooth_sdk.protobuf import events_pb2
from sawtooth_sdk.protobuf import client_event_pb2
from sawtooth_sdk.protobuf.validator_pb2 import Message


TP_ADDRESS_PREFIX = 'a4d219f6a96d59f600864c47c965ee8f4806b814a52704da7e58a25e0a'

# The Transaction Family Name
FAMILY_NAME = 'panasonic'
# TF Prefix is first 6 characters of SHA-512("cookiejar"), a4d219

def _hash(data):
    return hashlib.sha512(data).hexdigest()

class main_server(object):

    def __init__(self, base_url, key_file=None):
        '''Initialize the client class.

           This is mainly getting the key pair and computing the address.
        '''
        self._base_url = base_url

        if key_file is None:
            self._signer = None
            return
        """
        try:
            with open(key_file) as key_fd:
                private_key_str = key_fd.read().strip()
                print(private_key_str)
        except OSError as err:
            raise Exception(
                'Failed to read private key {}: {}'.format(
                    key_file, str(err)))
        """
        private_key_str='ad5009452d3c24f034c4349c57f0042a750ee859238ece21728dd0d32edf1751'

        try:
            private_key = Secp256k1PrivateKey.from_hex(private_key_str)
        except ParseError as err:
            raise Exception( \
                'Failed to load private key: {}'.format(str(err)))

        self._signer = CryptoFactory(create_context('secp256k1')) \
            .new_signer(private_key)
        self._public_key = self._signer.get_public_key().as_hex()

        # Address is 6-char TF prefix + hash of "mycookiejar"'s public key
        self._address = _hash(FAMILY_NAME.encode('utf-8'))[0:6] + \
            _hash(self._public_key.encode('utf-8'))[0:52]

   
    def bake(self, amount):
        return self._wrap_and_send("bake", amount, wait=10)

    def _send_to_rest_api(self, suffix, data=None, content_type=None):
        '''Send a REST command to the Validator via the REST API.

           Called by count() &  _wrap_and_send().
           The latter caller is made on the behalf of bake() & eat().
        '''
        url = "{}/{}".format(self._base_url, suffix)
        print("URL to send to REST API is {}".format(url))

        headers = {}

        if content_type is not None:
            headers['Content-Type'] = content_type

        try:
            if data is not None:
                result = requests.post(url, headers=headers, data=data)
            else:
                result = requests.get(url, headers=headers)

            if not result.ok:
                raise Exception("Error {}: {}".format(
                    result.status_code, result.reason))
        except requests.ConnectionError as err:
            raise Exception(
                'Failed to connect to {}: {}'.format(url, str(err)))
        except BaseException as err:
            raise Exception(err)

        return result.text

    def _wait_for_status(self, batch_id, wait, result):
        '''Wait until transaction status is not PENDING (COMMITTED or error).

           'wait' is time to wait for status, in seconds.
        '''
        if wait and wait > 0:
            waited = 0
            start_time = time.time()
            while waited < wait:
                result = self._send_to_rest_api("batch_statuses?id={}&wait={}"
                                               .format(batch_id, wait))
                status = yaml.safe_load(result)['data'][0]['status']
                waited = time.time() - start_time

                if status != 'PENDING':
                    
                    return result
            return "Transaction timed out after waiting {} seconds." \
               .format(wait)
        else:
            return result


    def _wrap_and_send(self, action, amount, wait=None):
        '''Create a transaction, then wrap it in a batch.

           Even single transactions must be wrapped into a batch.
           Called by bake() and eat().
        '''
        amount=str(amount)
        
        amount=amount.replace('[','')
        amount=amount.replace(']','')


        print(amount)
        payload = str(amount).encode('utf-8')

        # Construct the address where we'll store our state.
        # We just have one input and output address (the same one).
        input_and_output_address_list = [self._address]

        # Create a TransactionHeader.
        header = TransactionHeader(
            signer_public_key=self._public_key,
            family_name=FAMILY_NAME,
            family_version="1.0",
            inputs=input_and_output_address_list,
            outputs=input_and_output_address_list,
            dependencies=[],
            payload_sha512=_hash(payload),
            batcher_public_key=self._public_key,
            nonce=random.random().hex().encode()
        ).SerializeToString()

        # Create a Transaction from the header and payload above.
        transaction = Transaction(
            header=header,
            payload=payload,
            header_signature=self._signer.sign(header)
        )

        transaction_list = [transaction]

        # Create a BatchHeader from transaction_list above.
        header = BatchHeader(
            signer_public_key=self._public_key,
            transaction_ids=[txn.header_signature for txn in transaction_list]
        ).SerializeToString()

        # Create Batch using the BatchHeader and transaction_list above.
        batch = Batch(
            header=header,
            transactions=transaction_list,
            header_signature=self._signer.sign(header))

        # Create a Batch List from Batch above
        batch_list = BatchList(batches=[batch])
        batch_id = batch_list.batches[0].header_signature

        # Send batch_list to the REST API
        result = self._send_to_rest_api("batches",
                                       batch_list.SerializeToString(),
                                       'application/octet-stream')
        
        filters = [events_pb2.EventFilter(key="address",
                                      match_string=
                                      TP_ADDRESS_PREFIX + ".*",
                                      filter_type=events_pb2.
                                      EventFilter.REGEX_ANY)]

        try:
            # To listen to all events, pass delta_filters=None :
            #listen_to_events(delta_filters=None)
            notification=listen_to_events(delta_filters=filters)
            #print(notification)
          
        except KeyboardInterrupt:
            pass
        except SystemExit as err:
            raise err
        except BaseException as err:
            traceback.print_exc(file=sys.stderr)
            sys.exit(1)
        
        # Wait until transaction status is COMMITTED, error, or timed out
        return self._wait_for_status(batch_id, wait, result),notification

