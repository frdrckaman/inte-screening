from django.db import models
from django_crypto_fields.fields import EncryptedCharField
from edc_constants.choices import YES_NO, SELECTION_METHOD
from edc_model.models import BaseUuidModel
from edc_screening.model_mixins import ScreeningModelMixin
from edc_screening.screening_identifier import ScreeningIdentifier

from ..eligibility import check_eligible_final
from django.core.validators import RegexValidator, MinLengthValidator,\
    MaxLengthValidator


class SubjectScreeningModelError(Exception):
    pass


class ScreeningIdentifier(ScreeningIdentifier):

    template = "S{random_string}"


class SubjectScreening(
    ScreeningModelMixin,
    BaseUuidModel,
):

    identifier_cls = ScreeningIdentifier

    screening_consent = models.CharField(
        verbose_name=(
            "Has the subject given his/her verbal consent "
            "to be screened for the INTE Africa trial?"
        ),
        max_length=15,
        choices=YES_NO,
    )

    selection_method = models.CharField(
        verbose_name="How was the patient selected from the outpatients CTC?",
        max_length=25,
        choices=SELECTION_METHOD,
    )

    initials = EncryptedCharField(
        validators=[
            RegexValidator("[A-Z]{1,3}", "Invalid format"),
            MinLengthValidator(2),
            MaxLengthValidator(3),
        ],
        help_text="Use UPPERCASE letters only. May be 2 or 3 letters.",
        blank=False,
    )

    hospital_identifier = EncryptedCharField(unique=True, blank=False)

    hiv_pos = models.CharField(
        verbose_name="Is the patient HIV positive", max_length=15, choices=YES_NO
    )

    diabetic = models.CharField(
        verbose_name=(
            "Is the patient diabetic"),
        max_length=25,
        choices=YES_NO,
    )

    hypertensive = models.CharField(
        verbose_name=(
            "Is the patient hypertensive"),
        max_length=25,
        choices=YES_NO,
    )

    requires_acute_care = models.CharField(
        verbose_name=(
            "Does the patient require acute care including in-patient admission"),
        max_length=25,
        choices=YES_NO,
    )

    lives_nearby = models.CharField(
        verbose_name=(
            "Is the patient living within the catchment population of the facility"
        ),
        max_length=15,
        choices=YES_NO,
    )

    staying_nearby = models.CharField(
        verbose_name=(
            "Is the patient planning to remain in the catchment area "
            "for at least 6 months"
        ),
        max_length=15,
        choices=YES_NO,
    )

    def save(self, *args, **kwargs):
        check_eligible_final(self)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Subject Screening"
        verbose_name_plural = "Subject Screening"