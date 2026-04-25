from django import forms
from .models import Atividade, PerfilAluno, Turma, CriterioAtividade, GrupoAtividade


class AtividadeComCriteriosForm(forms.ModelForm):
    class Meta:
        model = Atividade
        fields = ['nome', 'descricao', 'criterios_avaliacao', 'data_inicio', 'data_fim', 
                  'hora_inicio', 'hora_fim', 'max_pontos_por_aluno', 'turmas']
        widgets = {
            'data_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'data_fim': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'hora_inicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hora_fim': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'criterios_avaliacao': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'max_pontos_por_aluno': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'turmas': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


class DistribuicaoPontosForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop('turma', None)
        self.atividade = kwargs.pop('atividade', None)
        self.total_disponivel = kwargs.pop('total_disponivel', 0)
        super().__init__(*args, **kwargs)
        
        if self.turma:
            for aluno in self.turma.alunos.all():
                field_name = f'pontos_aluno_{aluno.id}'
                initial_value = 0
                if args and isinstance(args[0], dict):
                    initial_value = int(args[0].get(field_name, 0))
                elif kwargs.get('initial') and field_name in kwargs['initial']:
                    initial_value = int(kwargs['initial'][field_name])
                
                self.fields[field_name] = forms.IntegerField(
                    min_value=0,
                    max_value=self.total_disponivel if self.total_disponivel > 0 else 1000,
                    required=False,
                    initial=initial_value,
                    widget=forms.NumberInput(attrs={
                        'class': 'pontos-input',
                        'step': '1',
                        'data-aluno-id': aluno.id
                    })
                )
    
    def get_pontos_por_aluno(self):
        pontos = {}
        for name, value in self.cleaned_data.items():
            if name.startswith('pontos_aluno_'):
                aluno_id = name.replace('pontos_aluno_', '')
                if value and value > 0:
                    pontos[aluno_id] = value
        return pontos
    
    def get_total_distribuido(self):
        return sum(self.get_pontos_por_aluno().values())


class GrupoForm(forms.ModelForm):
    class Meta:
        model = GrupoAtividade
        fields = ['nome', 'alunos']
    
    def __init__(self, *args, **kwargs):
        self.turma = kwargs.pop('turma', None)
        super().__init__(*args, **kwargs)
        if self.turma:
            self.fields['alunos'].queryset = PerfilAluno.objects.filter(turma=self.turma)
        self.fields['alunos'].widget = forms.CheckboxSelectMultiple()
        self.fields['alunos'].required = False


from django.forms import modelformset_factory

GrupoFormSet = modelformset_factory(
    GrupoAtividade,
    form=GrupoForm,
    fields=['nome', 'alunos'],
    extra=1,
    can_delete=True
)