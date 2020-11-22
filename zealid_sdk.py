from base64 import b64encode
from urllib.request import urljoin
import hashlib
import regex
import requests

class Identiway:
    def __init__(self, api_key, api_endpoint='https://api.identiway.com/'):
        self.base_url = api_endpoint
        self.default_headers = {
                'user-agent': 'zealid-python-sdk/0.0.1',
                'Content-type': 'application/json',
                'x-api-key': api_key,
                }

    def validate(self, picture, document_type, sha1=None):
        """
        Consider using extractMRZ instead. This method will only call the validate endpoint
        without working around OCR bugs.
        """
        if not isinstance(picture, (bytes, bytearray)):
            raise Exception('expected "picture" to be bytes-like. TODO make exception hierarchy.')
        actual_sha1 = hashlib.sha1(picture).hexdigest()
        if sha1 and sha1 != actual_sha1:
            raise Exception('"picture" does not match given hash. TODO make exception hierarchy.')
        data = {
                'document': b64encode(picture).decode(),
                'digest': actual_sha1,
                'type': document_type,
                }
        r = requests.post(urljoin(self.base_url, 'docs/validate'), headers=self.default_headers, json=data)
        print(r.json())
        return r.json()

    def extractMRZ(self, picture, document_type, error_margin=3, sha1=None):
        """
        Calls validate method and does the following:
        * Replace \u304f with <
        * Remove all whitespace and encoded unicode characters.
        * Change all characters to uppercase
        * Replace O with 0
        * Do fuzzy regex search on OCR output.
        * Replace 0 with O in name and surname

        This method assumes document is a passport.
        Returns dict of 'names', 'surnames', 'birthdate'
        """
        is_lt = document_type == 'lt_pass_rev'
        regex_parts = [
                # line 1
                r'P',
                r'<' if is_lt else r'[A-Z]',
                r'(?P<country>LTU)' if is_lt else r'(?P<country>[A-Z<]{3})',
                r'(?P<surnames>\w+(<\w+)*)<<(?P<names>\w+(<\w+)*)',
                r'<*',
                # line 2
                r'[0-9]{8}<' if is_lt else r'[0-9A-Z<]{9}',
                r'[0-9]',
                r'(?P=country)',
                r'(?P<birthdate>[0-9]{6})',
                r'[0-9]',
                r'[MF<]',
                r'[0-9]{6}',
                r'[0-9]',
                r'[0-9]{11}<<<' if is_lt else r'[0-9A-Z<]{14}',
                r'[0-9<]',
                r'[0-9]',
                ]
        mrz_regex = regex.compile('(?e)({re}){{e<={error_margin}}}'.format(
                re=''.join(regex_parts), error_margin=error_margin))
        ocr_data = self.validate(picture, document_type, sha1)['ocr_texts'][0]
        print(ocr_data)
        ocr_data = ocr_data.translate({ord('く'): '<', ord(' '): '', ord('\n'): ''}).upper().replace('O', '0')
        print(ocr_data)
        match = mrz_regex.search(ocr_data)
        if not match:
            raise Exception('failed to extract MRZ from passport. TODO make exception hierarchy.')
        print(match)
        print(match.group('country'))
        print(match.group('surnames'))
        return {
                'names': match.group('names').replace('0', 'O').split('<'),
                'surnames': match.group('surnames').replace('0', 'O').split('<'),
                'birthdate': match.group('birthdate'),
                }
