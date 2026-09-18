# studhub_core/forms.py
from django import forms
from .models import Material, Discipline

class MaterialUploadForm(forms.ModelForm):
    class Meta:
        model = Material
        fields = ['title', 'description', 'material_type', 'file_attachment', 'external_url', 'discipline']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем стили Tailwind к полям формы, чтобы они выглядели красиво
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 mt-1 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:border-indigo-500 text-sm'
            })
            
    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file_attachment')
        url = cleaned_data.get('external_url')
        
        # Бизнес-логика: нельзя отправить пустую карточку
        if not file and not url:
            raise forms.ValidationError("Необходимо загрузить файл или указать внешнюю ссылку.")
        return cleaned_data
