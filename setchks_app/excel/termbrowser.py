def termbrowser_hyperlink(sctid=None, destination_sctid=None):
    if destination_sctid is None:
        destination_sctid = sctid
    formatted_string = (
        "=HYPERLINK("
        f'"https://termbrowser.nhs.uk/?perspective=full&conceptId1={destination_sctid}'
        '&langRefset=999001261000000100,999000691000001104",'
        f'"{sctid}")'
    )
    return formatted_string
