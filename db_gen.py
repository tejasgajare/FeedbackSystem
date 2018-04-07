from app import models

DOTS = '..............'

SUBJECTS = {
    'System Programming and Operating System':'SPOS',
    'Embedded Systems and Internet of Things':'ES&IoT',
    'Software Modelling and Design':'SMD',
    'Web Technologies':'WT',
    'Design and Analysis of Algorithms':'DAA'
}

FACULTIES = {
    'faculty1':{
        'name':'Faculty1',
        'email':'faculty1@faculty.com',
        'phone_number':'9494949494',
    },
    'faculty2':{
        'name':'Faculty2',
        'email':'faculty2@faculty.com',
        'phone_number':'9494949494',
    },
    'faculty3':{
        'name':'Faculty3',
        'email':'faculty3@faculty.com',
        'phone_number':'9494949494',
    },
    'faculty4':{
        'name':'Faculty4',
        'email':'faculty4@faculty.com',
        'phone_number':'9494949494',
    },
    'faculty5':{
        'name':'Faculty5',
        'email':'faculty5@faculty.com',
        'phone_number':'9494949494',
    }
}

AUDITORS = {
    'auditor1':{
        'name':'Auditor1',
        'email':'auditor1@auditor.com',
        'phone_number':'9494949494'
    }
}

COORDINATORS = {
    'coordinator1':{
        'name':'Coordinator1',
        'email':'coordinator1@coordinator.com',
        'phone_number':'9494949494'
    }
}

def pts(text):
    print(DOTS+str(text)+DOTS)

def student_dictionary(filename):
    pts('creating students from csv')
    students = open(filename,'r').read().split('\n')
    retdict = {}
    for student in students[1:]:
        student = student.split(',')
        print(student)
        retdict[student[0]] = {
            'name':student[1],
            'email':student[2],
            'phone_number':student[3],
            'year':student[4].split(' ')[0],
            'div':student[4].split(' ')[1]
        }
    return retdict

def creating_departments():
    pts('creating department')
    dept = models.Department(name='Computer')
    dept.save()

def creating_subjects():
    pts('creating subjects')
    for subject, code in SUBJECTS.items():
        sub = models.Subject(name=subject, subject_code=code)
        sub.save()

def creating_classrooms():
    pts('creating classrooms')
    classroom = models.Classroom(
        department=models.Department.objects.all()[0],
        year='TE',
        div='A'
    )
    classroom.save()

def creating_students():
    pts('creating students and resp users+profiles')
    for roll_no,details in student_dictionary('DataSet1.csv').items():
        user = models.User.objects.create_user(roll_no,password='admin123')
        user.save()

        profile = models.Profile(
            name=details['name'],
            email=details['email'],
            phone_number=details['phone_number']
        )
        profile.save()

        print(models.Classroom.objects.all())
        classroom = models.Classroom.objects.all()[0]

        student = models.Student(
            user=user,
            profile=profile,
            classroom=classroom
        )
        student.save()

def creating_faculties():
    pts('creating faculties')
    for username,details in FACULTIES.items():
        print(username)
        user = models.User.objects.create_user(username,password='admin123')
        user.save()

        profile = models.Profile(
            name=details['name'],
            email=details['email'],
            phone_number=details['phone_number']
        )
        profile.save()

        faculty = models.Faculty(
            user=user,
            profile=profile,
        )
        faculty.save()

def creating_auditors():
    pts('creating auditors')
    for username,details in AUDITORS.items():
        user = models.User.objects.create_user(username,password='admin123')
        user.save()

        profile = models.Profile(
            name=details['name'],
            email=details['email'],
            phone_number=details['phone_number']
        )
        profile.save()

        auditor = models.Auditor(
            user=user,
            profile=profile,
        )
        auditor.save()

def creating_coordinators():
    pts('creating coordinators')
    for username,details in COORDINATORS.items():
        user = models.User.objects.create_user(username,password='admin123')
        user.save()

        profile = models.Profile(
            name=details['name'],
            email=details['email'],
            phone_number=details['phone_number']
        )
        profile.save()

        coordinator = models.Coordinator(
            user=user,
            profile=profile,
        )
        coordinator.save()

def creating_teachersubject():
    classroom = models.Classroom.objects.all()[0]
    for teacher,subject in zip(
        models.Faculty.objects.all(),
        models.Subject.objects.all()
    ):
        teachersubject = models.TeacherSubject(
            teacher=teacher,
            subject=subject,
            classroom=classroom
        )
        teachersubject.save()


pts('')
pts('')
pts('')
pts('')
creating_departments()
creating_subjects()
creating_classrooms()
creating_students()
creating_faculties()
creating_auditors()
creating_coordinators()
creating_teachersubject()
pts('end')

# exec(open('db_gen.py','r').read())