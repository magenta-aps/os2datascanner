#!/usr/bin/env python
# The contents of this file are subject to the Mozilla Public License
# Version 2.0 (the "License"); you may not use this file except in
# compliance with the License. You may obtain a copy of the License at
#    http://www.mozilla.org/MPL/
#
# Software distributed under the License is distributed on an "AS IS"basis,
# WITHOUT WARRANTY OF ANY KIND, either express or implied. See the License
# for the specific language governing rights and limitations under the
# License.
#
# OS2datascanner was developed by Magenta in collaboration with OS2 the
# Danish community of open source municipalities (https://os2.eu/).
#
# The code is currently governed by OS2 the Danish community of open
# source municipalities ( https://os2.eu/ )
import collections
from urllib.parse import urlencode
import structlog
from django.conf import settings

from django.db.models import Count
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import View, TemplateView, ListView
from django.db.models import Q

from ..models.documentreport_model import DocumentReport
from ..models.roles.defaultrole_model import DefaultRole
from ..models.userprofile_model import UserProfile
from ..models.organization_model import Organization

from os2datascanner.engine2.rules.cpr import CPRRule
from os2datascanner.engine2.rules.regex import RegexRule
from os2datascanner.engine2.rules.rule import Sensitivity

logger = structlog.get_logger()

RENDERABLE_RULES = (CPRRule.type_label, RegexRule.type_label,)


class LoginRequiredMixin(View):
    """Include to require login."""

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        """Check for login and dispatch the view."""
        return super().dispatch(*args, **kwargs)


class LoginPageView(View):
    template_name = 'login.html'


class MainPageView(ListView, LoginRequiredMixin):
    template_name = 'index.html'
    paginate_by = 10  # Determines how many objects pr. page.

class LogoutPageView(TemplateView, View):
    template_name = 'logout.html'


class MainPageView(TemplateView, LoginRequiredMixin):
    template_name = 'index.html'
    data_results = None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        # First attempt to make some usefull logging.
        # The report module task is to log every action the user makes
        # for the security of the user.
        # If the system can document the users actions the user can defend
        # them self against any allegations of wrong doing.
        logger.info('{} is watching {}.'.format(user, self.template_name))

        roles = user.roles.select_subclasses() or [DefaultRole(user=user)]
        results = DocumentReport.objects.none()
        for role in roles:
            results |= role.filter(DocumentReport.objects.all())

        # Calls func to do initial filtering
        filter_matches(results)
        # Results are grouped by the rule they where found with,
        # together with the count.
        sensitivities = {}
        for dr in results:
            if dr.matches:
                sensitivity = dr.matches.sensitivity
                if not sensitivity in sensitivities:
                    sensitivities[sensitivity] = 0
                sensitivities[sensitivity] += 1
        context['dashboard_results'] = sensitivities

        context['dashboard_results'] = {}
        context['dashboard_results']['critical'] = Sensitivity.CRITICAL
        context['dashboard_results']['problem'] = Sensitivity.PROBLEM
        context['dashboard_results']['warning'] = Sensitivity.WARNING
        context['dashboard_results']['notification'] = Sensitivity.NOTICE

        sensitivity_list = [e.value for e in Sensitivity]  # Makes a list of possible sensitivity values
        sensitivity_list.remove(0)  # Removes "information" 0 value, not possible to use or show currently

        # Checks which sensitivities have matches and removes those from list.
        for sensitivity, count in sensitivities.items():
            if sensitivity.value in sensitivity_list:
                sensitivity_list.remove(sensitivity.value)

            # Displays the matches with sensitivities
            for s, c in sensitivities.items():
                # Notification uses both NOTICE here and notification elsewhere.
                # Should consider making it consistent to avoid this extra if statement
                if s.value == 250:
                    temp = {'sensitivity': Sensitivity(s), 'count': c, 'label': "notification"}
                    context['dashboard_results']['notification'] = temp
                else:
                    temp = {'sensitivity': Sensitivity(s), 'count': c, 'label': Sensitivity(s).name}
                    context['dashboard_results'][s.name.lower()] = temp

        # Displays sensitivity categories with no matches.
        for se in sensitivity_list:
            # Same notification "issue" as above
            if se == 250:
                temp = {'sensitivity': Sensitivity(se), 'count': 0, 'label': "notification"}
                context['dashboard_results']['notification'] = temp
            else:
                temp = {'sensitivity': Sensitivity(se), 'count': 0, 'label': Sensitivity(se).name}
                context['dashboard_results'][Sensitivity(se).name.lower()] = temp

        return context


