import requests
from lxml.html import fromstring


class Authentication:
    AUTH_URL = "https://utslogin.nlm.nih.gov/cas/v1/api-key"
    SERVICE = "http://umlsks.nlm.nih.gov"

    def __init__(self, apikey: str):
        self.apikey = apikey
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Content-type": "application/x-www-form-urlencoded",
                "Accept": "text/plain",
                "User-Agent": "python",
            }
        )

    def gettgt(self):
        resp = self.session.post(self.AUTH_URL, data={"apikey": self.apikey})
        response = fromstring(resp.text)
        # extract the entire URL needed from the HTML form (action attribute) returned -
        # eg., https://utslogin.nlm.nih.gov/cas/v1/tickets/TGT-36471-aYqNLN2rFIJPXKzxwdTNC5ZT7z3B3cTAKfSc5ndHQcUxeaDOLN-cas
        # we make a POST call to this URL in the getst method
        tgt = response.xpath("//form/@action")[0]
        return tgt

    def getst(self, tgt):
        return self.session.post(tgt, data={"service": self.SERVICE}).text
