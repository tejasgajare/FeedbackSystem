from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator, MaxLengthValidator

PROFILE_TYPES = (
    (u'STUDENT', 'Student'),
    (u'FACULTY', 'Faculty'),
    (u'COORDINATOR', 'Coordinator'),
    (u'AUDITOR', 'Auditor'),
)

YEAR_NAME = (
    (u'FE', 'First Year'),
    (u'SE', 'Second Year'),
    (u'TE', 'Third Year'),
    (u'BE', 'Fourth Year'),
)

DIV_NAME = (
    (u'A', 'A DIV'),
    (u'B', 'B DIV'),
    (u'C', 'C DIV'),
    #(u'D', 'D DIV'),
)

class Subject(models.Model):
	name = models.CharField(max_length = 30)
	subject_code = models.CharField(max_length = 10)
	def __str__(self):
		return self.name

class Department(models.Model):
	name = models.CharField(max_length = 30)
	def __str__(self):
		return self.name

#common field resides here
class Profile(models.Model):
	name = models.TextField(max_length = 250)
	email = models.EmailField(max_length = 254, blank=True)
	phone_number = models.CharField(max_length=13, blank=True)
	def __str__(self):
		return self.name

#classroom is class where we are linking dept, year and div
class Classroom(models.Model):
    department = models.ForeignKey(Department,on_delete = models.CASCADE)
    year = models.CharField(choices = YEAR_NAME, max_length = 16)
    div = models.CharField(choices = DIV_NAME, max_length = 16)
    def __str__(self):
        return (self.year +" "+ self.div) 

# used just to define the relation between User and Profile
class Student(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    profile = models.OneToOneField(Profile,on_delete = models.CASCADE)
    type = models.CharField(choices=PROFILE_TYPES, max_length=16, default = 'STUDENT')
    classroom = models.ForeignKey(Classroom,on_delete = models.CASCADE)
    def __str__(self):
        return self.profile.name

class Faculty(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    profile = models.OneToOneField(Profile,on_delete = models.CASCADE)
    type = models.CharField(choices=PROFILE_TYPES, max_length=16, default = 'FACULTY')
    def __str__(self):
        return self.profile.name


#following class is to link faculty with classroom and students
#Teaches changed to TeacherSubject
class TeacherSubject(models.Model):
    teacher = models.ForeignKey(Faculty,on_delete = models.CASCADE)
    classroom = models.ForeignKey(Classroom, on_delete = models.CASCADE)
    subject = models.ForeignKey(Subject,on_delete = models.CASCADE)
    def __str__(self):
        return (self.teacher.profile.name +" "+self.classroom.year +" "+ self.classroom.div+" "+ self.subject.name)

#profile for auditor
class Auditor(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    profile = models.OneToOneField(Profile,on_delete = models.CASCADE)
    type = models.CharField(choices=PROFILE_TYPES, max_length=16, default = 'AUDITOR')
    def __str__(self):
        return self.profile.name

#profile for coordinator
class Coordinator(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE)
    profile = models.OneToOneField(Profile,on_delete = models.CASCADE)
    type = models.CharField(choices=PROFILE_TYPES, max_length=16, default = 'COORDINATOR')
    def __str__(self):
        return self.profile.name

class Tag(models.Model):
    tag_title = models.CharField(max_length=16)
    def __str__(self):
        return self.tag_title

# for academics/ infrastructure / Faculty
class QuestionType(models.Model):
    title = models.CharField(max_length=16)
    def __str__(self):
        return self.title

class FeedbackForm(models.Model):
    title = models.CharField(max_length=50)
    is_active = models.BooleanField(default=False)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title + "-is_active :" + str(self.is_active) + " is_published:" + str(self.is_published)

class Question(models.Model):
    text = models.CharField(max_length=200)
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, null=True, blank=True)
    feedback_form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.feedback_form) + " - " + self.text

class FeedbackResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answer = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE, null=True, blank=True)
    def __str__(self):
        return str(self.student) + " - " + str(self.question)

class TextualResponse(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    type = models.ForeignKey(QuestionType, on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey(TeacherSubject, on_delete=models.CASCADE, null=True, blank=True)
    answer = models.TextField(null=True, blank=True)
    feedback_form = models.ForeignKey(FeedbackForm, on_delete=models.CASCADE)
    def __str__(self):
        return str(self.student) + " - " + str(self.type)