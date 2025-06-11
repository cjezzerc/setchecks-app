"""class to hold info about official namespaces and function to populate a list of namepaces"""


class Namespace:
    def __init__(self, details_dict):
        self.namespace = details_dict["namespace"]
        self.organization_name = details_dict["organizationName"]
        self.organization_and_contact_details = details_dict[
            "organizationAndContactDetails"
        ]
        self.date_issued = details_dict["data_issued"]
        self.email = details_dict["email"]
        self.notes = details_dict["notes"]


def get_namespaces():
    pass


if __name__ == "__main__":
    import sys

    namespace = sys.argv[1]
