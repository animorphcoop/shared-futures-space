import re

from django.http import HttpResponse

# TODO: They would be loaded via upload_conf with locations
active_postcodes = ['BT48', 'BT48', 'BT17', 'BT12', 'BT7', 'BT4', 'BT15', 'WD23']

# TODO: make sure on the front the post code is no shorter than 3chars

def filter_postcode(typed_postcode):
    # strip from whitespaces
    entered_postcode = typed_postcode.replace(" ", "")

    # get outcode and make upper for a match
    m = re.match(r'([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)([0-9][a-zA-Z]{2})?', entered_postcode)
    if m is None:
        # not a valid postcode
        raise ValueError('not a valid postcode: ' + entered_postcode)
    entered_postcode = m.group(1).upper()

    # look for one with upper - make sure exact match is there,
    # particularly in a situation where people enter a full postcode
    # but in fact only first 3 chars matter, check first 3
    for postcode in active_postcodes:
        if postcode == entered_postcode:
            entered_postcode = postcode
        else:
            if postcode == entered_postcode[0:3]:
                entered_postcode = postcode

    return entered_postcode
