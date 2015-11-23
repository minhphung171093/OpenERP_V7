# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
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
    "name" : "Evaluation Management",
    "version" : "1.1",
    "author": "Serpent Consulting Services",
    "website" : "http://www.serpentcs.com",
    "category": "School Management",
    "complexity": "easy",
    "description": """A module to Student Evaluation.
    A Module support the following functionalities:
    
    1. In This Module we can define the terms which we want to consider In Evaluation.
    2. student and Faculty Both can Evaluate This.
    """,
    "depends" : [
        "hr",
        "school"
    ],
    "data" : ['student_evaluation_view.xml',
              "security/ir.model.access.csv",
     ],
    "demo": [
             "demo/student_evaluation_demo.xml"
             ],

    "installable": True,
    "auto_install": False,
    "application": True,
}