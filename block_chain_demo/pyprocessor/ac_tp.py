#!/usr/bin/env python3

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
CookieJarTransactionHandler class interfaces for cookiejar Transaction Family.
'''

import traceback
import sys
import hashlib
import logging
import datetime

from sawtooth_sdk.processor.handler import TransactionHandler
from sawtooth_sdk.processor.exceptions import InvalidTransaction
from sawtooth_sdk.processor.exceptions import InternalError
from sawtooth_sdk.processor.core import TransactionProcessor

# hard-coded for simplicity (otherwise get the URL from the args in main):
#DEFAULT_URL = 'tcp://localhost:4004'
# For Docker:
DEFAULT_URL = 'tcp://validator:4004'

LOGGER = logging.getLogger(__name__)

FAMILY_NAME = 'panasonic'
# TF Prefix is first 6 characters of SHA-512("cookiejar"), a4d219

def _hash(data):
    '''Compute the SHA-512 hash and return the result as hex characters.'''
    return hashlib.sha512(data).hexdigest()
"""
def _date(day):

    if day=="current_date"":

        return datetime.datetime.today().strftime ('%d%m%Y') # format the date to ddmmyyyy
    
    elif day=="previous_date":

        Previous_Date = datetime.datetime.today() - datetime.timedelta(days=1)
        return Previous_Date.strftime ('%d%m%Y') # format the date to ddmmyyyy
    
    else:
        return -1
"""
def _get_ac_address(ac_id,date,from_key):
    '''
    Return the address of a cookiejar object from the cookiejar TF.

    The address is the first 6 hex characters from the hash SHA-512(TF name),
    plus the result of the hash SHA-512(cookiejar public key).
    '''
    print(date)
    return _hash(FAMILY_NAME.encode('utf-8'))[0:6] + _hash(from_key.encode('utf-8'))[0:52]+_hash(ac_id.encode('utf-8'))[0:6]+_hash(date.encode('utf-8'))[0:6]


class AC_TransactionHandler(TransactionHandler):
    '''
    Transaction Processor class for the ac Transaction Family.

    This TP communicates with the Validator using the accept/get/set functions.
    This implements functions to "bake" or "eat" cookies in a cookie jar.
    '''
    def __init__(self, namespace_prefix):
        '''Initialize the transaction handler class.

           This is setting the "cookiejar" TF namespace prefix.
        '''
        self._namespace_prefix = namespace_prefix

    @property
    def family_name(self):
        '''Return Transaction Family name string.'''
        return FAMILY_NAME

    @property
    def family_versions(self):
        '''Return Transaction Family version string.'''
        return ['1.0']

    @property
    def namespaces(self):
        '''Return Transaction Family namespace 6-character prefix.'''
        return [self._namespace_prefix]

    def apply(self, transaction, context):
        '''This implements the apply function for the TransactionHandler class.

           The apply function does most of the work for this class by
           processing a transaction for the cookiejar transaction family.
        '''

        # Get the payload and extract the cookiejar-specific information.
        # It has already been converted from Base64, but needs deserializing.
        # It was serialized with CSV: action, value
        header = transaction.header
        payload_list = transaction.payload.decode('utf-8')
        print(payload_list)
        payload_list=payload_list.replace("'"," ")
        
        payload_list=payload_list.split(" , ")
        print(payload_list)
        date=int(payload_list[0])
        payload_list=payload_list[1:]
        num=int(len(payload_list)/2)
        
        AC_ID=[0]*num
        filter_rate=[0]*num
        
        for i in range(int(len(payload_list)/2)):
            AC_ID[i]= int(payload_list[2*i])
            filter_rate[i] = int(payload_list[2*i+1])

        # Get the signer's public key, sent in the header from the client.
        from_key = header.signer_public_key
        
        self._check(context,date,AC_ID,filter_rate,from_key)


    @classmethod
    def _check(cls,context,date,AC_ID,filter_rate,from_key):
        '''Bake (add) "amount" cookies.'''

        for i in range(len(AC_ID)):
            pre_date = (date) - 1
            
            
            previous_date_ac_address = _get_ac_address(str(AC_ID[i]),str(pre_date),from_key)
            LOGGER.info('Got the AC ID %s and the previous address is %s.',
                        str(AC_ID[i]), previous_date_ac_address)
            state_entries = context.get_state([previous_date_ac_address])
            

            if state_entries == []:
                n=0
            else:
                try:
                    data_state = state_entries[0].data
                    LOGGER.info(data_state)
                    data_list = data_state.decode().split(",")
                    LOGGER.info(data_list)
                    n = int(data_list[0])
                    LOGGER.info(n)
                except:
                    raise InternalError('Failed to load state data')
                
            threshold = 30
            if n==0:
                if filter_rate[i]>threshold:
                    n=0
                    context.add_event(event_type="AC is in good condition",attributes=[("filter rate", str(filter_rate[i]))])
                else :
                    n = n+1
                    #add_event(faulty)
                    LOGGER.info("AC has a problem")
                    context.add_event(event_type="AC is malfunctioning",attributes=[("filter rate", str(filter_rate[i]))])
            elif n!=0:
                if filter_rate[i]> threshold:
                   
                    #add_event(fixed)
                    LOGGER.info("AC is fixed")
                    context.add_event(event_type="Maintenance fixed the AC",attributes=[("Repaired after the following days", str(n))])
                    n=0
                else:
                    n = n+1
                    #add_event(still fault, N)
                    LOGGER.info("AC is still not fixed")
                    context.add_event(event_type="Maintenance hasn't fixed the AC yet",attributes=[("since the following days", str(n))])
                    
            else:
                LOGGER.info("No proper input from filter")

            raw_payload = ",".join([str(n), str(filter_rate[i])])
            
            state_data=raw_payload.encode('utf-8')
            
            

            current_ac_address=_get_ac_address(str(AC_ID[i]),str(date),from_key)
            LOGGER.info(current_ac_address)
            addresses = context.set_state({current_ac_address: state_data})
            

            if len(addresses) < 1:
                raise InternalError("State Error")
            

    

def main():
    '''Entry-point function for the cookiejar Transaction Processor.'''
    try:
        # Setup logging for this class.
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)

        # Register the Transaction Handler and start it.
        processor = TransactionProcessor(url=DEFAULT_URL)
        sw_namespace = _hash(FAMILY_NAME.encode('utf-8'))[0:6]
        handler = AC_TransactionHandler(sw_namespace)
        processor.add_handler(handler)
        processor.start()
    except KeyboardInterrupt:
        pass
    except SystemExit as err:
        raise err
    except BaseException as err:
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
