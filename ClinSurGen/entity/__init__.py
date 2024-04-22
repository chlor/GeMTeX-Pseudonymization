class Entity:
    """
    Entity properties
    """

    def __init__(self, text, label, start, end, id):
        self.norm_case = None
        self.text = text
        self.label = label
        self.start = start
        self.end = end
        self.id = id

    # set case normalized token
    def set_norm_case(self, token_norm_case):
        self.norm_case = token_norm_case
