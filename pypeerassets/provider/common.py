'''Common provider class with basic features.'''

from abc import ABC, abstractmethod
from decimal import Decimal
import urllib.request

from btcpy.structs.address import Address, InvalidAddress

from pypeerassets.exceptions import UnsupportedNetwork
from pypeerassets.pa_constants import PAParams, param_query
from pypeerassets.networks import Constants, net_query


class Provider(ABC):

    net = ""

    headers = {"User-Agent": "pypeerassets"}

    @staticmethod
    def _netname(name: str) -> dict:
        '''resolute network name,
        required because some providers use shortnames and other use longnames.'''

        try:
            long = net_query(name).name
            short = net_query(name).shortname
        except AttributeError:
            raise UnsupportedNetwork('''This blockchain network is not supported by the pypeerassets, check networks.py for list of supported networks.''')

        return {'long': long,
                'short': short}

    @property
    def network(self) -> str:
        '''return network full name'''

        return self._netname(self.net)['long']

    @property
    def pa_parameters(self) -> PAParams:
        '''load network PeerAssets parameters.'''

        return param_query(self.network)

    @property
    def network_properties(self) -> Constants:
        '''network parameters [min_fee, denomination, ...]'''

        return net_query(self.network)

    @property
    def is_testnet(self) -> bool:
        """testnet or not?"""

        if "testnet" in self.network:
            return True
        else:
            return False

    @classmethod
    def sendrawtransaction(cls, rawtxn: str) -> str:
        '''sendrawtransaction remote API'''

        if cls.is_testnet:
            url = 'https://explorer.thepandacoin.net/api/sendrawtransaction?hex={0}'.format(rawtxn)
        else:
            url = 'https://chainz.cryptoid.info/pnd/api.dws?q=pushtx&key=1205735eba8c'.format(rawtxn)

        resp = urllib.request.urlopen(url)
        return resp.read().decode('utf-8')

    @abstractmethod
    def getblockhash(self, blocknum: int) -> str:
        '''get blockhash using blocknum query'''
        raise NotImplementedError

    @abstractmethod
    def getblockcount(self) -> int:
        '''get block count'''
        raise NotImplementedError

    @abstractmethod
    def getblock(self, hash: str) -> dict:
        '''query block using <blockhash> as key.'''
        raise NotImplementedError

    @abstractmethod
    def getdifficulty(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def getbalance(self, address: str) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def getreceivedbyaddress(self, address: str) -> Decimal:
        raise NotImplementedError

    @abstractmethod
    def listunspent(self, address: str) -> list:
        raise NotImplementedError

    @abstractmethod
    def select_inputs(self, address: str, amount: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def getrawtransaction(self, txid: str, decrypt: int=1) -> dict:
        raise NotImplementedError

    @abstractmethod
    def listtransactions(self, address: str) -> list:
        raise NotImplementedError

    def validateaddress(self, address: str) -> bool:
        "Returns True if the passed address is valid, False otherwise."

        try:
            Address.from_string(address, self.network_properties)
        except InvalidAddress:
            return False

        return True
