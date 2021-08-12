from rest_framework import serializers
from .models import Poll, Question, Variant, Answer

from dateutil.parser import parse

class GetPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = (
            'id', 'name', 'description', 'start_date', 'finish_date'
        )

class PostPollSerializer(serializers.ModelSerializer):
    class Meta:
        model = Poll
        fields = (
            'name', 'description', 'start_date', 'finish_date'
        )

    def validate(self, data):
        if data['start_date'] > data['finish_date']:
            raise serializers.ValidationError("Finish date must be after start date!")
        return data

class UpdatePollSerializer(serializers.Serializer):
    field = serializers.CharField()
    value = serializers.CharField()

    def validate_field(self, value):
        if value == "id" or value == "start_date":
            raise serializers.ValidationError("This field cannot be changed in poll")
        return value

    def validate(self, data):
        if data['field'] == 'finish_date':
            try:
                parse(data['value'], fuzzy=False)
            except ValueError:
                raise serializers.ValidationError("This value is not in date format")
        return data

class GetVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = (
            'number', 'text'
        )

class PostVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Variant
        fields = (
            'number', 'question_id', 'text'
        )

    def validate_question_id(self, value):
        try:
            question = Question.objects.get(id=value)
            if question.type == 0:
                raise serializers.ValidationError("Question does not support answers via variants!")
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question does not exists!")
        return value

class UpdateVariantSerializer(serializers.Serializer):
    field = serializers.CharField()
    value = serializers.CharField()

    def validate_field(self, value):
        if value == "number" or value == "question_id" or value == "id":
            raise serializers.ValidationError("This field cannot be changed in variant")
        return value

class GetQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'poll_id', 'id', 'text', 'variants'
        )

    variants = serializers.SerializerMethodField()

    def get_variants(self, obj):
        question_variants = Variant.objects.filter(question_id=obj.id).distinct()
        return GetVariantSerializer(question_variants, many=True).data

class PostQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = (
            'poll_id', 'text', 'type'
        )

    def validate(self, data):
        try:
            Poll.objects.get(id=data['poll_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Poll does not exists!")
        return data

class UpdateQuestionSerializer(serializers.Serializer):
    field = serializers.CharField()
    value = serializers.CharField()

    def validate_field(self, value):
        if value != "text":
            raise serializers.ValidationError("This field cannot be changed in question")
        return value

class PostAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'question_id', 'user_id', 'variants_numbers', 'text'
        )

    def validate(self, data):
        data['variants_number'] = distinct(data['variants_number'])

        try:
            question = Question.objects.get(id=data['question_id'])
        except Question.DoesNotExist:
            raise serializers.ValidationError("Question does not exists!")

        try:
            Answer.objects.get(question_id=data['question_id'],
                               user_id=data['user_id'])
            try:
                if data['user_id']:
                    raise serializers.ValidationError("This person has answered on this question yet!")
            except KeyError:
                pass
        except Answer.DoesNotExist:
            pass

        if question.type == 0:
            try:
                if data['variants_number']:
                    raise serializers.ValidationError("Answer on this question must be only in text!")
            except KeyError:
                pass

            try:
                if data['text']:
                    pass
            except KeyError:
                raise serializers.ValidationError("Answer on this question must include text field!")

        if question.type != 0:
            try:
                if data['text']:
                    raise serializers.ValidationError("Answer on this question cannot contain text field!")
            except KeyError:
                pass

            try:
                if data['variants_number']:
                    if len(data['variants_number']) == 0:
                        raise serializers.ValidationError("There is not any variants in answer")
                    if len(data['variants_number']) != 0:
                        try:
                            variant = Variant.objects.get(number=data['variant_id'][0],
                                                          question_id=data['question_id'])
                        except Variant.DoesNotExist:
                            raise serializers.ValidationError("Variant does not exists!")
                        if variant.question_id != data['question_id']:
                            raise serializers.ValidationError("Question has not this variant!")
                    if len(data['variants_number']) > 1:
                        if question.type != 2:
                            raise serializers.ValidationError("This question cannot contain more then 1 answer!")
                        for variant_id in data['variants_number']:
                            try:
                                variant = Variant.objects.get(number=variant_id,
                                                              question_id=data['question_id'])
                            except Variant.DoesNotExist:
                                raise serializers.ValidationError("Variant does not exists!")
                            if variant.question_id != data['question_id']:
                                raise serializers.ValidationError("Question has not this variant!")
            except KeyError:
                serializers.ValidationError("Answer on this text must include variant")

        return data

class GetUserActivitySerializer(serializers.ModelSerializer):
    poll_id = serializers.SerializerMethodField()
    question_text = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = (
            'poll_id', 'question_id', 'question_text', 'variants_numbers', 'text'
        )

    def get_poll_id(self, obj):
        question = Question.objects.get(id=obj.question_id)
        return question.poll_id

    def get_question_text(self, obj):
        question = Question.objects.get(id=obj.question_id)
        return question.text

def distinct(answer_list):
    unique_answers_list = []

    for answer in answer_list:
        if answer not in unique_answers_list:
            unique_answers_list.append(answer)

    return unique_answers_list