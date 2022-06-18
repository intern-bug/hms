import complaints
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.validators import MinLengthValidator
from institute.validators import numeric_only, date_no_future
from institute.constants import FLOOR_OPTIONS
from students.models import Outing
from security.models import OutingInOutTimes
from django.utils import timezone


# Create your models here.
class Student(models.Model):
    YEAR = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
    )

    GENDER=(
        ('Male','Male'),
        ('Female','Female'),
    )

    def photo_storage_path(instance, filename):
        extension = filename.split('.')[-1]
        return 'Student-Photos/Year-{}/{}.{}'.format(instance.year, instance.regd_no, extension)

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    account_email = models.EmailField(unique=True, null=False)
    regd_no = models.CharField(unique=True, null=False, max_length=8, validators=[MinLengthValidator(6)])
    roll_no = models.CharField(unique=True, null=False, max_length=8, validators=[MinLengthValidator(6)])
    name = models.CharField(max_length=100, null=False)
    email = models.EmailField(null=True, blank=True)
    year = models.IntegerField(null=False, choices=YEAR)
    branch = models.CharField(max_length=40,null=False)
    gender = models.CharField(max_length=7,choices=GENDER,null=False)
    pwd = models.BooleanField(null=False, default=False)
    community = models.CharField(max_length=25, null=True, blank=True)
    aadhar_number = models.CharField(max_length=15, null=True, blank=True)
    dob = models.DateField(null=False, validators=[date_no_future])
    blood_group = models.CharField(max_length=25, null=True, blank=True)
    father_name = models.CharField(max_length=100, null=True, blank=True)
    mother_name = models.CharField(max_length=100, null=True, blank=True)
    phone = models.CharField(null=False, max_length=10, validators=[numeric_only])
    parents_phone = models.CharField(null=False, max_length=10, validators=[numeric_only])
    emergency_phone = models.CharField(null=True, blank=True, max_length=10, validators=[numeric_only])
    address = models.TextField(null=False)
    photo = models.ImageField(null=True, blank=True, upload_to=photo_storage_path)
    is_hosteller = models.BooleanField(null=False, default=True)
    rating = models.DecimalField(null=False, default=5.0, max_digits=3, decimal_places=2)

    def __str__(self):
        return str(self.regd_no)

    def clean(self):
        super().clean()
        if not self.is_hosteller and hasattr(self, 'roomdetail'):
            raise ValidationError("Day scholars cannot be alloted a room.")

    def block(self):
        return self.roomdetail.block

    def calculate_rating(self, outingInOutObj):
        outingInOutObjs = OutingInOutTimes.objects.filter(outing__student=self).filter(inTime__isnull=False)
        invalid = int((5-self.rating)*len(outingInOutObjs))
        if outingInOutObj.outing.type == 'Local':
            if outingInOutObj.outing.student.gender == 'Male' and outingInOutObj.inTime != None:
                if (outingInOutObj.inTime.hour*100 + outingInOutObj.inTime.minute) > 2115 :
                    invalid+=1.5
                elif ((outingInOutObj.inTime - outingInOutObj.outing.toTime).total_seconds()/60) > 60.0:
                    invalid+=1
                elif ((outingInOutObj.inTime - outingInOutObj.outing.toTime).total_seconds()/60) > 15.0:
                    invalid+=0.5
            elif outingInOutObj.outing.student.gender == 'Female' and outingInOutObj.inTime != None:
                if (outingInOutObj.inTime.hour*100 + outingInOutObj.inTime.minute) > 2045 :
                    invalid+=1.5
                elif ((outingInOutObj.inTime - outingInOutObj.outing.toTime).total_seconds()/60) > 60.0:
                    invalid+=1
                elif ((outingInOutObj.inTime - outingInOutObj.outing.toTime).total_seconds()/60) > 15.0:
                    invalid+=0.5
        else:
            if outingInOutObj.inTime != None and ((outingInOutObj.inTime - outingInOutObj.outing.toDate).total_seconds()/3600) > 24:
                invalid+=2
            elif outingInOutObj.inTime != None and ((outingInOutObj.inTime - outingInOutObj.outing.toDate).total_seconds()/3600) > 12:
                invalid+=1.5
            elif outingInOutObj.inTime != None and ((outingInOutObj.inTime - outingInOutObj.outing.toDate).total_seconds()/3600) > 6:
                invalid+=1
            elif outingInOutObj.inTime != None and ((outingInOutObj.inTime - outingInOutObj.outing.toDate).total_seconds()/3600) > 1.5:
                invalid+=0.5    
        if len(outingInOutObjs)!=0:
            rating = 5-(invalid/(len(outingInOutObjs)+1))
        elif (len(outingInOutObjs)-invalid) < 0:
            rating = 0
        else:
            rating = 5
        return rating


