from MyCapytain.errors import UndispatchedTextError


class CollectionDispatcher:
    """ Collection Dispatcher provides a utility to divide automatically texts and collections \
    into different collections

    :param collection: The root collection
    :param default_inventory_name: The default name of the default collection
    """
    def __init__(self, collection, default_inventory_name=None):
        self.collection = collection
        if default_inventory_name is None:
            default_inventory_name = list(self.collection.children.values())[0].id
        self.__methods__ = [(default_inventory_name, lambda x, **kwargs: True)]

    @property
    def methods(self):
        """ List of methods to dispatch resources.

        Each element is a tuple with two elements :
            - First one is the inventory identifier to dispatch to
            - Second one is a function which, if returns true, will activate dispatching to given

        :rtype: List
        """
        return self.__methods__

    def add(self, func, inventory_name):
        """ Register given function as a filter.

        If this function "func" returns True when given an object, said object will be dispatched to \
        Collection(inventory_name)

        :param func: Callable
        :param inventory_name: Identifier of the collection to dispatch to
        """
        self.methods.append((inventory_name, func))

    def inventory(self, inventory_name):
        """ Decorator to register filters for given inventory. For a function "abc", it has the same effect

        :param inventory_name:
        :return:

        .. code-block:: python

            tic = CtsTextInventoryCollection()
            latin = CtsTextInventoryMetadata("urn:perseus:latinLit", parent=tic)
            latin.set_label("Classical Latin", "eng")
            dispatcher = CollectionDispatcher(tic)

            @dispatcher.inventory("urn:perseus:latinLit")
            def dispatchLatinLit(collection, path=None, **kwargs):
                if collection.id.startswith("urn:cts:latinLit:"):
                    return True
                return False

        """
        def decorator(f):
            self.add(func=f, inventory_name=inventory_name)
            return f
        return decorator

    def dispatch(self, collection, **kwargs):
        """ Dispatch a collection using internal filters

        :param collection: Collection object
        :param kwargs: Additional keyword arguments that could be used by internal filters
        :return: None
        :raises:
        """
        for inventory, method in self.methods[::-1]:
            if method(collection, **kwargs) is True:
                collection.parent = self.collection.children[inventory]
                return
        raise UndispatchedTextError("CapitainsCtsText not dispatched %s" % collection.id)
