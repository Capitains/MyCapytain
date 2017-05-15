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
