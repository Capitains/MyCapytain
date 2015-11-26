Known issues and recommendations
################################

XPath Issues
************

`lxml`, which is the package powering xml support here, does not accept XPath notations such as `/div/(a or b)[@n]`. Solution for this edge case is `/div/*[self::a or self::b][@n]`