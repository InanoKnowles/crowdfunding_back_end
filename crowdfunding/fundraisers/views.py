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

        is_open = request.query_params.get("is_open")
        if is_open is not None:
            fundraisers = fundraisers.filter(is_open=(is_open.lower() == "true"))

        goal_lte = request.query_params.get("goal_lte")
        if goal_lte:
            fundraisers = fundraisers.filter(goal__lte=int(goal_lte))

        goal_gte = request.query_params.get("goal_gte")
        if goal_gte:
            fundraisers = fundraisers.filter(goal__gte=int(goal_gte))

        owner = request.query_params.get("owner")
        if owner:
            fundraisers = fundraisers.filter(owner__id=int(owner))

        has_deadline = request.query_params.get("has_deadline")
        if has_deadline is not None:
            if has_deadline.lower() == "true":
                fundraisers = fundraisers.exclude(deadline=None)
            else:
                fundraisers = fundraisers.filter(deadline=None)
        
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

        fundraiser_id = request.query_params.get("fundraiser")
        if fundraiser_id:
            pledges = pledges.filter(fundraiser__id=int(fundraiser_id))

        supporter_id = request.query_params.get("supporter")
        if supporter_id:
            pledges = pledges.filter(supporter__id=int(supporter_id))

        anonymous = request.query_params.get("anonymous")
        if anonymous is not None:
            pledges = pledges.filter(anonymous=(anonymous.lower() == "true"))

        amount_lte = request.query_params.get("amount_lte")
        if amount_lte:
            pledges = pledges.filter(amount__lte=int(amount_lte))

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
        
        author_id = request.query_params.get("author")
        if author_id:
            comments = comments.filter(author__id=int(author_id))

        anonymous = request.query_params.get("anonymous")
        if anonymous is not None:
            comments = comments.filter(anonymous=(anonymous.lower() == "true"))

        search = request.query_params.get("search")
        if search:
            comments = comments.filter(content__icontains=search)

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