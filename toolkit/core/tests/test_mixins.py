from django.test import TestCase

from .models import Thing


class IsDeletedManagerTestCase(TestCase):
    def setUp(self):
        Thing.objects.create(name='thing1')
        Thing.objects.create(name='thing2')
        Thing.objects.create(name='thing3')
        Thing.objects.create(name='thing4', is_deleted=True)
        Thing.objects.create(name='thing5', is_deleted=True)

    def test_all(self):
        things = Thing.objects.all()
        self.assertEqual(things.count(), 3)
        self.assertEqual(things[0].name, 'thing1')
        self.assertEqual(things[1].name, 'thing2')
        self.assertEqual(things[2].name, 'thing3')

    def test_all_with_deleted(self):
        things = Thing.objects.all_with_deleted()
        self.assertEqual(things.count(), 5)
        self.assertEqual(things[0].name, 'thing1')
        self.assertEqual(things[1].name, 'thing2')
        self.assertEqual(things[2].name, 'thing3')
        self.assertEqual(things[3].name, 'thing4')
        self.assertEqual(things[4].name, 'thing5')

    def test_deleted(self):
        things = Thing.objects.deleted()
        self.assertEqual(things.count(), 2)
        self.assertEqual(things[0].name, 'thing4')
        self.assertEqual(things[1].name, 'thing5')


class IsDeletedMixinTestCase(TestCase):
    def test_delete(self):
        thing = Thing.objects.create(name='thing')
        self.assertFalse(thing.is_deleted)
        thing.delete()
        self.assertTrue(thing.is_deleted)


class IsDeletedQuerySetTestCase(TestCase):
    def setUp(self):
        Thing.objects.create(name='thing1')
        Thing.objects.create(name='thing2')
        Thing.objects.create(name='thing3')
        Thing.objects.create(name='thing4', is_deleted=True)
        Thing.objects.create(name='thing5', is_deleted=True)

    def test_delete(self):
        self.assertEqual(Thing.objects.all().count(), 3)
        self.assertEqual(Thing.objects.deleted().count(), 2)

        Thing.objects.all().delete()

        self.assertEqual(Thing.objects.all().count(), 0)
        self.assertEqual(Thing.objects.deleted().count(), 5)

