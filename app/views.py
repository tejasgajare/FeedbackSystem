import json
from django.shortcuts import render
from django.conf.urls import include
from django.template import loader
from .models import Student, Faculty,Department, TeacherSubject, FeedbackForm, Question, QuestionType, FeedbackResponse, Tag, TextualResponse
from .forms import SignUpForm,LogInForm,CreateNewForm, Subject
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from app.db_api.authentication import authenticate_role
from app.db_api.logic import collect_feedback
from django.contrib.auth import login as user_login
from app.decorators import student_required, faculty_required, auditor_required, coordinator_required
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from .final_new import get_sentiment, get_tags, get_sentiments

from django.db.models import Count,Sum,Avg,IntegerField,Case,When
from django.shortcuts import render_to_response

#sentiment
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
analyzer = SentimentIntensityAnalyzer()

def get_sentiment(sentence):
	vs = analyzer.polarity_scores(sentence)
	vs.pop('compound')
	type = max(vs.items(),key=lambda x:x[1])[0]
	print("Sentiment is",type)
	return type

@login_required
def home(request):
    return render(request, 'base-vuetify.html')

@student_required
def student_dashboard(request):
	feedbackforms = FeedbackForm.objects.filter(is_active=True, is_published=True)
	context = {
		'numberofforms':len(feedbackforms),
		'feedbackforms':feedbackforms
	}
	return render(request, 'student_dashboard_new_new.html', context)

@student_required
def ajax_student_dashboard(request):
	feedbackforms = FeedbackForm.objects.filter(is_active=True, is_published=True)
	student = request.user.student
	context = {}	
	for form in feedbackforms:
		responses = FeedbackResponse.objects.filter(student=student,question__feedback_form=form)
		count = responses.count()
		if count == 0:
			context['form'+str(form.id)] = 'Urgent'
		elif count < 50:
			context['form'+str(form.id)] = 'Incomplete'
		else:
			context['form'+str(form.id)] = 'Complete'
	return JsonResponse(context)

@student_required
def student_profile(request):
	return render(request, 'student_profile_new.html')

@student_required
def events(request):
	return render(request, 'events.html')

@faculty_required
def faculty_dashboard(request):
	#formid
	context = {}  
	forms = list(FeedbackForm.objects.filter(is_published=True))
	teacher_subjects = list(TeacherSubject.objects.filter(teacher=request.user.faculty))
	compare_tags = {}
	for form in forms:
		if list(FeedbackResponse.objects.filter(question__feedback_form=form)):
			data = list(FeedbackResponse.objects.filter(teacher_subject__teacher=request.user.faculty,question__feedback_form=form).values('question__tag__tag_title').annotate(avg=Avg('answer')))
			for tag in data:
				if tag['question__tag__tag_title'] not in compare_tags:
					compare_tags[tag['question__tag__tag_title']] = []
				compare_tags[tag['question__tag__tag_title']].append(tag['avg'])
			context[form] = {}
			for teacher_subject in teacher_subjects:
				context[form][teacher_subject.subject] = {}
				context[form][teacher_subject.subject]['overall'] = {}
				avg = list(FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question__feedback_form=form).values('teacher_subject').annotate(avg =Avg('answer')))
				for data in avg:
					temp =None
					for key,value in data.items():
						if(key == 'avg'):
							temp =value
					data['avg'] = round(temp,2)
					data['counter_avg'] = 5-round(temp, 2)
				context[form][teacher_subject.subject]['overall'] = {}
				context[form][teacher_subject.subject]['overall']['avg'] = avg
				context[form][teacher_subject.subject]['overall']['scores'] = {6:{'val':0,'perc':100}}
				maxv = 0
				for i in range(1, 6):
					context[form][teacher_subject.subject]['overall']['scores'][i] = {}
					context[form][teacher_subject.subject]['overall']['scores'][i]['val'] = FeedbackResponse.objects.filter(teacher_subject=teacher_subject, question__feedback_form=form, answer=i).count()
					if maxv < context[form][teacher_subject.subject]['overall']['scores'][i]['val']:
						maxv = context[form][teacher_subject.subject]['overall']['scores'][i]['val']
					context[form][teacher_subject.subject]['overall']['scores'][6]['val'] += context[form][teacher_subject.subject]['overall']['scores'][i]['val']
				if maxv:	
					for i in range(1, 6):
						context[form][teacher_subject.subject]['overall']['scores'][i]['perc'] = int((context[form][teacher_subject.subject]['overall']['scores'][i]['val']/maxv)*100)
				else:
					context[form][teacher_subject.subject]['overall']['scores'][i]['perc'] =0

				context[form][teacher_subject.subject]['responses'] = {}
				context[form][teacher_subject.subject]['strength'] = set()
				context[form][teacher_subject.subject]['weakness'] = set()
				responses = list(FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question__feedback_form=form))
				for response in responses:
					question = response.question
					#print(question.tag.tag_title)
					context[form][teacher_subject.subject]['responses'][question] = {}
					temp = list(FeedbackResponse.objects.filter(question=question).values('question').annotate(avg =Avg('answer')))
					context[form][teacher_subject.subject]['responses'][question]['overall'] = temp[0]['avg']
					context[form][teacher_subject.subject]['responses'][question]['scores'] = {}
					maxv = 0
					for i in range(1,6):
						context[form][teacher_subject.subject]['responses'][question]['scores'][i] = {}
						context[form][teacher_subject.subject]['responses'][question]['scores'][i]['val'] = FeedbackResponse.objects.filter(question=question,answer=i).count()
						if maxv < context[form][teacher_subject.subject]['responses'][question]['scores'][i]['val']:
							maxv = context[form][teacher_subject.subject]['responses'][question]['scores'][i]['val']
					print(context[form][teacher_subject.subject]['responses'][question]['scores'])
					for i in range(1,6):
						context[form][teacher_subject.subject]['responses'][question]['scores'][i]['perc'] = round((context[form][teacher_subject.subject]['responses'][question]['scores'][i]['val']/maxv)*100,2)
	
					for data in temp:
						if question.tag == None:
							continue
						if(data['avg'] > 3.5):#not working
							print("adding strength")
							context[form][teacher_subject.subject]['strength'].add(question.tag)
						else:
							print("adding weakness")
							context[form][teacher_subject.subject]['weakness'].add(question.tag)
					scores= {}
					for i in range(1,6):
							scores[i] = FeedbackResponse.objects.filter(teacher_subject=teacher_subject,question=question,answer =i).count()
					
			#print(context[form][teacher_subject.subject]['strength'])
			#print(context[form][teacher_subject.subject]['weakness'])
			context[form][teacher_subject.subject]['strength'] = list(
				context[form][teacher_subject.subject]['strength'])
			context[form][teacher_subject.subject]['weakness'] = list(
				context[form][teacher_subject.subject]['weakness'])
			while(len(context[form][teacher_subject.subject]['strength']) != len(context[form][teacher_subject.subject]['weakness'])):
				if(len(context[form][teacher_subject.subject]['strength']) < len(context[form][teacher_subject.subject]['weakness'])):
					context[form][teacher_subject.subject]['strength'].append("")
				else:
					context[form][teacher_subject.subject]['weakness'].append("")

			#print(context[form][teacher_subject.subject]['strength'])
			#print(context[form][teacher_subject.subject]['weakness'])
			strength_weakness = []
			for i in range(len(context[form][teacher_subject.subject]['strength'])):
				strength_weakness.append(
					(context[form][teacher_subject.subject]['strength'][i],
					context[form][teacher_subject.subject]['weakness'][i]))
			context[form][teacher_subject.subject]['strength_weakness'] = strength_weakness

			responses = TextualResponse.objects.filter(feedback_form=form)
			sentiments = {}
			for response in responses:
				sentiments[response] = get_sentiments(response.answer)
			#print("Akshay sentiments:", sentiments)
			# context = {
			# "positive":pos,
			# "negative":neg,
			# }


		#print(context)
	graphs=compare_tags
	return render_to_response( 'faculty_dashboard.html',locals())


@faculty_required
def faculty_profile(request):
	return render(request, 'faculty_profile.html')

@auditor_required
def auditor_profile(request):
	return render(request, 'auditor_profile.html')

@auditor_required
def auditor_dashboard(request):

	context = {}
	forms   = list(FeedbackForm.objects.filter(is_published=True))
	departments = list( Department.objects.all() )
	for form in forms:
		context[form] = {}
		if list(FeedbackResponse.objects.filter(question__feedback_form=form)):
			types = list(QuestionType.objects.all())
			types_overall_rating=list(FeedbackResponse.objects.filter(question__feedback_form =form).values('question__type__title').annotate(avg =Avg('answer')))
			for type_ in types_overall_rating:
				type_['avg']=round(((type_['avg']/5)*100),2)
				if type_['avg'] > 75:
					type_['color'] = 'green'
				elif type_['avg'] > 60:
					type_['color'] = 'orange'
				else:
					type_['color'] = 'red'
			context[form]['types_overall_rating'] =types_overall_rating
		overall_list=FeedbackResponse.objects.filter(question__feedback_form=form).values("question__feedback_form").annotate(avgs=Avg('answer'))[0]
		# print("HELLO WORLD", overall_list)
		overall_list['avgs'] = round(overall_list['avgs'], 2)
		context[form]['scores'] = {}
		context[form]['scores'][6] = {'val':0,'perc':100}
		maxv = 0
		for i in range(1,6):
			context[form]['scores'][i] = {}
			context[form]['scores'][i]['val'] = FeedbackResponse.objects.filter(question__feedback_form=form,answer=i).count()
			context[form]['scores'][6]['val'] += context[form]['scores'][i]['val']
			if maxv < context[form]['scores'][i]['val']:
				maxv = context[form]['scores'][i]['val']

		if maxv:
			for i in range(1,6):
				context[form]['scores'][i]['perc'] = round((context[form]['scores'][i]['val']/maxv)*100,2)
		else:
			for i in range(1,6):
				context[form]['scores'][i]['perc'] = 0
					
		context[form]['overall']=overall_list
		context[form]['tags'] = list(Question.objects.filter(feedback_form=form,type__title='Faculty').only('tag'))
		context[form]['score'] = []
		context[form]['columns'] = ["Name", "Dept"]
		de_dupe = {}
		for t in context[form]['tags']:
			if t.tag is not None and t.tag.tag_title not in de_dupe:
				de_dupe[t.tag.tag_title] = 1
				context[form]['columns'].append(t.tag.tag_title)
		context[form]['columns'].append("Overall")

		for faculty in Faculty.objects.all():
			cur_faculty = []
			cur_faculty.append(faculty.profile.name)
			cur_faculty.append(TeacherSubject.objects.filter(teacher=faculty)[0].classroom.department.name)
			
			tag_merge = {}
			for resp in context[form]['tags']:
					cur_resp = list(FeedbackResponse.objects.filter(question__feedback_form=form,
													teacher_subject__teacher=faculty, question=resp)
													.values("question__tag__tag_title")
													.annotate(avgs=Avg('answer')))
					if cur_resp[0]['question__tag__tag_title'] not in tag_merge:
						tag_merge[cur_resp[0]['question__tag__tag_title']] = []
					tag_merge[cur_resp[0]['question__tag__tag_title']].append(cur_resp[0]["avgs"])
			
			print("Akshay tag_merge:", tag_merge)
			tag_score = {}
			overall = 0
			for k, v in tag_merge.items():
				cur_avg = 0
				for val in v:
					cur_avg += val
				cur_avg /= len(v)
				tag_score[k] = round(cur_avg, 2)
				overall += cur_avg
			if tag_score:
				overall /= len(tag_score.keys())
				overall = round(overall, 2)
			print("Akshay tag_score:", tag_score)
			de_dupe = {}
			for resp in context[form]['tags']:
				if resp.tag is not None and resp.tag.tag_title not in de_dupe:
					de_dupe[resp.tag.tag_title] = 1
					cur_tag = resp.tag.tag_title
					cur_faculty.append(tag_score[cur_tag])
			print("Akshay cur_faculty:", cur_faculty)
			cur_faculty.append(overall)
			context[form]['score'].append(cur_faculty)
		print("$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$\n\n", context[form])
	
	return render_to_response('auditor_dashboard.html',locals())

@auditor_required
def ajax_data_table(request, formid=None, dept=None, minimum=None, maximum=None):
	if formid:
		if dept:
			if minimum or maximum:
				minimum = max(0,minimum)
				maximum = min(5,maximum)
				faculty_question_data = FeedbackResponse.objects.filter(question__feedback_form__id  = formid).values('teacher_subject__teacher','question__tag').annotate(avg = Avg('answer'))
				print(faculty_question_data)
				return JsonResponse({'x':'y'})
			else:
				return JsonResponse({'x':'y2'})
		else:
			return JsonResponse({'x':'y3'})
	else:
		return JsonResponse({'error':'no formid'})


@coordinator_required
def coordinator_dashboard(request):
	forms = FeedbackForm.objects.all()
	context = {
		'forms':forms
	}
	return render(request, 'coordinator_dashboard.html', context)

@coordinator_required
def publish_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_published = True
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def activate_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_active = True
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def deactivate_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.is_active = False
	form.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def copy_form(request, formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.pk = None
	form.title = form.title + ' - Copy'
	form.is_active = False
	form.is_published = False
	form.save()
	for question in Question.objects.filter(feedback_form=FeedbackForm.objects.get(pk=formid)):
		question.pk = None
		question.feedback_form = form
		question.save()
	return redirect('coordinator_dashboard')

@coordinator_required
def ajax_delete_question(request):
	formid = request.POST['formid']
	qid = request.POST['qid']
	Question.objects.get(pk=qid, feedback_form=FeedbackForm.objects.get(pk=formid)).delete()
	return JsonResponse({'success':'true'});

@student_required
def ajax_text_response(request):
	print('here')
	form = FeedbackForm.objects.get(pk=request.POST['formid'])
	student = Student.objects.get(pk=request.POST['student'])
	text = request.POST['text']
	type = QuestionType.objects.get(title=request.POST['type'])

	text_response = TextualResponse(
		student=student,
		type=type,
		answer=text,
		feedback_form=form
	)
	text_response.save()
	print('text response saved')

	sentiment = get_sentiment(text)

	return JsonResponse({'sentiment':sentiment})

@coordinator_required
def ajax_predict_tags(request):
	text = request.POST['text']
	tag = get_tags(text)
	print("Tag is", tag)
	if tag != -1:
		tag_obj = Tag.objects.get(pk=tag)
		return JsonResponse({'tag':tag_obj.tag_title})
	else:
		return JsonResponse({'tag':''})


@coordinator_required
def edit_form_title(request):
	formid = request.POST['formid']
	title = request.POST['title']
	form = FeedbackForm.objects.get(pk=formid)
	form.title = title
	form.save()
	return JsonResponse({'success':'true'})

@coordinator_required
def delete_form(request,formid):
	form = FeedbackForm.objects.get(pk=formid)
	form.delete()
	return redirect('coordinator_dashboard')

@coordinator_required
def edit_form(request, formid=None):
	ACADEMICS = QuestionType.objects.get(title='Academics')
	INFRASTRUCTURE = QuestionType.objects.get(title='Infrastructure')
	FACULTY = QuestionType.objects.get(title='Faculty')
	if formid:
		form = FeedbackForm.objects.get(pk=formid)
	else:
		form = FeedbackForm(title='Blank Form')
		form.save()
		return redirect('/edit_form/'+str(form.id))
	questions = Question.objects.filter(feedback_form=form)
	acadquestions = questions.filter(type=ACADEMICS)
	infraquestions = questions.filter(type=INFRASTRUCTURE)
	facultyquestions = questions.filter(type=FACULTY)
	tags = Tag.objects.all()
	context = {
		'form':form,
		'acadquestions':acadquestions,
		'infraquestions':infraquestions,
		'facultyquestions':facultyquestions,
		'tags':tags
	}
	return render(request, 'edit_questions.html', context)

@coordinator_required
def coordinator_profile(request):
	return render(request, 'coordinator_profile.html')

@coordinator_required
def create_form(request):
	if request.method == 'POST':
		form = CreateNewForm(request.POST)
		if form.is_valid():
			title = form.cleaned_data['title']
			new_form = FeedbackForm(title=title)
			new_form.save()
			return redirect('add_questions',formid=new_form.id)
	else:
		form = CreateNewForm()
	return render(request, 'create_form.html', {'form':form})

@coordinator_required
def add_questions(request,formid):
	curr_form = FeedbackForm.objects.get(pk=formid)
	context = {
		'curr_form':curr_form
	}
	return render(request, 'add_questions.html', context)

@coordinator_required
def ajax_add_questions(request):
	print(request.POST)
	data = request.POST
	q = Question(
		text=data['text'],
		tag=Tag.objects.get(pk=int(data['tagid'])),
		type=QuestionType.objects.get(title=data['type']),
		feedback_form=FeedbackForm.objects.get(pk=int(data['form']))
	)
	q.save()
	
	context = {}
	return redirect('edit_form',data['form'])

@coordinator_required
def edit_form_question(request):
	print(request.POST)
	data = request.POST
	tag_obj = None

	if data['tagid'] != "":
		tag_obj = Tag.objects.get(pk=int(data['tagid']))

	q = Question(
		text=data['text'],
		tag=tag_obj,
		type=QuestionType.objects.get(title=data['type']),
		feedback_form=FeedbackForm.objects.get(pk=int(data['formid']))
	)
	q.save()
	
	context = {}
	return redirect('edit_form',data['formid'])


@student_required
def feedback_faculty(request,formid):
	ACADEMICS = QuestionType.objects.get(title='Academics')
	INFRASTRUCTURE = QuestionType.objects.get(title='Infrastructure')
	FACULTY = QuestionType.objects.get(title='Faculty')	
	curr_user = request.user
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject: teaching.teacher for teaching in teachings}
	feedbackform = FeedbackForm.objects.get(pk=formid)
	questions = Question.objects.filter(feedback_form=feedbackform)
	facultyquestions = questions.filter(type=FACULTY)
	context = {
		'courses': courses,
		'facultyquestions':facultyquestions
	}
	return render(request, 'feedback_faculty.html', context)

@student_required
def student_feedback(request, formid):
	print('in student_feedback',formid)
	ACADEMICS = QuestionType.objects.get(title='Academics')
	INFRASTRUCTURE = QuestionType.objects.get(title='Infrastructure')
	FACULTY = QuestionType.objects.get(title='Faculty')
	curr_user = request.user
	feedbackform = FeedbackForm.objects.get(pk=formid)
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject: teaching.teacher for teaching in teachings}
	questions = Question.objects.filter(feedback_form=feedbackform)
	acadquestions = questions.filter(type=ACADEMICS)
	infraquestions = questions.filter(type=INFRASTRUCTURE)
	
	context = {
		'form':feedbackform,
		'courses': courses,
		'acadquestions':acadquestions,
		'infraquestions':infraquestions,
	}

	return render(request, 'feedback_new.html', context)

@student_required
def student_feedback_response_set(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	a_val = request.GET.get('a_val',None)

	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	a_val = int(a_val)

	try:
		fr = FeedbackResponse.objects.get(student=student,question=question)
	except:
		fr = FeedbackResponse.objects.create(student=student,question=question,answer=a_val)
	fr.answer = a_val
	print(fr.answer)
	fr.save()
	
	return JsonResponse({
		'success':'success'
	})

@student_required
def student_feedback_response_get(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	
	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	
	try:
		fr = FeedbackResponse.objects.get(student=student,question=question)
		ansval = fr.answer
		print(ansval)
		return JsonResponse({
			'ans':ansval
		})
	except:
		return JsonResponse({
			'ans':0
		})

@student_required
def student_feedback_faculty_response_set(request):
	print('\n\n\n\n\n\n\n SFFRS called \n\n\n\n\n\n\n')

	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	f_id = request.GET.get('f_id',None)
	sub_id = request.GET.get('sub_id',None)
	a_val = request.GET.get('a_val',None)

	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	faculty = Faculty.objects.filter(pk=f_id).first()
	subject = Subject.objects.filter(pk=sub_id).first()

	teacher_subject = TeacherSubject.objects.filter(classroom=student.classroom,teacher=faculty,subject=subject).first()

	print(q_id, f_id, s_id, sub_id, a_val, question, student, faculty, subject, teacher_subject)
	
	a_val = int(a_val)

	try:
		fr = FeedbackResponse.objects.get(student=student,question=question,teacher_subject=teacher_subject)
	except:
		fr = FeedbackResponse.objects.create(student=student,question=question,teacher_subject=teacher_subject,answer=a_val)
	fr.answer = a_val
	print(fr.answer)
	fr.save()
	
	return JsonResponse({
		'success':'success'
	})

@student_required
def student_feedback_faculty_response_get(request):
	q_id = request.GET.get('q_id',None)
	s_id = request.GET.get('s_id',None)
	f_id = request.GET.get('f_id',None)
	sub_id = request.GET.get('sub_id',None)
	
	question = Question.objects.filter(pk=q_id).first()
	student = Student.objects.filter(pk=s_id).first()
	faculty = Faculty.objects.filter(pk=f_id).first()
	subject = Subject.objects.filter(pk=sub_id).first()

	teacher_subject = TeacherSubject.objects.filter(classroom=student.classroom,teacher=faculty,subject=subject).first()
	
	try:
		fr = FeedbackResponse.objects.get(student=student,question=question,teacher_subject=teacher_subject)
		ansval = fr.answer
		print(ansval)
		return JsonResponse({
			'ans':ansval
		})
	except:
		return JsonResponse({
			'ans':0
		})		

@student_required
def feedback_faculty_theory(request):
	curr_user = request.user
	teachings = TeacherSubject.objects.filter(classroom=curr_user.student.classroom)
	courses = {teaching.subject:teaching.teacher for teaching in teachings}
	pass

@student_required
def feedback_infrastructure(request):
	#add form here and redirect to page
	pass

@student_required
def feedback_academics(request):
	#add form here and redirect to page
	pass

def signup(request):
	"""	if request.method == 'POST':
			form = SignUpForm(request.POST)
			if form.is_valid():
				user = form.save()
				user.refresh_from_db()  # load the profile instance created by the signal
				user.student.role = "student"
				user.student.student_name = form.cleaned_data.get('student_name')
				user.student.email = form.cleaned_data.get('email')
				user.student.phone_number = form.cleaned_data.get('phone_number')
				raw_password = form.cleaned_data.get('password1')
				user.student.save()
				user = authenticate(username=user.username, password=raw_password)
				login(request, user)
				return redirect('home')

		else:
			form = SignUpForm()
		return render(request, 'signup.html', {'form': form})
	"""
	pass

def login(request):
	ACADEMICS = QuestionType.objects.get(title='Academics')
	INFRASTRUCTURE = QuestionType.objects.get(title='Infrastructure')
	FACULTY = QuestionType.objects.get(title='Faculty')
	if request.method == 'POST':
		form=LogInForm(request.POST)
		if form.is_valid():
			user=form
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				user_login(request, user)
				role=authenticate_role(user)

				if(role == 'STUDENT'):
					return redirect('student_dashboard')
				elif (role == 'FACULTY'):
					return redirect('faculty_dashboard')
				elif (role =='AUDITOR'):
					return redirect('auditor_dashboard')
				elif(role == 'COORDINATOR'):
					return redirect('coordinator_dashboard')

			else:
				messages.error(request, 'Username or Password Incorrect')

	else:
		form=LogInForm()
	return render(request, 'login_new.html', {'form': form})


def logout_view(request):
	logout(request)
	return redirect('login')

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            #messages.success(request, 'Your password was successfully updated!')
            role=authenticate_role(user)

            if(role == 'STUDENT'):
                return redirect('student_dashboard')
            elif (role == 'FACULTY'):
                return redirect('faculty_dashboard')
            elif (role =='AUDITOR'):
                return redirect('auditor_profile')
            elif(role == 'COORDINATOR'):
                return redirect('coordinator_dashboard')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })

import json
from django.db.models import Sum,Count
from django.core import serializers
def test_graph(request):
	"""academic_response =  FeedbackResponse.objects.filter(question__type__title="Academics").values('question').annotate(dsum=Sum('answer'),dcount = Count('student'))
				context = serializers.serialize('json', academic_response)
			"""
	return render(request, 'test_graph.html')
