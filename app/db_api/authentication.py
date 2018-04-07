from app.models import Subject, Department, Profile, Student, Faculty, TeacherSubject, Classroom
def authenticate_role(user):
	# if Student username exists and password is matching:
	# 	return "student"
	# elif Faculty username exists and password is matching:
	# 	return "faculty's role"
	# else:
	# 	return -1
    """ try:
        obj = Student.objects.get(user = user)
    except Student.DoesNotExist:
        obj = None
    if(obj is not None):
        print('student was here')
        return 'Student'
    else:
        obj = Employee.objects.get(user = user)

        if(obj.role == 'Faculty'):
            return 'Faculty'

        elif(obj.role == 'Auditor'):
            return 'Auditor'
        
        else:
            return 'Co-ordinator' """
    #print ("is in authentication.py")
    if hasattr(user, 'student'):
        #print (user.student.type)
        return user.student.type
    elif hasattr(user, 'faculty'):
        return user.faculty.type
    elif hasattr(user, 'auditor'):
        return user.auditor.type
    elif hasattr(user, 'coordinator'):
        return user.coordinator.type
    else:
        return -1
