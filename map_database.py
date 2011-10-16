#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from sqlalchemy import MetaData
from sqlalchemy.orm import class_mapper
from tools.sqlalchemy_schemadisplay3 import create_schema_graph, create_uml_graph
import model
import settings

"""Generate graphics with a diagram describing the database structure

See http://www.sqlalchemy.org/trac/wiki/UsageRecipes/SchemaDisplay

TODO sqlalchemy_schemadisplay3 is now bound to PostgreSQL and does not work for SQLite (yet)
Howeever, since we normally work with PostgreSQL it is not worth the effort for this little project

"""

#------------------------------------------------------------------------------------------------
# Diagram based on metadata
#------------------------------------------------------------------------------------------------

# create the pydot graph object by autoloading all tables via a bound metadata object
graph = create_schema_graph(metadata=MetaData('sqlite://' + settings.DATABASE_NAME),
   show_datatypes=False,            # The image would get nasty big if we'd show the datatypes
   show_indexes=False,              # ditto for indexes
   rankdir='LR',                    # From left to right (instead of top to bottom)
   concentrate=False                # Don't try to join the relation lines together
)
graph.write_png('dbschema.png')     # write out the file


#------------------------------------------------------------------------------------------------
# UML diagram based on model definition
#------------------------------------------------------------------------------------------------
# lets find all the mappers in our model
mappers = []
for attr in dir(model):
    if attr[0] == '_': continue
    try:
        cls = getattr(model, attr)
        mappers.append(class_mapper(cls))
    except:
        pass

# pass them to the function and set some formatting options
graph = create_uml_graph(mappers,
    show_operations=False,          # not necessary in this case
    show_multiplicity_one=False     # some people like to see the ones, some don't
)
graph.write_png('schema.png')       # write out the file