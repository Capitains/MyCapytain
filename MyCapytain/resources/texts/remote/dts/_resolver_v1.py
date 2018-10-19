from ....prototypes.text import InteractiveTextualNode


class DtsResolverText(InteractiveTextualNode):
    def __init__(self, identifier, resolver, **kwargs):
        super(InteractiveTextualNode, self).__init__(identifier=identifier, **kwargs)
        self.__childIds__ = None