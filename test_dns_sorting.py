import unittest
from dns_sorting import Record
from dns_sorting import A_record
from io import StringIO
from contextlib import redirect_stdout

class RecordTest(unittest.TestCase):
    def test_init(self):
        record = Record(TTL=3600, type_="A", comment="This is a test record")
        self.assertEqual(record.TTL, 3600)
        self.assertEqual(record.class_, "IN")
        self.assertEqual(record.type_, "A")
        self.assertEqual(record.comment, "This is a test record")

    def test_show(self):
        record = Record(TTL=3600, type_="A", comment="This is a test record")
        expected_output = "class : IN\n" \
                            "TTL : 3600\n" \
                            "comment : This is a test record\n" \
                            "type : A\n"
                            
                        
        with StringIO() as buf, redirect_stdout(buf):
            record.show()
            output = buf.getvalue()
        self.assertEqual(output, expected_output)

class ARecordTest(unittest.TestCase):
    def test_init(self):
        a_record = A_record(server_name="example.com", TTL=3600, target="192.0.2.1", comment="This is a test A record")
        self.assertEqual(a_record.server_name, "example.com")
        self.assertEqual(a_record.TTL, 3600)
        self.assertEqual(a_record.class_, "IN")
        self.assertEqual(a_record.type_, "A")
        self.assertEqual(a_record.target, "192.0.2.1")
        self.assertEqual(a_record.comment, "This is a test A record")

    def test_show(self):
        a_record = A_record(server_name="example.com", TTL=3600, target="192.0.2.1", comment="This is a test A record")
        expected_output = "class : IN\n" \
                          "TTL : 3600\n" \
                          "type : A\n" \
                          "comment : This is a test A record\n" \
                          "server name : example.com\n" \
                          "target : 192.0.2.1\n\n"
        with StringIO() as buf, redirect_stdout(buf):
            a_record.show()
            output = buf.getvalue()
        self.assertEqual(output, expected_output)

    def test_eq(self):
        a_record1 = A_record(server_name="example.com", TTL=3600, target="192.0.2.1", comment="This is a test A record")
        a_record2 = A_record(server_name="example.com", TTL=3600, target="192.0.2.1", comment="This is a test A record")
        self.assertTrue(a_record1 == a_record2)

    def test_trim(self):
        a_record = A_record(server_name=" example.com ", TTL=3600, target=" 192.0.2.1 ", comment=" This is a test A record ")
        a_record.trim()
        self.assertEqual(a_record.server_name, "example.com")
        self.assertEqual(a_record.target, "192.0.2.1")
        self.assertEqual(a_record.comment, "This is a test A record")

if __name__ == '__main__':
    unittest.main()