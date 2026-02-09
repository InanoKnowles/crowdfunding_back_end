from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse
from django.utils import timezone
from .models import Fundraiser, Pledge, Comment
from .serializers import (
    FundraiserSerializer,
    FundraiserDetailSerializer,
    PledgeSerializer,
    CommentSerializer,
)
from .permissions import IsOwnerOrReadOnly, IsAuthorOrReadOnly

class ContactView(APIView):
    def post(self, request):
        return Response(
            {"detail": "Message received"},
            status=status.HTTP_200_OK
        )

class FundraiserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        fundraisers = Fundraiser.objects.all()
        serializer = FundraiserSerializer(fundraisers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = FundraiserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FundraiserDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_object(self, pk):
        try:
            fundraiser = Fundraiser.objects.get(pk=pk)
            self.check_object_permissions(self.request, fundraiser)
            return fundraiser
        except Fundraiser.DoesNotExist:
            return None

    def get(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)

    def put(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FundraiserDetailSerializer(
            instance=fundraiser, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        fundraiser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = PledgeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fundraiser = serializer.validated_data["fundraiser"]
        amount = serializer.validated_data["amount"]

        if not fundraiser.is_accepting_pledges():
            return Response({"detail": "Fundraiser is closed."}, status=status.HTTP_400_BAD_REQUEST)

        if fundraiser.owner == request.user:
            return Response({"detail": "Cannot pledge to own fundraiser."}, status=status.HTTP_400_BAD_REQUEST)

        if fundraiser.total_pledged() + amount > fundraiser.goal:
            return Response({"detail": "Goal amount exceeded."}, status=status.HTTP_400_BAD_REQUEST)

        pledge = serializer.save(supporter=request.user)
        fundraiser.refresh_open_status(save=True)

        return Response(PledgeSerializer(pledge).data, status=status.HTTP_201_CREATED)


class PledgeDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_object(self, pk):
        try:
            return Pledge.objects.get(pk=pk)
        except Pledge.DoesNotExist:
            return None

    def get(self, request, pk):
        pledge = self.get_object(pk)
        if pledge is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)

    def put(self, request, pk):
        return Response(
            {"detail": "Pledges cannot be updated."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def delete(self, request, pk):
        return Response(
            {"detail": "Pledges cannot be deleted."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class CommentList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        comments = Comment.objects.all()
        fundraiser_id = request.query_params.get("fundraiser")
        if fundraiser_id:
            comments = comments.filter(fundraiser_id=fundraiser_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentDetail(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def get_object(self, pk):
        try:
            comment = Comment.objects.get(pk=pk)
            self.check_object_permissions(self.request, comment)
            return comment
        except Comment.DoesNotExist:
            return None

    def get(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(instance=comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def custom_404(request, exception):
    return JsonResponse({"detail": "Not found."}, status=404)
