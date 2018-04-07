from app import models
from random import choice,randint
from app.final_new import get_tags

'''
2500 students
4-5 depts -> 14-15 faculties
classroom -> 1 dept -> 4 years -> 3 div / year
FeedbackForm -> 1
'''
topc_counter = 1
topf_counter = 1

PARAMS = [1,2,3,3,4,4,4,5,5]

first_names = []
last_names = []
fin_names = open('Names.csv','r').read().split('\n')
for name in fin_names:
    namel = name.split(',')
    print(namel)
    first_names.append(namel[0])
    last_names.append(namel[1])

def gen_name():
    name = []
    name.append(choice(first_names))
    name.append(choice(last_names))
    print(name)
    return ' '.join(name)

print(gen_name())

with open("FeedbackQuestions.txt", "r") as f:
    questions = f.readlines()

def gen_question_types():
    models.QuestionType(title='Academics').save()
    models.QuestionType(title='Infrastructure').save()
    models.QuestionType(title='Faculty').save()
    print('created question types')

DEPARTMENTS = {
    'Computer':'CO',
    #'Mechanical':'ME',
    #'Electronics and Telecommunications':'ET',
    #'Information Technology':'IT'
}

YEARS = [
    'FE',
    #'SE',
    #'TE',
    #'BE'
]

DIVS = [
    'A',
    #'B',
    #'C'
]

SUBS = {
    'Computer':{name:name for name in [
        'DAA',
        'ES-IOT',
        'WT',
        'SPOS',
        'SMD'
    ]},
    'Mechanical':{name:name for name in [
        'RAAC',
        'CADCAM',
        'DOM',
        'PPE',
        'MSD'
    ]},
    'Electronics and Telecommunications':{name:name for name in [
        'VLSI',
        'CN',
        'ME',
        'DIP',
        'EPD'
    ]},
    'Information Technology':{name:name for name in [
        'BCS',
        'ICS',
        'ML',
        'ADS',
        'RTES'
    ]}
}

def gen_subs():
    print('generating subjects')
    for dept,subdict in SUBS.items():
        for subname in subdict:
            sub = models.Subject(name=subname,subject_code=subname)
            sub.save()

def gen_depts():
    print('generating departments')
    for key in DEPARTMENTS.keys():
        dept = models.Department(name=key)
        dept.save()
        print('Dept',dept.name,'saved')

def gen_classroom(dept,year,div):
    classroom = models.Classroom(
        department=models.Department.objects.get(name=dept),
        year=year,
        div=div
    )
    print(classroom.department,classroom.year,classroom.div,'generated')
    classroom.save()
    return classroom

def gen_faculty(department, cur_count):
    dept = models.Department.objects.get(name=department)
    name =  gen_name() 
    user = models.User.objects.create_user(username="faculty" + str(cur_count), password='admin123')
    user.save()
    email = name.replace(' ','')+'@college.com'
    phone_number = '9090909090'
    profile = models.Profile(name=name,email=email,phone_number=phone_number)
    profile.save()
    faculty = models.Faculty(user=user,profile=profile)
    faculty.save()
    print(dept,name,'generated')
    return faculty

def gen_auditor():
    name =  gen_name() 
    user = models.User.objects.create_user(username="auditor1", password='admin123')
    user.save()
    email = name.replace(' ','')+'@college.com'
    phone_number = '9090909090'
    profile = models.Profile(name=name,email=email,phone_number=phone_number)
    profile.save()
    auditor = models.Auditor(user=user,profile=profile)
    auditor.save()
    return auditor

def gen_coordinator():
    name =  gen_name() 
    user = models.User.objects.create_user(username="coordinator1", password='admin123')
    user.save()
    email = name.replace(' ','')+'@college.com'
    phone_number = '9090909090'
    profile = models.Profile(name=name,email=email,phone_number=phone_number)
    profile.save()
    coordinator = models.Coordinator(user=user,profile=profile)
    coordinator.save()
    return coordinator


def gen_student(rollno,dept,year,div):
    user = models.User.objects.create_user(username="student" + str(rollno), password='admin123')
    user.save()
    name =  gen_name()
    classroom = models.Classroom.objects.get(
        department=models.Department.objects.get(name=dept),
        year=year,
        div=div
    )
    email = str(rollno)+'@college.com'
    phone_number = '9090909090'
    profile = models.Profile(name=name,email=email,phone_number=phone_number)
    profile.save()
    student = models.Student(user=user,profile=profile,classroom=classroom)
    student.save()
    print(dept,rollno,'generated')

def fill_feedback(student, form, questions, teacher_subjects):
    acadq = questions["Academics"]
    for q in acadq:
        models.FeedbackResponse(student=student,question=q,answer=choice(PARAMS)).save()

    infraq = questions["Infrastructure"]
    for q in infraq:
        models.FeedbackResponse(student=student,question=q,answer=choice(PARAMS)).save()

    facultyq = questions["Faculty"]
    for teacher_subject in teacher_subjects:
        for q in facultyq:
            models.FeedbackResponse(student=student,question=q,answer=choice(PARAMS),teacher_subject=teacher_subject).save()
    print(student,'feedback generated')

def gen_tags():
    print("generating tags")
    for tag in TAGS:
        models.Tag(tag_title=tag).save()

gen_depts()
gen_subs()
gen_question_types()
gen_auditor()
gen_coordinator()

for dept,dept_code in DEPARTMENTS.items():
    faculties = []
    for i in range(15):
        faculties.append(gen_faculty(dept, topf_counter))
        topf_counter += 1
    subs = set(SUBS[dept].keys())
    faculty_subject = []
    temp_subs = []
    for faculty in faculties:
        if len(temp_subs) == 0:
            temp_subs = list(SUBS[dept].keys())
        faculty_subject.append((faculty, models.Subject.objects.get(name=temp_subs[0])))
        temp_subs.pop(0)
    for year in YEARS:
        for div in DIVS:
            cur_classroom = gen_classroom(dept,year,div)
            for f_s in faculty_subject:
                teacher_subject = models.TeacherSubject(teacher=f_s[0],
                                                    classroom=cur_classroom,
                                                    subject=f_s[1])
                teacher_subject.save()
            for i in range(1,5):
                gen_student(topc_counter,dept,year,div)
                topc_counter += 1

forms = ["Feedback Form 1", "Feedback Form 2", "Feedback Form 3",
            "Feedback Form 4", "Feedback Form 5"]
for title in forms:
    form  = models.FeedbackForm(title=title,is_active=True,is_published=True)
    form.save()
    print('%s created' % title)

    for i in range(0, len(questions), 3):
        question = questions[i].strip()
        question_type = models.QuestionType.objects.get(title=questions[i+1].strip())
        tag = questions[i+2].strip()
        cur_tag = None
        try:
            cur_tag = models.Tag.objects.get(tag_title=tag)
        except:
            if cur_tag == None and tag != "None":
                cur_tag = models.Tag(tag_title=tag)
                cur_tag.save()
        models.Question(text=question,type=question_type,tag=cur_tag,feedback_form=form).save()
        print('question created:', question, cur_tag)

    all_questions = models.Question.objects.filter(feedback_form=form)
    question_dict = {}
    for a_q in all_questions:
        if not a_q.type.title in question_dict:
            question_dict[a_q.type.title] = []
        question_dict[a_q.type.title].append(a_q)

    for student in models.Student.objects.all():
        fill_feedback(student, form, question_dict, models.TeacherSubject.objects.filter(classroom=student.classroom))