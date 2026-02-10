from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.http import JsonResponse
from django.utils import timezone
from .models import Fundraiser, Pledge, Comment
from .serializers import FundraiserSerializer, FundraiserDetailSerializer, PledgeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly, IsAuthorOrReadOnly


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
            fundraisers = fundraisers.filter(title__icontains=search) | fundraisers.filter(description__icontains=search)

        serializer = FundraiserSerializer(fundraisers, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        serializer = FundraiserSerializer(data=request.data, context={"request": request})
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
        serializer = FundraiserDetailSerializer(fundraiser, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        fundraiser = self.get_object(pk)
        if fundraiser is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FundraiserDetailSerializer(instance=fundraiser, data=request.data, partial=True, context={"request": request})
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

    def get(self, request):
        pledges = Pledge.objects.all()

        fundraiser_id = request.query_params.get("fundraiser")
        if fundraiser_id:
            pledges = pledges.filter(fundraiser__id=int(fundraiser_id))

        supporter_id = request.query_params.get("supporter")
        if supporter_id:
            pledges = pledges.filter(supporter__id=int(supporter_id))

        mine = request.query_params.get("mine")
        if mine and mine.lower() == "true":
            if not request.user.is_authenticated:
                return Response({"detail": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
            pledges = pledges.filter(supporter=request.user)

        anonymous = request.query_params.get("anonymous")
        if anonymous is not None:
            pledges = pledges.filter(anonymous=(anonymous.lower() == "true"))

        amount_lte = request.query_params.get("amount_lte")
        if amount_lte:
            pledges = pledges.filter(amount__lte=int(amount_lte))

        search = request.query_params.get("search")
        if search:
            pledges = pledges.filter(comment__icontains=search)

        serializer = PledgeSerializer(pledges, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "You must be logged in to make a pledge."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = PledgeSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        fundraiser = serializer.validated_data["fundraiser"]
        amount = serializer.validated_data["amount"]

        if fundraiser.owner == request.user:
            return Response({"detail": "You cannot pledge to your own fundraiser."}, status=status.HTTP_400_BAD_REQUEST)

        if fundraiser.deadline and timezone.now() >= fundraiser.deadline:
            fundraiser.is_open = False
            fundraiser.save(update_fields=["is_open"])
            return Response({"detail": "This fundraiser has reached its deadline and is now closed."}, status=status.HTTP_400_BAD_REQUEST)

        total_pledged = fundraiser.total_pledged()

        if total_pledged >= fundraiser.goal:
            fundraiser.is_open = False
            fundraiser.save(update_fields=["is_open"])
            return Response({"detail": "This fundraiser has already reached its target and is now closed."}, status=status.HTTP_400_BAD_REQUEST)

        if total_pledged + amount > fundraiser.goal:
            return Response({"detail": "This fundraiser only needs the remaining target amount."}, status=status.HTTP_400_BAD_REQUEST)

        pledge = serializer.save(supporter=request.user)

        if fundraiser.total_pledged() >= fundraiser.goal:
            fundraiser.is_open = False
            fundraiser.save(update_fields=["is_open"])

        return Response(PledgeSerializer(pledge, context={"request": request}).data, status=status.HTTP_201_CREATED)


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
        return Response(PledgeSerializer(pledge, context={"request": request}).data)

    def put(self, request, pk):
        return Response({"detail": "Pledges cannot be updated once made."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def delete(self, request, pk):
        return Response({"detail": "Pledges cannot be deleted once made."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


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

        serializer = CommentSerializer(comments, many=True, context={"request": request})
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "You must be logged in to comment."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = CommentSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            fundraiser = serializer.validated_data["fundraiser"]
            is_anon = Pledge.objects.filter(fundraiser=fundraiser, supporter=request.user, anonymous=True).exists()
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
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer(comment, context={"request": request})
        return Response(serializer.data)

    def put(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = CommentSerializer(instance=comment, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save(anonymous=comment.anonymous, author=comment.author, fundraiser=comment.fundraiser)
            return Response(serializer.data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        comment = self.get_object(pk)
        if comment is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ContactView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        name = (request.data.get("name") or "").strip()
        email = (request.data.get("email") or "").strip()
        subject = (request.data.get("subject") or "").strip()
        message = (request.data.get("message") or "").strip()

        if not name or not email or not subject or not message:
            return Response({"detail": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Message received."}, status=status.HTTP_201_CREATED)


def custom_404(request, exception):
    return JsonResponse({"detail": "Alas, the requested resource cannot be found."}, status=404)
