from django.db import models

class Response(models.Model):
    created_time = models.DateTimeField()
    client_id    = models.IntegerField()
    command      = models.CharField(max_length=20)
    data         = models.TextField()
    
    def __str__(self):
        return "client: {}, command:{}, data:{}".format(self.client_id, self.command,  self.data[:20]+'...')
