from django.contrib import admin
from django.template.loader import render_to_string
from django.urls.base import reverse
from django.urls.exceptions import NoReverseMatch
from django.utils.safestring import mark_safe
from django.utils.translation import gettext as _
from django_audit_fields.admin import audit_fieldset_tuple
from edc_dashboard.url_names import url_names
from edc_model_admin import SimpleHistoryAdmin
from edc_model_admin.dashboard import ModelAdminSubjectDashboardMixin

from ..admin_site import inte_screening_admin
from ..eligibility import format_reasons_ineligible
from ..forms import SubjectScreeningForm
from ..models import SubjectScreening


@admin.register(SubjectScreening, site=inte_screening_admin)
class SubjectScreeningAdmin(ModelAdminSubjectDashboardMixin, SimpleHistoryAdmin):

    form = SubjectScreeningForm

    post_url_on_delete_name = "screening_listboard_url"
    subject_listboard_url_name = "screening_listboard_url"

    additional_instructions = (
        "Patients must meet ALL of the inclusion criteria and NONE of the "
        "exclusion criteria in order to proceed to the final screening stage"
    )

    fieldsets = (
        [
            None,
            {
                "fields": (
                    "screening_consent",
                    "report_datetime",
                    "clinic_type",
                    "selection_method",
                ),
            },
        ],
        ["Demographics", {"fields": ("initials", "gender", "age_in_years",),},],
        [
            "Criteria",
            {
                "fields": (
                    "qualifying_condition",
                    "lives_nearby",
                    "requires_acute_care",
                ),
            },
        ],
        [
            "Additional Comments",
            {
                "fields": (
                    "unsuitable_for_study",
                    "reasons_unsuitable",
                    "unsuitable_agreed",
                ),
            },
        ],
        audit_fieldset_tuple,
    )

    list_display = (
        "screening_identifier",
        "eligiblity_status",
        "demographics",
        "reasons",
        "report_datetime",
        "user_created",
        "created",
    )

    list_filter = (
        "report_datetime",
        "gender",
        "eligible",
        "consented",
        "refused",
        "eligible",
        "clinic_type",
        "qualifying_condition",
    )

    search_fields = (
        "screening_identifier",
        "subject_identifier",
        "initials",
        "reasons_ineligible",
    )

    radio_fields = {
        "clinic_type": admin.VERTICAL,
        "gender": admin.VERTICAL,
        "qualifying_condition": admin.VERTICAL,
        "lives_nearby": admin.VERTICAL,
        "requires_acute_care": admin.VERTICAL,
        "screening_consent": admin.VERTICAL,
        "selection_method": admin.VERTICAL,
        "unsuitable_agreed": admin.VERTICAL,
        "unsuitable_for_study": admin.VERTICAL,
    }

    def post_url_on_delete_kwargs(self, request, obj):
        return {}

    def demographics(self, obj=None):
        return mark_safe(
            f"{obj.get_gender_display()} {obj.age_in_years}yrs {obj.initials.upper()}"
        )

    def reasons(self, obj=None):
        return format_reasons_ineligible(obj.reasons_ineligible)

    def eligiblity_status(self, obj=None):
        return "Eligible" if obj.eligible else "Ineligible"

    def dashboard(self, obj=None, label=None):
        try:
            url = reverse(
                self.get_subject_dashboard_url_name(),
                kwargs=self.get_subject_dashboard_url_kwargs(obj),
            )
        except NoReverseMatch:
            url = reverse(url_names.get("screening_listboard_url"), kwargs={})
            context = dict(
                title=_("Go to screening listboard"),
                url=f"{url}?q={obj.screening_identifier}",
                label=label,
            )
        else:
            context = dict(title=_("Go to subject dashboard"), url=url, label=label)
        return render_to_string("dashboard_button.html", context=context)
