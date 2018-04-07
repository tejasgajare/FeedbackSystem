from app import models

resposes = models.FeedbackResponse.objects.all()

for i in resposes:
	