#!/usr/bin/python3
"""Unit tests for the HBNB console (console.py)."""
import os
import unittest
from io import StringIO
from unittest.mock import patch

from console import HBNBCommand
from models import storage


def run_cmd(command):
    """Run one console command and return its stripped output."""
    console = HBNBCommand()
    with patch('sys.stdout', new=StringIO()) as output:
        console.onecmd(console.precmd(command))
    return output.getvalue().strip()


class TestConsoleBasics(unittest.TestCase):
    """Console behavior that does not depend on the storage engine."""

    def test_emptyline(self):
        """An empty line prints nothing."""
        self.assertEqual(run_cmd(''), '')

    def test_quit(self):
        """quit exits the console."""
        with self.assertRaises(SystemExit):
            HBNBCommand().onecmd('quit')

    def test_eof(self):
        """EOF exits the console."""
        with patch('sys.stdout', new=StringIO()):
            with self.assertRaises(SystemExit):
                HBNBCommand().onecmd('EOF')

    def test_help_quit(self):
        """help quit prints its documentation."""
        self.assertIn('Exits the program', run_cmd('help quit'))

    def test_help_create(self):
        """help create prints its documentation."""
        self.assertIn('create', run_cmd('help create'))

    def test_create_missing_class(self):
        """create without a class name prints an error."""
        self.assertEqual(run_cmd('create'), '** class name missing **')

    def test_create_bad_class(self):
        """create with an unknown class prints an error."""
        self.assertEqual(run_cmd('create MyModel'),
                         "** class doesn't exist **")

    def test_show_missing_class(self):
        """show without a class name prints an error."""
        self.assertEqual(run_cmd('show'), '** class name missing **')

    def test_show_bad_class(self):
        """show with an unknown class prints an error."""
        self.assertEqual(run_cmd('show MyModel 123'),
                         "** class doesn't exist **")

    def test_show_missing_id(self):
        """show without an id prints an error."""
        self.assertEqual(run_cmd('show User'), '** instance id missing **')

    def test_destroy_missing_class(self):
        """destroy without a class name prints an error."""
        self.assertEqual(run_cmd('destroy'), '** class name missing **')

    def test_destroy_bad_class(self):
        """destroy with an unknown class prints an error."""
        self.assertEqual(run_cmd('destroy MyModel 123'),
                         "** class doesn't exist **")

    def test_destroy_missing_id(self):
        """destroy without an id prints an error."""
        self.assertEqual(run_cmd('destroy User'),
                         '** instance id missing **')

    def test_all_bad_class(self):
        """all with an unknown class prints an error."""
        self.assertEqual(run_cmd('all MyModel'), "** class doesn't exist **")

    def test_update_missing_class(self):
        """update without a class name prints an error."""
        self.assertEqual(run_cmd('update'), '** class name missing **')

    def test_update_bad_class(self):
        """update with an unknown class prints an error."""
        self.assertEqual(run_cmd('update MyModel 123'),
                         "** class doesn't exist **")

    def test_update_missing_id(self):
        """update without an id prints an error."""
        self.assertEqual(run_cmd('update User'), '** instance id missing **')


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') == 'db',
                 'FileStorage only')