class SensitivityPageView(ListView, LoginRequiredMixin):
    template_name = 'sensitivity.html'
    paginate_by = 25  # Determines how many objects pr. page.
    context_object_name = "matches"  # object_list renamed to something more relevant
    model = DocumentReport
    matches = DocumentReport.objects.filter(
        data__matches__matched=True).filter(
        resolution_status__isnull=True)
    scannerjob_filters = None

    def get_queryset(self):
        user = self.request.user
        roles = user.roles.select_subclasses() or [DefaultRole(user=user)]

        # Filter by organization
        try:
            user_organization = user.profile.organization
            # Include matches without organization (backwards compatibility)
            self.matches = self.matches.filter(Q(organization=None) | Q(organization=user_organization))
        except UserProfile.DoesNotExist:
            # No UserProfile has been set on the request user
            # Default action depends on how many organization objects we have
            # If more than one exist, limit matches to ones without an organization (safety measure)
            if Organization.objects.count() > 1:
                self.matches = self.matches.filter(organization=None)

        for role in roles:
            # Filter matches by role.
            self.matches = role.filter(self.matches)

        if self.request.GET.get('scannerjob') \
                and self.request.GET.get('scannerjob') != 'all':
            # Filter by scannerjob
            self.matches = self.matches.filter(
                data__scan_tag__scanner__pk=int(
                    self.request.GET.get('scannerjob'))
            )
        if self.request.GET.get('sensitivities') \
                and self.request.GET.get('sensitivities') != 'all':
            # Filter by sensitivities
            self.matches = self.matches.filter(
                sensitivity=int(
                    self.request.GET.get('sensitivities'))
            )

        # matches are always ordered by sensitivity desc. and probability desc.
        return self.matches

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["renderable_rules"] = RENDERABLE_RULES

        if self.scannerjob_filters is None:
            # Create select options
            self.scannerjob_filters = self.matches.order_by(
                'data__scan_tag__scanner__pk').values(
                'data__scan_tag__scanner__pk').annotate(
                total=Count('data__scan_tag__scanner__pk')
            ).values(
                'data__scan_tag__scanner__name',
                'total',
                'data__scan_tag__scanner__pk'
            )

        context['scannerjobs'] = (self.scannerjob_filters,
                                  self.request.GET.get('scannerjob', 'all'))

        sensitivities = self.matches.order_by(
            '-sensitivity').values(
            'sensitivity').annotate(
            total=Count('sensitivity')
        ).values(
            'sensitivity', 'total'
        )

        context['sensitivities'] = (((Sensitivity(s["sensitivity"]),
                                      s["total"]) for s in sensitivities),
                                    self.request.GET.get('sensitivities', 'all'))

        return context

class StatisticsPageView(TemplateView):
    template_name = 'statistics.html'


class ApprovalPageView(TemplateView):
    template_name = 'approval.html'


class StatsPageView(TemplateView):
    template_name = 'stats.html'


class SettingsPageView(TemplateView):
    template_name = 'settings.html'


class AboutPageView(TemplateView):
    template_name = 'about.html'

# Function to do initial filtering in matches. Used at both index and sensitivity page.
def filter_matches(results):
    # Filter out anything we don't know how to show in the UI
    data_results = []
    for result in results:
        if (result.data
                and "matches" in result.data
                and result.data["matches"]):
            match_message_raw = result.data["matches"]
            renderable_fragments = [
                frag for frag in match_message_raw["matches"]
                if frag["rule"]["type"] in RENDERABLE_RULES
                   and frag["matches"]]
            if renderable_fragments:
                match_message_raw["matches"] = renderable_fragments
                # Rules are under no obligation to produce matches in any
                # particular order, but we want to display them in
                # descending order of probability
                for match_fragment in renderable_fragments:
                    match_fragment["matches"].sort(
                        key=lambda match_dict: match_dict.get(
                            "probability", 0.0),
                        reverse=True)
                data_results.append(result)
    data_results.sort(key=
                      lambda result: (result.matches.sensitivity.value, result.pk))
    return data_results


def oidc_op_logout_url_method(request):
    logout_url = settings.LOGOUT_URL
    return_to_url = settings.LOGOUT_REDIRECT_URL
    return logout_url + '?' + urlencode({'redirect_uri': return_to_url, 'client_id': settings.OIDC_RP_CLIENT_ID})
