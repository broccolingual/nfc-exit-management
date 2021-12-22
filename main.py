import binascii
import json
import os
import pprint
import sys
import time

from dotenv import load_dotenv
import requests
import nfc

load_dotenv(verbose=True)
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

NFC_READER_ID = "usb:054c:06c3"
LINE_NOTIFY_TOKEN = os.environ.get("LINE_NOTIFY_TOKEN")
LINE_NOTIFY_ENDPOINT = "https://notify-api.line.me/api/notify"

def sendNotify(content: str):
    if content is not None and 1 <= len(content) <= 1000:
        payload = {"message": content, "notificationDisabled": "false"}
        r = requests.post(LINE_NOTIFY_ENDPOINT, headers={"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}, data=payload)
        return r

def main(args):
    if not os.path.isfile("tags.json"):
        with open("tags.json", "w") as f:
            json.dump([], f)

    while True:
        with nfc.ContactlessFrontend(NFC_READER_ID) as clf:
            tag = clf.connect(rdwr={"on-connect": lambda tag: False})
            if tag.TYPE == "Type3Tag":
                idm = binascii.hexlify(tag.idm).decode()
            elif tag.TYPE == "Type4Tag":
                idm = binascii.hexlify(tag.identifier).decode()
            
            with open("tags.json", "r") as f:
                json_data = json.load(f)
            
            registared_idms = set()
            for registared_idm in json_data:
                registared_idms.add(registared_idm["idm"])

            if idm not in registared_idms:
                idm_name = input("Please type your name > ")
                json_data.append({"idm": idm, "name": idm_name})
            else:
                for data in json_data:
                    if idm == data["idm"]:
                        name = data["name"]
                print(f"{tag.TYPE}: {idm} registared as {name}")
                sendNotify(f"{name}さんが帰宅しました")

            with open("tags.json", "w") as f:
                json.dump(json_data, f)

            time.sleep(3) 

if __name__ == "__main__":
    main(sys.argv)
