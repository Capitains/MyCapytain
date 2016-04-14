Endpoints
=========

Introduction
############

A first important point for MyCapytains endpoint is that the resources are not parsed into object but should only
provide the request by default.

Getting Passage from an endpoint using a Retriever
##################################################

.. code-block:: python

    from MyCapytain.retrievers import cts5
    from MyCapytain.resources.texts.api import Text

    # We set the variable up, as if we were in a function
    # This URN won't work (urn:cts:greekLit:tlg0032.tlg005.perseus-grc1) because it has no TEI namespace
    urn = 'urn:cts:latinLit:phi1294.phi002.perseus-lat2'
    ref = "1.1-1.2"

    # We set the api up. Endpoint takes one required argument
    #  (the URI) and one inventory as optional argument
    cts = cts5.CTS('http://services2.perseids.org/exist/restxq/cts', inventory="nemo")

    # We set up a text object to be able to retrieve passage of it
    # Text in API modules takes endpoint as resource and URN as param

    text = Text(urn=urn, resource=cts)

    # We use the method getPassage which takes a reference argument
    passage = text.getPassage(reference=ref)

    # Passage then has different methods and properties
    # Most of them (except next, prev and prevnext properties) are inherited from MyCapytain.resources.texts.tei.Text
    # For example
    print(passage.text(exclude=["note", "head"]))  # Will get the text without "note" and "head" TEI nodes
    print(passage.xml)  # The xml property can be used as an argument for XSLT for example