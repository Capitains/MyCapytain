MyCapytain API Documentation
============================

Utilities, metadata and references
##################################

Module common contains tools such as a namespace dictionary as well as cross-implementation objects, like URN, Citations...

URN, References and Citations
*****************************

.. autoclass:: MyCapytain.common.reference.URN
.. autoclass:: MyCapytain.common.reference.Reference

.. autoclass:: MyCapytain.common.reference.Citation
    :members: fill, __iter__, __len__

Metadata containters
********************

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

API Endpoints
#############

Module endpoints contains prototypes and implementation of endpoints calls in MyCapytain

Ahab
****

.. automodule:: MyCapytain.endpoints.ahab
    :members:
    :undoc-members:
    :show-inheritance:

CTS 5 API
*********

.. automodule:: MyCapytain.endpoints.cts5
    :members:
    :undoc-members:
    :show-inheritance:

Prototypes
**********

.. automodule:: MyCapytain.endpoints.proto
    :members:
    :undoc-members:
    :show-inheritance:

Texts and inventories
#####################

Text
****

TEI based texts
+++++++++++++++

.. autoclass:: MyCapytain.resources.texts.tei.Citation
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.tei.Passage
    :members:
    :undoc-members:
    :show-inheritance:

Locally read text
+++++++++++++++++

.. autoclass:: MyCapytain.resources.texts.local.Text
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.local.Passage
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.local.ContextPassage
    :members:
    :undoc-members:
    :show-inheritance:

API's Text results
++++++++++++++++++

.. autoclass:: MyCapytain.resources.texts.api.Text
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: MyCapytain.resources.texts.api.Passage
    :members:
    :undoc-members:
    :show-inheritance:

Inventories
***********

.. automodule:: MyCapytain.resources.inventory
    :members:
    :undoc-members:
    :show-inheritance:

Prototypes
**********

.. automodule:: MyCapytain.resources.proto.text
    :members:
    :undoc-members:
    :show-inheritance:

.. automodule:: MyCapytain.resources.proto.inventory
    :members:
    :undoc-members:
    :show-inheritance:
