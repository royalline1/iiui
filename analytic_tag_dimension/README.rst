
======================
Analytic Tag Dimension
======================

This module allows to group Analytic Tags on Dimensions.

Dimensions are created as custom field, then you can group by Dimensions on:

* Account/Adviser/Journal Items
* Account/Reports/Business Intelligence/Analytic Entries

When you set Tags on Analytic Entries, each custom field for dimensions is updated with its Tag.

One Tag is only allowed on one Dimension, and you can not set more than one Tag from same Dimensions on Analytic Entry.


Configuration
=============

To configure this module, you need to:

* go to /Accounting/Configuration/Analytic Accounting/Analytic Accounts Dimensions to create new Analytic Dimensions.
* You can create new Analytic Tags on this form, or go to /Accounting/Configuration/Analytic Accounting/Analytic Accounts Tags and set Dimension for each Tag.


Known issues / Roadmap
======================

* Analytic Entries with Tags created before installing this module are not updated with theirs Dimensions.
* Set color on Analytic Dimensions, and get it on Analytic Tags.
* Change implementation to create stored computed fields, instead of rewrite create and write functions.
* On the function that create fields, get all the models that inherit from AbstractModel
* Set dimension on invoice report
* Improve fields_view_get to create filters on search view




