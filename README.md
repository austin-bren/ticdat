# ticdat

`ticdat` is a lightweight, relational, data library. It is partly inspired by csv.DictReader
and csv.DictWriter.  When primary keys are specified, each table is a dictionary of dictionaries.
Otherwise, each table is an enumerable of dictionaries (as in DictReader/DictWriter). 

When foreign keys arespecified, they can be used to for a variety of purposes.
  * `find_foreign_key_failures` can be find the data rows in child tables that fail to cross reference with their parent table
  * used to create links between the "row dictionaries" of the parent table to the matching
"row dictionaries" of the child objects.
Although ticDat was specifically designed with Mixed Integer Programming data sets in mind, it can be used for
rapidly developing a wide variety of mathematical engines. It facilitates creating one definition of your
input data schema and one solve module, and reusing this same code, unchanged, on data from different
sources. This "separation of model from data" enables a user to move easily from toy, hard coded data to
larger, more realistic data sets. In addition, Opalytics Inc. (the developer of the ticDat library) can support
cloud deployments of solve engines that use the ticDat library.
The ticDat library is distributed under the BSD2 open source license.
