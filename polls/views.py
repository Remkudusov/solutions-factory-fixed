from django.shortcuts import render

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .serializers import *
from .models import *

from datetime import datetime

def index(request):
    return render(request, "polls/index.html")

class AdminPollView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, action, poll_id=None, *args, **kwargs):
        if action == "post":
            serializer = PostPollSerializer(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        if poll_id != None:
            if action == "update":
                serializer = UpdatePollSerializer(data=request.data)
                if serializer.is_valid():
                    poll = Poll.objects.get(id=poll_id)
                    setattr(poll, serializer.data['field'], serializer.data['value'])
                    poll.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            if action == "delete":
                Poll.objects.get(id=poll_id).delete()
                data = {
                    'message': 'Poll deleted!'
                }
                return Response(data)
        else:
            data = {
                'message': 'Poll ID required!'
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class AdminQuestionView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, action, question_id=None, *args, **kwargs):
        if action == "post":
            serializer = PostQuestionSerializer(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        if question_id != None:
            if action == "update":
                serializer = UpdateQuestionSerializer(data=request.data)
                if serializer.is_valid():
                    question = Question.objects.get(id=question_id)
                    setattr(question, serializer.data['field'], serializer.data['value'])
                    question.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            if action == "delete":
                Question.objects.get(id=question_id).delete()
                data = {
                    'message': 'Question deleted!'
                }
                return Response(data)
        else:
            data = {
                'message': 'Question ID required!'
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class AdminVariantView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, action, question_id=None, variant_number=None):
        if action == "post":
            serializer = PostVariantSerializer(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors)
        if question_id != None and variant_number != None:
            if action == "update":
                serializer = UpdateVariantSerializer(data=request.data)
                if serializer.is_valid():
                    variant = Variant.objects.get(question_id=question_id, number=variant_number)
                    setattr(variant, serializer.data['field'], serializer.data['value'])
                    variant.save()
                    return Response(serializer.data)
                return Response(serializer.errors)
            if action == "delete":
                Variant.objects.get(question_id=question_id, number=variant_number).delete()
                data = {
                    'message': 'Variant deleted!'
                }
                return Response(data)
        else:
            data = {
                'message': 'Variant number and question ID required!'
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class PollsView(APIView):
    def get(self, request, subject, *args, **kwargs):
        if subject == "polls":
            current_date = datetime.date(datetime.now())
            actual_polls = []
            polls = Poll.objects.all()
            for poll in polls:
                if current_date > poll.start_date and current_date < poll.finish_date:
                    actual_polls.append(poll)
            serializer = GetPollSerializer(actual_polls, many=True)
            return Response(serializer.data)
        elif subject == "questions":
            questions = Question.objects.all()
            serializer = GetQuestionSerializer(questions, many=True)
            return Response(serializer.data)
        else:
            data = {
                'message': 'Subject name required!'
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

class AnswerView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        if user_id != None:
            answers = Answer.objects.filter(user_id=user_id)
            if len(answers) != 0:
                serializer = GetUserActivitySerializer(answers, many=True)
                return Response(serializer.data)
            else:
                data = {
                    'message': 'No answers for this user ID!'
                }
                return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        else:
            data = {
                'message': 'User ID required!'
            }
            return Response(data, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def post(self, request, *args, **kwargs):
        serializer = PostAnswerSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