class TestConsoleFileStorage(unittest.TestCase):
    """Console behavior that relies on FileStorage."""

    @classmethod
    def tearDownClass(cls):
        """Remove the JSON file written by the tests."""
        try:
            os.remove('file.json')
        except OSError:
            pass

    def _create(self, cls_name='User'):
        """Create an instance through the console and return its id."""
        return run_cmd('create {}'.format(cls_name))

    def test_create_stores_instance(self):
        """create prints an id and stores the new instance."""
        obj_id = self._create()
        self.assertIn('User.' + obj_id, storage.all())

    def test_create_every_class(self):
        """create works for every supported class."""
        for cls_name in HBNBCommand.classes:
            with self.subTest(cls_name=cls_name):
                obj_id = self._create(cls_name)
                self.assertIn(cls_name + '.' + obj_id, storage.all())

    def test_show_instance(self):
        """show prints the string form of an existing instance."""
        obj_id = self._create()
        output = run_cmd('show User {}'.format(obj_id))
        self.assertIn('[User]', output)
        self.assertIn(obj_id, output)

    def test_show_no_instance(self):
        """show with an unknown id prints an error."""
        self.assertEqual(run_cmd('show User not-an-id'),
                         '** no instance found **')

    def test_destroy_instance(self):
        """destroy removes an existing instance."""
        obj_id = self._create()
        run_cmd('destroy User {}'.format(obj_id))
        self.assertNotIn('User.' + obj_id, storage.all())

    def test_destroy_no_instance(self):
        """destroy with an unknown id prints an error."""
        self.assertEqual(run_cmd('destroy User not-an-id'),
                         '** no instance found **')

    def test_all(self):
        """all lists every instance."""
        obj_id = self._create()
        self.assertIn(obj_id, run_cmd('all'))

    def test_all_filters_by_class(self):
        """all <class> lists only instances of that class."""
        user_id = self._create('User')
        state_id = self._create('State')
        output = run_cmd('all User')
        self.assertIn(user_id, output)
        self.assertNotIn(state_id, output)

    def test_count(self):
        """count goes up by one after a create."""
        before = int(run_cmd('count State'))
        self._create('State')
        self.assertEqual(int(run_cmd('count State')), before + 1)

    def test_update_no_instance(self):
        """update with an unknown id prints an error."""
        self.assertEqual(run_cmd('update User not-an-id'),
                         '** no instance found **')

    def test_update_missing_attribute(self):
        """update without an attribute name prints an error."""
        obj_id = self._create()
        self.assertEqual(run_cmd('update User {}'.format(obj_id)),
                         '** attribute name missing **')

    def test_update_missing_value(self):
        """update without a value prints an error."""
        obj_id = self._create()
        self.assertEqual(
            run_cmd('update User {} first_name'.format(obj_id)),
            '** value missing **')

    def test_update_string(self):
        """update sets a quoted string attribute."""
        obj_id = self._create()
        run_cmd('update User {} first_name "Betty"'.format(obj_id))
        self.assertEqual(storage.all()['User.' + obj_id].first_name,
                         'Betty')

    def test_update_casts_int(self):
        """update casts known numeric attributes to int."""
        obj_id = self._create('Place')
        run_cmd('update Place {} max_guest 6'.format(obj_id))
        self.assertEqual(storage.all()['Place.' + obj_id].max_guest, 6)

    def test_dot_all(self):
        """<class>.all() lists instances of the class."""
        obj_id = self._create()
        self.assertIn(obj_id, run_cmd('User.all()'))

    def test_dot_count(self):
        """<class>.count() matches the count command."""
        self._create()
        self.assertEqual(run_cmd('User.count()'), run_cmd('count User'))

    def test_dot_show(self):
        """<class>.show(<id>) prints the instance."""
        obj_id = self._create()
        self.assertIn(obj_id, run_cmd('User.show("{}")'.format(obj_id)))

    def test_dot_destroy(self):
        """<class>.destroy(<id>) removes the instance."""
        obj_id = self._create()
        run_cmd('User.destroy("{}")'.format(obj_id))
        self.assertNotIn('User.' + obj_id, storage.all())

    def test_dot_update_dict(self):
        """<class>.update(<id>, <dict>) sets every attribute."""
        obj_id = self._create()
        run_cmd('User.update("' + obj_id + '", {"first_name": "John"})')
        self.assertEqual(storage.all()['User.' + obj_id].first_name,
                         'John')


@unittest.skipIf(os.getenv('HBNB_TYPE_STORAGE') != 'db',
                 'DBStorage only')
class TestConsoleDBStorage(unittest.TestCase):
    """Console behavior checked directly against MySQL."""

    def _count_states(self):
        """Return the number of rows in the states table.

        A new connection is opened each time so the count is not read
        from a stale transaction snapshot.
        """
        import MySQLdb
        db = MySQLdb.connect(host=os.getenv('HBNB_MYSQL_HOST'),
                             user=os.getenv('HBNB_MYSQL_USER'),
                             passwd=os.getenv('HBNB_MYSQL_PWD'),
                             db=os.getenv('HBNB_MYSQL_DB'))
        cursor = db.cursor()
        cursor.execute('SELECT COUNT(*) FROM states')
        count = cursor.fetchone()[0]
        cursor.close()
        db.close()
        return count

    def test_create_state_adds_record(self):
        """create State adds exactly one row to the states table."""
        before = self._count_states()
        run_cmd('create State name="California"')
        self.assertEqual(self._count_states() - before, 1)


if __name__ == '__main__':
    unittest.main()
