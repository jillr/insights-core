"""
Lssap - command ``/usr/sap/hostctrl/exe/lssap``
===============================================

This module provides processing for the output of the ``lssap`` command on
SAP systems. The spec handled by this command inlude::

    "lssap"                     : CommandSpec("/usr/sap/hostctrl/exe/lssap")

Class ``Lssap`` parses the output of the ``lssap`` command.  Sample
output of this command looks like::

 - lssap version 1.0 -
 ==========================================
   SID   Nr   Instance    SAPLOCALHOST                        Version                 DIR_EXECUTABLE
   HA2|  16|       D16|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D16/exe
   HA2|  22|       D22|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D22/exe
   HA2|  50|       D50|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D50/exe
   HA2|  51|       D51|         lu0417|749, patch 10, changelist 1698137|          /usr/sap/HA2/D51/exe

Examples:
    >>> lssap.instances
    ['D16', 'D22', 'D50', 'D51']
    >>> lssap.version('D51')
    '749, patch 10, changelist 1698137'
    >>> lssap.is_hana()
    False
    >>> lssap.data[3]['Instance']
    'D51'
"""
from .. import parser, CommandParser
from insights.parsers import ParseException, parse_delimited_table
from insights.specs import Specs


@parser(Specs.lssap)
class Lssap(CommandParser):
    """Class to parse ``lssap`` command output.

    Raises:
        ParseException: Raised if any error occurs parsing the content.

    Attributes:
        data (list): List of dicts, where the keys in each dict are the column
            headers and each item in the list represents a SID.
        sid (list): List of the SIDs from the SID column.
        instances (list): List of instances running on the system.
        instance_types (list): List of instance types running on the system.
    """
    def parse_content(self, content):
        self.data = []
        # remove lssap version and bar text from content
        clean_content = content[2:-1]
        if len(clean_content) > 0 and "SID" in clean_content[0]:
            self.data = parse_delimited_table(clean_content, delim='|', header_delim=None)
        else:
            raise ParseException("Lssap: Unable to parse {0} line(s) of content: ({1})".format(len(content), content))

        self.sid = sorted(set(row["SID"] for row in self.data if "SID" in row))
        self.instances = [row["Instance"] for row in self.data if "Instance" in row]
        self.instance_types = sorted(set(inst.rstrip('1234567890') for inst in self.instances))

    def version(self, instance):
        """str: returns the Version column corresponding to the ``instance`` in
        Instance or ``None`` if ``instance`` is not found.
        """
        for row in self.data:
            if instance == row['Instance']:
                return row["Version"]

    def is_netweaver(self):
        """bool: SAP Netweaver is running on the system."""
        return 'D' in self.instance_types

    def is_hana(self):
        """bool: SAP HANA is running on the system."""
        return 'HDB' in self.instance_types

    def is_ascs(self):
        """bool: SAP System Central Services is running on the system."""
        return 'ASCS' in self.instance_types
