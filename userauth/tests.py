from django.contrib.auth.models import User, Permission, Group
from django.contrib.auth import SESSION_KEY
from django.test import TestCase, Client
from unittest.mock import Mock, MagicMock, patch
from django.urls import reverse
from zoo.models import *
from django.contrib import auth
from django.db import IntegrityError

def create_user():
    return {'username': 'testuser',
            'password': 'secret',
            'email': 'test@test.com'}


class LogInTest(TestCase):
    def setUp(self):
        self.credentials = create_user()
        User.objects.create_user(**self.credentials)
    def test_login(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)
    def test_logout(self):
        # send logout data
        response = self.client.post('/logout/')
        # should be logged out now
        self.assertEquals(response.status_code, 302)


class ChangePasswordTest(TestCase):
    def setUp(self):
        self.credentials = create_user()
        self.user = User.objects.create_user(**self.credentials)
    def test_view(self):
        # access to page to change password
        response = self.client.get('/password_reset')
        self.failUnlessEqual(response.status_code, 200)
    def test_valid_email(self):
        # enter valid email of registered user
        c = {'email': self.user.email}
        response = self.client.post('/password_reset', c)
        self.failUnlessEqual(response.status_code, 302)
    def test_invalid_email(self):
        # enter email of unregistered user or invalid email of registered user
        c = {'email': 'dummy@address.co'}
        response = self.client.post('/password_reset', c)
        self.assertContains(response, "An invalid email has been entered.")


class CaregiversGroupPermissionsTests(TestCase):

    def setUp(self):
        # create group Caregivers, ie permission to change animal
        group_name = "My Test Group"
        self.group = Group(name=group_name)
        self.group.save()
        change_animal = Permission.objects.get(codename='change_animal', content_type__app_label='zoo', content_type__model='animal')
        self.group.permissions.add(change_animal)
        
        # instantiate user
        self.credentials = create_user()
        self.user = User.objects.create_user(**self.credentials)

        # instantiate animal
        self.species = Species.objects.create(diet_type='CARNIVORE', name='bar')
        self.species.save()
        self.animal = Animal.objects.create(name='foo', species=self.species, gender='MALE', image='foo.txt')
        self.animal.save()


    def test_user_cannot_access(self):
        """user NOT in group should NOT have access
        """
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.change_animal'), False)
        self.assertNotContains(response, "new enclosure")
        
        
    def test_user_can_access(self):
        """user in group should have access
        """
        self.user.groups.add(self.group)
        self.user.save()
        
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        ### print('BEFORE SELF.CLIENT', response.wsgi_request.user)
        ### self.client = Client()
        # fixtures = ['/userauth/fixtures/dump.json',]
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.change_animal'), True)
        ### print('AFTER SELF.CLIENT', response.wsgi_request.user)
        self.assertContains(response, "new enclosure")


class StaffVetGroupPermissionsTests(TestCase):

    def setUp(self):
        # create group Vet, ie permission to add medical report
        group_name = "My Test Group"
        self.group = Group(name=group_name)
        self.group.save()
        add_medicalreport = Permission.objects.get(codename='add_medicalreport', content_type__app_label='zoo', content_type__model='medicalreport')
        self.group.permissions.add(add_medicalreport)

        # instantiate user
        self.credentials = create_user()
        self.user = User.objects.create_user(**self.credentials)
        # instantiate animal
        self.species = Species.objects.create(diet_type='CARNIVORE', name='bar')
        self.species.save()
        self.animal = Animal.objects.create(name='foo', species=self.species, gender='MALE', image='foo.txt')
        self.animal.save()

    def test_user_cannot_access(self): # user has neither Staff status nor is member of group
        """user NOT in group should NOT have access to view or add medical reports
        """
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), False)
        self.assertNotContains(response, "Add a medical report:")
        self.assertNotContains(response, "Medical Reports")
        
        
    def test_user_staff_no_perms_cannot_access(self): # user has Staff status but is NOT member of group
        """user NOT in group should have access to view but NOT to add medical reports
        """
        self.user.is_staff = True
        self.user.save()
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), False)
        self.assertNotContains(response, "Add a medical report:")
        self.assertContains(response, "Medical Reports")

    def test_user_perms_not_staff_cannot_access(self): # user is member of group and has NO Staff status
        """user NOT in group should NOT have access to view or add medical reports
        """
        self.user.groups.add(self.group)
        response = self.client.post('/login/', self.credentials, follow=True)
        self.assertTrue(response.context['user'].is_active)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), True)
        self.assertNotContains(response, "Add a medical report:")
        self.assertNotContains(response, "Medical Reports")

    def test_user_can_access(self): # user is member of group and has Staff status
        """user in group should have access to view and to add medical reports
        """
        self.user.groups.add(self.group)
        self.user.is_staff = True
        self.user.save()        
        response = self.client.post('/login/', self.credentials, follow=True)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), True)
        self.assertEqual(self.user.has_perm('zoo.change_animal'), False)
        self.assertContains(response, "Medical Reports")
        self.assertContains(response, "Add a medical report:")

