from rest_framework import serializers

from .models import *

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['student_id', 'name', 'email', 'password']

class CourseScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSchedule
        fields = ['schedule_id', 'days', 'start_time', 'endTime', 'room_no']

class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'description', 'instructor_name', 'schedule', 'prerequisites', 'capacity']


class StudentRegistrationSerializer(serializers.Serializer):
    student_id = serializers.IntegerField()
    course_code = serializers.CharField(max_length=100)

    def validate(self, data):
        student_id = data.get('student_id')
        course_code = data.get('course_code')

        # Check if student exists
        try:
            student = Student.objects.get(student_id=student_id)
        except Student.DoesNotExist:
            raise serializers.ValidationError("Student not found")

        # Check if course exists
        try:
            course = Course.objects.get(course_code=course_code)
        except Course.DoesNotExist:
            raise serializers.ValidationError("Course not found")

        # Check if course is full
        registered_students_count = StudentsRegs.objects.filter(course_id=course).count()
        if registered_students_count >= course.capacity:
            raise serializers.ValidationError("Course is already at full capacity")

        # Check if student meets the prerequisites
        prerequisite = course.prerequisites
        if prerequisite and not StudentsRegs.objects.filter(student_id=student, course_id=prerequisite).exists():
            raise serializers.ValidationError("Student has not completed the prerequisites for this course")

        # Check for scheduling conflicts
        student_courses = StudentsRegs.objects.filter(student_id=student)
        course_schedule = course.schedule

        for reg in student_courses:
            registered_course = reg.course_id
            registered_schedule = registered_course.schedule

            # Check if the days overlap
            if course_schedule.days == registered_schedule.days:
                # Check if the times overlap
                if not (course_schedule.endTime <= registered_schedule.start_time or course_schedule.start_time >= registered_schedule.endTime):
                    raise serializers.ValidationError("Schedule conflict detected")

        data['student'] = student
        data['course'] = course
        return data

    def create(self, validated_data):
        student = validated_data['student']
        course = validated_data['course']
        registration = StudentsRegs(student_id=student, course_id=course)
        registration.save()
        return registration

    def to_representation(self, instance):
        return {
            'id': instance.id,
            'student_id': instance.student_id.student_id,
            'student_name': instance.student_id.name,
            'course_code': instance.course_id.course_code,
            'course_name': instance.course_id.course_name
        }

class newsSerializer(serializers.ModelSerializer):
    class Meta:
        model = news
        fields = ['id', 'title', 'content', 'publishedDate']


class CourseInfoSerializer(serializers.ModelSerializer):
    schedule = serializers.StringRelatedField()
    
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'description', 'instructor_name', 'schedule']

class SuggestedCourseSerializer(serializers.ModelSerializer):
    schedule = serializers.StringRelatedField()
    
    class Meta:
        model = Course
        fields = ['course_code', 'course_name', 'description', 'instructor_name', 'schedule']