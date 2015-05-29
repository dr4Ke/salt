# -*- coding: utf-8 -*-

# Import Salt Testing libs
from salttesting import TestCase, skipIf
from salttesting.helpers import ensure_in_syspath
from salttesting.mock import (
    MagicMock,
    patch,
    NO_MOCK,
    NO_MOCK_REASON
)

ensure_in_syspath('../../')

# Import Salt libs
from salt.exceptions import SaltException
from salt.modules import grains as grainsmod

grainsmod.__opts__ = {
  'conf_file': '/tmp/__salt_test_grains',
  'cachedir':  '/tmp/__salt_test_grains_cache_dir'
}

grainsmod.__salt__ = {}


@patch.dict(grainsmod.__salt__, {'saltutil.sync_grains': MagicMock()})
@skipIf(NO_MOCK, NO_MOCK_REASON)
class GrainsModuleTestCase(TestCase):

    def test_filter_by(self):
        grainsmod.__grains__ = {
          'os_family': 'MockedOS'
        }

        dict1 = {'A': 'B', 'C': {'D': {'E': 'F', 'G': 'H'}}}
        mdict = {'D': {'E': 'I'}, 'J': 'K'}

        # test None result with non existent grain and no default
        res = grainsmod.filter_by(dict1, grain='xxx')
        self.assertIs(res, None)

        # test None result with os_family grain and no matching result
        res = grainsmod.filter_by(dict1)
        self.assertIs(res, None)

        # test with non existent grain, and a given default key
        res = grainsmod.filter_by(dict1, grain='xxx', default='C')
        self.assertEqual(res, {'D': {'E': 'F', 'G': 'H'}})

        # add a merge dictionnary, F disapears
        res = grainsmod.filter_by(dict1, grain='xxx', merge=mdict, default='C')
        self.assertEqual(res, {'D': {'E': 'I', 'G': 'H'}, 'J': 'K'})
        # dict1 was altered, restablish
        dict1 = {'A': 'B', 'C': {'D': {'E': 'F', 'G': 'H'}}}

        # default is not present in dict1, check we only have merge in result
        res = grainsmod.filter_by(dict1, grain='xxx', merge=mdict, default='Z')
        self.assertEqual(res, mdict)

        # default is not present in dict1, and no merge, should get None
        res = grainsmod.filter_by(dict1, grain='xxx', default='Z')
        self.assertIs(res, None)

        #test giving a list as merge argument raise exception
        self.assertRaises(
            SaltException,
            grainsmod.filter_by,
            dict1,
            'xxx',
            ['foo'],
            'C'
        )

        #Now, re-test with an existing grain (os_family), but with no match.
        res = grainsmod.filter_by(dict1)
        self.assertIs(res, None)
        res = grainsmod.filter_by(dict1, default='C')
        self.assertEqual(res, {'D': {'E': 'F', 'G': 'H'}})
        res = grainsmod.filter_by(dict1, merge=mdict, default='C')
        self.assertEqual(res, {'D': {'E': 'I', 'G': 'H'}, 'J': 'K'})
        # dict1 was altered, restablish
        dict1 = {'A': 'B', 'C': {'D': {'E': 'F', 'G': 'H'}}}
        res = grainsmod.filter_by(dict1, merge=mdict, default='Z')
        self.assertEqual(res, mdict)
        res = grainsmod.filter_by(dict1, default='Z')
        self.assertIs(res, None)
        # this one is in fact a traceback in updatedict, merging a string with a dictionnary
        self.assertRaises(
            TypeError,
            grainsmod.filter_by,
            dict1,
            merge=mdict,
            default='A'
        )

        #Now, re-test with a matching grain.
        dict1 = {'A': 'B', 'MockedOS': {'D': {'E': 'F', 'G': 'H'}}}
        res = grainsmod.filter_by(dict1)
        self.assertEqual(res, {'D': {'E': 'F', 'G': 'H'}})
        res = grainsmod.filter_by(dict1, default='A')
        self.assertEqual(res, {'D': {'E': 'F', 'G': 'H'}})
        res = grainsmod.filter_by(dict1, merge=mdict, default='A')
        self.assertEqual(res, {'D': {'E': 'I', 'G': 'H'}, 'J': 'K'})
        # dict1 was altered, restablish
        dict1 = {'A': 'B', 'MockedOS': {'D': {'E': 'F', 'G': 'H'}}}
        res = grainsmod.filter_by(dict1, merge=mdict, default='Z')
        self.assertEqual(res, {'D': {'E': 'I', 'G': 'H'}, 'J': 'K'})
        # dict1 was altered, restablish
        dict1 = {'A': 'B', 'MockedOS': {'D': {'E': 'F', 'G': 'H'}}}
        res = grainsmod.filter_by(dict1, default='Z')
        self.assertEqual(res, {'D': {'E': 'F', 'G': 'H'}})

    def test_append_not_a_list(self):
        # Failing append to an existing string, without convert
        grainsmod.__grains__ = {'b': 'bval'}
        res = grainsmod.append('b', 'd')
        # check the result
        self.assertEqual(res, 'The key b is not a valid list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'b': 'bval'})

        # Failing append to an existing dict
        grainsmod.__grains__ = {'b': {'b1': 'bval1'}}
        res = grainsmod.append('b', 'd')
        # check the result
        self.assertEqual(res, 'The key b is not a valid list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'b': {'b1': 'bval1'}})

    def test_append_already_in_list(self):
        # Append an existing value
        grainsmod.__grains__ = {'a_list': ['a', 'b', 'c'], 'b': 'bval'}
        res = grainsmod.append('a_list', 'b')
        # check the result
        self.assertEqual(res, 'The val b was already in the list a_list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a_list': ['a', 'b', 'c'], 'b': 'bval'})

    def test_append_ok(self):
        # Append to an existing list
        grainsmod.__grains__ = {'a_list': ['a', 'b', 'c'], 'b': 'bval'}
        res = grainsmod.append('a_list', 'd')
        # check the result
        self.assertEqual(res, {'a_list': ['a', 'b', 'c', 'd']})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a_list': ['a', 'b', 'c', 'd'], 'b': 'bval'})

        # Append to an non existing list
        grainsmod.__grains__ = {'b': 'bval'}
        res = grainsmod.append('a_list', 'd')
        # check the result
        self.assertEqual(res, {'a_list': ['d']})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a_list': ['d'], 'b': 'bval'})

        # Append to an existing string, with convert
        grainsmod.__grains__ = {'b': 'bval'}
        res = grainsmod.append('b', 'd', convert=True)
        # check the result
        self.assertEqual(res, {'b': ['bval', 'd']})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'b': ['bval', 'd']})

        # Append to an existing dict, with convert
        grainsmod.__grains__ = {'b': {'b1': 'bval1'}}
        res = grainsmod.append('b', 'd', convert=True)
        # check the result
        self.assertEqual(res, {'b': [{'b1': 'bval1'}, 'd']})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'b': [{'b1': 'bval1'}, 'd']})

    def test_append_nested_not_a_list(self):
        # Failing append to an existing string, without convert
        grainsmod.__grains__ = {'a': {'b': 'bval'}}
        res = grainsmod.append('a:b', 'd')
        # check the result
        self.assertEqual(res, 'The key a:b is not a valid list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'b': 'bval'}})

        # Failing append to an existing dict
        grainsmod.__grains__ = {'a': {'b': {'b1': 'bval1'}}}
        res = grainsmod.append('a:b', 'd')
        # check the result
        self.assertEqual(res, 'The key a:b is not a valid list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'b': {'b1': 'bval1'}}})

    def test_append_nested_already_in_list(self):
        # Append an existing value
        grainsmod.__grains__ = {'a': {'a_list': ['a', 'b', 'c'], 'b': 'bval'}}
        res = grainsmod.append('a:a_list', 'b')
        # check the result
        self.assertEqual(res, 'The val b was already in the list a:a_list')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'a_list': ['a', 'b', 'c'], 'b': 'bval'}})

    def test_append_nested_ok(self):
        # Append to an existing list
        grainsmod.__grains__ = {'a': {'a_list': ['a', 'b', 'c'], 'b': 'bval'}}
        res = grainsmod.append('a:a_list', 'd')
        # check the result
        self.assertEqual(res, {'a': {'a_list': ['a', 'b', 'c', 'd'], 'b': 'bval'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'a_list': ['a', 'b', 'c', 'd'], 'b': 'bval'}})

        # Append to an non existing list
        grainsmod.__grains__ = {'a': {'b': 'bval'}}
        res = grainsmod.append('a:a_list', 'd')
        # check the result
        self.assertEqual(res, {'a': {'a_list': ['d'], 'b': 'bval'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'a_list': ['d'], 'b': 'bval'}})

        # Append to an existing string, with convert
        grainsmod.__grains__ = {'a': {'b': 'bval'}}
        res = grainsmod.append('a:b', 'd', convert=True)
        # check the result
        self.assertEqual(res, {'a': {'b': ['bval', 'd']}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'b': ['bval', 'd']}})

        # Append to an existing dict, with convert
        grainsmod.__grains__ = {'a': {'b': {'b1': 'bval1'}}}
        res = grainsmod.append('a:b', 'd', convert=True)
        # check the result
        self.assertEqual(res, {'a': {'b': [{'b1': 'bval1'}, 'd']}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': {'b': [{'b1': 'bval1'}, 'd']}})

    def test_append_to_an_element_of_a_list(self):
        # Append to an element in a list
        # It currently fails silently
        grainsmod.__grains__ = {'a': ['b', 'c']}
        res = grainsmod.append('a:b', 'd')
        # check the result
        self.assertEqual(res, {'a': ['b', 'c']})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': ['b', 'c']})

    def test_set_value_already_set(self):
        grainsmod.__grains__ = {'a': 12, 'c': 8}
        res = grainsmod.set('a', 12)
        # check the result
        self.assertEqual(res, 'The value \'12\' was already set for key \'a\'')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 12, 'c': 8})

        grainsmod.__grains__ = {'a': ['item', 12], 'c': 8}
        res = grainsmod.set('a', ['item', 12])
        # check the result
        self.assertEqual(res, 'The value \'[\'item\', 12]\' was already set for key \'a\'')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': ['item', 12], 'c': 8})

        grainsmod.__grains__ = {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8}
        res = grainsmod.set('b,nested', 'val', delimiter=',')
        # check the result
        self.assertEqual(res, 'The value \'val\' was already set for key \'b,nested\'')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8})

    def test_set_simple_value(self):
        grainsmod.__grains__ = {'a': ['b', 'c'], 'c': 8}
        res = grainsmod.set('b', 'bval')
        # check the result
        self.assertEqual(res, {'b': 'bval'})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': ['b', 'c'], 'b': 'bval', 'c': 8})

    def test_set_replace_value(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('a', 12)
        # check the result
        self.assertEqual(res, {'a': 12})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 12, 'c': 8})

    def test_set_None_ok(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('b', None)
        # check the result
        self.assertEqual(res, {'b': None})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': None, 'c': 8})

    def test_set_None_ok_destructive(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('b', None, destructive=True)
        # check the result
        self.assertEqual(res, {'b': None})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'c': 8})

    def test_set_None_replace_ok(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('a', None)
        # check the result
        self.assertEqual(res, {'a': None})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': None, 'c': 8})

    def test_set_None_force_destructive(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('a', None, force=True, destructive=True)
        # check the result
        self.assertEqual(res, {'a': None})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'c': 8})

    def test_set_fail_replacing_existing_complex_key(self):
        grainsmod.__grains__ = {'a': ['item', 12], 'c': 8}
        res = grainsmod.set('a', ['item', 14])
        # check the result
        self.assertEqual(res, 'The key \'a\' exists but is a dict or a list. Use \'force=True\' to overwrite.')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': ['item', 12], 'c': 8})

        grainsmod.__grains__ = {'a': 'aval', 'b': ['l1', {'l2': ['val1']}], 'c': 8}
        res = grainsmod.set('b,l2', 'val2', delimiter=',')
        # check the result
        self.assertEqual(res, 'The key \'b,l2\' exists but is a dict or a list. Use \'force=True\' to overwrite.')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': ['l1', {'l2': ['val1']}], 'c': 8})

    def test_set_replace_value_was_complex_force(self):
        grainsmod.__grains__ = {'a': ['item', 12], 'c': 8}
        res = grainsmod.set('a', 'aval', force=True)
        # check the result
        self.assertEqual(res, {'a': 'aval'})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'c': 8})

    def test_set_complex_value_fail(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('a', ['item', 12])
        # check the result
        self.assertEqual(res, 'The key \'a\' exists and the given value is a dict or a list. Use \'force=True\' to overwrite.')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'c': 8})

    def test_set_complex_value_force(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('a', ['item', 12], force=True)
        # check the result
        self.assertEqual(res, {'a': ['item', 12]})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': ['item', 12], 'c': 8})

    def test_set_nested_create(self):
        grainsmod.__grains__ = {'a': 'aval', 'c': 8}
        res = grainsmod.set('b,nested', 'val', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'nested': 'val'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8})

    def test_set_nested_update_dict(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8}
        res = grainsmod.set('b,nested', 'val2', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'nested': 'val2'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'nested': 'val2'}, 'c': 8})

    def test_set_nested_update_dict_remove_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8}
        res = grainsmod.set('b,nested', None, delimiter=',', destructive=True)
        # check the result
        self.assertEqual(res, {'b': {}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {}, 'c': 8})

    def test_set_nested_update_dict_new_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': {'nested': 'val'}, 'c': 8}
        res = grainsmod.set('b,b2', 'val2', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'b2': 'val2', 'nested': 'val'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'b2': 'val2', 'nested': 'val'}, 'c': 8})

    def test_set_nested_list_replace_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': ['l1', 'l2'], 'c': 8}
        res = grainsmod.set('b,l2', 'val2', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': ['l1', {'l2': 'val2'}]})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': ['l1', {'l2': 'val2'}], 'c': 8})

    def test_set_nested_list_update_dict_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': ['l1', {'l2': 'val1'}], 'c': 8}
        res = grainsmod.set('b,l2', 'val2', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': ['l1', {'l2': 'val2'}]})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': ['l1', {'l2': 'val2'}], 'c': 8})

    def test_set_nested_list_update_dict_key_overwrite(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': ['l1', {'l2': ['val1']}], 'c': 8}
        res = grainsmod.set('b,l2', 'val2', delimiter=',', force=True)
        # check the result
        self.assertEqual(res, {'b': ['l1', {'l2': 'val2'}]})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': ['l1', {'l2': 'val2'}], 'c': 8})

    def test_set_nested_list_append_dict_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': ['l1', {'l2': 'val2'}], 'c': 8}
        res = grainsmod.set('b,l3', 'val3', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': ['l1', {'l2': 'val2'}, {'l3': 'val3'}]})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': ['l1', {'l2': 'val2'}, {'l3': 'val3'}], 'c': 8})

    def test_set_nested_existing_value_is_the_key(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': 'l3', 'c': 8}
        res = grainsmod.set('b,l3', 'val3', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'l3': 'val3'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'l3': 'val3'}, 'c': 8})

    def test_set_nested_existing_value_fails(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': 'l1', 'c': 8}
        res = grainsmod.set('b,l3', 'val3', delimiter=',')
        # check the result
        self.assertEqual(res, 'The key \'b\' value is \'l1\', which is different from the provided key \'l3\'. Use \'force=True\' to overwrite.')
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': 'l1', 'c': 8})

    def test_set_nested_existing_value_overwrite(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': 'l1', 'c': 8}
        res = grainsmod.set('b,l3', 'val3', delimiter=',', force=True)
        # check the result
        self.assertEqual(res, {'b': {'l3': 'val3'}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'l3': 'val3'}, 'c': 8})

    def test_set_deeply_nested_update(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': {'l1': ['l21', 'l22', {'l23': 'l23val'}]}, 'c': 8}
        res = grainsmod.set('b,l1,l23', 'val', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'l1': ['l21', 'l22', {'l23': 'val'}]}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'l1': ['l21', 'l22', {'l23': 'val'}]}, 'c': 8})

    def test_set_deeply_nested_create(self):
        grainsmod.__grains__ = {'a': 'aval', 'b': {'l1': ['l21', 'l22', {'l23': 'l23val'}]}, 'c': 8}
        res = grainsmod.set('b,l1,l24,l241', 'val', delimiter=',')
        # check the result
        self.assertEqual(res, {'b': {'l1': ['l21', 'l22', {'l23': 'l23val'}, {'l24': {'l241': 'val'}}]}})
        # check the whole grains
        self.assertEqual(grainsmod.__grains__, {'a': 'aval', 'b': {'l1': ['l21', 'l22', {'l23': 'l23val'}, {'l24': {'l241': 'val'}}]}, 'c': 8})


if __name__ == '__main__':
    from integration import run_tests
    run_tests(GrainsModuleTestCase, needs_daemon=False)
