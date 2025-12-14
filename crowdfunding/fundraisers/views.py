from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import Http404
from .models import Fundraiser, Pledge, Comment
from .serializers import FundraiserSerializer, FundraiserDetailSerializer, PledgeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsSupporterOrReadOnly, IsAuthorOrReadOnly

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
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FundraiserDetailSerializer(fundraiser)
        return Response(serializer.data)

    def put(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FundraiserDetailSerializer(
            instance=fundraiser,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)

        fundraiser.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PledgeList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request):
        pledges = Pledge.objects.all()

        search = request.query_params.get("search")
        if search:
            pledges = pledges.filter(comment__icontains=search)

        serializer = PledgeSerializer(pledges, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PledgeSerializer(data=request.data)
        if serializer.is_valid():
            fundraiser = serializer.validated_data["fundraiser"]

            if fundraiser.owner == request.user:
                return Response(
                    {"detail": "You cannot pledge to your own fundraiser."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not fundraiser.is_open:
                return Response(
                    {"detail": "This fundraiser is closed to new pledges."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save(supporter=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PledgeSerializer(pledge)
        return Response(serializer.data)

    def put(self, request, pk):
        return Response(
            {"detail": "Pledges cannot be updated once made."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def delete(self, request, pk):
        return Response(
            {"detail": "Pledges cannot be deleted once made."},
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
            fundraiser = serializer.validated_data["fundraiser"]

            is_anon = Pledge.objects.filter(
                fundraiser=fundraiser,
                supporter=request.user,
                anonymous=True
            ).exists()

            serializer.save(author=request.user, anonymous=is_anon)
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
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "oh WHAT?! It was not found. Try again."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(instance=comment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save(anonymous=comment.anonymous, author=comment.author, fundraiser=comment.fundraiser)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "oh WHAT?! It was oh WHAT?! It was not found. Try again. Try again."}, status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def custom_404(request, exception):
    return Response(
        {"detail": "Alas, the requested resource cannot be found."},
        status=status.HTTP_404_NOT_FOUND
    )