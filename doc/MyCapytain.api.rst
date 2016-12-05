MyCapytain API Documentation
============================

Utilities, metadata and references
##################################

Module common contains tools such as a namespace dictionary as well as cross-implementation objects, like URN, Citations...

URN, References and Citations
*****************************

.. autoclass:: MyCapytain.common.reference.Node
    :members:

.. autoclass:: MyCapytain.common.reference.URN
    :members:

.. autoclass:: MyCapytain.common.reference.Reference
    :members:

.. autoclass:: MyCapytain.common.reference.Citation
    :members: fill, __iter__, __len__

Metadata containers
*******************

.. automodule:: MyCapytain.common.metadata
    :members:
    :undoc-members:
    :show-inheritance:

Utilities
*********

.. automodule:: MyCapytain.common.utils
    :members:
    :undoc-members:
    :show-inheritance:

API Retrievers
##############

Module endpoints contains prototypes and implementation of retrievers in MyCapytain

Ahab
****

.. automodule:: MyCapytain.retrievers.ahab
    :members:
    :undoc-members:
    :show-inheritance:

CTS 5 API
*********

.. automodule:: MyCapytain.retrievers.cts5
    :members:
    :undoc-members:
    :show-inheritance:

Prototypes
**********

.. automodule:: MyCapytain.retrievers.prototypes
    :members:
    :undoc-members:
    :show-inheritance:

Texts and inventories
#####################

Text
****

TEI based texts
+++++++++++++++

.. autoclass:: MyCapytain.resources.texts.tei.TEIResource
    :members:
    :undoc-members:
    :show-inheritance:

Locally read text
+++++++++++++++++

.. autoclass:: MyCapytain.resources.texts.local.tei.Text
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.local.tei.Passage
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.local.tei.__SimplePassage__
    :members:
    :undoc-members:
    :show-inheritance:

CTS API Texts
+++++++++++++

Formerly MyCapytain.resources.texts.api (< 2.0.0)

.. autoclass:: MyCapytain.resources.texts.api.cts.Text
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.api.cts.Passage
    :members:
    :undoc-members:
    :show-inheritance:

Collections
***********

Metadata
++++++++

.. automodule:: MyCapytain.resources.prototypes.metadata
    :members:
    :undoc-members:
    :show-inheritance:

CTS inventory
+++++++++++++

.. automodule:: MyCapytain.resources.collections.cts
    :members:
    :undoc-members:
    :show-inheritance:

CTS Inventory Prototypes
++++++++++++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.cts.inventory
    :members:
    :undoc-members:
    :show-inheritance:

Text Prototypes
+++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.text
    :members:
    :undoc-members:
    :show-inheritance:
