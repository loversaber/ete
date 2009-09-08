# #START_LICENSE###########################################################
#
# Copyright (C) 2009 by Jaime Huerta Cepas. All rights reserved.  
# email: jhcepas@gmail.com
#
# This file is part of the Environment for Tree Exploration program (ETE). 
# http://ete.cgenomics.org
#  
# ETE is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#  
# ETE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#  
# You should have received a copy of the GNU General Public License
# along with ETE.  If not, see <http://www.gnu.org/licenses/>.
#
# #END_LICENSE#############################################################
from coretype import *

try:
    from phylo import *
except ImportError, e: 
    print "Phylogeny module could not be loaded"
    print e

try:
    from clustering import *
except ImportError, e: 
    print "Clustering module could not be loaded."
    print e

try:
    from phylomedb import *
except ImportError, e: 
    print "PhylomeDB API could not be loaded."
    print e

try:
    from treeview import *
except ImportError, e: 
    print "tree visualization  module could not be loaded."
    print e 

