# -*- coding: utf-8 -*-
"""
    Registrar
    ~~~~~

    copyright: (c) 2014 by Halfmoon Labs, Inc.
    copyright: (c) 2015 by Blockstack.org

This file is part of Registrar.

    Registrar is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Registrar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with Registrar. If not, see <http://www.gnu.org/licenses/>.
"""

import json

from .utils import get_hash, pretty_print
from .network import bs_client
from .network import get_dht_client

from .utils import config_log

log = config_log(__name__)


def get_blockchain_record(fqu):

    data = {}

    try:
        resp = bs_client.get_name_blockchain_record(fqu)
        resp = resp[0]
    except Exception as e:
        data['error'] = e
        return data

    return resp


def get_dht_profile(fqu):

    resp = get_blockchain_record(fqu)

    if resp is None:
        return None

    profile_hash = resp['value_hash']

    profile = None

    dht_client = get_dht_client()

    try:
        resp = dht_client.get(profile_hash)
        profile = resp[0]['value']
    except Exception as e:
        print "Error DHT get: (%s, %s)" % (fqu, profile_hash)

    return profile


def write_dht_profile(profile):

    resp = None
    dht_client = get_dht_client()

    key = get_hash(profile)
    value = json.dumps(profile, sort_keys=True)

    print "DHT write (%s, %s)" % (key, value)

    try:
        resp = dht_client.set(key, value)
        pretty_print(resp)
    except Exception as e:
        print e

    return resp


def usernameRegistered(fqu):

    data = get_blockchain_record(fqu)

    if "error" in data:
        return False
    else:
        return True


def ownerUsername(fqu, btc_address):
    """ return True if btc_address owns the username
    """

    record = get_blockchain_record(fqu)

    if record['address'] == btc_address:
        return True
    else:
        return False


def registrationComplete(fqu, profile, btc_address):
    """ return True if properly registered
    """

    record = get_blockchain_record(fqu)

    if 'address' not in record or 'value_hash' not in record:
        log.debug("ERROR in resp")
        log.debug(record)
        return False

    if record['address'] != btc_address:
        # if incorrect owner address
        return False

    if record['value_hash'] == get_hash(profile):
        # if hash of profile is in correct
        return False

    return True
