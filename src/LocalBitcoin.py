import hmac
import json
import urllib
import hashlib
import requests
from urllib import urlencode
from datetime import datetime


class LocalBitcoin:

    baseurl = 'https://localbitcoins.com'

    def __init__(self, hmac_auth_key, hmac_auth_secret, debug = False):
        self.hmac_auth_key = hmac_auth_key
        self.hmac_auth_secret = hmac_auth_secret
        self.debug = debug

    """
    Returns public user profile information
    """
    def getAccountInfo(self, username):
        return self.sendRequest('/api/account_info/' + username + '/', '', 'get')

    """
    Return the information of the currently logged in user (the owner of authentication token).
    """
    def getMyself(self):
        return self.sendRequest('/api/myself/', '', 'get')

    """
    Checks the given PIN code against the user's currently active PIN code.
    You can use this method to ensure the person using the session is the legitimate user.
    """
    def checkPinCode(self, code):
        return self.sendRequest('/api/pincode/', {'code': code}, 'post')

    """
    Return open and active contacts
    """
    def getDashboard(self):
        return self.sendRequest('/api/dashboard/', '', 'get')

    """
    Return released (successful) contacts
    """
    def getDashboardReleased(self):
        return self.sendRequest('/api/dashboard/released/', '', 'get')

    """
    Return canceled contacts
    """
    def getDashboardCanceled(self):
        return self.sendRequest('/api/dashboard/canceled/', '', 'get')

    """
    Return closed contacts, both released and canceled
    """
    def getDashboardClosed(self):
        return self.sendRequest('/api/dashboard/closed/', '', 'get')

    """
    Releases the escrow of contact specified by ID {contact_id}.
    On success there's a complimentary message on the data key.
    """
    def contactRelease(self, contact_id):
        return self.sendRequest('/api/contact_release/' + contact_id + '/', '', 'post')

    """
    Releases the escrow of contact specified by ID {contact_id}.
    On success there's a complimentary message on the data key.
    """
    def contactReleasePin(self, contact_id, pincode):
        return self.sendRequest('/api/contact_release_pin/' + contact_id + '/', {'pincode': pincode}, 'post')

    """
    Reads all messaging from the contact. Messages are on the message_list key.
    On success there's a complimentary message on the data key.
    attachment_* fields exist only if there is an attachment.
    """
    def getContactMessages(self, contact_id):
        return self.sendRequest('/api/contact_messages/' + contact_id + '/', '', 'get')

    """
    Marks a contact as paid.
    It is recommended to access this API through /api/online_buy_contacts/ entries' action key.
    """
    def markContactAsPaid(self, contact_id):
        return self.sendRequest('/api/contact_mark_as_paid/' + contact_id + '/', '', 'get')

    """
    Post a message to contact
    """
    def postMessageToContact(self, contact_id, message):
        return self.sendRequest('/api/contact_message_post/' + contact_id + '/', {'msg': message}, 'post')

    """
    Starts a dispute with the contact, if possible.
    You can provide a short description using topic. This helps support to deal with the problem.
    """
    def startDispute(self, contact_id, topic = None):
        topic = ''
        if topic != None:
            topic = {'topic': topic}
        return self.sendRequest('/api/contact_dispute/' + contact_id + '/', topic, 'post')

    """
    Cancels the contact, if possible
    """
    def cancelContact(self, contact_id):
        return self.sendRequest('/api/contact_cancel/' + contact_id + '/', '', 'post')

    """
    Attempts to fund an unfunded local contact from the seller's wallet.
    """
    def fundContact(self, contact_id):
        return self.sendRequest('/api/contact_fund/' + contact_id + '/', '', 'post')

    """
    Attempts to create a contact to trade bitcoins.
    Amount is a number in the advertisement's fiat currency.
    Returns the API URL to the newly created contact at actions.contact_url.
    Whether the contact was able to be funded automatically is indicated at data.funded.
    Only non-floating LOCAL_SELL may return unfunded, all other trade types either fund or fail.
    """
    def createContact(self, contact_id, ammount, message = None):
        post = ''
        if message == None:
            post = {'ammount': ammount}
        else:
            post = {'ammount': ammount, 'message': message}
        return self.sendRequest('/api/contact_create/' + contact_id + '/', post, 'post')

    """
    Gets information about a single contact you are involved in. Same fields as in /api/contacts/.
    """
    def getContactInfo(self, contact_id):
        return self.sendRequest('/api/contact_info/' + contact_id + '/', '', 'get')

    """
    contacts is a comma-separated list of contact IDs that you want to access in bulk.
    The token owner needs to be either a buyer or seller in the contacts, contacts that do not pass this check are simply not returned.
    A maximum of 50 contacts can be requested at a time.
    The contacts are not returned in any particular order.
    """
    def getContactsInfo(self, contacts):
        return self.sendRequest('/api/contact_info/', {'contacts': contacts}, 'get')

    """
    Returns maximum of 50 newest trade messages.
    Messages are ordered by sending time, and the newest one is first.
    The list has same format as /api/contact_messages/, but each message has also contact_id field.
    """
    def getRecentMessages(self):
        return self.sendRequest('/api/recent_messages/', '', 'get')

    """
    Gets information about the token owner's wallet balance.
    """
    def getWallet(self):
        return self.sendRequest('/api/wallet/', '', 'get')

    """
    Same as /api/wallet/ above, but only returns the message, receiving_address_list and total fields.
    (There's also a receiving_address_count but it is always 1: only the latest receiving address is ever returned by this call.)
    Use this instead if you don't care about transactions at the moment.
    """
    def getWalletBallance(self):
        return self.sendRequest('/api/wallet-balance/', '', 'get')

    """
    Sends amount bitcoins from the token owner's wallet to address.
    Note that this API requires its own API permission called Money.
    On success, this API returns just a message indicating success.
    It is highly recommended to minimize the lifetime of access tokens with the money permission.
    Call /api/logout/ to make the current token expire instantly.
    """
    def walletSend(self, ammount, address):
        return self.sendRequest('/api/wallet-send/', {'ammount': ammount, 'address': address}, 'post')

    """
    As above, but needs the token owner's active PIN code to succeed.
    Look before you leap. You can check if a PIN code is valid without attempting a send with /api/pincode/.
    Security concern: To get any security beyond the above API, do not retain the PIN code beyond a reasonable user session, a few minutes at most.
    If you are planning to save the PIN code anyway, please save some headache and get the real no-pin-required money permission instead.
    """
    def walletSendWithPin(self, ammount, address, pincode):
        return self.sendRequest('/api/wallet-send-pin/', {'ammount': ammount, 'address': address, 'pincode': pincode}, 'post')

    """
    Gets an unused receiving address for the token owner's wallet, its address given in the address key of the response.
    Note that this API may keep returning the same (unused) address if called repeatedly.
    """
    def getWalletAddress(self):
        return self.sendRequest('/api/wallet-addr/', '', 'post')

    """
    Expires the current access token immediately.
    To get a new token afterwards, public apps will need to reauthenticate, confidential apps can turn in a refresh token.
    """
    def logout(self):
        return self.sendRequest('/api/logout/', '', 'post')

    """
    Lists the token owner's all ads on the data key ad_list, optionally filtered. If there's a lot of ads, the listing will be paginated.
    Refer to the ad editing pages for the field meanings. List item structure is like so:
    """
    def getOwnAds(self):
        return self.sendRequest('/api/ads/', '', 'post')

    def sendRequest(self, endpoint, params, method):

        params_encoded = ''
        if params != '':
            params_encoded = urllib.urlencode(params)
            if method == 'get':
              params_encoded = '?' + params_encoded

        now = datetime.utcnow()
        epoch = datetime.utcfromtimestamp(0)
        delta = now - epoch
        nonce = int(delta.total_seconds() * 1000)

        message = str(nonce) + self.hmac_auth_key + endpoint + params_encoded
        signature = hmac.new(self.hmac_auth_secret, msg = message, digestmod = hashlib.sha256).hexdigest().upper()

        headers = {}
        headers['Apiauth-key'] = self.hmac_auth_key
        headers['Apiauth-Nonce'] = str(nonce)
        headers['Apiauth-Signature'] = signature
        if method == 'get':
            response = requests.get(self.baseurl + endpoint, headers = headers, params = params)
        else:
            response = requests.post(self.baseurl + endpoint, headers = headers, data = params)

        if self.debug == True:
            print 'REQUEST: ' + self.baseurl + endpoint
            print 'PARAMS: ' + str(params)
            print 'METHOD: ' + method
            print 'RESPONSE: ' + response.text

        return json.loads(response.text)['data']
