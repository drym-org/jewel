
def unique_name(namespace, location):
    """ Generate a unique name using namespace and a "location" as raw
    material. The location is just any additional information that could help
    in generating the unique name, for instance a containing folder name that
    may serve to differentiate the entity from other entities like it.

    For now we simply concatenate these two strings, as that is sufficient for
    our purposes.
    """
    return ".".join([namespace, location]).strip(".")
