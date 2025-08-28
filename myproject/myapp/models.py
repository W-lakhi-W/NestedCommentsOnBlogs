# from django.db import models
# from django.contrib.auth.models import User

# # Create your models here.


# class Blog(models.Model):

#     title = models.CharField(max_length=200)
#     content = models.TextField(max_length=400000)
#     owner = models.ForeignKey(User,on_delete=models.CASCADE)

#     # def __str__(self):
#     #     return self.id


from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()  # No need for max_length; it's unlimited by default
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blogs'  # Optional: allows user.blogs.all()
    )
    created_at = models.DateTimeField(auto_now_add=True)  # Optional: for timestamps
    updated_at = models.DateTimeField(auto_now=True)      # Optional: for timestamps

    def __str__(self):
        return f"{self.title} by {self.owner.username}"
    
    
class Comment(models.Model):
    blog = models.ForeignKey(Blog, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'
