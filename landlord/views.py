from django.shortcuts import render

# Create your views here.
class LandlordView:
    def get(self, request):
        # Logic to handle GET request\
        return render(request, 'landlord/landlord.html')
        