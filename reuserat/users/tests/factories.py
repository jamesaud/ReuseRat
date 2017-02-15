import factory


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: 'user-{0}'.format(n))
    email = factory.Sequence(lambda n: 'user-{0}@example.com'.format(n))
    password = factory.PostGenerationMethodCall('set_password', 'password')
    first_name = factory.Sequence(lambda n: 'first_name-{0}'.format(n))
    last_name = factory.Sequence(lambda n: 'last_name-{0}'.format(n))

    class Meta:
        model = 'users.User'
        django_get_or_create = ('username', )
