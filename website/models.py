from django.db import models
from datetime import timedelta
from django.utils import timezone


# Create your models here.
class Team(models.Model):
    name = models.CharField(max_length=50, unique=True)
    team_number = models.IntegerField(default=-1)

    def __str__(self):
        return self.name


class Problem(models.Model):
    name = models.CharField(max_length=50, unique=True)
    port = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class Binary(models.Model):
    SLA_STATUS_CHOICES = (
        ('OK', 'OK'),
        ('FAIL', 'FAIL'),
        ('UNKNOWN', 'UNKNOWN'),
    )
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    hash = models.CharField(max_length=100, unique=True)
    sla_status = models.CharField(max_length=10, choices=SLA_STATUS_CHOICES, default='UNKNOWN')
    description = models.TextField(blank=True)

    def __str__(self):
        return '%s (%s)' % (self.hash[:8], {
            'OK': '+',
            'FAIL': '-',
            'UNKNOWN': '?'
        }[self.sla_status])

    def link(self):
        return '<a href="/binary/{}">{}</a>'.format(self.hash, str(self))


class PatchManager(models.Manager):
    def latest_patch(self, team_name, problem_name):
        team = Team.objects.get(name=team_name)
        problem = Problem.objects.get(name=problem_name)

        q = self.filter(team=team, binary__problem=problem)
        if q.exists():
            return q.latest('timestamp')
        else:
            return None


class Patch(models.Model):
    id = models.IntegerField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)
    binary = models.ForeignKey(Binary, on_delete=models.PROTECT)

    objects = PatchManager()


class AttackLogManager(models.Manager):
    def has_recent_successful_attack(self, team_name, problem_name):
        team = Team.objects.get(name=team_name)
        problem = Problem.objects.get(name=problem_name)

        standard = timezone.now() - timedelta(minutes=7)

        return self.filter(team=team, problem=problem, timestamp__gte=standard).exists()


class AttackLog(models.Model):
    problem = models.ForeignKey(Problem, on_delete=models.PROTECT)
    team = models.ForeignKey(Team, on_delete=models.PROTECT)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = AttackLogManager()
