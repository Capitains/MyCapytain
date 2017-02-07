from MyCapytain.resources.collections.dts import DTSCollection
from MyCapytain.common.constants import Mimetypes

x = {
  "@id": "urn:cts:latinLit:phi0959.phi005",
  "type": "http://homermultitext.org/rdfvocab/work",
  "license": "https://creativecommons.org/licenses/by-sa/3.0/",
  "size": 1,
  "label": [
    {
      "lang": "lat",
      "value": "Remedia amoris"
    }
  ],
  "@context": {
      "dc": "http://purl.org/dc/elements/1.1/"
  },
  "capabilities": {
    "isOrdered": True,
    "hasRoles": True
  },
  "metadata": {
      "http://purl.org/dc/elements/1.1/labels": [
      {
        "@lang": "lat",
        "@value": "Remedia amoris"
      }
    ]
  },
  "members": {
    "contents": [
      {
        "@id": "urn:cts:latinLit:phi0959.phi005.perseus-lat2",
        "type": "http://homermultitext.org/rdfvocab/edition",
        "model": "http://dts.org/model"
      }
    ],
    "next_cursor": "21-30",
    "prev_cursor": "1-20"
  },
  "version": "a555194",
  "parents": [
    {
      "@id": "urn:cts:latinLit:phi0959.phi005",
      "type": "http://homermultitext.org/rdfvocab/work",
      "labels": [
        {
          "lang": "lat",
          "value": "Remedia amoris"
        }
      ]
    }
  ],
  "next": {
    "@id": "urn:cts:latinLit:phi0959.phi005",
    "type": "http://homermultitext.org/rdfvocab/work",
    "labels": [
      {
        "lang": "lat",
        "value": "Remedia amoris"
      }
    ]
  },
  "prev": {
    "@id": "urn:cts:latinLit:phi0959.phi005",
    "type": "http://homermultitext.org/rdfvocab/work",
    "labels": [
      {
        "lang": "lat",
        "value": "Remedia amoris"
      }
    ]
  }
}

Collection = DTSCollection.parse(x)
from pprint import pprint
pprint(Collection.export(Mimetypes.JSON.DTS.Std))