class SuperuserPermissionsTests(TestCase): # access to move animals, view and add medical reports, and more!

    def setUp(self):
        self.credentials = create_user()
        self.species = Species.objects.create(diet_type='CARNIVORE', name='bar')
        self.species.save()
        self.animal = Animal.objects.create(name='foo', species=self.species, gender='MALE', image='foo.txt')
        self.animal.save()
    

    def test_user_cannot_access(self):
        """user NOT in group should NOT have access
        """
        self.user = User.objects.create_user(**self.credentials) # regular user
        self.user.save()        
        response = self.client.post('/login/', self.credentials, follow=True)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('auth.add_group'), False)
        self.assertEqual(self.user.has_perm('auth.change_user'), False)
        self.assertEqual(self.user.has_perm('zoo.add_animal'), False)
        self.assertEqual(self.user.has_perm('zoo.add_enclosure'), False)
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), False)
        self.assertNotContains(response, "Medical Reports")
        self.assertNotContains(response, "Add a medical report:")


    def test_user_can_access(self):
        """user in group should have access
        """
        self.user = User.objects.create_superuser(**self.credentials) # superuse
        self.user.save()
        response = self.client.post('/login/', self.credentials, follow=True)
        response = self.client.get(reverse('animal', kwargs={'id': self.animal.id}))
        self.assertEqual(self.user.has_perm('auth.add_group'), True)
        self.assertEqual(self.user.has_perm('auth.change_user'), True)
        self.assertEqual(self.user.has_perm('zoo.add_animal'), True)
        self.assertEqual(self.user.has_perm('zoo.add_enclosure'), True)
        self.assertEqual(self.user.has_perm('zoo.add_medicalreport'), True)
        self.assertContains(response, "Medical Reports")
        self.assertContains(response, "Add a medical report:")


class TestAddViewFav(TestCase): # add animal to Favourite and view Favourite page
    def setUp(self):
        self.credentials = create_user()
        self.user = User.objects.create_user(**self.credentials)
        self.user.save()
        self.species = Species.objects.create(diet_type='CARNIVORE', name='bar')
        self.species.save()
        self.animal = Animal.objects.create(name='foo', species=self.species, gender='MALE', image='foo.txt')
        self.animal.save()
    

    def test_pageFav_user_cannot_access(self):
        """un-logged in user should NOT have access to Favourites page
        """
        response = self.client.get('/favourite')
        self.failUnlessEqual(response.status_code, 302)
    

    def test_pageFav_user_can_access(self):
        """logged in user should have access to Favourites page
        """
        self.client.post('/login/', self.credentials, follow=True)
        response = self.client.get('/favourite')
        self.failUnlessEqual(response.status_code, 200)


    def test_add_new_animal(self):
        """add new animal to Favourites page
        """
        self.client.post('/login/', self.credentials, follow=True)
        c = {'reg_user': self.user.id, 'fav_animal': id}
        response = self.client.post(reverse('add_fav', kwargs={'id': self.animal.id}), c)
        self.failUnlessEqual(response.status_code, 302)

    
    def test_add_favourited_animal(self):
        """add animal already added to Favourites page
        """
        self.client.post('/login/', self.credentials, follow=True)
        self.fav_animal = FavAnimal.objects.create(reg_user=self.user, fav_animal=self.animal)
        self.fav_animal.save()
        c = {'reg_user': self.user.id, 'fav_animal': id}
        response = self.client.post(reverse('add_fav', kwargs={'id': self.animal.id}), c)

        with self.assertRaises(IntegrityError) as context:
            FavAnimal.objects.create(reg_user=self.user, fav_animal=self.animal)
        self.assertTrue('UNIQUE constraint failed' in str(context.exception))
