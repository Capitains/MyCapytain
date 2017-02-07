class CollectionDispatcher:
    """

    :param collection:
    :param default_inventory_name:
    """
    def __init__(self, collection, default_inventory_name=None):
        self.collection = collection
        if default_inventory_name is None:
            default_inventory_name = list(self.collection.children.values())[0].id
        self.__methods__ = [(default_inventory_name, lambda x, **k: True)]

    @property
    def methods(self):
        return self.__methods__

    def add(self, func, inventory_name=None):
        self.methods.append((inventory_name, func))

    def inventory(self, inventory_name):
        def decorator(f):
            self.add(func=f, inventory_name=inventory_name)
            return f
        return decorator

    def dispatch(self, collection, **kwargs):
        for inventory, method in self.methods[::-1]:
            if method(collection, **kwargs) is True:
                collection.parent = self.collection.children[inventory]
                return
        raise Exception("Text not dispatched %s" % collection.id)
