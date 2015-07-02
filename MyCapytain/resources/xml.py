from .proto import inventory
from lxml import etree
from io import IOBase, StringIO
from past.builtins import basestring

ns = {
    "tei" : "http://www.tei-c.org/ns/1.0",
    "ahab" : "lala",
    "ti" : "http://chs.harvard.edu/xmlns/cts"
}

def parse(xml):
    if isinstance(xml, IOBase):
        pass
    elif isinstance(xml, (basestring)):
        xml = StringIO(xml)
    else:
        raise TypeError("Unsupported type of resource")
    parsed = etree.parse(xml)
    xml.close()
    return parsed


class TextInventory(inventory.TextInventory):
    """ Represents a CTS Inventory file
    """

    def parse(self, resource):
        self.xml = parse(resource)
        self.textgroups = [textgroup for textgroup in self.xml.xpath('//ti:textgroup', namespaces=ns)]
