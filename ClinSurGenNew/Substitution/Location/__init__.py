def sub_org(self, sg_file, token):
    """substitute organizations"""
    return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.org)


def sub_street(self, sg_file, token):
    """substitute street names"""
    return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.street)


def sub_city(self, sg_file, token):
    """substitute city names"""
    return self.get_surrogate_name(sg_file, token.text, token.norm_case, token.label, self.city)
