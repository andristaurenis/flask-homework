from flask import Flask, render_template, request
from unidecode import unidecode
from os import getenv
from os.path import join, dirname
from dotenv import load_dotenv

# Load .env
load_dotenv()
ZEAL_ID_API_KEY = getenv('ZEAL_ID_API_KEY')

from .zealid_sdk import Identiway
identiway = Identiway(ZEAL_ID_API_KEY)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compare/', methods=['POST'])
def compare():
    mrz_data = identiway.extractMRZ(request.files['passportpicture'].read(), 'lt_pass_rev')
    comparison = {}
    for key in ('name', 'surname'):
        mrz_names = mrz_data[key + 's']
        provided_names = unidecode(request.form[key]).upper().translate(str.maketrans('.,-_', '    ')).split()
        if len(mrz_names) == len(provided_names):
            if mrz_names == provided_names:
                comparison[key] = 'ok - perfect match'
            elif sorted(mrz_names) == sorted(provided_names):
                comparison[key] = 'ok - wrong order of words'
            else:
                comparison[key] = f'wrong - Expected: ({mrz_names}) Given: ({provided_names})'
        elif set(provided_names).issubset(mrz_names):
            comparison[key] = f'wrong - Did you forget your middle name? Expected: ({mrz_names}) Given: ({provided_names})'
        else:
            comparison[key] = f'wrong - Expected: ({mrz_names}) Given: ({provided_names})'

    d = mrz_data['birthdate']
    mrz_birth = f'{d[0:2]}-{d[2:4]}-{d[4:6]}'
    if request.form['birthdate'][2:10] == mrz_birth:
        comparison['birthdate'] = 'ok'
    else:
        comparison['birthdate'] = f'wrong - Expected: ({mrz_birth}) Given: ({request.form["birthdate"][2:10]})'

    return render_template('compare.html', comparison=comparison)

if __name__ == '__main__':
    app.run()
