def string_to_bool(string_value):
    return str(string_value).lower() == "true"

def to_dict(self):
    print(self)
    object_dictionary = vars(self)
    del object_dictionary["_sa_instance_state"]
    return object_dictionary