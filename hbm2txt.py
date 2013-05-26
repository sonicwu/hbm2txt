#!/usr/bin/python

import os
import sys
import xml.dom.minidom
from xml.dom.minidom import Node

class Table:
    def __init__(self, xml_file_path):
        self.is_ready = False
        try:
            doc = xml.dom.minidom.parse(xml_file_path)

            for class_node in doc.getElementsByTagName('class'):
                self.name = class_node.attributes['table'].value
            
            self.columns = []       
            # Single PK.
            id_nodes = class_node.getElementsByTagName('id')
            if id_nodes != None and len(id_nodes) > 0:
                column_name = self.get_column_name(id_nodes[0])
                column_type = self.get_column_type(id_nodes[0])
                self.columns.append(Column(column_name, Column.IS_PK, column_type))

            # Composite PK.
            composite_id_nodes = class_node.getElementsByTagName('composite-id')
            if composite_id_nodes != None and len(composite_id_nodes) > 0:
                key_properties = composite_id_nodes[0].getElementsByTagName('key-property')
                for key_property in key_properties:
                    column_name = self.get_column_name(key_property)
                    column_type = self.get_column_type(key_property)
                    self.columns.append(Column(column_name, Column.IS_PK, column_type))

            # Columns.
            for property_node in class_node.getElementsByTagName('property'):
                column_name = self.get_column_name(property_node)
                column_type = self.get_column_type(property_node)
                self.columns.append(Column(column_name, Column.IS_NOT_PK, column_type))
            
            self.is_ready = True
        except:
            print 'Unexpected error in parsing xml [{0}]:'.format(xml_file_path)
            print sys.exc_info()

    def get_column_name(self, target_node):
        column_name = 'UNKNOWN'
        if 'column' in target_node.attributes.keys():
            column_name = target_node.attributes['column']
        else:
            col_nodes = target_node.getElementsByTagName('column')
            if col_nodes != None and len(col_nodes) > 0:
                column_name = col_nodes[0].attributes['name']

        return column_name

    def get_column_type(self, target_node):
        column_type = 'UNKNOWN'
        if 'type' in target_node.attributes.keys():
            column_type = target_node.attributes['type']

        return column_type

    def __str__(self):
        # TODO output pattern.
        if self.is_ready == False:
            return ''

        return self.name.upper() + '\n'

class Column:
    IS_PK = True
    IS_NOT_PK = False

    def __init__(self, name, is_pk=IS_NOT_PK, type_str='', description=''):
        self.name = name
        self.is_pk = is_pk
        self.type_str = type_str
        self.description = description


def find_in_dir(target_dir, output_file):
    lines = []
    hbm_set = []
    for (dirpath, dirname, filenames) in os.walk(target_dir):
        for fname in filenames:
            if fname[-8:] == '.hbm.xml' and fname not in hbm_set:
                hbm_set.append(fname)
                hbm_file_path = dirpath + os.sep + fname

                table = Table(hbm_file_path)
                table_str = str(table)
                if table_str != '':
                    lines.append(table_str)

    f = open(output_file, 'w')
    f.writelines(lines)
    f.flush()
    f.close()   

if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] == '--help':
        print 'usage: /usr/bin/python <target directory> <output file>'
        sys.exit(0)

    target_dir = sys.argv[1]
    if os.path.exists(target_dir) == False:
        print "error: target directory '{0}' does not exist".format(target_dir)
        sys.exit(0)

    output_file = sys.argv[2]
    find_in_dir(target_dir, output_file)