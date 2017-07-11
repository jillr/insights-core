import unittest
import os
import tempfile
import uuid
import insights.client.utilities as util
import re

machine_id = str(uuid.uuid4())
remove_file_content = """
[remove]
foo = bar
potato = pancake
""".strip()


class TestUtilites(unittest.TestCase):

    def test_display_name(self):
        self.assertEquals(util.determine_hostname(display_name='foo'), 'foo')

    def test_determine_hostname(self):
        import socket
        hostname = socket.gethostname()
        fqdn = socket.getfqdn()
        self.assertEquals(hostname or fqdn, util.determine_hostname())
        self.assertNotEquals('foo', util.determine_hostname())

    def test_get_time(self):
        time_regex = re.match('\d{4}-\d{2}-\d{2}\D\d{2}:\d{2}:\d{2}\.\d+',
                              util.get_time())
        assert time_regex.group(0) is not None

    def test_write_to_disk(self):
        content = 'boop'
        filename = '/tmp/testing'
        util.write_to_disk(filename, content=content)
        assert os.path.isfile(filename)
        with open(filename, 'r') as f:
            result = f.read()
        assert result == 'boop'
        self.assertEquals(util.write_to_disk(filename, delete=True), None)

    def test_generate_machine_id(self):
        machine_id_regex = re.match('\w{8}-\w{4}-\w{4}-\w{4}-\w{12}',
                                    util.generate_machine_id(destination_file='/tmp/testmachineid'))
        assert machine_id_regex.group(0) is not None
        with open('/tmp/testmachineid', 'r') as _file:
            machine_id = _file.read()
        self.assertEquals(machine_id, util.generate_machine_id(destination_file='/tmp/testmachineid'))
        os.remove('/tmp/testmachineid')

    def test_expand_paths(self):
        assert util._expand_paths('/tmp') == ['/tmp']

    def test_magic_plan_b(self):
        tf = tempfile.NamedTemporaryFile()
        with open(tf.name, 'w') as f:
            f.write('testing stuff')
        assert util.magic_plan_b(tf.name) == 'text/plain; charset=us-ascii'

    def test_run_command_get_output(self):
        cmd = 'echo hello'
        assert util.run_command_get_output(cmd) == {'status': 0, 'output': u'hello\n'}

    def test_validate_remove_file(self):
        tf = '/tmp/remove.cfg'
        with open(tf, 'wb') as f:
            f.write(remove_file_content)
        self.assertEqual(util.validate_remove_file(remove_file='/tmp/boop'), False)
        os.chmod(tf, 0o644)
        self.assertEqual(util.validate_remove_file(remove_file=tf), False)
        os.chmod(tf, 0o600)
        self.assertNotEqual(util.validate_remove_file(remove_file=tf), False)