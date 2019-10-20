from mailtojson import MailJson
from pathlib import Path
import base64
import hashlib
import argparse


class MailAnalyzer:
    def __init__(self, mailpath):

        self.outputdir = Path("./output")
        self.outputdir.mkdir(parents=True, exist_ok=True)
        self.mailpath = mailpath
        self.maildir = Path(mailpath)

    def parse_and_save(self, content):
        mj = MailJson(content)
        mj.parse()
        data = mj.get_data()
        for k in data["attachments"]:
            outputfile = (
                k["filename"]
                + "_"
                + hashlib.sha256(base64.decodebytes(k["content"])).hexdigest()
            )
            path = self.outputdir / outputfile
            with open(path, "wb") as f:
                f.write(base64.decodebytes(k["content"]))

    def process_folder(self):
        for message in self.maildir.rglob("*.eml"):
            content = open(message, "r").read()
            self.parse_and_save(content)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", help="directory emails are stored in", required=True)
    args = parser.parse_args()
    mail = MailAnalyzer(args.d)
    mail.process_folder()


if __name__ == "__main__":
    main()
