# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Stock Move Ext
#    Copyright (C) 2013 Enterprise Objects Consulting
#                       http://www.eoconsulting.com.ar
#    Authors: Mariano Ruiz <mrsarm@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    "name" : "Stock Move Ext",
    "description":"""
Improve the Stock Picking and Stock Move features. 

Enhancements:

 * Allow users to delete stock move when state != draft.
 * Fix the update of min/max date and expected date in
   calendar view of Stock Picking
 * Better message exceptions
 * Take default "Delivery Method" from default "Picking Policy" in
   Sale Order (configurable by "Setup Picking Policy" wizard)
 * Better translation to Spanish (es) and Spanish (AR)
 * Currently in development ...
""",
    "version" : "0.1",
    "author" : "Enterprise Objects Consulting",
    "website" : "http://www.eoconsulting.com.ar",
    "category" : "Warehouse Management",
    "depends" : ["stock", "delivery"],
    "active": False,
    "installable": True
}
