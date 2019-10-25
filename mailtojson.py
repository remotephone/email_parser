#!/usr/bin/env python

## Open Sourced by - Newsman App www.newsmanapp.com
## (c) 2013 Newsman App
## https://github.com/Newsman/MailToJson

import sys, email, re, csv, base64, json, pprint
from optparse import OptionParser
from io import StringIO
from datetime import datetime

VERSION = "1.3.2"


# regular expresion from https://github.com/django/django/blob/master/django/core/validators.py


class MailJson:
    def __init__(self, content=None):
        self.data = {}
        self.raw_parts = []
        self.encoding = "utf-8"  # output encoding
        self.setContent(content)

        self.email_re = re.compile(
            r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
            # quoted-string, see also http://tools.ietf.org/html/rfc2822#section-3.2.5
            r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-\011\013\014\016-\177])*"'
            r")@((?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)$)"  # domain
            r"|\[(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}\]$",
            re.IGNORECASE,
        )

        self.email_extract_re = re.compile(
            "<(([.0-9a-z_+-=]+)@(([0-9a-z-]+\.)+[0-9a-z]{2,9}))>", re.M | re.S | re.I
        )
        self.filename_re = re.compile(
            'filename="(.+)"|filename=([^;\n\r"\']+)', re.I | re.S
        )

        self.begin_tab_re = re.compile("^\t{1,}", re.M)
        self.begin_space_re = re.compile("^\s{1,}", re.M)

    def setEncoding(self, encoding):
        self.encoding = encoding

    def setContent(self, content):
        self.content = content

    def _fixEncodedSubject(self, subject):
        if subject is None:
            return ""

        subject = "%s" % subject
        subject = subject.strip()

        if len(subject) < 2:
            # empty string or not encoded string ?
            return subject
        if subject.find("\n") == -1:
            # is on single line
            return subject
        if subject[0:2] != "=?":
            # not encoded
            return subject

        subject = subject.replace("\r", "")
        subject = self.begin_tab_re.sub("", subject)
        subject = self.begin_space_re.sub("", subject)
        lines = subject.split("\n")

        new_subject = ""
        for l in lines:
            new_subject = "%s%s" % (new_subject, l)
            if l[-1] == "=":
                new_subject = "%s\n " % new_subject

        return new_subject

    def _extract_email(self, s):
        ret = self.email_extract_re.findall(s)
        if len(ret) < 1:
            p = s.split(" ")
            for e in p:
                e = e.strip()
                if self.email_re.match(e):
                    return e

            return None
        else:
            return ret[0][0]

    def _decode_headers(self, v):
        if type(v) is not list:
            v = [v]

        ret = []
        for h in v:
            h = email.header.decode_header(h)
            h_ret = []
            for h_decoded in h:
                hv = h_decoded[0]
                h_encoding = h_decoded[1]
                if h_encoding is None:
                    h_encoding = "utf-8"
                elif h_encoding == "iso-8859-1":
                    hv = hv.decode("utf-8", errors="replace")
                    h_encoding = "utf-8"
                elif h_encoding == "unknown-8bit":
                    hv = hv.decode("utf-8", errors="replace")
                    h_encoding = "utf-8"
                else:
                    hv = hv.decode("utf-8", errors="replace")
                    h_encoding = h_encoding.lower()
                hv = str(hv.encode(self.encoding), h_encoding).strip().strip("\t")

                h_ret.append(hv.encode(self.encoding))

            ret.append(str(b" ".join(h_ret), self.encoding))

        return ret

    def _parse_recipients(self, v):
        if v is None:
            return None

        ret = []

        # Sometimes a list is passed, which breaks .replace()
        if isinstance(v, list):
            v = ",".join(v)
        v = v.replace("\n", " ").replace("\r", " ").strip()
        s = StringIO(v)
        c = csv.reader(s)
        try:
            row = next(c)
        except StopIteration:
            return ret

        for entry in row:
            entry = entry.strip()
            if self.email_re.match(entry):
                e = entry
                entry = ""
            else:
                e = self._extract_email(entry)
                entry = entry.replace("<%s>" % e, "")
                entry = entry.strip()
                if e and entry.find(e) != -1:
                    entry = entry.replace(e, "").strip()

            # If all else has failed
            if entry and e is None:
                e_split = entry.split(" ")
                e = e_split[-1].replace("<", "").replace(">", "")
                entry = " ".join(e_split[:-1])

            ret.append({"name": entry, "email": e})

        return ret

    def _parse_date(self, v):
        if v is None:
            return datetime.now()

        tt = email.utils.parsedate_tz(v)

        if tt is None:
            return datetime.now()

        timestamp = email.utils.mktime_tz(tt)
        date = datetime.fromtimestamp(timestamp)
        return date

    def _get_part_headers(self, part):
        # raw headers
        headers = {}
        for k in list(part.keys()):
            k = k.lower()
            v = part.get_all(k)
            v = self._decode_headers(v)

            if len(v) == 1:
                headers[k] = v[0]
            else:
                headers[k] = v

        return headers

    def parse(self):
        self.msg = email.message_from_bytes(bytes(self.content, "utf-8"))

        content_charset = self.msg.get_content_charset()
        if content_charset == None:
            content_charset = "utf-8"

        headers = self._get_part_headers(self.msg)
        self.data["headers"] = headers
        self.data["datetime"] = self._parse_date(headers.get("date", None)).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self.data["subject"] = self._fixEncodedSubject(headers.get("subject", None))
        self.data["to"] = self._parse_recipients(headers.get("to", None))
        self.data["reply-to"] = self._parse_recipients(headers.get("reply-to", None))
        self.data["from"] = self._parse_recipients(headers.get("from", None))
        self.data["cc"] = self._parse_recipients(headers.get("cc", None))

        attachments = []
        parts = []
        for part in self.msg.walk():
            if part.is_multipart():
                continue

            content_disposition = part.get("Content-Disposition", None)
            if content_disposition:
                # we have attachment
                r = self.filename_re.findall(content_disposition)
                if r:
                    filename = sorted(r[0])[1]
                else:
                    filename = "undefined"

                a = {
                    "filename": filename,
                    "content": base64.b64encode(part.get_payload(decode=True)),
                    "content_type": part.get_content_type(),
                }
                attachments.append(a)
            else:
                try:
                    p = {
                        "content_type": part.get_content_type(),
                        "content": str(
                            part.get_payload(decode=1), content_charset, "ignore"
                        ),
                        "headers": self._get_part_headers(part),
                    }
                    parts.append(p)
                    self.raw_parts.append(part)
                except LookupError:
                    # Sometimes an encoding isn't recognised - not much to be done
                    pass

        self.data["attachments"] = attachments
        self.data["parts"] = parts
        self.data["encoding"] = self.encoding

        return self.get_data()

    def get_data(self):
        return self.data

    def get_raw_parts(self):
        return self.raw_parts
