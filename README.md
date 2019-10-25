## Email Parser and Attachement Locator and Extractor (epale!)

This would have been a lot more work had it not been for https://github.com/Newsman/MailToJson. There was an unmerged pull  request in https://github.com/Newsman/MailToJson/pull/5 by @grintor I was able to merge into mine to make everything python 3 compatible. Together, that let me very quickly take an email and put it into json using Python3. 

I took that, converted it to a class so I could more easily import it in another larger project I'm working on, added a focus on attachment extraction and hashing, and epale! Here we are. I ran both python files through [black](https://pypi.org/project/black/) to clean up formatting.

Usage is simple:

~~~
python3 test.py -d /home/epale/emails/
~~~

Currently outputs into `./output` in the working directory and names files following the `filename_sha256hash` format. 

ToDo:
- Add proper logging
- Test on a lot more samples to find bugs (done, used [this](https://github.com/mikel/mail/tree/master/spec/fixtures) does not handle non-ascii filenames??)
- Check hash values against virustotal
- Extract urls from body of the email (done)
