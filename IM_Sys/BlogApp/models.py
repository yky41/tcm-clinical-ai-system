
from django.db import models
# from UserApp.models import User
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "IM_Sys.IM_Sys.settings")
# Create your models here.
class Post(models.Model):#论坛文章
    post_id=models.AutoField(primary_key=True)#	文章编号	int
    u_id=models.ForeignKey("UserApp.User", on_delete=models.CASCADE,null=True,related_name='belonguser')#发布用户
    post_type= models.CharField(max_length=20)  # 文章类型	
    post_title= models.CharField(max_length=200)  #	文章标题
    users_like = models.ManyToManyField("UserApp.User",verbose_name='点赞用户',blank=True)
    post_content= models.TextField()  #	文章内容
    c_time = models.DateTimeField(auto_now_add=True)  # 创建时间

class News(models.Model):
    news_id=models.AutoField(primary_key=True)#	新闻编号	int
    news_title= models.CharField(max_length=200)  #	文章标题	
    news_content= models.TextField()  #	文章内容
    news_img=models.TextField(default="/static/img/news-1.jpg")#新闻展示图片地址
    c_time = models.DateTimeField(auto_now_add=True)  # 创建时间
class Comment(models.Model):#评论
    c_id=models.AutoField(primary_key=True)#评论编号
    p_id=models.ForeignKey("Post", on_delete=models.CASCADE)
    u_id=models.ForeignKey(to="UserApp.User", on_delete=models.CASCADE)
    content= models.TextField()  #	评论内容
    
    c_time = models.DateTimeField(auto_now_add=True)  # 创建时间

