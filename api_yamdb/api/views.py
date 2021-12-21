from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters import rest_framework
from rest_framework import filters, mixins, viewsets
from rest_framework.exceptions import ValidationError

from .filters import TitleFilter
from .permissions import IsAdmin, IsAuthor, IsModerator, IsReadOnly
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, ReviewSerializer, TitleSerializer)

from reviews.models import (Category, Comment, Genre, Review,  # isort:skip
                            Title)


class MixinsViewSet(mixins.DestroyModelMixin,
                    mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    viewsets.GenericViewSet):
    filter_backends = [filters.SearchFilter]
    permission_classes = (IsAdmin | IsReadOnly,)
    search_fields = ('name', 'slug')
    lookup_field = 'slug'


class GenreViewSet(MixinsViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(MixinsViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializer
    permission_classes = (IsAdmin | IsReadOnly,)
    filter_backends = [rest_framework.DjangoFilterBackend]
    filterset_class = TitleFilter


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthor | IsModerator | IsAdmin | IsReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return Review.objects.filter(title=title)

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        if Review.objects.filter(
            author=self.request.user, title=title
        ).exists():
            raise ValidationError('TODO')
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAuthor | IsModerator | IsAdmin | IsReadOnly,)

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        review = get_object_or_404(
            Review, title=title, id=self.kwargs.get('review_id')
        )
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
