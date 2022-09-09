# TODO: They would be loaded via upload_conf with locations
active_postcodes = ['BT48', 'BT48', 'BT17', 'BT12', 'BT7', 'BT4', 'BT15', 'WD23']

# TODO: make sure on the front the post code is no shorter than 3chars

def filter_postcode(typed_postcode):
    # strip from whitespaces
    entered_postcode = typed_postcode.replace(" ", "")

    # get starting part and make upper for a match
    if len(entered_postcode) >= 4:
        entered_postcode = entered_postcode[0:4].upper()
    else:
        entered_postcode = entered_postcode[0:3].upper()

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