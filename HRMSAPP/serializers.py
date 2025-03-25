from rest_framework import serializers
from HRMSAPP.models import *

class HRSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = HR
        fields = '__all__'
        extra_kwargs = {
            'email': {'required': True},
            'password': {'required': True, 'write_only': True},
            'first_name':{'required':True},
            'last_name':{'required':True},
        }

    def create(self, validated_data):
            user = HR.objects.create(
                email=validated_data['email'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                date_of_birth=validated_data.get('date_of_birth'),
                contact_number=validated_data.get('contact_number'),
                gender=validated_data.get('gender'),
                address=validated_data.get('address'),
            )
            user.set_password(validated_data['password']) 
            user.save()
            return user
    
class DomainInterestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainInterest
        fields = '__all__'

    
class QualificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Qualification
        fields = '__all__'

class InterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interview
        fields = '__all__'
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("is_put", True):  
            for field in self.fields:
                self.fields[field].required = False 

class CandidateTechAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = CandidateTechArea
        fields = '__all__'


class TechAreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechArea
        fields = '__all__'

class CandidateSerializer(serializers.ModelSerializer):
    tech_areas = serializers.SerializerMethodField()
    doamin=serializers.CharField(source="domain_of_interest.domain_name",read_only=True)
    interviews = InterviewSerializer(source="interview_candidate", many=True, read_only=True)
    qualification_name=serializers.CharField(source="qualification.qualification_name",read_only=True)
    qualification_desc=serializers.CharField(source="qualification.qualification_desc",read_only=True)
    qualification_id=serializers.CharField(source="qualification.id",read_only=True)

    class Meta:
        model = Candidate
        fields = '__all__'

    def get_tech_areas(self, obj):
       
        tech_areas = TechArea.objects.filter(candidate_tech_area_tech_area__candidate=obj).distinct()
        return TechAreaSerializer(tech_areas, many=True).data

class InternshipSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Internship
        fields = '__all__'
    
    candidate_profile = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.filter(is_selected=True) )


    def validate(self, data):
        offered_date = data.get('approximate_offered_joining_date')
        actual_date = data.get('actual_joining_date')

        if actual_date and actual_date < offered_date:
            raise serializers.ValidationError("Actual joining date cannot be before the offered joining date.")
        return data

class SelectionAndJoiningSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = SelectionAndJoining
        fields = '__all__'
    
    Experienced_candidate = serializers.PrimaryKeyRelatedField(queryset=Candidate.objects.filter(is_selected=True))

    Intern_candidate = serializers.PrimaryKeyRelatedField(queryset=Internship.objects.filter(candidate_profile__is_selected=True, completed_internship=True))

    def validate(self, data):
        offered_date = data.get('offered_joining_date')
        joining_date = data.get('joining_date')

        if not data.get('Experienced_candidate') and not data.get('Intern_candidate'):
            raise serializers.ValidationError("Either 'Experienced_candidate' or 'Intern_candidate' must be selected.")
        
        if joining_date and joining_date < offered_date:
            raise serializers.ValidationError("Joining date cannot be before the offered joining date.")
        return data