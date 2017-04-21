from inspect import getmro


class Exportable(object):
    """ Objects that supports Export

    :cvar EXPORT_TO: List of Mimetypes the resource can export to
    """
    EXPORT_TO = []
    DEFAULT_EXPORT = None

    def __init__(self, *args, **kwargs):
        pass

    @property
    def export_capacities(self):
        """  List Mimetypes that current object can export to
        """
        return [export for cls in getmro(type(self)) if hasattr(cls, "EXPORT_TO") for export in cls.EXPORT_TO]

    def __export__(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        return None

    def export(self, output=None, **kwargs):
        """ Export the collection item in the Mimetype required.

        :param output: Mimetype to export to (Uses MyCapytain.common.utils.Mimetypes)
        :type output: str
        :return: Object using a different representation
        """
        if output is None:
            output = self.DEFAULT_EXPORT
        if output is not None and output in self.export_capacities:
            for cls in getmro(type(self)):
                if hasattr(cls, "EXPORT_TO") and output in cls.EXPORT_TO:
                    return cls.__export__(self, output, **kwargs)
        raise NotImplementedError(
            "Mimetype {} has not been implemented for this resource".format(output or "(No Mimetype)")
        )