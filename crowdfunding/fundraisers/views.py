from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Fundraiser, Pledge
from .serializers import FundraiserSerializer, PledgeSerializer, FundraiserDetailSerializer
from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly

class FundraiserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        fundraisers = Fundraiser.objects.all()
        
        search = request.query_params.get("search")
        if search:
            fundraisers = fundraisers.filter(
                title__icontains=search
            ) | fundraisers.filter(
                description__icontains=search
            )

        serializer = FundraiserSerializer(fundraisers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FundraiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(
                serializer.data,
            status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

class FundraiserDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    ]

    def get_object(self, pk):
        try:
            fundraiser = Fundraiser.objects.get(pk=pk)
            self.check_object_permissions(self.request, fundraiser)
            return fundraiser
        except Fundraiser.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        fundraiser = self.get_object(pk)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)
    
    def put(self, request, pk):
        fundraiser = self.get_object(pk)
        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        fundraiser = self.get_object(pk)
        fundraiser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        pledges = Pledge.objects.all()
        
        search = request.query_params.get("search")
        if search:
            pledges = pledges.filter(
                comment__icontains=search
                )
        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        if serializer.is_valid():
            fundraiser = serializer.validated_data["fundraiser"]
            
            if fundraiser.owner == request.user:
                return Response(
                    {"detail": "You cannot pledge to your own fundraiser."},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
            if not fundraiser.is_open:
                return Response(
                    {"detail": "This fundraiser is closed."},
                    status=status.HTTP_400_BAD_REQUEST
                    )
            
            serializer.save(supporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PledgeDetail(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        IsSupporterOrReadOnly
    ]

    def get_object(self, pk):
        try:
            pledge = Pledge.objects.get(pk=pk)
            self.check_object_permissions(self.request, pledge)
            return pledge
        except Pledge.DoesNotExist:
            raise Http404
    
    def get(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)
    
    def put(self, request, pk):
        pledge = self.get_object(pk)
        serializer = PledgeSerializer(
            instance= pledge,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        pledge = self.get_object(pk)
        pledge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)