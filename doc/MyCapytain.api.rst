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
    :inherited-members:

Utilities
*********

.. automodule:: MyCapytain.common.utils
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

API Retrievers
##############

Module endpoints contains prototypes and implementation of retrievers in MyCapytain

CTS 5 API
*********

.. automodule:: MyCapytain.retrievers.cts5
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Prototypes
**********

.. automodule:: MyCapytain.retrievers.prototypes
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:


Resolvers
#########

Remote CTS API
**************

.. autoclass:: MyCapytain.resolvers.api.cts.HttpCTSResolver
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Prototypes
**********

.. automodule:: MyCapytain.resolvers.prototypes
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:


Texts and inventories
#####################

Text
****

TEI based texts
+++++++++++++++

.. autoclass:: MyCapytain.resources.texts.encodings.TEIResource
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Locally read text
+++++++++++++++++

.. autoclass:: MyCapytain.resources.texts.local.tei.Text
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.local.tei.Passage
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.local.tei.__SimplePassage__
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

CTS API Texts
+++++++++++++

Formerly MyCapytain.resources.texts.api (< 2.0.0)

.. autoclass:: MyCapytain.resources.texts.api.cts.Text
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

.. autoclass:: MyCapytain.resources.texts.api.cts.Passage
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Collections
***********

Metadata
++++++++

.. automodule:: MyCapytain.resources.prototypes.metadata
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

CTS inventory
+++++++++++++

.. automodule:: MyCapytain.resources.collections.cts
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

CTS Inventory Prototypes
++++++++++++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.cts.inventory
    :members:
    :undoc-members:
    :show-inheritance:
    :inherited-members:

Text Prototypes
+++++++++++++++

.. automodule:: MyCapytain.resources.prototypes.text
    :members:
    :undoc-members:
    :inherited-members:
    :show-inheritance:

