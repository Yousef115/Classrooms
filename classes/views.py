from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate

from .models import Classroom, Student
from .forms import ClassroomForm, SignupForm, SigninForm, AddStudentForm

########## USER VIEWS ##########

def signup(request):
	form = SignupForm()
	if request.method == 'POST':
		form = SignupForm(request.POST)

		if form.is_valid():
			user = form.save(commit=False)
			user.set_password(user.password)
			user.save()
			signin(request, user)

			return redirect ('classroom-list')
	context = {
		"form":form
	}

	return render (request, 'signup.html', context)

def signin(request):
	form = SigninForm()
	if request.method == 'POST':
		form = SigninForm(request.POST)

		if form.is_valid():
			username = form.cleaned_data ['username']
			password = form.cleaned_data ['password']

			auth_user = authenticate(username=username, password=password)
			if auth_user != None:
				login (request, auth_user)
				return redirect ('classroom-list')
	context = {
		"form":form
	}

	return render (request, 'login.html', context)

def signout(request):
	logout(request)
	return redirect('classroom-list')

########## CLASSROOM VIEWS ##########

def classroom_list(request):
	classrooms = Classroom.objects.all()
	context = {
		"classrooms": classrooms,
	}
	return render(request, 'classroom_list.html', context)

def classroom_detail(request, classroom_id):
	classroom_obj = Classroom.objects.get(id=classroom_id)
	student_obj = Student.objects.filter(classroom = classroom_obj).order_by('-name','-exam_grade')
	context = {
		"classroom": classroom_obj,
		"students": student_obj,
	}
	return render(request, 'classroom_detail.html', context)

def classroom_create(request):
	if not request.user.is_authenticated:
		return redirect('signin')
	form = ClassroomForm()
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None)
		if form.is_valid():
			form = form.save(commit=False)
			form.teacher = request.user
			form.save()
			messages.success(request, "Successfully Created!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	}
	return render(request, 'create_classroom.html', context)

def classroom_update(request, classroom_id):
	classroom = Classroom.objects.get(id=classroom_id)
	form = ClassroomForm(instance=classroom)
	if request.method == "POST":
		form = ClassroomForm(request.POST, request.FILES or None, instance=classroom)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-list')
		print (form.errors)
	context = {
	"form": form,
	"classroom": classroom,
	}
	return render(request, 'update_classroom.html', context)

def classroom_delete(request, classroom_id):
	Classroom.objects.get(id=classroom_id).delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('classroom-list')

########## STUDENT VIEWS ##########

def student_create(request, classroom_id):
	classroom_obj = Classroom.objects.get(id=classroom_id)
	if request.user != classroom_obj.teacher:
		messages.warning(request, "You can only add students to your own class.")
		return redirect('classroom-list')
	form = AddStudentForm()
	if request.method == "POST":
		form = AddStudentForm(request.POST)
		if form.is_valid():
			form = form.save(commit=False)
			form.classroom = classroom_obj
			form.save()
			messages.success(request, "Successfully Created!")
			return redirect('classroom-detail', classroom_id )
		print (form.errors)
	context = {
	"form": form,
	"classroom":classroom_obj,
	}
	return render(request, 'create_student.html', context)

def student_delete(request, student_id, classroom_id):
	Student.objects.get(id=student_id).delete()
	messages.success(request, "Successfully Deleted!")
	return redirect('classroom-detail', classroom_id )

def student_update(request, student_id, classroom_id):
	student = Student.objects.get(id=student_id)
	form = AddStudentForm(instance=student)
	if request.method == "POST":
		form = AddStudentForm(request.POST, instance=student)
		if form.is_valid():
			form.save()
			messages.success(request, "Successfully Edited!")
			return redirect('classroom-detail', classroom_id )
		print (form.errors)
	context = {
	"form": form,
	"student": student,
	}
	return render(request, 'update_student.html', context)