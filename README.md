# dependencies
* python-dotenv
* flask
* unidecode
* regex
* requests

# install
```bash
python3 -m venv venv
. ./venv/bin/activate
pip install -r stable-req.txt
```

# run
create `.env` file. See `.env.example`.
`FLASK_APP=server.py flask run`

# service
This service is hosted on http://78.58.52.209:5000/

# solution
Remove diatrics from user input because MRZ will only contain characters without them.
Apply fuzzy regular expression on the OCR output to find the MRZ.
Extract names, surnames and birth date from MRZ.
Compare with user provided input using some custom logic. Not a lot of effort was put into this(Task requirements were not very specific). Maybe FuzzyWuzzy should be used.

# problems
Many small problems were not touched because the task took a lot of time of investigating. This section can be considered a TODO list. Maybe not all my insights will be summerised here - I think it is worth to have another talk.

The ORC service API endpoint is not very good. It seems to recognize any utf8 character even though we are only interested in basic latin and decimals. Many < characters are read as く (U+304F HIRAGANA LETTER KU). There are some other random characters present in the OCR output. This also raises concerns about the Russian alphabet where some letters look exactly the same as latin ones. Also the recognition is not very precise.

Usage of the `unidecode` library which is under GPL might conflict with the existing company policy.

Speed can be optimized by precompiling the regular expression.

Code is not very structured because there is too little content to structure (i.e. does not resemble some serious production grade project)

The output of ORC could be improved by preprocessing the image. If given more time I could work on it, but at this point it seems more worthwhile to improve the ORC itself.
This is an interesting read.
https://www.pyimagesearch.com/2015/11/30/detecting-machine-readable-zones-in-passport-images/

Checksum digits in the MRZ were not checked.

Did not write any tests. 

Perhaps it is worth using an external service for this job.
https://github.com/DoubangoTelecom/ultimateMRZ-SDK
