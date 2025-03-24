from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager

class HRManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not password:
            raise ValueError('The Password field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

    
class HR(AbstractUser):
    GENDER = (
        ('Male', 'Male'),
        ('Female', 'Female'),
    )
    email = models.CharField(max_length=200, unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    username=None
    date_of_birth = models.DateField(null=True, blank=True)
    contact_number = models.CharField(max_length=15, null=True, blank=True)
    gender = models.CharField(max_length=100, choices=GENDER, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    objects = HRManager()
   
    def __str__(self):
        return self.email


class DomainInterest(models.Model):
    domain_name = models.CharField(max_length=255, unique=True)
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="modified_domains")
    ModifyDateTime = models.DateTimeField(auto_now=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="deleted_domains", blank=True)
    DeletedDateTime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.domain_name
    
class Qualification(models.Model):
    qualification_name = models.CharField(max_length=255, unique=True)
    qualification_desc = models.TextField(blank=True, null=True)
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="modified_qualification")
    ModifyDateTime = models.DateTimeField(auto_now=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="deleted_qualification", blank=True)
    DeletedDateTime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.qualification_name

    
class Candidate(models.Model):
    EXPERIENCE_CHOICES = (
        (True, 'Yes'),
        (False, 'No'),
    )
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=13)
    resume = models.FileField(upload_to="resume/")
    is_experienced = models.BooleanField(choices=EXPERIENCE_CHOICES, default=False)
    date_of_birth = models.DateField()
    father_name = models.CharField(max_length=255)
    address = models.TextField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    gap = models.IntegerField(default=0, null=True, blank=True)
    last_company = models.CharField(max_length=255, null=True, blank=True)
    exp_years = models.IntegerField(default=0, null=True, blank=True)
    domain_of_interest = models.ForeignKey(DomainInterest, related_name='candidates_interest',on_delete=models.CASCADE)
    qualification = models.ForeignKey(Qualification, related_name='candidates_qualification',on_delete=models.CASCADE )
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True, related_name='modifier')
    ModifyDateTime = models.DateTimeField(null=True, blank=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True, related_name='delete_record')
    DeletedDateTime = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class TechArea(models.Model):
    tech_specification = models.CharField(max_length=255, unique=True)
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="modified_tech")
    ModifyDateTime = models.DateTimeField(auto_now=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="deleted_tech", blank=True)
    DeletedDateTime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.tech_specification



class CandidateTechArea(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="candidate_tech_area_candidate" )
    tech_area = models.ForeignKey(TechArea, on_delete=models.CASCADE, related_name="candidate_tech_area_tech_area")
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="modified_candidate_tech")
    ModifyDateTime = models.DateTimeField(auto_now=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, related_name="deleted_candidate_tech", blank=True)
    DeletedDateTime = models.DateTimeField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.candidate.name} - {self.tech_area.tech_specification}"
    
class Interview(models.Model):
    STAGE_CHOICES=(
        ('Screening', 'Screening'),
        ('Technical', 'Technical'),
        ('HR', 'HR'),
        ('Final', 'Final')
    )
    MODE_CHOICES=( ('Online', 'Online'),
        ('Offline', 'Offline'))
    STATUS_CHOICES=(  ('Scheduled', 'Scheduled'),
        ('Rescheduled', 'Rescheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'))
    candidate_profile = models.ForeignKey(Candidate, related_name='interview_candidate',on_delete=models.CASCADE )
    ModifiedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True, related_name='modified_interviews')
    ModifyDateTime = models.DateTimeField(null=True, blank=True)
    DeletedByUserid = models.ForeignKey(HR, on_delete=models.SET_NULL, null=True, blank=True, related_name='deleted_interviews')
    DeletedDateTime = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)    
    joining_date = models.DateField(null=True, blank=True)
    interview_date = models.DateField()
    interview_time = models.TimeField()
    interviewers = models.TextField(null=True, blank=True) 
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES)
    mode = models.CharField(max_length=50, choices=MODE_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,null=True, blank=True)
    remark = models.TextField(blank=True, null=True)
    meeting_link = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"Interview for {self.candidate_profile.name} on {self.interview_date} at {self.interview_time}"