class Official(models.Model):
    EMP=(
        ('Caretaker','Caretaker'),
        ('Warden','Warden'),
        ('Deputy Chief-Warden', 'Deputy Chief-Warden'),
        ('Chief-Warden','Chief-Warden'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    account_email = models.EmailField(unique=True, null=False)
    emp_id = models.CharField(unique=True,null=False, max_length=20)
    name = models.CharField(max_length=100)
    designation = models.CharField(max_length=20,choices=EMP)
    phone = models.CharField(max_length=10, null=False, validators=[numeric_only])
    email = models.EmailField(null=True, blank=True)
    block = models.ForeignKey('institute.Block', on_delete=models.SET_NULL, null=True, blank=True)

    def is_chief(self):
        return (self.designation == 'Deputy Chief-Warden' or self.designation == 'Chief-Warden')
    
    def is_caretaker(self):
        return (self.designation == 'Caretaker')

    def is_warden(self):
        return self.designation == 'Warden'

    def clean(self):
        if self.is_chief() and self.block != None:
            raise ValidationError('Chief Warden and Deputy Chief Warden cannot be assigned a block.')
    
    def related_outings(self):
        if self.is_warden():
            return Outing.objects.filter(student__in=self.block.students(), permission__in=['Processing', 'Processing Extension']).\
                filter(toDate__gt=timezone.now()).exclude(status='Closed')
        elif self.is_caretaker():
            return Outing.objects.filter(student__in=self.block.students(), permission__in=['Pending', 'Pending Extension']).\
                filter(toDate__gt=timezone.now()).exclude(status='Closed')
        else:
            raise ValidationError('You are not authorized to view outings.')

    def related_complaints(self, pending=True):
        if self.is_chief():
            if pending:
                return complaints.models.Complaint.objects.filter(status__in=['Registered', 'Processing']) # | complaints.models.Complaint.objects.filter(status='Processing')
            else:
                return complaints.models.Complaint.objects.all()
        else:
            students = self.block.students()
            users = students.values_list('user', flat=True)
            if pending:
                return complaints.models.Complaint.objects.filter(user__in=users, status__in=['Registered', 'Processing']) | self.user.complaint_set.filter(status__in=['Registered', 'Processing'])
            else:
                return complaints.models.Complaint.objects.filter(user__in=users) | self.user.complaint_set.all()

    def related_medical_issues(self, pending=True):
        if self.is_chief():
            if pending:
                return complaints.models.MedicalIssue.objects.filter(status='Registered')
            else:
                return complaints.models.MedicalIssue.objects.all()
        else:
            students = self.block.students()
            users = students.values_list('user', flat=True)
            if pending:
                return complaints.models.MedicalIssue.objects.filter(user__in=users, status='Registered') | self.user.medicalissue_set.filter(status='Registered')
            else:
                return complaints.models.MedicalIssue.objects.filter(user__in=users) | self.user.medicalissue_set.all()
                

    def __str__(self):
        return str(self.emp_id)


class Block(models.Model):
    OPTION=(
          ('1S','One student per Room'),
          ('2S','Two students per Room'),
          ('4S','Four students per Room'),
     )

    GENDER=(
        ('Male','Male'),
        ('Female','Female'),
     )

    block_id = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=50,null=False)
    room_type = models.CharField(max_length=2,choices=OPTION)
    gender = models.CharField(max_length=7,choices=GENDER)
    floor_count = models.IntegerField(null=False, verbose_name="No. of Floors")
    capacity = models.IntegerField(null=False)

    def __str__(self):
        return self.name

    def short_name(self):
        return self.name.split()[0]

    def available_floors(self):
        return FLOOR_OPTIONS[:self.floor_count]

    def per_room_capacity(self):
        import re
        # Regex to find room_capacity from room_type
        return int(re.search(r'\d+', self.room_type).group())

    def student_capacity(self):
        if self.room_type == '4S':   return self.capacity*4
        elif self.room_type == '2S': return self.capacity*2
        elif self.room_type == '1S': return self.capacity

    def roomdetails(self):
        return self.roomdetail_set.all()

    def students(self):
        student_rooms = self.roomdetail_set.all()
        student_ids = student_rooms.values_list('student', flat=True)
        return Student.objects.filter(pk__in=student_ids)

    def caretaker(self):
        return self.official_set.filter(designation='Caretaker').first()

    def warden(self):
        return self.official_set.filter(designation='Warden').first()