import re
from area.models import PostCode


def filter_postcode(typed_postcode) -> str:
    # strip from whitespaces
    entered_postcode = typed_postcode.replace(" ", "")
    active_postcodes = PostCode.objects.all().values_list('code')

    # get outcode and make upper for a match
    m = re.match(r'([a-zA-Z]{1,2}[0-9][a-zA-Z0-9]?)([0-9][a-zA-Z]{2})?', entered_postcode)
    if m is not None:
        # recognised postcode form, normalise
        entered_postcode = m.group(1).upper()

    # look for one with upper - make sure exact match is there,
    # particularly in a situation where people enter a full postcode
    # but in fact only first 4 chars matter, check first 4
    for postcode in active_postcodes:
        if postcode == entered_postcode[0:4]:
            entered_postcode = postcode

    if len(entered_postcode) > 4:
            entered_postcode = entered_postcode[0:4]

    return entered_postcode
