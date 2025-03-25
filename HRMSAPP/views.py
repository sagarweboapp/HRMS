from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.hashers import check_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import *
from django.utils import timezone
from django.db.models import Q

class HRSignupView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = HRSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "HR registered successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class HRLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = HR.objects.get(email=email)
        except HR.DoesNotExist:
            return Response({"response": "No User exists"}, status=status.HTTP_401_UNAUTHORIZED)

        if not check_password(password, user.password):
            return Response({"response": "Incorrect Password"}, status=status.HTTP_401_UNAUTHORIZED)

        if user.is_deleted:
            return Response({'response': 'No User Found'}, status=status.HTTP_204_NO_CONTENT)
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        return Response({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'email': user.email ,
            'first_name': user.first_name,
            'last_name': user.last_name
        }, status=status.HTTP_200_OK)     

class HRLogoutView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
           
            if not refresh_token:
                return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
            token = RefreshToken(refresh_token)
            
            token.blacklist()  

            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class CandidateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        candidates = Candidate.objects.filter(is_deleted=False)
        serializer = CandidateSerializer(candidates, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        existing_candidate = Candidate.objects.filter(email=request.data.get('email'),is_deleted=True).first()

        if existing_candidate:
            existing_candidate.is_deleted = False
            existing_candidate.DeletedDateTime = None  
            existing_candidate.ModifiedByUserid = request.user
            existing_candidate.ModifyDateTime = timezone.now()
            existing_candidate.save()
            return Response({"message": "Candidate restored successfully"}, status=status.HTTP_200_OK)
        serializer = CandidateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "Candidate added successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CandidateGetUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, pk):
        try:
            return Candidate.objects.get(pk=pk, is_deleted=False)
        except Candidate.DoesNotExist:
            return None

    def get(self, request, pk):
        candidate = self.get_object(pk)
        if candidate:
            serializer = CandidateSerializer(candidate)
            return Response(serializer.data)
        return Response({"detail": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        candidate = self.get_object(pk)
        if candidate:
            serializer = CandidateSerializer(candidate, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        candidate = self.get_object(pk)
        if candidate:
            candidate.is_deleted = True
            candidate.DeletedByUserid=request.user
            candidate.DeletedDateTime=timezone.now()
            candidate.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Candidate not found"}, status=status.HTTP_404_NOT_FOUND)



class TechAreaCreateGetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        tech_areas = TechArea.objects.filter(is_deleted=False)
        serializer = TechAreaSerializer(tech_areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        existing_tech = TechArea.objects.filter(tech_specification=request.data.get('tech_specification'),is_deleted=True).first()

        if existing_tech:
            existing_tech.is_deleted = False
            existing_tech.DeletedDateTime = None  
            existing_tech.ModifiedByUserid = request.user
            existing_tech.ModifyDateTime = timezone.now()
            existing_tech.save()
            return Response({"message": "TechArea restored successfully"}, status=status.HTTP_200_OK)
        serializer = TechAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "TechArea created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TechAreaUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return TechArea.objects.get(pk=pk, is_deleted=False)
        except TechArea.DoesNotExist:
            return None

    def get(self, request, pk):
        tech_area = self.get_object(pk)
        if tech_area:
            serializer = TechAreaSerializer(tech_area)
            return Response(serializer.data)
        return Response({"detail": "TechArea not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        tech_area = self.get_object(pk)
        if tech_area:
            serializer = TechAreaSerializer(tech_area, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response({"message": "TechArea updated successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "TechArea not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        tech_area = self.get_object(pk)
        if tech_area:
            tech_area.is_deleted = True
            tech_area.DeletedByUserid=request.user
            tech_area.DeletedDateTime=timezone.now()
            tech_area.save()
            return Response({"message": "TechArea deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "TechArea not found"}, status=status.HTTP_404_NOT_FOUND)

class DomainInterestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        domain_areas = DomainInterest.objects.filter(is_deleted=False)
        serializer = DomainInterestSerializer(domain_areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        existing_domain = DomainInterest.objects.filter(domain_name=request.data.get('domain_name'),is_deleted=True).first()

        if existing_domain:
           
            existing_domain.is_deleted = False
            existing_domain.DeletedDateTime = None 
            existing_domain.ModifiedByUserid = request.user
            existing_domain.ModifyDateTime = timezone.now()
            existing_domain.save()
            return Response({"message": "Domain interest restored successfully"}, status=status.HTTP_200_OK)
        
        serializer = DomainInterestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "Doamin Area created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class DomainInterestUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return DomainInterest.objects.get(pk=pk, is_deleted=False)
        except DomainInterest.DoesNotExist:
            return None

    def get(self, request, pk):
        domain_area = self.get_object(pk)
        if domain_area:
            serializer = TechAreaSerializer(domain_area)
            return Response(serializer.data)
        return Response({"detail": "Domain not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        domain_area = self.get_object(pk)
        if domain_area:
            serializer = DomainInterestSerializer(domain_area, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response({"message": "Domain updated successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Domain not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        domain_area = self.get_object(pk)
        if domain_area:
            domain_area.is_deleted = True
            domain_area.DeletedByUserid=request.user
            domain_area.DeletedDateTime=timezone.now()
            domain_area.save()
            return Response({"message": "Domain deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Domain not found"}, status=status.HTTP_404_NOT_FOUND)

class QualificationCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qualifications = Qualification.objects.filter(is_deleted=False)
        serializer = QualificationSerializer(qualifications, many=True)
        return Response(serializer.data)

    def post(self, request):

        existing_qualification = Qualification.objects.filter(qualification_name=request.data.get('qualification_name'),is_deleted=True).first()

        if existing_qualification:
     
            existing_qualification.is_deleted = False
            existing_qualification.DeletedDateTime = None 
            existing_qualification.ModifiedByUserid = request.user
            existing_qualification.ModifyDateTime = timezone.now()
            existing_qualification.save()
            return Response({"message": "Qualification restored successfully"}, status=status.HTTP_200_OK)
        

        serializer = QualificationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "Qualification created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QualificationUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Qualification.objects.get(pk=pk, is_deleted=False)
        except Qualification.DoesNotExist:
            return None

    def get(self, request, pk):
        qualification = self.get_object(pk)
        if qualification:
            serializer = QualificationSerializer(qualification)
            return Response(serializer.data)
        return Response({"detail": "Qualification not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        qualification = self.get_object(pk)
        if qualification:
            serializer = QualificationSerializer(qualification, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response({"message": "Qualification updated successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Qualification not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        qualification = self.get_object(pk)
        if qualification:
            qualification.is_deleted = True
            qualification.DeletedByUserid=request.user
            qualification.DeletedDateTime=timezone.now()
            qualification.save()
            return Response({"message": "Qualification deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Qualification not found"}, status=status.HTTP_404_NOT_FOUND)

class CandidateTechAreaView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        candidate_tech_areas = CandidateTechArea.objects.filter(is_deleted=False)
        serializer = CandidateTechAreaSerializer(candidate_tech_areas, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CandidateTechAreaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "CandidateTechArea created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CandidateTechAreaUpdateDeleteView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return CandidateTechArea.objects.get(pk=pk, is_deleted=False)
        except CandidateTechArea.DoesNotExist:
            return None

    def get(self, request, pk):
        candidate_tech_area = self.get_object(pk)
        if candidate_tech_area:
            serializer = CandidateTechAreaSerializer(candidate_tech_area)
            return Response(serializer.data)
        return Response({"detail": "CandidateTechArea not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        candidate_tech_area = self.get_object(pk)
        if candidate_tech_area:
            serializer = CandidateTechAreaSerializer(candidate_tech_area, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response({"message": "CandidateTechArea updated successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "CandidateTechArea not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        candidate_tech_area = self.get_object(pk)
        if candidate_tech_area:
            candidate_tech_area.is_deleted = True
            candidate_tech_area.DeletedByUserid=request.user
            candidate_tech_area.DeletedDateTime=timezone.now()
            candidate_tech_area.save()
            return Response({"message": "CandidateTechArea deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "CandidateTechArea not found"}, status=status.HTTP_404_NOT_FOUND)
    
class ScheduleInterviewCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        schedules = Interview.objects.filter(is_deleted=False)
        serializer = InterviewSerializer(schedules, many=True)
        return Response(serializer.data)

    def post(self, request):

        existing_interview = Interview.objects.filter(candidate_profile=request.data.get('candidate_profile'),interview_date=request.data.get('interview_date'),interview_time=request.data.get('interview_time'),is_deleted=True).first()

        if existing_interview:
     
            existing_interview.is_deleted = False
            existing_interview.DeletedDateTime = None
            existing_interview.ModifiedByUserid = request.user
            existing_interview.ModifyDateTime = timezone.now()
            existing_interview.save()
            return Response({"message": "Interview restored successfully"}, status=status.HTTP_200_OK)
        

        serializer = InterviewSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "Interview created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InterviewUpdateDelete(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Interview.objects.get(pk=pk, is_deleted=False)
        except Interview.DoesNotExist:
            return None

    def get(self, request, pk):
        schedule = self.get_object(pk)
        if schedule:
            serializer = InterviewSerializer(schedule)
            return Response(serializer.data)
        return Response({"detail": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        schedule = self.get_object(pk)
        if schedule:
            old_date = schedule.interview_date
            old_time = schedule.interview_time
            serializer = InterviewSerializer(schedule, data=request.data)
            if serializer.is_valid():
                new_date = request.data.get("interview_date", old_date)
                new_time = request.data.get("interview_time", old_time)
                if new_date != old_date or new_time != old_time:
                    schedule.status = "Rescheduled"
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response({"message": "Schedule updated successfully"})
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        schedule = self.get_object(pk)
        if schedule:
            schedule.is_deleted = True
            schedule.DeletedByUserid=request.user
            schedule.DeletedDateTime=timezone.now()
            schedule.save()
            return Response({"message": "Schedule deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Schedule not found"}, status=status.HTTP_404_NOT_FOUND)
    
class Search(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        query = request.GET.get("query")
        if not query:
            return Response({"error": "Please enter something to Search"}, status=400)
        results = Candidate.objects.filter(
            Q(name__icontains=query) | 
            Q(mobile__icontains=query) | 
            Q(email__icontains=query) |
            Q(qualification__qualification_name__icontains=query) | 
            Q(domain_of_interest__domain_name__icontains=query) |
            Q(interview_candidate__status__icontains=query) |
            Q(interview_candidate__joining_date__icontains=query)
        ).filter(is_deleted=False).distinct()
        serializer = CandidateSerializer(results, many=True)
        return Response(serializer.data)

class QualificationSearch(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qualification_id = request.GET.get("qualification")
        
        if not qualification_id:
            return Response({"error": "Please select a qualification"}, status=400)

        candidates = Candidate.objects.filter(qualification__id__iexact=qualification_id, is_deleted=False).distinct()
        serializer = CandidateSerializer(candidates, many=True)

        return Response(serializer.data)

class InternshipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        internships = Internship.objects.filter(is_deleted=False,candidate_profile__is_selected=True)
        serializer = InternshipSerializer(internships, many=True)
        return Response(serializer.data)

    def post(self, request):

        existing_internship = Internship.objects.filter(candidate_profile=request.data.get('candidate_profile'),is_deleted=True).first()

        if existing_internship:
     
            existing_internship.is_deleted = False
            existing_internship.DeletedDateTime = None 
            existing_internship.ModifiedByUserid = request.user
            existing_internship.ModifyDateTime = timezone.now()
            existing_internship.save()
            return Response({"message": "Internship restored successfully"}, status=status.HTTP_200_OK)
        

        serializer = InternshipSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "Internship created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InternshipDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Internship.objects.get(pk=pk, is_deleted=False,candidate_profile__is_selected=True)
        except Internship.DoesNotExist:
            return None

    def get(self, request, pk):
        internship = self.get_object(pk)
        if internship:
            serializer = InternshipSerializer(internship)
            return Response(serializer.data)
        return Response({"detail": "Internship not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        internship = self.get_object(pk)
        if internship:
            serializer = InternshipSerializer(internship, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Internship not found"}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        internship = self.get_object(pk)
        if internship:
            internship.is_deleted = True
            internship.DeletedByUserid=request.user
            internship.DeletedDateTime=timezone.now()
            internship.save()
            return Response({"message": "Internship deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Internship not found"}, status=status.HTTP_404_NOT_FOUND)

class SelectionAndJoiningView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        employees = SelectionAndJoining.objects.filter(is_deleted=False,Experienced_candidate__is_selected=True).union(SelectionAndJoining.objects.filter(is_deleted=False,Intern_candidate__completed_internship=True))
        serializer = SelectionAndJoiningSerializer(employees, many=True)
        return Response(serializer.data)

    def post(self, request):

        existing_employees=SelectionAndJoining.objects.filter(Intern_candidate=request.data.get('Intern_candidate'),Experienced_candidate=request.data.get('Experienced_candidate'),is_deleted=True).first()
        if existing_employees:
     
            existing_employees.is_deleted = False
            existing_employees.DeletedDateTime = None 
            existing_employees.ModifiedByUserid = request.user
            existing_employees.ModifyDateTime = timezone.now()
            existing_employees.save()
            return Response({"message": "joining restored successfully"}, status=status.HTTP_200_OK)
        
        serializer = SelectionAndJoiningSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
            return Response({"message": "joining created successfully"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SelectionAndJoiningDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return SelectionAndJoining.objects.get(pk=pk, is_deleted=False,Experienced_candidate__is_selected=True,Intern_candidate__completed_internship=True)
        except SelectionAndJoining.DoesNotExist:
            return None

    def get(self, request, pk):
        joined = self.get_object(pk)
        if joined:
            serializer = SelectionAndJoiningSerializer(joined)
            return Response(serializer.data)
        return Response({"detail": "joining data not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        joined = self.get_object(pk)
        if joined:
            serializer = SelectionAndJoiningSerializer(joined, data=request.data)
            if serializer.is_valid():
                serializer.save(ModifiedByUserid = request.user, ModifyDateTime = timezone.now())
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({"detail": "Joining data not found"}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        joining = self.get_object(pk)
        if joining:
            joining.is_deleted = True
            joining.DeletedByUserid=request.user
            joining.DeletedDateTime=timezone.now()
            joining.save()
            return Response({"message": "Joining data deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": "Joining data not found"}, status=status.HTTP_404_NOT_FOUND)