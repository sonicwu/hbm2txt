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
                column_comment = self.get_column_comment(property_node)
                self.columns.append(Column(column_name, Column.IS_NOT_PK, column_type, column_comment))
            
            self.is_ready = True
        except:
            print 'Unexpected error in parsing xml [{0}]:'.format(xml_file_path)
            print sys.exc_info()

    def get_column_name(self, target_node):
        column_name = 'UNKNOWN'
        if 'column' in target_node.attributes.keys():
            column_name = target_node.attributes['column'].value
        else:
            col_nodes = target_node.getElementsByTagName('column')
            if col_nodes != None and len(col_nodes) > 0:
                column_name = col_nodes[0].attributes['name'].value

        return column_name.upper()

    def get_column_type(self, target_node):
        column_type = 'UNKNOWN'
        column_attrs = target_node.attributes
        
        inner_col_attrs = None
        col_nodes = target_node.getElementsByTagName('column')
        if col_nodes != None and len(col_nodes) > 0:
            inner_col_attrs = col_nodes[0].attributes

        if 'type' in column_attrs.keys():
            type_str = column_attrs['type'].value.split('.')[-1].upper()
            
            if 'STRING' == type_str:
                column_type = 'VARCHAR2'
                if 'length' in column_attrs.keys():
                    column_type += '({0})'.format(column_attrs['length'].value)
                elif inner_col_attrs != None and 'length' in inner_col_attrs.keys():
                    column_type += '({0})'.format(inner_col_attrs['length'].value)

            elif type_str in ['SHORT', 'INTEGER', 'LONG', 'DOUBLE', 'BIGDECIMAL']:
                column_type = 'NUMBER'

                precision = '0'
                scale = '0'
                if 'precision' in column_attrs.keys():
                    precision = column_attrs['precision'].value
                    if 'scale' in column_attrs.keys():
                        scale = column_attrs['scale'].value
                elif inner_col_attrs != None and 'precision' in inner_col_attrs.keys():
                    precision = inner_col_attrs['precision'].value
                    if 'scale' in inner_col_attrs.keys():
                        scale = inner_col_attrs['scale'].value

                if precision != '0':
                    column_type += '({0}, {1})'.format(precision, scale)
            elif 'DATE' in type_str:
                column_type = 'DATE'

        return column_type

    def get_column_comment(self, target_node):
        comment_nodes = target_node.getElementsByTagName('comment')
        if comment_nodes != None and len(comment_nodes) > 0:
            for text_node in comment_nodes[0].childNodes:
                if text_node.nodeType == Node.TEXT_NODE:
                    return text_node.data

        return ''

    def __str__(self):
        if self.is_ready == False:
            return ''

        str_list = []
        str_list.append('<table border="1">')
        str_list.append('<tr><th colspan="4">{0}</th></tr>'.format(self.name.upper()))
        str_list.append('<tr><th>Name</th><th>Is PK</th><th>Type</th><th>Description</th></tr>')

        for col in self.columns:
            column_str = '<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'\
                .format(col.name, 'PK' if col.is_pk else '', col.type_str, col.description.encode('UTF-8'))

            str_list.append(column_str)

        str_list.append('</table>')
        str_list.append('<br/>')

        return '\n'.join(str_list)

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
                    lines.append('\n')

    f = open(output_file, 'w')
    f.write('<html>')
    f.write('<meta charset="UTF-8">')
    f.writelines(lines)
    f.write('</html>')
    f.flush()
    f.close()   

if __name__ == '__main__':
    if len(sys.argv) < 3 or sys.argv[1] == '--help':
        print 'usage: /usr/bin/python hbm2txt.py <target directory> <output file>'
        sys.exit(0)

    target_dir = sys.argv[1]
    if os.path.exists(target_dir) == False:
        print "error: target directory '{0}' does not exist".format(target_dir)
        sys.exit(0)

    output_file = sys.argv[2]
    find_in_dir(target_dir, output_file)