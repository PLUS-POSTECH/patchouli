import os.path

from django import forms
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from patchouli import settings
from .models import *


def response_with_code(content, code):
    response = HttpResponse(content)
    response.status_code = code
    return response


class IndexView(View):
    def get(self, request):
        def mapping(problem):
            attack_count = 0
            for team in Team.objects.all():
                if AttackLog.objects.has_recent_successful_attack(team.name, problem.name):
                    attack_count += 1

            return {
                'name': problem.name,
                'port': problem.port,
                'our_patch': Patch.objects.latest_patch(settings.TEAM_NAME, problem.name),
                'attack_count': attack_count,
            }
        return render(request, 'index.html', {
            'problems': map(mapping, Problem.objects.all()),
        })


class ProblemView(View):
    def get(self, request, name):
        problem = get_object_or_404(Problem, name=name)

        team_info = []
        hash_counter = {}
        for team in Team.objects.all():
            latest_patch = Patch.objects.latest_patch(team.name, problem.name)

            has_recent_attack = AttackLog.objects.has_recent_successful_attack(team.name, problem.name)
            attack_time = None
            if has_recent_attack:
                attack_time = AttackLog.objects.filter(team=team, problem=problem).latest('timestamp').timestamp

            team_info.append({
                'name': team.name,
                'latest_patch': latest_patch,
                'attacking': has_recent_attack,
                'attack_time': attack_time,
            })
            if latest_patch:
                k = latest_patch.binary.hash
                if k in hash_counter:
                    hash_counter[k] += 1
                else:
                    hash_counter[k] = 1

        return render(request, 'problem.html', {
            'problem_name': name,
            'problem_port': problem.port,
            'teams': team_info,
            'hash_counter': hash_counter,
        })


class BinaryView(View):
    def get(self, request, hash):
        problem = get_object_or_404(Problem, binary__hash=hash)
        download_url = os.path.join(settings.MEDIA_URL + '{}/{}.bin'.format(problem.name, hash))

        # <a href="/media/{{ legit_binary.problem.name }}/{{ legit_binary.hash }}.bin">Original Binary (LegitBS)</a>
        first_patch = Patch.objects.filter(binary__hash=hash).earliest('timestamp')

        binary = get_object_or_404(Binary, hash=hash)

        return render(request, 'binary.html', {
            'binary': binary,
            'first_patch': first_patch,
            'download_url': download_url,
        })


class ApiNewPatchForm(forms.Form):
    patch_id = forms.IntegerField()
    problem_name = forms.CharField(max_length=50)
    team_name = forms.CharField(max_length=50)
    hash = forms.CharField(max_length=100)
    binary_file = forms.FileField()


@method_decorator(csrf_exempt, name='dispatch')
class ApiNewPatchView(View):
    def post(self, request):
        form = ApiNewPatchForm(request.POST, request.FILES)

        if form.is_valid():
            patch_id = form.cleaned_data['patch_id']
            if Patch.objects.filter(id=patch_id).exists():
                return response_with_code('Exist', 200)

            # team
            team_name = form.cleaned_data['team_name']
            team, _ = Team.objects.get_or_create(name=team_name)

            # problem
            problem_name = form.cleaned_data["problem_name"]
            problem, _ = Problem.objects.get_or_create(name=problem_name)

            # binary
            hash = form.cleaned_data['hash']
            binaries = Binary.objects.filter(hash=hash)
            if binaries.exists():
                binary = binaries.first()
            else:
                binary = Binary(
                    problem=problem,
                    hash=hash,
                    description=''
                )
                binary.save()

                problem_dir = os.path.join(settings.MEDIA_ROOT, problem_name)
                if not os.path.exists(problem_dir):
                    os.makedirs(problem_dir)
                binary_path = os.path.join(problem_dir, '{}.bin'.format(hash))
                with open(binary_path, 'wb') as f:
                    for chunk in request.FILES['binary_file']:
                        f.write(chunk)

            # patch
            patch = Patch(
                id=patch_id,
                team=team,
                binary=binary
            )
            patch.save()

            return response_with_code('Added', 200)
        return response_with_code('Invalid', 400)


class ApiNewAttackForm(forms.Form):
    team_id = forms.IntegerField()
    problem_name = forms.CharField(max_length=50)


@method_decorator(csrf_exempt, name='dispatch')
class ApiNewAttackView(View):
    def post(self, request):
        form = ApiNewAttackForm(request.POST)

        if form.is_valid():
            # team
            team_id = form.cleaned_data['team_id']
            team = get_object_or_404(Team, team_number=team_id)

            # problem
            problem_name = form.cleaned_data["problem_name"]
            problem = get_object_or_404(Problem, name=problem_name)

            # attack log
            log = AttackLog(
                team=team,
                problem=problem,
            )
            log.save()

            return response_with_code('Added', 200)
        return response_with_code('Invalid', 400)
