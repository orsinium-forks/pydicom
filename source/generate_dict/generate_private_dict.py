"""Update the _private_dict.py file using data from the GDCM private dict."""

import os
import xml.etree.ElementTree as ET

try:
    import urllib2
    # python2
except ImportError:
    import urllib.request as urllib2
    # python3

GDCM_PRIVATE_DICT = "https://raw.githubusercontent.com/malaterre/GDCM"
GDCM_PRIVATE_DICT = '%s/master/Source/DataDictionary' % (GDCM_PRIVATE_DICT)
GDCM_PRIVATE_DICT = "%s/privatedicts.xml" % (GDCM_PRIVATE_DICT)
PYDICOM_DICT_NAME = (
    'private_dictionaries: Dict[str, Dict[str, Tuple[str, str, str, str]]]'
)
PYDICOM_DICT_FILENAME = '_private_dict.py'
PYDICOM_DICT_DOCSTRING = """DICOM private dictionary auto-generated by generate_private_dict.py.

Data generated from GDCM project\'s private dictionary.

The outer dictionary key is the Private Creator name ("owner"), while the inner
dictionary key is a map of DICOM tag to (VR, VM, name, is_retired).
"""


def parse_private_docbook(doc_root):
    """Return a dict containing the private dictionary data"""
    entries = {}
    for entry in root:
        owner = entry.attrib['owner']
        if owner not in entries:
            entries[owner] = {}

        tag = entry.attrib['group'] + entry.attrib['element']

        # Convert unknown element names to 'Unknown'
        if entry.attrib['name'] == '?':
            entry.attrib['name'] = 'Unknown'
        # Escape backslash in element names
        if "\\" in entry.attrib['name']:
            entry.attrib['name'] = entry.attrib['name'].replace("\\", "\\\\")

        entries[owner][tag] = (entry.attrib['vr'],
                               entry.attrib['vm'],
                               entry.attrib['name'],
                               '')

    return entries


def write_dict(fp, dict_name, dict_entries):
    """Write the `dict_name` dict to file `fp`.

    Dict Format
    -----------
    private_dictionaries = {
        'CREATOR_1' : {
            '0029xx00': ('US', '1', 'Unknown', ''),
            '0029xx01': ('US', '1', 'Unknown', ''),
        },
        ...
        'CREATOR_N' : {
            '0029xx00': ('US', '1', 'Unknown', ''),
            '0029xx01': ('US', '1', 'Unknown', ''),
        },
    }

    Parameters
    ----------
    fp : file
        The file to write the dict to.
    dict_name : str
        The name of the dict variable.
    attributes : list of str
        List of attributes of the dict entries.
    """
    fp.write("\n{0} = {{\n".format(dict_name))
    for owner in sorted(dict_entries):
        fp.write("    '{0}': {{\n".format(owner))
        for entry in sorted(dict_entries[owner]):
            if "'" in dict_entries[owner][entry][2]:
                format_str = "        '{0}': ('{1}', '{2}', \"{3}\", '{4}'),  # noqa\n"
            else:
                format_str = "        '{0}': ('{1}', '{2}', '{3}', '{4}'),  # noqa\n"
            fp.write(format_str.format(entry,
                                       dict_entries[owner][entry][0],
                                       dict_entries[owner][entry][1],
                                       dict_entries[owner][entry][2],
                                       dict_entries[owner][entry][3]))
        fp.write("    },\n")
    fp.write("}\n")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.realpath(__file__))
    project_dir = os.path.abspath(os.path.join(current_dir,
                                               "..",
                                               "..",
                                               "pydicom"))
    output_file = os.path.join(project_dir, PYDICOM_DICT_FILENAME)
    response = urllib2.urlopen(GDCM_PRIVATE_DICT)
    tree = ET.parse(response)
    root = tree.getroot()

    entries = parse_private_docbook(root)

    py_file = open(output_file, "w")
    py_file.write('"""' + PYDICOM_DICT_DOCSTRING + '"""')
    py_file.write('\n')
    py_file.write("from typing import Dict, Tuple\n\n")
    write_dict(py_file, PYDICOM_DICT_NAME, entries)
    py_file.close()
