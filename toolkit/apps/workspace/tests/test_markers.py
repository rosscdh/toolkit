# -*- coding: utf-8 -*-
#from django.test import TestCase  # With DB Acess
import unittest  # No DB Acess

from ..markers import BaseSignalMarkers, Marker
from ..markers import MissingMarkersException

from toolkit.utils import get_namedtuple_choices

SINGLE_MARKER = Marker(1, name='monkey_nuts')

MULTIPLE_MARKERS = [
    Marker(2, name='monkey_bum', description='something here'),
    Marker(3, name='monkey_hands', description='something there'),
    Marker(4, name='monkey_feet', description='something everywhere', long_description='But this one goes all the time'),
]


class BaseSignalMarkersTest(unittest.TestCase):
    def setUp(self):
        self.subject = BaseSignalMarkers

    def _get_test_subject(self, markers=None):
        """
        Return a class that can be tested against
        saves repeating this code all over the show
        """
        class CustomTestMarkers(self.subject):
            signal_map = markers  # Heres whats important for this test

        return CustomTestMarkers()

    def test_incorrect_init(self):
        """
        Test that the BaseSignalMarkers class requires the signal_map
        to have a value
        """
        with self.assertRaises(MissingMarkersException) as context:
            self.subject()

    def test_correct_init(self):
        """
        Provide a test MarkerBase
        """
        subject = self._get_test_subject(markers=[SINGLE_MARKER])

        self.assertEqual(len(subject.signal_map), 1)
        self.assertEqual(type(subject.marker('monkey_nuts')), Marker)
        self.assertEqual(subject.marker('monkey_nuts'), SINGLE_MARKER)

        self.assertEqual(subject.previous, None)
        self.assertEqual(subject.current, SINGLE_MARKER)
        self.assertEqual(subject.next, None)

    def test_correct_init_multiple_markers(self):
        """
        Provide a test MarkerBase
        """
        subject = self._get_test_subject(markers=MULTIPLE_MARKERS)

        self.assertEqual(len(subject.signal_map), len(MULTIPLE_MARKERS))
        self.assertEqual(type(subject.marker('monkey_bum')), Marker)
        self.assertEqual(subject.marker('monkey_bum'), MULTIPLE_MARKERS[0])

        self.assertEqual(subject.previous, None)
        self.assertEqual(subject.current, MULTIPLE_MARKERS[0])
        self.assertEqual(subject.next, MULTIPLE_MARKERS[1])

    def test_get_marker_by_name(self):
        subject = self._get_test_subject(markers=MULTIPLE_MARKERS)
        self.assertEqual(subject.marker('monkey_bum'), MULTIPLE_MARKERS[0])
        self.assertEqual(subject.marker_by_name('monkey_feet'), MULTIPLE_MARKERS[2])

    def test_get_marker_by_val(self):
        subject = self._get_test_subject(markers=MULTIPLE_MARKERS)
        self.assertEqual(subject.marker(2), MULTIPLE_MARKERS[0])
        self.assertEqual(subject.marker_by_val(4), MULTIPLE_MARKERS[2])

    def test_named_tuple(self):
        subject = self._get_test_subject(markers=MULTIPLE_MARKERS)
        # set up the test comparison
        # take our basic list and turn it into a named tuple
        EXPECTED_MONKEYS = get_namedtuple_choices('MONKEYS', tuple([(signal_marker.val, signal_marker.name, signal_marker.description) for signal_marker in MULTIPLE_MARKERS]))
        self.assertEqual(subject.named_tuple(name='MONKEYS'), EXPECTED_MONKEYS)


class InvalidMarkerTest(unittest.TestCase):
    """
    Invalid markers
    """
    def setUp(self):
        super(InvalidMarkerTest, self).setUp()
        self.subject = Marker

    def test_invalid_init(self):
        with self.assertRaises(TypeError) as context:
            subject = self.subject()

        self.assertEqual(context.exception.message, '__init__() takes exactly 2 arguments (1 given)')


class ValidMarkerTest(unittest.TestCase):
    """
    Invalid markers
    """
    def setUp(self):
        super(ValidMarkerTest, self).setUp()
        self.subject = Marker

    def test_valid_init(self):
        subject = self.subject(1, name='test_marker')
        self.assertEqual(subject.val, 1)
        self.assertEqual(hasattr(subject, 'name'), True)
        self.assertEqual(subject.name, 'test_marker')
        self.assertEqual(hasattr(subject, 'description'), True)
        self.assertEqual(hasattr(subject, 'long_description'), True)
        self.assertEqual(type(subject), Marker)

    def test_invalid_action(self):
        """
        Each marker must define a get_action_url and or a .action property
        the .action property defines display business logix
        while the get_action_url allows us to access the action url regardless
        of business logic
        """
        subject = self.subject(1, name='test_marker')
        with self.assertRaises(NotImplementedError) as context:
            subject.action
        with self.assertRaises(NotImplementedError) as context:
            subject.get_action_url()
