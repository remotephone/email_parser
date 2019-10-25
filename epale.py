import argparse
import base64
import hashlib
import re
from pathlib import Path

from mailtojson import MailJson


class MailAnalyzer:
    def __init__(self, message, outputdir=None):

        if outputdir == None:
            self.outputdir = Path("./output")
        else:
            self.outputdir = outputdir

        self.outputdir.mkdir(parents=True, exist_ok=True)
        self.message = open(message, "r").read()
        self.mj = MailJson(self.message)
        self.mj.parse()
        self.data = self.mj.get_data()

    def handle_attachments(self):
        for k in self.data["attachments"]:
            outputfile = (
                k["filename"]
                + "_"
                + hashlib.sha256(base64.decodebytes(k["content"])).hexdigest()
            )
            path = self.outputdir / outputfile
            with open(path, "wb") as f:
                f.write(base64.decodebytes(k["content"]))

    def extract_urls(self):
        for k in self.data["parts"]:
            urls = re.findall('"((http|ftp|file)s?://.*?)"', k["content"])
            for url in urls:
                print(url)


def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-d", "--dir", help="directory emails are stored in")
    group.add_argument("-m", "--msg", help="single original.msg or eml file to parse")
    parser.add_argument(
        "-u",
        "--url",
        help="parse and extract URLs from message body",
        action="store_true",
    )
    parser.add_argument(
        "-a", "--attch", help="parse and extract attachments", action="store_true"
    )
    parser.add_argument("-o", "--out", help="output directory", default="./output")
    args = parser.parse_args()

    messages = []
    if args.dir:
        maildir = Path(args.dir)
        for message in maildir.rglob("*.eml"):
            messages.append(message)
    elif args.msg:
        messages.append(Path(args.msg))

    outputdir = Path(args.out)
    outputdir.mkdir(parents=True, exist_ok=True)

    for message in messages:
        print(message)
        mail = MailAnalyzer(message)
        mail.handle_attachments()
        mail.extract_urls()


if __name__ == "__main__":
    main()
