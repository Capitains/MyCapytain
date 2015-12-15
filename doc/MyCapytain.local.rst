The MyCapytain local file implementation
========================================

Introduction
############

The module `MyCapytain.resources.local.text` requires the `guidelines of Capitains <https://capitains.github.io/pages/guidelines.html>`_ to be implemented in your files.

Basics and examples
###################

Getting all passages from a test
********************************

.. code-block:: python

    # We import the correct classes from the local module
    from MyCapytain.resources.texts.local import Text, Passage

    # We open a file
    with open("/tests/testing_data/texts/sample.xml") as f:
        # We initiate a Text object giving the IO instance to resource argument
        text = Text(resource=f)

    # Text objects have a citation property
    # len(Citation(...)) gives the depth of the citation scheme
    # in the case of this sample, this would be 3 (Book, Poem, Line)
    for ref in text.getValidReff(level=len(text.citation)):
        # We retrieve a Passage object for each reference that we find
        # We can pass the reference many way, including in the form of a list of strings
        psg = text.getPassage(ref.split("."))
        # We print the passage from which we retrieve <note> nodes
        print("\t".join([ref, psg.text(exclude=["note"])]))

