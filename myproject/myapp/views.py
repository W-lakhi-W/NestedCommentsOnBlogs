# from django.shortcuts import render,get_object_or_404
# from rest_framework.response import Response
# from rest_framework import status
# from .models import Blog,User
# from .serializers import BlogSerializer,RegisterationSerializer,LoginSerializer,DetailSerializer
# from rest_framework.views import APIView
# from django.http import Http404
# from rest_framework.permissions import IsAuthenticated
# from .permissions import IsOwnerOrReadOnly
# from rest_framework_simplejwt.tokens import RefreshToken

# # Create your views here.
# class RegisterView(APIView):

#     def post(self,request):
#         serializer = RegisterationSerializer(data = request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response({'message':"User is created Successfully"},status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# class LoginView(APIView):

#     def post(self,request):
#         serializer = LoginSerializer(data = request.data)
#         if serializer.is_valid():
            
#             user = serializer.validated_data['user']
#             refresh = RefreshToken.for_user(user)

#             return Response(
#                 {
#                     "refresh":str(refresh),
#                     "access":str(refresh.access_token),
#                     'username': user.username,
#                 },
#                 status=status.HTTP_200_OK
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# class BlogView(APIView):

#     permission_classes = [IsOwnerOrReadOnly]

#     def get(self,request):

#         obj = Blog.objects.all()

#         serializer = BlogSerializer(obj,many=True)

#         return Response(serializer.data,status=status.HTTP_200_OK)
    
#     def post(self,request):

#         print(request.FILES)

#         serializer = BlogSerializer(data = request.data,context={'request': request})
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data,status=status.HTTP_201_CREATED)
#         return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
    
# class EditBlog(APIView):

#     permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

#     def get_object(self, pk):
#         try:
#             return Blog.objects.get(pk=pk)
#         except Blog.DoesNotExist:
#             raise Http404

#     def get(self,request,pk):
#         blog = self.get_object(pk)

#         serializer = BlogSerializer(blog)
#         return Response(serializer.data)

    
#     def put(self,request,pk):
#         blog = self.get_object(pk)
#         self.check_object_permissions(request, blog)
#         serializer = BlogSerializer(blog, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     def delete(self,request,pk):
#         blog = self.get_object(pk=pk)
#         self.check_object_permissions(request, blog)
#         blog.delete()
#         return Response({"message": "Blog deleted successfully."}, status=status.HTTP_204_NO_CONTENT)


# class BlogDetail(APIView):
#     permission_classes = [IsOwnerOrReadOnly]
#     def get_object(self, pk):
#         try:
#             return Blog.objects.get(pk=pk)
#         except Blog.DoesNotExist:
#             raise Http404
    
#     def get(self,request,pk):
#         blog = self.get_object(pk=pk)
#         self.check_object_permissions(request, blog)
#         serializer = DetailSerializer(blog)
#         return Response(serializer.data)

# class DashboardBlogs(APIView):

#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         blogs = Blog.objects.filter(owner=self.request.user)
#         serializer = BlogSerializer(blogs,many=True)
#         return Response(serializer.data)

from rest_framework import status, generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken


from .models import Blog,Comment
from .serializers import (
    BlogSerializer,
    RegisterationSerializer,
    LoginSerializer,
    DetailSerializer,
    CommentSerializer,
    UserSerializer,
)
from .permissions import IsOwnerOrReadOnly,IsOwnerOrAdmin
from rest_framework.permissions import IsAuthenticatedOrReadOnly,IsAuthenticated

from django.contrib.auth import get_user_model

User = get_user_model()

# --- User Registration ---
class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': "User created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- User Login with JWT ---
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# --- Blog List & Create ---
class BlogListCreateView(generics.ListCreateAPIView):
    """
    GET: List all blogs
    POST: Create a blog (authenticated user only)
    """
    serializer_class = BlogSerializer
    queryset = Blog.objects.all().order_by('-created_at')
    permission_classes = [IsOwnerOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

# --- Blog Retrieve, Update, Delete ---
class BlogRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET: Retrieve a blog (detailed)
    PUT: Update a blog (owner only)
    DELETE: Delete a blog (owner only)
    """
    serializer_class = BlogSerializer
    queryset = Blog.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DetailSerializer
        return BlogSerializer

# --- Dashboard: User's Own Blogs ---
class DashboardBlogsView(generics.ListAPIView):
    """
    GET: List all blogs owned by the current authenticated user.
    """
    serializer_class = BlogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Blog.objects.filter(owner=self.request.user)

# --- Optionally, if you need a simple blog Detail as in BlogDetail ---
class BlogDetailView(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, pk):
        blog = get_object_or_404(Blog, pk=pk)
        self.check_object_permissions(request, blog)
        serializer = DetailSerializer(blog)
        return Response(serializer.data)



class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request):
        blog_id = request.GET.get("blog")
        if not blog_id:
            return Response({"error": "Blog ID is required"}, status=400)

        comments = Comment.objects.filter(blog_id=blog_id, parent=None).order_by("-created_at")
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        blog_id = request.data.get("blog")
        content = request.data.get("content")
        parent_id = request.data.get("parent")

        if not blog_id or not content:
            return Response({"error": "Blog ID and content are required"}, status=400)

        parent = Comment.objects.filter(id=parent_id).first() if parent_id else None

        comment = Comment.objects.create(
            blog_id=blog_id,
            user=request.user,
            content=content,
            parent=parent
        )
        serializer = CommentSerializer(comment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CommentDeleteView(APIView):
    permission_classes = [IsOwnerOrAdmin]

    def delete(self, request, pk):
        try:
            comment = Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return Response({"error": "Comment not found"}, status=404)

        # Only the owner or admin can delete
        if comment.user != request.user and not request.user.is_staff:
            return Response({"error": "You do not have permission to delete this comment"}, status=403)

        comment.delete()
        return Response({"message": "Comment deleted successfully"}, status=204)
    

class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)