def process_specimen(specimen=None):
    requester_specimen_id=specimen.identifier[0].value # just take first identifier
    laboratory_accession_id=specimen.accessionIdentifier.value
    specimen_type=specimen.type.coding[0].display # just take first coding
    collected_date=specimen.collection.collectedDateTime
    received_date=specimen.receivedTime
    return requester_specimen_id, laboratory_accession_id, specimen_type, collected_date, received_date