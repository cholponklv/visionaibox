from rest_framework.exceptions import ValidationError, NotFound

ACTION_MAP = {
    'get': 'list',
    'post': 'create',
    'put': 'update',
    'patch': 'partial_update',
    'delete': 'destroy',
    'options': 'metadata',

}


class ActionSerializerClassMixin:
    action_serializer_class = {}

    def set_action(self):
        if not hasattr(self, 'action'):
            if self.request.method.lower() == 'get' and self.kwargs.get('pk'):
                self.action = 'retrieve'
            else:
                self.action = ACTION_MAP[self.request.method.lower()]

    def get_serializer_class(self):
        self.set_action()
        if self.action_serializer_class and self.action in self.action_serializer_class:
            return self.action_serializer_class[self.action]
        return super().get_serializer_class()


class ActionPermissionClassMixin:
    action_permission_classes = {}

    def set_action(self):
        if not hasattr(self, 'action'):
            if self.request.method.lower() == 'get' and self.kwargs.get('pk'):
                self.action = 'retrieve'
            else:
                self.action = ACTION_MAP[self.request.method.lower()]

    def get_permissions(self):
        self.set_action()
        if self.action_permission_classes and self.action in self.action_permission_classes:
            return [permission() for permission in self.action_permission_classes[self.action]]
        return super().get_permissions()


class NestedViewSetMixin(object):
    unique_together_field = None
    parent = None
    is_set_user = False

    def get_model_lookup(self):
        return self.lookup[:-2] + 'id'

    def get_model(self):
        return self.get_queryset().model

    def get_parent(self):
        model = self.get_model()
        model_lookup = self.get_model_lookup()
        assert hasattr(model, model_lookup), f'Model {model.__name__} has no attribute ' \
                                             f'{model_lookup}, viewset: {self.__class__.__name__}'
        related_field = model._meta.get_field(model_lookup)
        parent_model = related_field.related_model
        try:
            parent = parent_model.objects.get(id=self.kwargs[self.lookup])
        except parent_model.DoesNotExist:
            raise NotFound()

        return parent

    def filter_queryset(self, queryset):
        model_lookup = self.get_model_lookup()
        parent = self.get_parent()
        queryset = queryset.filter(**{model_lookup: parent.id})
        return super().filter_queryset(queryset)

    def __check_existence(self, validated_data):
        model = self.get_model()
        parent = self.parent
        model_look_up = self.get_model_lookup()
        query = model.objects.filter(**{model_look_up: parent.id,
                                        self.unique_together_field + '_id': validated_data[self.unique_together_field]})
        if query.exists():
            raise ValidationError({self.unique_together_field: 'already exist'}, 'unique')

    def perform_create(self, serializer):
        self.parent = self.get_parent()
        if self.unique_together_field:
            self.__check_existence(serializer.validated_data)
        if self.is_set_user:
            serializer.save(created_by=self.request.user, **{self.get_model_lookup(): self.parent.id})
        else:
            serializer.save(**{self.get_model_lookup(): self.parent.id})
