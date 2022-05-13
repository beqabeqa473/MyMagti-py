from enum import IntEnum
import requests
import time

class MyMagtiAuthorizationError(Exception):
    pass

class RoamingType(IntEnum):
    ROAMING = 1
    INTERNET = 2

class MyMagti():

    OAUTH_STRING = "TXltYWd0aUFwcE5ldzpQaXRhbG9AI2RkZWVyYWFzYXNERjIxMyQl"
    CLIENT_ID = "MymagtiAppNew"
    OAUTH_URL = "https://oauth.magticom.ge/auth/"
    REST_URL = "https://rest.magticom.ge/"

    def __init__(self, username, password):
        self._expiresAt = None
        self._token = None
        self.userId = None
        self.username = username
        self.password = password

    def checkUser(self):
        res = requests.get(f"{self.OAUTH_URL}user/user/check/{self.username}").text
        return False if res == "false" else True

    def login(self):
        headers = {"Authorization": f"Basic {self.OAUTH_STRING}"}
        if not self.checkUser():
            raise MyMagtiAuthorizationError("Account doesn't exist")
        res = requests.post(f"{self.OAUTH_URL}oauth/token?grant_type=password", data={"username": self.username, "password": self.password, "client_id": self.CLIENT_ID}, headers=headers)
        if res.status_code != 200:
            raise MyMagtiAuthorizationError("Couldnot authorize! Check your credentials")
        res = res.json()
        self._token = res["access_token"]
        self._expiresAt = time.time() + res["expires_in"]
        self.userId = res["userId"]

    @property
    def token(self):
        if not time.time() >= self._expiresAt:
            return self._token
        else:
            self.login()
            return self._token

    def getSavedNumbers(self, userId=None):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"userId": self.userId if userId is None else userId}
        res = requests.get(f"{self.REST_URL}mymagti-rest-safe/rest/subscriber/saved/numbers", params=params, headers=headers)
        return res.json()

    def getSubscriberAccountGroupInfo(self, phoneNumber=None):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"phoneNumber": self.username if phoneNumber is None else phoneNumber}
        res = requests.get(f"{self.REST_URL}mymagti-rest-safe/rest/subscriber/account/group", params=params, headers=headers)
        return res.json()

    def getContractType(self, phoneNumber=None):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"phoneNumber": self.username if phoneNumber is None else phoneNumber}
        res = requests.get(f"{self.REST_URL}mymagti-rest-safe/rest/contract/type/ext", params=params, headers=headers)
        return res.json()

    def checkRoaming(self, phoneNumber=None, roamingType=RoamingType.ROAMING):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"phoneNumber": self.username if phoneNumber is None else phoneNumber, "serviceId": "190" if roamingType is RoamingType.ROAMING else "191"}
        res = requests.get(f"{self.REST_URL}mymagti-rest-safe/rest/services/check", params=params, headers=headers)
        return res.json()

    def setInternetRoamigStatus(self, phoneNumber=None, isActivate="1"):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"phoneNumber": self.username if phoneNumber is None else phoneNumber, "isActivate": isActivate}
        res = requests.post(f"{self.REST_URL}mymagti-rest-safe/rest/services/roaming/", params=params, headers=headers)
        return res.json()

    def setRoamigStatus(self, phoneNumber=None, isActivate="1"):
        headers = {"Authorization": f"bearer {self.token}"}
        params = {"phoneNumber": self.username if phoneNumber is None else phoneNumber, "isActivate": isActivate}
        res = requests.post(f"{self.REST_URL}mymagti-rest-safe/rest/services/roaming/camel", params=params, headers=headers)
        return res.json()
