from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Note, Product, Order
from .serializers import (
    NoteSerializer,
    RegisterSerializer,
    UserSerializer,
    ProductSerializer,
    OrderSerializer,
)


def _cache_delete_pattern(pattern: str) -> None:
    delete_pattern = getattr(cache, "delete_pattern", None)
    if callable(delete_pattern):
        delete_pattern(pattern)
    else:
        cache.clear()


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({"status": "API is running"})


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    return Response(UserSerializer(request.user).data)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def note_list_create(request):
    if request.method == 'GET':
        cache_key = f"notes:{request.user.id}:{request.GET.urlencode()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        notes = Note.objects.filter(user=request.user).order_by('-created_at')
        serializer = NoteSerializer(notes, many=True)
        cache.set(cache_key, serializer.data, timeout=30)
        return Response(serializer.data)

    if request.method == 'POST':
        serializer = NoteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            _cache_delete_pattern(f"notes:{request.user.id}:*")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def note_detail(request, pk):
    try:
        note = Note.objects.get(pk=pk)
    except Note.DoesNotExist:
        return Response({"error": "Note not found"}, status=status.HTTP_404_NOT_FOUND)

    if note.user != request.user:
        return Response({"error": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)

    if request.method == 'GET':
        serializer = NoteSerializer(note)
        return Response(serializer.data)

    if request.method == 'PUT':
        serializer = NoteSerializer(note, data=request.data)
        if serializer.is_valid():
            serializer.save()
            _cache_delete_pattern(f"notes:{request.user.id}:*")
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        note.delete()
        _cache_delete_pattern(f"notes:{request.user.id}:*")
        return Response(status=status.HTTP_204_NO_CONTENT)

    return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)


class ProductListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()
    filterset_fields = ['name', 'price', 'stock']
    ordering_fields = ['price', 'stock', 'created_at', 'name']
    search_fields = ['name', 'description']

    def list(self, request, *args, **kwargs):
        cache_key = f"products:{request.GET.urlencode()}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, timeout=30)
        return response

    def perform_create(self, serializer):
        instance = serializer.save()
        _cache_delete_pattern("products:*")
        return instance


class ProductDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    queryset = Product.objects.all()

    def perform_update(self, serializer):
        instance = serializer.save()
        _cache_delete_pattern("products:*")
        return instance

    def perform_destroy(self, instance):
        instance.delete()
        _cache_delete_pattern("products:*")


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'product', 'created_at']
    ordering_fields = ['created_at', 'quantity', 'status']
    search_fields = ['product__name']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('product')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related('product')
