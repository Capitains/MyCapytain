### 2019-07-01 3.0.0 @ponteineptique

- Added DTS !
- New Generic / Prototype CitationSetObject
    - New .match(passageId) function
- New Generic / Prototype Citation Object
    - New .children Property
    - New .depth property (Not ported to CTS Citation object yet)
    - New meaning of .__len__() magic method
- New .root and is_root properties to link back to the citation set (for match implementations)
- Guidelines / CTS Citation Object
    - Implementation of the .match(passageId) method
- CitationSet.is_root -> CitationSet.is_root() # Keep in check with other practices
- BaseCitation.is_empty() now checks if the object has children
- BaseCitation.is_set() checks if objects have their properties set
- cts.Citation.isEmpty() old behaviour is now in .is_set() and has been reversed in meaning
    - Old system would check if the CTS Citation was not set, old code such as
    - if citation.isEmpty() should be moved to if citation.is_set()
- Guidelines / CTS Citation Object
- New Generic / Prototype Citation Object
    - RetroPorted .start and .end Properties (see below for breaking change)
    - New .is_range property

From MyCapytain.resources.prototypes.text to MyCapytain.resources.prototypes.cts.text :

- `CtsNode` now `PrototypeCtsNode`
- `CtsPassage` now `PrototypeCtsPassage`
- `CtsText` now `PrototypeCtsText`

Texts class:
- `self.__attr__` to `self._attr`

CTS Citation:
- `CTSCitation.isEmpty()` to `CTSCitation.is_empty()`

### 2019-04-10 2.0.10 @sonofmun

- Corrected JSON.Std export for metadata to include all objects for a predicate

### 2018-07-27 2.0.9 @sonofmun

 - Removed a random print statement that had been used for debugging empty references

### 2018-06-25 2.0.8 @sonofmun

- Corrected error on the empty references exception from 2.0.7
- Now raises an exception when there is no refsDecl found (MissingRefsDecl)
- The exception now raised by a citation request that is deeper than the citation scheme is a CitationDepthError

### 2018-06-22 2.0.7 @sonofmun

- Added exception for empty references

### 2017-11-16 2.0.6 @ponteineptique

- Added a way to specify the joining string for Plaintext export in TEIResource (Fixed #146)
- Fixed some examples in the doc which had a trailing slash for the test remote API

### 2017-10-30 2.0.5 @ponteineptique

Contributions by @brosner

- Added error handling for failed requests to CTS API
- Explicitly set fallback encoding for CTS API responses

### 2017-08-21 2.0.4 @ponteineptique

- Issue 137 : Fixed a bug where a passage extraction would not work even if the passage was found in the reff extraction. Origin of the issue was replacing too much .// in the xpath and thus breaking it

### 2017-06-16 2.0.3 @ponteineptique

- Issue 135 : Added support for empty namespace in string expansion for structured metadata"
- Upgraded travis script to work correctly on tag release

### 2017-06-15 2.0.2 @ponteineptique

- Issue 133 : Fixed a limitation of CapiTainS that did not allow to use any other attribute than @n in MyCapytain local capitains text parser and getReffs"
- Addeted a travis setting to upload directly to pypi on github release.

### 2017-05-15 2.0.1 @sonofmun

Corrected bug with the `CtsCapitainsLocalResolver.__getText__` that it would stop if a text was mentioned in the metadata but the file did not exist

### 2017-04-06 2.0.0rc1 @ponteineptique

- Simplified Metadata object and its relation to other items. Metadata is now more of an helper to mediate with triple regarding an object (text, passage or collection)
- Added support for CapiTainS Structured Metadata
- (via @sonofmun) Added support for Commentary

### 2017-04-21 @ponteineptique

Made a lot of renaming for clarity :

| Old name | New name |
|--------------|---------------|
| MyCapytain.common.constants.Exportable | MyCapytain.common.base.Exportable | 
| MyCapytain.common.constants.NS | MyCapytain.common.constants.XPATH_NAMESPACES |
| MyCapytain.common.constants.NAMESPACES | MyCapytain.common.constants.RDF_NAMESPACES |
| MyCapytain.resources.texts.api | MyCapytain.resources.texts.remote |
| MyCapytain.resources.texts.api.Passage | MyCapytain.resources.texts.remote.cts.CtsPassage |
| MyCapytain.resources.texts.api.Text | MyCapytain.resources.texts.remote.cts.CtsText |
| MyCapytain.resources.texts.locals | MyCapytain.resources.texts.local |
| MyCapytain.resources.texts.locals.tei | MyCapytain.resources.texts.local.capitains.cts |
| MyCapytain.resources.texts.locals.tei.Text | MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsText |
| MyCapytain.resources.texts.locals.tei.Passage | MyCapytain.resources.texts.local.capitains.cts.CapitainsCtsPassage |
| MyCapytain.resources.texts.locals.encodings | MyCapytain.resources.texts.base.tei |
| MyCapytain.resources.prototypes.cts.inventory.TextPrototype | MyCapytain.resources.prototypes.cts.inventory.CtsTextMetadata |
| MyCapytain.resources.prototypes.cts.inventory.EditionPrototype | MyCapytain.resources.prototypes.cts.inventory.CtsEditionMetadata |
| MyCapytain.resources.prototypes.cts.inventory.TranslationPrototype | MyCapytain.resources.prototypes.cts.inventory.CtsTranslationMetadata |
| MyCapytain.resources.prototypes.cts.inventory.WorkPrototype | MyCapytain.resources.prototypes.cts.inventory.CtsWorkMetadata |
| MyCapytain.resources.prototypes.cts.inventory.TextgroupPrototype | MyCapytain.resources.prototypes.cts.inventory.CtsTextgroupMetadata |
| MyCapytain.resources.prototypes.cts.inventory.TextInventoryMedata | MyCapytain.resources.prototypes.cts.inventory.CtsTextInventoryMetadata |
| MyCapytain.resources.prototypes.cts.inventory.TextInventoryCollection | MyCapytain.resources.prototypes.cts.inventory.CtsTextInventoryCollection |
| MyCapytain.resources.collections.cts.Text | MyCapytain.resources.collections.cts.inventory.XmlCtsTextMetadata |
| MyCapytain.resources.collections.cts.Edition | MyCapytain.resources.collections.cts.inventory.XmlCtsEditionMetadata |
| MyCapytain.resources.collections.cts.Translation | MyCapytain.resources.collections.cts.inventory.XmlCtsTranslationMetadata |
| MyCapytain.resources.collections.cts.Work | MyCapytain.resources.collections.cts.inventory.XmlCtsWorkMetadata |
| MyCapytain.resources.collections.cts.Textgroup | MyCapytain.resources.collections.cts.inventory.XmlCtsTextgroupMetadata |
| MyCapytain.resources.collections.cts.TextInventory | MyCapytain.resources.collections.cts.inventory.XmlCtsTextInventoryMetadata |
| MyCapytain.retrievers.cts5.CTS | MyCapytain.retrievers.cts5.HttpCtsRetriever |

Automatically moved all names matching "CTS\w+" to "Cts\w+"
