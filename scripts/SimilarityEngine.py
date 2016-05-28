import django, os, re, sys
from fuzzywuzzy import fuzz, process
from nltk.corpus import stopwords
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "semesterly.settings")
django.setup()
from timetable.models import *
from timetable.school_mappers import VALID_SCHOOLS

class SimilarityFinder:

	def __init__(self):
		self.cachedStopWords = stopwords.words("english")
		self.mode_type = ""
		if len(sys.argv) != 2 or sys.argv[1] not in VALID_SCHOOLS:
			print "Please provide a valid university."
			exit()
		self.school = sys.argv[1]
		self.courses = Course.objects.filter(school=self.school)
		self.unstop_descriptions()

	def parse_classes(self):
		for course in self.courses:
			if course.description not in ["Infomration not required for this course type","Not Available","None provided"]:
				department_matches = Course.objects.filter(school=self.school, department=course.department).values_list('description', flat=True)
				matches = process.extract(course.description,department_matches, limit=4)
				try:
					itermatches = iter(matches)
					next(itermatches)
				except:
					continue
				for match in itermatches:
					course_match = Course.objects.filter(school=self.school, description=match[0])[0]
					try:
						course.related_courses.get(code=course_match.code)
						print "PREVIOUSLY related", course_match, " to ", course
					except Course.DoesNotExist:
						print "ADDING", course_match, "as related to", course
						course.related_courses.add(course_match)

	def unstop_descriptions(self):
		courses = self.courses.filter(unstopped_description="")
		for course in courses:
			print "Unstopping: " + course.name
			course.unstopped_description = ' '.join([word for word in course.description.split() if word not in (self.cachedStopWords)])
			course.save()
			print course.unstopped_description

if __name__ == '__main__':
	cf = SimilarityFinder()
	cf.parse_classes()
