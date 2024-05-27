from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework import filters
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from .models import *
from .serializers import *
# Create your views here.
#==========================================student================================================

# register student
class StudentCreateView(generics.CreateAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response({"message": "successfully"}, status=status.HTTP_201_CREATED,)
        return Response({"message": "failed"}, status=status.HTTP_400_BAD_REQUEST)
    
# login student 

class StudentLoginView(generics.GenericAPIView):
    serializer_class = StudentSerializer

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            student = Student.objects.get(email=email)
            if check_password(password, student.password):
                serializer = self.get_serializer(student)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "failed"}, status=status.HTTP_401_UNAUTHORIZED)
        except Student.DoesNotExist:
            return Response({"message": "failed"}, status=status.HTTP_401_UNAUTHORIZED)
        



#==========================================search================================================
# all courses
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

# search courses by name 
class CourseSearchView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['course_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.kwargs.get('name', '')
        if search_query:
            queryset = queryset.filter(course_name__icontains=search_query)
        return queryset
# search courses by instructor_name
class CourseSearchInstructorView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['instructor_name']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.kwargs.get('instructor', '')
        if search_query:
            queryset = queryset.filter(instructor_name__icontains=search_query)
        return queryset
# search courses by code
class CourseSearchCodeView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['course_code']

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.kwargs.get('code', '')
        if search_query:
            queryset = queryset.filter(course_code__icontains=search_query)
        return queryset
    


#==========================================news================================================
class newsListView(generics.ListAPIView):
    queryset = news.objects.all()
    serializer_class = newsSerializer

#==========================================regestraion a course================================================

class RegisterStudentView(generics.CreateAPIView):
    serializer_class = StudentRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response({"message": "successfully"})
#==========================================regestraion course for user================================================
  
class UserCoursesView(APIView):
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')
        
        # Check if student exists
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)
        
        # Get the courses for the student
        student_regs = StudentsRegs.objects.filter(student_id=student)
        courses = Course.objects.filter(id__in=student_regs.values('course_id'))
        
        # Serialize the course data
        serializer = CourseInfoSerializer(courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#==========================================Suggested course for user================================================

class SuggestedCoursesView(APIView):
    def post(self, request, *args, **kwargs):
        student_id = request.data.get('student_id')

        # Check if student exists
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            return Response({"error": "Student not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get the courses the student is already registered for
        registered_courses = StudentsRegs.objects.filter(student_id=student).values_list('course_id', flat=True)
        registered_schedules = CourseSchedule.objects.filter(course__in=registered_courses)

        # Get all courses not at full capacity
        available_courses = Course.objects.filter(capacity__gt=StudentsRegs.objects.filter(course_id__isnull=False).count())

        suggested_courses = []
        for course in available_courses:
            # Check if the student has completed the prerequisites
            if course.prerequisites:
                if not StudentsRegs.objects.filter(student_id=student, course_id=course.prerequisites).exists():
                    continue

            # Check for scheduling conflicts
            conflict = False
            course_schedule = course.schedule
            for reg_schedule in registered_schedules:
                if (course_schedule.days == reg_schedule.days and
                    (course_schedule.start_time < reg_schedule.endTime and course_schedule.endTime > reg_schedule.start_time)):
                    conflict = True
                    break

            if not conflict:
                suggested_courses.append(course)

        # Serialize the suggested courses data
        serializer = SuggestedCourseSerializer(suggested_courses, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)