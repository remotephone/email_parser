## Email Parser and Attachement Locator and Extractor (epale!)

This would have been a lot more work had it not been for https://github.com/Newsman/MailToJson. There was an unmerged pull  request in https://github.com/Newsman/MailToJson/pull/5 by @grintor I was able to merge into mine to make everything python 3 compatible. Together, that let me very quickly take an email and put it into json using Python3. I ran both python files through [black](https://pypi.org/project/black/) to clean up formatting.

I took that, converted it to a class so I could more easily import it in another larger project I'm working on, added a focus on attachment extraction and hashing, and epale! Here we are.

Usage is simple:

~~~
python3 test.py -d /home/epale/emails/
~~~
