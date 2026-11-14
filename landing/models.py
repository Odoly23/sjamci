from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone

LANGS = ('tet', 'pt', 'en', 'id')


class TranslatedMixin:
    """Kampu iha Tetun (prinsipál) ho tradusaun opsionál; se mamuk uza Tetun."""

    def text(self, field, lang):
        if lang != 'tet':
            value = getattr(self, f'{field}_{lang}', '')
            if value:
                return value
        return getattr(self, field)


class Announcement(TranslatedMixin, models.Model):
    """Informasaun importante ne'ebé hatudu iha pajina públiku."""
    LEVELS = [('info', 'Informasaun'), ('important', 'Importante')]

    title = models.CharField(max_length=160, verbose_name='Títulu (Tetun)')
    body = models.TextField(verbose_name='Konteúdu (Tetun)')
    title_pt = models.CharField(max_length=160, blank=True, verbose_name='Títulu (Português)')
    body_pt = models.TextField(blank=True, verbose_name='Konteúdu (Português)')
    title_en = models.CharField(max_length=160, blank=True, verbose_name='Títulu (English)')
    body_en = models.TextField(blank=True, verbose_name='Konteúdu (English)')
    title_id = models.CharField(max_length=160, blank=True, verbose_name='Títulu (Indonesia)')
    body_id = models.TextField(blank=True, verbose_name='Konteúdu (Indonesia)')
    level = models.CharField(max_length=10, choices=LEVELS, default='info', verbose_name='Nivel')
    publish_date = models.DateField(default=timezone.localdate, verbose_name='Data publikasaun')
    is_published = models.BooleanField(default=True, verbose_name='Publika')

    class Meta:
        ordering = ['-publish_date', '-id']
        verbose_name = 'Informasaun Importante'
        verbose_name_plural = 'Informasaun Importante'

    def __str__(self):
        return self.title


class Slide(TranslatedMixin, models.Model):
    """Slide iha pajina públiku. Se la iha slide ativu, sistema uza slide default."""
    title = models.CharField(max_length=120, verbose_name='Títulu (Tetun)')
    subtitle = models.CharField(max_length=240, blank=True, verbose_name='Sub-títulu (Tetun)')
    title_pt = models.CharField(max_length=120, blank=True, verbose_name='Títulu (Português)')
    subtitle_pt = models.CharField(max_length=240, blank=True, verbose_name='Sub-títulu (Português)')
    title_en = models.CharField(max_length=120, blank=True, verbose_name='Títulu (English)')
    subtitle_en = models.CharField(max_length=240, blank=True, verbose_name='Sub-títulu (English)')
    title_id = models.CharField(max_length=120, blank=True, verbose_name='Títulu (Indonesia)')
    subtitle_id = models.CharField(max_length=240, blank=True, verbose_name='Sub-títulu (Indonesia)')
    image = models.ImageField(upload_to='landing/slides/', blank=True,
                              validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
                              verbose_name='Imajen (rekomenda 1600×700)')
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Orden')
    is_active = models.BooleanField(default=True, verbose_name='Ativu')

    class Meta:
        ordering = ['order', 'id']
        verbose_name = 'Slide'
        verbose_name_plural = 'Slide'

    def __str__(self):
        return self.title
