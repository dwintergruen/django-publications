from django.db import models

class Person(models.Model):
    """Collect persons"""
    firstName = models.CharField(max_length=1024, blank=True, null=True)
    lastName = models.CharField(max_length=1024, blank=True, null=True)
    name = models.CharField(max_length=1024, blank=True, null=True)

    def __str__(self):
        if self.firstName or self.lastName:
            return "%s__%s" % (self.firstName,self.lastName)
        else:
            return self.name

class Role(models.Model):
    """ Role of the person in a publication something, like author, translator"""
    typ =  models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return self.typ

class Creator(models.Model):
    """Join persons and roles for the creator field"""
    person = models.ForeignKey(Person,on_delete=models.CASCADE)
    role = models.ForeignKey(Role,on_delete=models.CASCADE)

    def __str__(self):
        return "%s__%s" % (self.person,self.role)





