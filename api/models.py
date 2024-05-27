from django.db import models
from django.contrib.auth.hashers import make_password

class Student(models.Model):
    student_id = models.AutoField(unique=True,primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=100,unique=True)
    password = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        self.password = make_password(self.password)
        super().save(*args, **kwargs)
    def __str__(self):
        return self.name


class CourseSchedule(models.Model):
    schedule_id = models.AutoField(unique=True,primary_key=True)
    days = models.CharField(max_length=100 )
    start_time = models.TimeField()
    endTime = models.TimeField()
    room_no = models.CharField(max_length=10)    
    def __str__(self):
        return f"{self.days} ({self.start_time}) - Room {self.room_no}"


class Course(models.Model):
    course_code = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=100)
    description = models.TextField()
    instructor_name = models.CharField(max_length=100)
    schedule = models.ForeignKey('CourseSchedule', on_delete=models.CASCADE)
    prerequisites = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    capacity = models.IntegerField(default=10)
    def __str__(self):
        return self.course_code


class StudentsRegs(models.Model):
    id = models.AutoField(primary_key=True)
    student_id = models.ForeignKey('Student', on_delete=models.CASCADE)
    course_id = models.ForeignKey('Course', on_delete=models.CASCADE)
    def __str__(self):
        return f"Registration ID: {self.id}, Student ID: {self.student_id}, Course ID: {self.course_id}"

class news(models.Model):
    title = models.CharField(max_length=100)
    content = models.TextField()
    publishedDate = models.DateTimeField(auto_now_add=True)